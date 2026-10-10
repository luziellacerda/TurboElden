from __future__ import annotations

import hashlib
import random
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "versions/station-render-online-r106-20261010/native/d0"
PATCH = ROOT / "versions/station-native-cover-field-proposed-20261010/native/d0"


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


base_shader = text(BASE / "magazine_shader.h")
field_shader = text(PATCH / "magazine_shader.h")
base_native = text(BASE / "native_magazine.h")
field_native = text(PATCH / "native_magazine.h")
field_cache = text(PATCH / "native_magazine_field.h")
carousel = text(PATCH / "native_carousel.cpp")
canonical_glsl = field_shader.split('R"NEOMAG(', 1)[1].rsplit(')NEOMAG";', 1)[0]
assert canonical_glsl == text(PATCH / "premium-magazine-led-android.glsl")

# The bake vertex path is a full-screen triangle strip in clip space.  It must
# not depend on MVPMatrix, because the bake program intentionally has no MVP
# uniform location or upload.  An all-zero default matrix would otherwise
# produce w=0 for every vertex and silently leave an empty field texture.
bake_clip_block = (
    "#ifdef MAGAZINE_FIELD_BAKE\n"
    " // The prepass quad is already in clip space.  It must never depend on an\n"
    " // unset native carousel matrix (all-zero uniforms rasterize no fragments).\n"
    " gl_Position=vec4(VertexCoord,0.0,1.0);\n"
    "#else\n"
    " gl_Position=MVPMatrix*vec4(VertexCoord,0.0,1.0);\n"
    "#endif"
)
assert bake_clip_block in field_shader
assert 'bakeMvp' not in field_cache

quad = ((-1.0, -1.0, 1.0), (-1.0, 1.0, 1.0),
        (1.0, -1.0, 1.0), (1.0, 1.0, 1.0))


def triangle_area(a, b, c):
    assert a[2] == b[2] == c[2] == 1.0
    return abs((b[0] - a[0]) * (c[1] - a[1]) -
               (b[1] - a[1]) * (c[0] - a[0])) * 0.5


bake_clip_coverage = triangle_area(quad[0], quad[1], quad[2]) + triangle_area(
    quad[2], quad[1], quad[3]
)
assert bake_clip_coverage == 4.0

# Removing the single optimization dispatch and header restores native_magazine
# byte-for-byte.  This is the executable fallback proof, including uniforms,
# time expression, hue selection and original draw call.
native_added = (
    " // The cache is an optimization only.  It requires the already-proven R106\n"
    " // vertex classifier; any failure falls through to the integral R106 program.\n"
    " if(p.vertexClassifier&&drawMagazineStaticField(q,count,src,dst,model,hue,matrix))return true;\n"
)
assert field_native.replace('#include "native_magazine_field.h"\n', "").replace(
    native_added, ""
) == base_native
assert carousel.index('#include "native_space3d.h"') < carousel.index(
    '#include "native_magazine.h"'
)

# Everything after the four static scalars remains byte-for-byte R106: clock,
# N64 short circuit, LED palette, gain, bloom, compositing and output.
tail_marker = "    float n64Mode=step(1.5,activeMagazineModel)*(1.0-step(2.5,activeMagazineModel));"
assert base_shader[base_shader.index(tail_marker) :] == field_shader[field_shader.index(tail_marker) :]

# The one-time bake evaluates the same R106 emitter and the same 8 directions
# at 2/5 artwork pixels.  The draw pass restores the four scalar names from
# RGBA in the same order before entering the unchanged tail above.
for exact in (
    "centralRegion=region(p);",
    "mask=emitterWithRegion(p,centralRegion);",
    "nearGlow+=emitter(p+dir*2.0);",
    "wideGlow+=emitter(p+dir*5.0);",
    "nearGlow/=8.0; wideGlow/=8.0;",
    "FragColor=vec4(mask,nearGlow,wideGlow,centralRegion);",
    "mask=staticField.r;",
    "nearGlow=staticField.g;",
    "wideGlow=staticField.b;",
    "centralRegion=staticField.a;",
):
    assert exact in field_shader, exact

# The integral fallback is the full R106 program and draw path, not a reduced
# approximation.  The original clock expression occurs in both paths.
clock = "(int)(((U)now*60u)/1000u)"
assert clock in base_native and clock in field_native and clock in field_cache
assert "if(p.vertexClassifier&&drawMagazineStaticField" in field_native
assert "g.UseProgram(p.id);g.UniformMatrix4fv" in field_native

# Cache identity and invalidation cover texture, catalog identity/revision,
# model and the complete viewport.  clearTextures explicitly invalidates it.
for token in (
    "c.source==source",
    "c.identity==identity",
    "c.model==modelKey",
    "c.viewport[i]==viewport[i]",
    "syncedRevision",
    "invalidateMagazineStaticField();",
):
    assert token in field_cache or token in carousel, token

# Every state family mutated by the prepass has an explicit save/restore path.
for token in (
    "SpaceState restore",
    "MagazineFieldCapabilityRestore extraRestore",
    "MagazineFieldReadFramebufferRestore readRestore",
    "s.BindFramebuffer",
    "s.Viewport",
    "s.ActiveTexture",
    "s.BindTexture",
    "s.BindBuffer",
    "s.BindVertexArray",
    "s.ColorMask",
    "s.DepthMask",
    "g.UseProgram",
    "m.BindSampler(1,0)",
    "m.BindSampler(1,(unsigned)samplerBinding)",
):
    assert token in field_cache, token

# GL_TEXTURE_BINDING_2D is not an indexed state in GLES.  The strict mock
# below deliberately reports GL_INVALID_ENUM for the former glGetIntegeri_v
# form, then exercises the patched active-unit/GetIntegerv sequence and proves
# that the caller's active unit and bindings survive without consuming or
# introducing a GL error.
GL_INVALID_ENUM = 0x0500
GL_ACTIVE_TEXTURE = 0x84E0
GL_TEXTURE0 = 0x84C0
GL_TEXTURE_BINDING_2D = 0x8069


class StrictGLES:
    def __init__(self):
        self.active = GL_TEXTURE0 + 3
        self.bindings = {GL_TEXTURE0: 101, GL_TEXTURE0 + 1: 202,
                         GL_TEXTURE0 + 3: 303}
        self.errors = []

    def active_texture(self, unit):
        if unit < GL_TEXTURE0 or unit >= GL_TEXTURE0 + 32:
            self.errors.append(GL_INVALID_ENUM)
            return
        self.active = unit

    def get_integerv(self, pname):
        if pname == GL_ACTIVE_TEXTURE:
            return self.active
        if pname == GL_TEXTURE_BINDING_2D:
            return self.bindings.get(self.active, 0)
        self.errors.append(GL_INVALID_ENUM)
        return 0

    def get_integeri_v(self, pname, index):
        # GLES indexed queries accept only indexed state names.  A texture
        # binding queried this way is the regression this test must catch.
        del index
        self.errors.append(GL_INVALID_ENUM)
        return 0

    def bind_texture_2d(self, texture):
        self.bindings[self.active] = texture


legacy_gl = StrictGLES()
legacy_gl.get_integeri_v(GL_TEXTURE_BINDING_2D, 0)
assert legacy_gl.errors == [GL_INVALID_ENUM]

strict_gl = StrictGLES()
initial_active = strict_gl.get_integerv(GL_ACTIVE_TEXTURE)
initial_bindings = dict(strict_gl.bindings)
strict_gl.active_texture(GL_TEXTURE0)
source_binding = strict_gl.get_integerv(GL_TEXTURE_BINDING_2D)
strict_gl.active_texture(initial_active)
assert source_binding == 101
assert strict_gl.active == initial_active
assert strict_gl.bindings == initial_bindings
assert strict_gl.errors == []

strict_gl.active_texture(GL_TEXTURE0 + 1)
field_binding = strict_gl.get_integerv(GL_TEXTURE_BINDING_2D)
strict_gl.bind_texture_2d(999)
strict_gl.active_texture(GL_TEXTURE0 + 1)
strict_gl.bind_texture_2d(field_binding)
strict_gl.active_texture(initial_active)
assert strict_gl.active == initial_active
assert strict_gl.bindings == initial_bindings
assert strict_gl.errors == []

assert "GetIntegeri_v" not in field_cache
assert "GetError" not in field_cache
assert (
    "s.ActiveTexture(0x84c0);g.GetIntegerv(0x8069,&source);"
    "s.ActiveTexture((unsigned)active);"
) in field_cache
assert "s.ActiveTexture(0x84c1);g.GetIntegerv(0x8069,&fieldBinding);" in field_cache
assert (
    "s.ActiveTexture(0x84c1);s.BindTexture(0x0de1,(unsigned)fieldBinding);"
    "m.BindSampler(1,(unsigned)samplerBinding);s.ActiveTexture((unsigned)active);"
) in field_cache

# Target creation is fail-closed and transactional.  In particular, framebuffer
# name 0 must never be interpreted as a complete cache target, a fresh texture
# is required when dimensions change (so TexImage OOM cannot expose old
# storage), and the new target is committed only after the FBO, object types
# and complete VBO storage pass. Same-sized cover changes reuse storage without
# reallocating ~5 MiB. No post-draw GL_QUERY_RESULT stall is allowed.
for exact in (
    "c.valid=false;c.source=0;c.identity=0;c.model=-1;",
    "bool reuseStorage=c.texture&&c.fbo&&c.width==width&&c.height==height;",
    "if(!target.texture||!target.fbo){c.unsupported=true;return false;}",
    "if(!m.IsTexture(target.texture)){c.unsupported=true;return false;}",
    "if(!m.IsFramebuffer(target.fbo)){c.unsupported=true;return false;}",
    "if(!c.vao)return false;",
    "if(!c.vbo)return false;",
    "if(!m.IsBuffer(c.vbo)){resetMagazineFieldGeometry();return false;}",
    "m.GetBufferParameteriv(0x8892,0x8764,&bufferBytes);",
    "if(bufferBytes!=(int)(sizeof(Vertex)*4))",
    "target.commit();",
):
    assert exact in field_cache, exact
assert field_cache.count("TexImage2D") == 1
assert field_cache.index("if(!target.texture||!target.fbo)") < field_cache.index(
    "CheckFramebufferStatus"
)
assert field_cache.index("if(bufferBytes!=(int)(sizeof(Vertex)*4))") < field_cache.index(
    "target.commit();"
)
assert "GetQueryObjectuiv" not in field_cache
assert "GL_QUERY_RESULT" not in field_cache
assert "GenQueries" not in field_cache
assert "BindFramebuffer(0x8ca8,(unsigned)read)" in field_cache
assert "readRestore.active&&readRestore.read==(int)c.fbo" in field_cache


def model_transaction(old_texture=41, old_fbo=42, old_size=(706, 934),
                      wanted_size=(706, 934), generated=(51, 52),
                      teximage_ok=True, framebuffer_complete=True,
                      buffer_bytes=80):
    # Mirrors the acceptance gates, not GL rendering.  It records whether an
    # allocation was attempted and which handles survive a failed transaction.
    valid = False
    key = None
    reuse = bool(old_texture and old_fbo and old_size == wanted_size)
    allocated = False
    if reuse:
        texture, fbo = old_texture, old_fbo
    else:
        allocated = True
        texture, fbo = generated
        if not texture or not fbo:
            return valid, key, (old_texture, old_fbo), allocated
        if not teximage_ok:
            framebuffer_complete = False
    if not texture or not fbo or not framebuffer_complete:
        return valid, key, (old_texture, old_fbo), allocated
    if buffer_bytes != 80:
        return valid, key, (old_texture, old_fbo), allocated
    valid = True
    key = "new-cover"
    return valid, key, (texture, fbo), allocated


# Even a mocked COMPLETE default framebuffer cannot pass with generated ID 0.
zero_id_case = model_transaction(old_texture=0, old_fbo=0, old_size=(0, 0),
                                 wanted_size=(800, 1000), generated=(0, 0),
                                 framebuffer_complete=True, buffer_bytes=80)
assert zero_id_case == (False, None, (0, 0), True)

# A failed resize allocates a new object, leaves the old handles untouched and
# cannot commit their stale storage under the new cover key.
oom_case = model_transaction(wanted_size=(800, 1000), teximage_ok=False,
                             framebuffer_complete=True, buffer_bytes=80)
assert oom_case == (False, None, (41, 42), True)

# New identity at identical dimensions reuses storage; missing VBO allocation
# still fails closed, while a complete quad commits without TexImage allocation.
bad_buffer_case = model_transaction(buffer_bytes=0)
assert bad_buffer_case == (False, None, (41, 42), False)
reuse_case = model_transaction(buffer_bytes=80)
assert reuse_case == (True, "new-cover", (41, 42), False)

# RGBA16F is used only when renderable.  Quantization is bounded and does not
# alter time, hue or formula structure.  This numeric probe records the worst
# representational delta for [0,1] static fields.
rng = random.Random(0x106107)
worst = 0.0
for _ in range(200_000):
    value = rng.random()
    rounded = struct.unpack("<e", struct.pack("<e", value))[0]
    worst = max(worst, abs(value - rounded))
assert worst <= 0.000245, worst

# No Java/server/online-control source belongs to this isolated native patch.
allowed = {
    "magazine_shader.h",
    "native_carousel.cpp",
    "native_magazine.h",
    "native_magazine_field.h",
    "native_lottie_gear.h",
    "premium-magazine-led-android.glsl",
    "station_chatbot_state.h",
}
assert {p.name for p in PATCH.iterdir() if p.is_file()} == allowed

print(
    {
        "base_shader_sha256": hashlib.sha256(base_shader.encode()).hexdigest(),
        "patched_shader_sha256": hashlib.sha256(field_shader.encode()).hexdigest(),
        "unchanged_dynamic_tail_sha256": hashlib.sha256(
            base_shader[base_shader.index(tail_marker) :].encode()
        ).hexdigest(),
        "bake_clip_space_coverage": bake_clip_coverage,
        "strict_gles_legacy_invalid_enum_detected": legacy_gl.errors == [GL_INVALID_ENUM],
        "strict_gles_patched_errors": strict_gl.errors,
        "zero_object_id_rejected": not zero_id_case[0],
        "teximage_oom_preserved_old_handles_without_commit": oom_case[2] == (41, 42),
        "invalid_vbo_storage_rejected": not bad_buffer_case[0],
        "post_draw_gpu_sync_query_present": "GetQueryObjectuiv" in field_cache,
        "same_size_identity_change_reuses_storage": reuse_case[0] and not reuse_case[3],
        "rgba16f_worst_static_scalar_delta": worst,
        "checks": "passed",
    }
)
