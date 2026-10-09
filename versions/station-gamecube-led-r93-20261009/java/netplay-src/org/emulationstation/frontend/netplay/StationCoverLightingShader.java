package org.emulationstation.frontend.netplay;
/** Identical shared carousel GLSL. */
final class StationCoverLightingShader {
    static final String SOURCE =
        "// Selected magazine only. Reference artwork: 1024x1536, top-left coordinates.\n" +
        "// Pixel color gating follows actual cyan emitters inside the measured frame,\n" +
        "// never the blue illustration. Texture-space bloom rotates/scales with the cover.\n" +
        "#if defined(VERTEX)\n" +
        "#if __VERSION__ >= 130\n" +
        "#define ATTR in\n" +
        "#define VARY out\n" +
        "#else\n" +
        "#define ATTR attribute\n" +
        "#define VARY varying\n" +
        "#endif\n" +
        "uniform mat4 MVPMatrix;\n" +
        "ATTR vec2 VertexCoord;\n" +
        "ATTR vec2 TexCoord;\n" +
        "ATTR vec4 COLOR;\n" +
        "VARY vec2 uv;\n" +
        "VARY vec4 tint;\n" +
        "void main() { gl_Position=MVPMatrix*vec4(VertexCoord,0.0,1.0); uv=TexCoord; tint=COLOR; }\n" +
        "#elif defined(FRAGMENT)\n" +
        "#if __VERSION__ >= 130\n" +
        "#define VARY in\n" +
        "#define TEX texture\n" +
        "out vec4 FragColor;\n" +
        "#else\n" +
        "#define VARY varying\n" +
        "#define TEX texture2D\n" +
        "#define FragColor gl_FragColor\n" +
        "#endif\n" +
        "#ifdef GL_ES\n" +
        "precision highp float;\n" +
        "precision highp int;\n" +
        "#endif\n" +
        "VARY vec2 uv;\n" +
        "VARY vec4 tint;\n" +
        "uniform sampler2D u_tex;\n" +
        "uniform int FrameCount;\n" +
        "uniform float saturation;\n" +
        "uniform vec4 ledColor;\n" +
        "uniform float ledGain;\n" +
        "uniform float sheenGain;\n" +
        "// 0: approved SNES map; 1: measured Mega Drive frame;\n" +
        "// 2: measured Nintendo 64 frame. Models 0/1 keep their original light engine.\n" +
        "uniform float magazineModel;\n" +
        "float activeMagazineModel;\n" +
        "\n" +
        "float box(vec2 p, vec2 lo, vec2 hi) {\n" +
        "    vec2 a=smoothstep(lo,lo+vec2(3.0),p);\n" +
        "    vec2 b=1.0-smoothstep(hi-vec2(3.0),hi,p);\n" +
        "    return a.x*a.y*b.x*b.y;\n" +
        "}\n" +
        "float segmentMask(vec2 p, vec2 a, vec2 b, float width) {\n" +
        "    vec2 ab=b-a;\n" +
        "    float t=clamp(dot(p-a,ab)/dot(ab,ab),0.0,1.0);\n" +
        "    return 1.0-smoothstep(width,width+3.0,length(p-a-t*ab));\n" +
        "}\n" +
        "float megaRegion(vec2 p) {\n" +
        "    // Original 1024x1536 artwork, not screen pixels. Sixteen main light bars.\n" +
        "    float m=max(box(p,vec2(164,3),vec2(284,35)),box(p,vec2(738,2),vec2(862,35)));\n" +
        "    m=max(m,box(p,vec2(927,64),vec2(1002,91)));\n" +
        "    m=max(m,box(p,vec2(926,115),vec2(1002,142)));\n" +
        "    m=max(m,box(p,vec2(164,185),vec2(268,203)));\n" +
        "    m=max(m,box(p,vec2(763,185),vec2(860,203)));\n" +
        "    m=max(m,box(p,vec2(34,488),vec2(74,635)));\n" +
        "    m=max(m,box(p,vec2(951,488),vec2(990,635)));\n" +
        "    m=max(m,box(p,vec2(34,808),vec2(74,974)));\n" +
        "    m=max(m,box(p,vec2(951,810),vec2(990,974)));\n" +
        "    // Bent lower rails need a path mask, not a box over blue game artwork.\n" +
        "    m=max(m,segmentMask(p,vec2(86,1106),vec2(85,1125),6.0));\n" +
        "    m=max(m,segmentMask(p,vec2(85,1125),vec2(30,1188),6.0));\n" +
        "    m=max(m,segmentMask(p,vec2(30,1188),vec2(30,1206),6.0));\n" +
        "    m=max(m,segmentMask(p,vec2(937,1106),vec2(938,1125),6.0));\n" +
        "    m=max(m,segmentMask(p,vec2(938,1125),vec2(993,1188),6.0));\n" +
        "    m=max(m,segmentMask(p,vec2(993,1188),vec2(993,1195),6.0));\n" +
        "    m=max(m,box(p,vec2(757,1343),vec2(947,1366)));\n" +
        "    m=max(m,box(p,vec2(46,1387),vec2(84,1481)));\n" +
        "    m=max(m,box(p,vec2(493,1389),vec2(533,1470)));\n" +
        "    m=max(m,box(p,vec2(937,1387),vec2(980,1481)));\n" +
        "    // Same treatment as SNES footer icons, never the badge's blue stars.\n" +
        "    m=max(m,box(p,vec2(104,1392),vec2(207,1483)));\n" +
        "    m=max(m,box(p,vec2(594,1404),vec2(677,1474)));\n" +
        "    return m;\n" +
        "}\n" +
        "float discMask(vec2 p, vec2 center, float radius) {\n" +
        "    return 1.0-smoothstep(radius-3.0,radius+3.0,length(p-center));\n" +
        "}\n" +
        "float n64Region(vec2 p) {\n" +
        "    // Original 1024x1536 N64 artwork. Every region below was measured on the\n" +
        "    // shared chassis; game artwork remains outside the mask.\n" +
        "    float m=max(box(p,vec2(160,0),vec2(315,35)),box(p,vec2(708,0),vec2(865,35)));\n" +
        "    m=max(m,box(p,vec2(174,185),vec2(270,203)));\n" +
        "    m=max(m,box(p,vec2(760,185),vec2(856,203)));\n" +
        "    m=max(m,box(p,vec2(887,114),vec2(941,133)));\n" +
        "    m=max(m,box(p,vec2(946,114),vec2(997,133)));\n" +
        "    m=max(m,box(p,vec2(887,137),vec2(941,156)));\n" +
        "    m=max(m,box(p,vec2(946,137),vec2(997,156)));\n" +
        "    m=max(m,discMask(p,vec2(44,235),31.0));\n" +
        "    m=max(m,discMask(p,vec2(980,235),31.0));\n" +
        "    m=max(m,box(p,vec2(18,317),vec2(57,477)));\n" +
        "    m=max(m,box(p,vec2(967,317),vec2(1006,477)));\n" +
        "    m=max(m,box(p,vec2(18,801),vec2(57,946)));\n" +
        "    m=max(m,box(p,vec2(967,801),vec2(1006,946)));\n" +
        "    m=max(m,box(p,vec2(755,1344),vec2(949,1372)));\n" +
        "    m=max(m,discMask(p,vec2(49,1454),31.0));\n" +
        "    m=max(m,discMask(p,vec2(975,1454),31.0));\n" +
        "    m=max(m,box(p,vec2(101,1392),vec2(220,1498)));\n" +
        "    m=max(m,box(p,vec2(602,1395),vec2(726,1498)));\n" +
        "    return m;\n" +
        "}\n" +
        "float dreamcastRegion(vec2 p) {\n" +
        "    // Only the orange rails on the provided dark metallic chassis.\n" +
        "    float m=max(box(p,vec2(24,104),vec2(45,1396)),box(p,vec2(978,104),vec2(999,1396)));\n" +
        "    m=max(m,box(p,vec2(70,90),vec2(88,153)));\n" +
        "    m=max(m,box(p,vec2(937,90),vec2(955,153)));\n" +
        "    m=max(m,box(p,vec2(21,380),vec2(51,411)));\n" +
        "    m=max(m,box(p,vec2(972,380),vec2(1003,411)));\n" +
        "    m=max(m,box(p,vec2(21,773),vec2(51,804)));\n" +
        "    m=max(m,box(p,vec2(972,773),vec2(1003,804)));\n" +
        "    m=max(m,segmentMask(p,vec2(28,56),vec2(49,30),5.0));\n" +
        "    m=max(m,segmentMask(p,vec2(47,57),vec2(67,31),5.0));\n" +
        "    m=max(m,segmentMask(p,vec2(957,30),vec2(978,56),5.0));\n" +
        "    m=max(m,segmentMask(p,vec2(977,30),vec2(999,56),5.0));\n" +
        "    m=max(m,segmentMask(p,vec2(34,1370),vec2(34,1408),7.0));\n" +
        "    m=max(m,segmentMask(p,vec2(34,1408),vec2(65,1442),6.0));\n" +
        "    m=max(m,segmentMask(p,vec2(989,1370),vec2(989,1408),7.0));\n" +
        "    m=max(m,segmentMask(p,vec2(989,1408),vec2(958,1442),6.0));\n" +
        "    m=max(m,segmentMask(p,vec2(28,1475),vec2(54,1501),5.0));\n" +
        "    m=max(m,segmentMask(p,vec2(47,1475),vec2(70,1501),5.0));\n" +
        "    m=max(m,segmentMask(p,vec2(953,1501),vec2(978,1475),5.0));\n" +
        "    m=max(m,segmentMask(p,vec2(974,1501),vec2(999,1475),5.0));\n" +
        "    return max(m,box(p,vec2(503,1427),vec2(521,1486)));\n" +
        "}\n" +
        "float dreamcastLamp(vec3 c) {\n" +
        "    return smoothstep(.15,.40,c.r-c.b)*smoothstep(.04,.22,c.g-c.b)*smoothstep(.40,.85,c.r);\n" +
        "}\n" +
        "\n" +
        "float blue(vec3 c);\n" +
        "\n" +
        "// Models 5..8: measured GameCube violet, Wii U cyan, Switch red, PS1 white.\n" +
        "// Same sweep/emitter/halo/compositor; only frame regions and color differ.\n" +
        "float frameRing(vec2 p,vec2 c,float radius){return 1.0-smoothstep(5.0,12.0,abs(length(p-c)-radius));}\n" +
        "float gamecubeRegion(vec2 p){\n" +
        " float m=max(segmentMask(p,vec2(78,30),vec2(38,73),7.0),segmentMask(p,vec2(38,73),vec2(38,162),7.0));\n" +
        " m=max(m,segmentMask(p,vec2(943,30),vec2(979,73),7.0));m=max(m,segmentMask(p,vec2(979,73),vec2(979,162),7.0));\n" +
        " m=max(m,segmentMask(p,vec2(12,238),vec2(33,260),6.0));m=max(m,box(p,vec2(20,255),vec2(42,405)));\n" +
        " m=max(m,segmentMask(p,vec2(1011,238),vec2(984,264),6.0));m=max(m,box(p,vec2(974,255),vec2(995,405)));\n" +
        " m=max(m,box(p,vec2(17,531),vec2(35,740)));m=max(m,box(p,vec2(983,531),vec2(1002,740)));\n" +
        " m=max(m,box(p,vec2(13,1002),vec2(30,1315)));m=max(m,box(p,vec2(992,1002),vec2(1008,1315)));\n" +
        " m=max(m,segmentMask(p,vec2(13,1385),vec2(42,1416),6.0));m=max(m,segmentMask(p,vec2(42,1416),vec2(42,1473),6.0));m=max(m,segmentMask(p,vec2(42,1473),vec2(78,1507),6.0));\n" +
        " m=max(m,segmentMask(p,vec2(1008,1385),vec2(979,1416),6.0));m=max(m,segmentMask(p,vec2(979,1416),vec2(979,1473),6.0));m=max(m,segmentMask(p,vec2(979,1473),vec2(943,1507),6.0));\n" +
        " // Violet rim and footer separator measured on the same GameCube chassis.\n" +
        " // Color gating keeps the white letters/stars and game art untouched.\n" +
        " m=max(m,frameRing(p,vec2(854.,1238.),128.));\n" +
        " return max(m,box(p,vec2(472.,1420.),vec2(485.,1495.)));\n" +
        "}\n" +
        "float wiiuRegion(vec2 p){\n" +
        " float m=max(segmentMask(p,vec2(100,57),vec2(61,100),6.0),segmentMask(p,vec2(61,100),vec2(61,150),6.0));\n" +
        " m=max(m,segmentMask(p,vec2(923,57),vec2(961,100),6.0));m=max(m,segmentMask(p,vec2(961,100),vec2(961,150),6.0));\n" +
        " m=max(m,box(p,vec2(168,183),vec2(292,197)));m=max(m,box(p,vec2(744,183),vec2(874,197)));\n" +
        " m=max(m,segmentMask(p,vec2(113,235),vec2(77,273),7.0));m=max(m,segmentMask(p,vec2(908,235),vec2(945,273),7.0));\n" +
        " m=max(m,box(p,vec2(56,302),vec2(79,585)));m=max(m,box(p,vec2(942,302),vec2(967,585)));\n" +
        " m=max(m,box(p,vec2(50,763),vec2(69,840)));m=max(m,box(p,vec2(950,763),vec2(970,1135)));\n" +
        " m=max(m,box(p,vec2(450,1327),vec2(568,1344)));m=max(m,box(p,vec2(420,1408),vec2(436,1486)));m=max(m,box(p,vec2(803,1408),vec2(819,1486)));\n" +
        " return max(m,box(p,vec2(422,1515),vec2(601,1534)));\n" +
        "}\n" +
        "float switchRegion(vec2 p){\n" +
        " float m=max(segmentMask(p,vec2(102,29),vec2(48,86),6.0),segmentMask(p,vec2(48,86),vec2(48,186),6.0));\n" +
        " m=max(m,segmentMask(p,vec2(922,29),vec2(975,86),6.0));m=max(m,segmentMask(p,vec2(975,86),vec2(975,186),6.0));\n" +
        " m=max(m,box(p,vec2(26,291),vec2(44,736)));m=max(m,box(p,vec2(980,291),vec2(998,736)));\n" +
        " m=max(m,box(p,vec2(26,955),vec2(44,1174)));m=max(m,box(p,vec2(980,955),vec2(998,1174)));\n" +
        " m=max(m,segmentMask(p,vec2(46,1250),vec2(46,1377),6.0));m=max(m,segmentMask(p,vec2(46,1377),vec2(94,1426),6.0));\n" +
        " m=max(m,segmentMask(p,vec2(975,1250),vec2(975,1377),6.0));return max(m,segmentMask(p,vec2(975,1377),vec2(931,1426),6.0));\n" +
        "}\n" +
        "float psxRegion(vec2 p){\n" +
        " float m=max(segmentMask(p,vec2(60,104),vec2(115,49),7.0),segmentMask(p,vec2(115,49),vec2(143,49),7.0));\n" +
        " m=max(m,segmentMask(p,vec2(963,104),vec2(907,49),7.0));m=max(m,segmentMask(p,vec2(907,49),vec2(879,49),7.0));\n" +
        " m=max(m,box(p,vec2(36,231),vec2(65,343)));m=max(m,box(p,vec2(954,231),vec2(986,343)));\n" +
        " m=max(m,box(p,vec2(42,531),vec2(61,1058)));m=max(m,box(p,vec2(962,531),vec2(981,1058)));\n" +
        " m=max(m,box(p,vec2(35,1191),vec2(67,1297)));return max(m,box(p,vec2(956,1191),vec2(987,1297)));\n" +
        "}\n" +
        "float newFrameLamp(vec3 c){\n" +
        " if(activeMagazineModel>7.5)return smoothstep(.55,.90,min(c.r,min(c.g,c.b)))*(1.0-smoothstep(.20,.45,max(c.r,max(c.g,c.b))-min(c.r,min(c.g,c.b))));\n" +
        " if(activeMagazineModel>6.5)return smoothstep(.18,.55,c.r-max(c.g,c.b))*smoothstep(.40,.86,c.r);\n" +
        " if(activeMagazineModel>5.5)return blue(c);\n" +
        " // SNES cyan transfer curve with violet channels: dark G replaces dark R.\n" +
        " return blue(c.grb);\n" +
        "}\n" +
        "\n" +
        "float neoRegion(vec2 p);\n" +
        "float neoChroma(vec3 c);\n" +
        "float region(vec2 p) {\n" +
        "    if(activeMagazineModel>7.5) return psxRegion(p);\n" +
        "    if(activeMagazineModel>6.5) return switchRegion(p);\n" +
        "    if(activeMagazineModel>5.5) return wiiuRegion(p);\n" +
        "    if(activeMagazineModel>4.5) return gamecubeRegion(p);\n" +
        "    if(activeMagazineModel>3.5) return dreamcastRegion(p);\n" +
        "    if(activeMagazineModel>2.5) return neoRegion(p);\n" +
        "    if(activeMagazineModel>1.5) return n64Region(p);\n" +
        "    if(activeMagazineModel>0.5) return megaRegion(p);\n" +
        "    float m=max(box(p,vec2(45,26),vec2(157,115)),box(p,vec2(860,23),vec2(975,115)));\n" +
        "    m=max(m,box(p,vec2(36,223),vec2(69,356)));\n" +
        "    m=max(m,box(p,vec2(953,223),vec2(989,356)));\n" +
        "    m=max(m,box(p,vec2(34,515),vec2(72,1065)));\n" +
        "    m=max(m,box(p,vec2(953,515),vec2(986,1065)));\n" +
        "    m=max(m,box(p,vec2(34,1187),vec2(73,1298)));\n" +
        "    m=max(m,box(p,vec2(951,1187),vec2(990,1298)));\n" +
        "    // Only the badge rim, not its white lettering or stars.\n" +
        "    float ring=1.0-smoothstep(7.0,16.0,abs(length((p-vec2(794,1200))*vec2(1.0,0.975))-146.0));\n" +
        "    m=max(m,ring);\n" +
        "    m=max(m,box(p,vec2(737,1285),vec2(852,1304)));\n" +
        "    m=max(m,box(p,vec2(108,1395),vec2(213,1491)));\n" +
        "    m=max(m,box(p,vec2(557,1405),vec2(658,1498)));\n" +
        "    return m;\n" +
        "}\n" +
        "vec4 sampleArt(vec2 p) { return TEX(u_tex,vec2(p.x/1024.0,1.0-p.y/1536.0)); }\n" +
        "float blue(vec3 c) {\n" +
        "    return smoothstep(0.08,0.32,c.b-c.r)*smoothstep(0.28,0.78,c.b)*smoothstep(0.08,0.35,c.g);\n" +
        "}\n" +
        "float n64Lamp(vec3 c) {\n" +
        "    float hi=max(c.r,max(c.g,c.b));\n" +
        "    float lo=min(c.r,min(c.g,c.b));\n" +
        "    return smoothstep(0.10,0.34,hi-lo)*smoothstep(0.20,0.72,hi);\n" +
        "}\n" +
        "float lampSample(vec3 c) {\n" +
        "    if(activeMagazineModel>4.5) return newFrameLamp(c);\n" +
        "    if(activeMagazineModel>3.5) return dreamcastLamp(c);\n" +
        "    if(activeMagazineModel>2.5) return neoChroma(c);\n" +
        "    if(activeMagazineModel>1.5) return n64Lamp(c);\n" +
        "    return blue(c);\n" +
        "}\n" +
        "float emitter(vec2 p) {\n" +
        "    if(region(p)<=0.0) return 0.0; // Equivalent zero mask; saves texture reads.\n" +
        "    vec4 c=sampleArt(p);\n" +
        "    float lamp=lampSample(c.rgb);\n" +
        "    // Recover the almost-white hot core only next to a measured colored pixel.\n" +
        "    float neighbor=max(max(lampSample(sampleArt(p+vec2(3,0)).rgb),lampSample(sampleArt(p-vec2(3,0)).rgb)),\n" +
        "                       max(lampSample(sampleArt(p+vec2(0,3)).rgb),lampSample(sampleArt(p-vec2(0,3)).rgb)));\n" +
        "    bool gamecubeEmitter=activeMagazineModel>4.5&&activeMagazineModel<5.5;\n" +
        "    float channelCore=gamecubeEmitter ? min(c.r,c.b) : (activeMagazineModel>1.5 ? max(c.r,max(c.g,c.b)) : min(c.g,c.b));\n" +
        "    float core=smoothstep(0.70,0.95,channelCore)*neighbor;\n" +
        "    return max(lamp,core)*region(p)*c.a;\n" +
        "}\n" +
        "vec4 lightEnvelope(vec2 p) {\n" +
        "    // One head/clock for both effects and both sides of the frame. Keep the\n" +
        "    // approved contour sweep speed; 625 frames are exactly three full passes.\n" +
        "    float t=float(FrameCount-((FrameCount/625)*625));\n" +
        "    float head=fract(t*0.0048);\n" +
        "    float behind=fract(head-(1.0-p.y/1536.0));\n" +
        "    float d=min(behind,1.0-behind);\n" +
        "    // xy: card LEDs use the carousel laser; zw: preserve the approved broad\n" +
        "    // photo sheen. They share position/time, never the same light footprint.\n" +
        "    return vec4(exp(-pow(d/0.007,2.0)),\n" +
        "                exp(-behind/0.100)*(1.0-smoothstep(0.28,0.38,behind)),\n" +
        "                1.0-smoothstep(0.016,0.145,d),\n" +
        "                1.0-smoothstep(0.040,0.330,d));\n" +
        "}\n" +
        "float hash11(float n) {\n" +
        "    return fract(sin(n*127.1)*43758.5453123);\n" +
        "}\n" +
        "float shortPeak(float phase, float center, float width) {\n" +
        "    return 1.0-smoothstep(0.0,width,abs(phase-center));\n" +
        "}\n" +
        "float n64ShortCircuit() {\n" +
        "    // Low unstable current most of the time, followed by short irregular\n" +
        "    // clusters: strong peaks, brief dropouts and no regular breathing rhythm.\n" +
        "    float frame=float(FrameCount);\n" +
        "    float weak=0.105+0.050*(0.5+0.5*sin(frame*0.071))\n" +
        "                       +0.035*(0.5+0.5*sin(frame*0.173+1.7));\n" +
        "    float cycle=floor(frame/211.0);\n" +
        "    float phase=fract(frame/211.0);\n" +
        "    float chaos=0.72+0.28*hash11(cycle+3.0);\n" +
        "    float cluster=max(shortPeak(phase,0.105,0.014),shortPeak(phase,0.148,0.010));\n" +
        "    cluster=max(cluster,shortPeak(phase,0.205,0.018));\n" +
        "    float late=shortPeak(phase,0.628,0.013)*step(0.48,hash11(cycle+17.0));\n" +
        "    float dropout=max(shortPeak(phase,0.286,0.026),shortPeak(phase,0.760,0.035));\n" +
        "    return clamp(weak*(1.0-0.72*dropout)+max(cluster,late)*chaos,0.035,1.0);\n" +
        "}\n" +
        "vec3 n64LampHue(vec2 p) {\n" +
        "    // Four stable 1.5 s states at the frontend's 60 Hz VSync. The existing\n" +
        "    // short-circuit envelope still controls weak current, dropouts and peaks;\n" +
        "    // only the N64 lamp color changes as one electrical bank.\n" +
        "    float colorStep=floor(mod(float(FrameCount),360.0)/90.0);\n" +
        "    if(colorStep<0.5) return vec3(0.035,1.00,0.120); // green\n" +
        "    if(colorStep<1.5) return vec3(1.00,0.035,0.055); // red\n" +
        "    if(colorStep<2.5) return vec3(0.025,0.360,1.00); // blue\n" +
        "    return vec3(1.00);                              // white\n" +
        "}\n" +
        "float luminance(vec3 c) { return dot(c,vec3(0.299,0.587,0.114)); }\n" +
        "float contourSheen(vec2 p,vec2 flow) {\n" +
        "    // Restore hero-neon-edge's moving contour light in cover-local space.\n" +
        "    // Reference offsets match one displayed pixel at 1360x768, not a screen\n" +
        "    // rectangle that could illuminate the back covers when the fan animates.\n" +
        "    vec2 dx=vec2(3.85,0.0),dy=vec2(0.0,3.90);\n" +
        "    float edge=abs(luminance(sampleArt(p+dx).rgb)-luminance(sampleArt(p-dx).rgb))\n" +
        "              +abs(luminance(sampleArt(p+dy).rgb)-luminance(sampleArt(p-dy).rgb));\n" +
        "    float wide=abs(luminance(sampleArt(p+dx*2.5).rgb)-luminance(sampleArt(p-dx*2.5).rgb))\n" +
        "              +abs(luminance(sampleArt(p+dy*2.5).rgb)-luminance(sampleArt(p-dy*2.5).rgb));\n" +
        "    float moving=flow.x;\n" +
        "    float tail=flow.y;\n" +
        "    return smoothstep(0.12,0.52,edge)*(0.14+tail*0.22+moving*0.50)\n" +
        "           +smoothstep(0.08,0.44,wide)*0.40*(0.08+moving*0.16);\n" +
        "}\n" +
        "// Neo Geo magazine chassis measured on original 1024 x 1536 artwork.\n" +
        "// Shared by svcplus.png and the local neogeo/media/revista corpus.\n" +
        "// The CD platform may use this chassis too, but the signature must match.\n" +
        "float neoRegion(vec2 p) {\n" +
        "    float m=max(box(p,vec2(160,0),vec2(316,32)),box(p,vec2(709,0),vec2(865,32)));\n" +
        "    m=max(m,box(p,vec2(170,185),vec2(266,201)));\n" +
        "    m=max(m,box(p,vec2(762,185),vec2(856,201)));\n" +
        "    m=max(m,box(p,vec2(887,116),vec2(992,152)));\n" +
        "    m=max(m,discMask(p,vec2(44,234),24.0));\n" +
        "    m=max(m,discMask(p,vec2(980,234),24.0));\n" +
        "    m=max(m,box(p,vec2(19,319),vec2(59,472)));\n" +
        "    m=max(m,box(p,vec2(965,319),vec2(1008,472)));\n" +
        "    m=max(m,box(p,vec2(23,810),vec2(50,951)));\n" +
        "    m=max(m,box(p,vec2(975,810),vec2(1007,951)));\n" +
        "    m=max(m,box(p,vec2(762,1344),vec2(946,1363)));\n" +
        "    m=max(m,discMask(p,vec2(48,1456),24.0));\n" +
        "    m=max(m,discMask(p,vec2(976,1456),24.0));\n" +
        "    m=max(m,box(p,vec2(107,1398),vec2(206,1484)));\n" +
        "    m=max(m,box(p,vec2(607,1409),vec2(686,1477)));\n" +
        "    return m;\n" +
        "}\n" +
        "float neoChroma(vec3 c) {\n" +
        "    float hi=max(c.r,max(c.g,c.b)),lo=min(c.r,min(c.g,c.b));\n" +
        "    return smoothstep(.06,.28,hi-lo)*smoothstep(.20,.75,hi);\n" +
        "}\n" +
        "float neoSignature() {\n" +
        "    // Measured bright rail interiors stay blue in both 1024x1536 and 262x393\n" +
        "    // textures. Edge probes at (38,406)/(790,12) attenuated the real frame.\n" +
        "    float bars=blue(sampleArt(vec2(240,14)).rgb)+blue(sampleArt(vec2(790,14)).rgb)\n" +
        "        +blue(sampleArt(vec2(34,406)).rgb)+blue(sampleArt(vec2(991,406)).rgb);\n" +
        "    vec3 amber=sampleArt(vec2(942,125)).rgb;\n" +
        "    float arcade=smoothstep(.22,.7,min(amber.r,amber.g)-amber.b);\n" +
        "    float dark=1.0-smoothstep(.10,.27,luminance(sampleArt(vec2(512,208)).rgb));\n" +
        "    return smoothstep(2.6,3.8,bars)*arcade*dark;\n" +
        "}\n" +
        "\n" +
        "float shoulder(vec2 p){\n" +
        " float a=lampSample(sampleArt(p).rgb);\n" +
        " a=max(a,lampSample(sampleArt(p+vec2(5,0)).rgb));a=max(a,lampSample(sampleArt(p-vec2(5,0)).rgb));\n" +
        " a=max(a,lampSample(sampleArt(p+vec2(10,0)).rgb));a=max(a,lampSample(sampleArt(p-vec2(10,0)).rgb));return a;\n" +
        "}\n" +
        "float bilateralSignature(float left,float right,float y1,float y2,float y3){\n" +
        " float l=max(shoulder(vec2(left,y1)),max(shoulder(vec2(left,y2)),shoulder(vec2(left,y3))));\n" +
        " float r=max(shoulder(vec2(right,y1)),max(shoulder(vec2(right,y2)),shoulder(vec2(right,y3))));\n" +
        " return smoothstep(.40,.80,min(l,r));\n" +
        "}\n" +
        "float measuredFrameSignature(){\n" +
        " if(activeMagazineModel>7.5)return bilateralSignature(52.,970.,555.,820.,985.);\n" +
        " if(activeMagazineModel>6.5)return bilateralSignature(34.,989.,350.,510.,675.);\n" +
        " if(activeMagazineModel>5.5)return bilateralSignature(66.,956.,340.,460.,550.);\n" +
        " if(activeMagazineModel>4.5)return bilateralSignature(27.,991.,558.,635.,701.);\n" +
        " return bilateralSignature(35.,988.,175.,530.,1040.);\n" +
        "}\n" +
        "\n" +
        "void main() {\n" +
        "    vec4 base=TEX(u_tex,uv);\n" +
        "    vec2 p=vec2(uv.x,1.0-uv.y)*vec2(1024,1536);\n" +
        "    // Require the recognizable premium-frame lamps. Plain game screenshots\n" +
        "    // and covers without this frame must not receive floating lights.\n" +
        "    float signature=blue(sampleArt(vec2(49,565)).rgb)+blue(sampleArt(vec2(963,565)).rgb)\n" +
        "                   +blue(sampleArt(vec2(120,42)).rgb)+blue(sampleArt(vec2(900,42)).rgb);\n" +
        "    float darkHeader=1.0-smoothstep(0.08,0.25,dot(sampleArt(vec2(512,30)).rgb,vec3(0.299,0.587,0.114)));\n" +
        "    float megaSignature=blue(sampleArt(vec2(220,12)).rgb)+blue(sampleArt(vec2(800,12)).rgb)\n" +
        "                 +blue(sampleArt(vec2(47,560)).rgb)+blue(sampleArt(vec2(976,560)).rgb);\n" +
        "    // Stay inside the wide dark separator. At y=215, ImageIO's FILTER_BOX\n" +
        "    // mixes the white rule at y=217 into the 262x393 texture and disables LEDs.\n" +
        "    // y=208 keeps a margin on both sides at native-sized textures, not just\n" +
        "    // when drawing the full-resolution source into a smaller viewport.\n" +
        "    float megaHeader=1.0-smoothstep(0.08,0.25,dot(sampleArt(vec2(512,208)).rgb,vec3(0.299,0.587,0.114)));\n" +
        "    float n64Signature=n64Lamp(sampleArt(vec2(240,14)).rgb)+n64Lamp(sampleArt(vec2(790,14)).rgb)\n" +
        "                 +n64Lamp(sampleArt(vec2(44,235)).rgb)+n64Lamp(sampleArt(vec2(980,235)).rgb)\n" +
        "                 +n64Lamp(sampleArt(vec2(975,1454)).rgb);\n" +
        "    float n64Header=1.0-smoothstep(0.08,0.25,dot(sampleArt(vec2(512,175)).rgb,vec3(0.299,0.587,0.114)));\n" +
        "    // Recognize the actual frame too: grouped systems may inherit the default\n" +
        "    // profile. A plain blue image still fails the dark separator requirement.\n" +
        "    activeMagazineModel=max(magazineModel,step(0.95,smoothstep(2.0,3.2,megaSignature)*megaHeader));\n" +
        "    if(activeMagazineModel>1.5) {\n" +
        "        signature=n64Signature;\n" +
        "        darkHeader=n64Header;\n" +
        "    } else if(activeMagazineModel>0.5) {\n" +
        "        signature=megaSignature;\n" +
        "        darkHeader=megaHeader;\n" +
        "    }\n" +
        "    float enabled=(activeMagazineModel>1.5 ? smoothstep(2.8,4.2,signature) : smoothstep(2.0,3.2,signature))*darkHeader;\n" +
        "    // Neo Geo/CD keeps its measured geometry and its artwork's lamp colors,\n" +
        "    // but uses the exact SNES envelope, emitter recovery, 2/5px halo and compositing.\n" +
        "    bool measuredMode=activeMagazineModel>3.5;\n" +
        "    bool gamecubeMode=activeMagazineModel>4.5&&activeMagazineModel<5.5;\n" +
        "    bool dreamcastMode=activeMagazineModel>3.5&&activeMagazineModel<4.5;\n" +
        "    bool neoMode=activeMagazineModel>2.5&&!measuredMode;\n" +
        "    if(neoMode){enabled=neoSignature();if(enabled<.01){FragColor=base*tint;return;}}\n" +
        "    if(measuredMode) enabled=measuredFrameSignature();\n" +
        "    if(enabled<.01){FragColor=base*tint;return;}\n" +
        "    float mask=emitter(p);\n" +
        "    float nearGlow=0.0,wideGlow=0.0;\n" +
        "    for(int i=0;i<8;i++) {\n" +
        "        float angle=float(i)*0.7853981634;\n" +
        "        vec2 dir=vec2(cos(angle),sin(angle));\n" +
        "        nearGlow+=emitter(p+dir*2.0);\n" +
        "        wideGlow+=emitter(p+dir*5.0);\n" +
        "    }\n" +
        "    nearGlow/=8.0; wideGlow/=8.0;\n" +
        "    vec4 flow=lightEnvelope(p);\n" +
        "    float n64Mode=step(1.5,activeMagazineModel)*(1.0-step(2.5,activeMagazineModel));\n" +
        "    float shortCircuit=n64ShortCircuit();\n" +
        "    flow=mix(flow,vec4(pow(shortCircuit,4.0),shortCircuit*0.24,shortCircuit,shortCircuit*0.38),n64Mode);\n" +
        "    float energy=max(flow.x,flow.y);\n" +
        "    vec3 hue=clamp(ledColor.rgb,0.0,1.0);\n" +
        "    if(activeMagazineModel>7.5) hue=vec3(.94,.97,1.0);\n" +
        "    else if(activeMagazineModel>6.5) hue=vec3(1.0,.025,.008);\n" +
        "    else if(activeMagazineModel>5.5) hue=vec3(.015,.65,1.0);\n" +
        "    else if(activeMagazineModel>4.5) hue=vec3(.64,.08,1.0);\n" +
        "    else if(dreamcastMode) hue=vec3(1.0,.26,.015);\n" +
        "    else if(neoMode) hue=base.rgb/max(max(base.r,max(base.g,base.b)),.001);\n" +
        "    else if(activeMagazineModel>1.5) hue=n64LampHue(p);\n" +
        "    else if(activeMagazineModel>0.5) hue=vec3(24.0,108.0,255.0)/255.0;\n" +
        "    float gain=clamp(ledGain,1.0,2.5);\n" +
        "    // Retint only the existing blue emitter and its baked blue falloff.\n" +
        "    // Positions and pulse stay fixed; preserve source contrast, not max-channel\n" +
        "    // brightness (blue is saturated even in the dim shoulders of these LEDs).\n" +
        "    float chroma=max(base.r,max(base.g,base.b))-min(base.r,min(base.g,base.b));\n" +
        "    vec3 emissionBase=gamecubeMode ? base.grb : base.rgb;\n" +
        "    float fringe=region(p)*(activeMagazineModel>1.5 && !gamecubeMode ? smoothstep(0.04,0.20,chroma)\n" +
        "                                                   : smoothstep(0.015,0.10,emissionBase.b-emissionBase.r));\n" +
        "    float recolor=enabled*max(mask,fringe);\n" +
        "    float value=dot(emissionBase,vec3(0.16,0.68,0.16));\n" +
        "    if(activeMagazineModel>1.5 && !neoMode && !measuredMode) value=max(base.r,max(base.g,base.b));\n" +
        "    // Cyan cores lose their red channel when reduced to the on-screen cover.\n" +
        "    // Use their green/blue energy instead of requiring already-white RGB.\n" +
        "    // Brighten only the emitter, not the halo or the dark red shoulders.\n" +
        "    float hot=smoothstep(0.48,0.82,min(emissionBase.g,emissionBase.b))\n" +
        "             *smoothstep(0.30,0.78,flow.x);\n" +
        "    if(activeMagazineModel>1.5 && !neoMode && !measuredMode)\n" +
        "        hot=smoothstep(0.62,0.94,max(base.r,max(base.g,base.b)))*smoothstep(0.38,0.82,flow.x);\n" +
        "    if(neoMode||(measuredMode&&!gamecubeMode)) hot=smoothstep(0.48,0.82,max(base.r,max(base.g,base.b)))\n" +
        "                  *smoothstep(0.30,0.78,flow.x);\n" +
        "    vec3 lamp=mix(hue*value*(0.30+0.80*energy),vec3(1.0),hot);\n" +
        "    vec3 rgb=mix(base.rgb,clamp(lamp,0.0,1.0),recolor);\n" +
        "    // Match carousel laser intensity: 2.2 for the red trail, 3.0 for the hot\n" +
        "    // head. Keep the compact 2/5px footprint: only the passing light intensifies.\n" +
        "    float laserPower=0.18+2.2*flow.y+3.0*flow.x;\n" +
        "    if(activeMagazineModel>1.5 && !neoMode && !measuredMode)\n" +
        "        laserPower=0.08+0.48*shortCircuit+3.35*pow(shortCircuit,4.0);\n" +
        "    float bloom=enabled*laserPower*gain*(mask*0.05+nearGlow*0.15+wideGlow*0.035);\n" +
        "    vec3 glowColor=mix(hue,vec3(1.0,0.90,0.92),flow.x);\n" +
        "    rgb=1.0-(1.0-rgb)*(1.0-clamp(glowColor*bloom,0.0,1.0));\n" +
        "    // White traveling photo sheen removed; measured side LEDs remain unchanged.\n" +
        "    float luma=dot(rgb,vec3(0.299,0.587,0.114));\n" +
        "    rgb=mix(vec3(luma),rgb,saturation);\n" +
        "    FragColor=vec4(rgb,base.a)*tint;\n" +
        "}\n" +
        "#endif\n";
}
