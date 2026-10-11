"""Closed R130 video-loop overlay: focused platforms only, one reused decoder.

Produces sources/headers, never an APK. All input identities and every inverse
are checked. The existing single-pass, end-frame, lifecycle and graphics masks
remain the path for collections, disabled loop and legacy callers.
"""
from __future__ import annotations

from pathlib import Path
import argparse
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
BASE = "versions/station-video-room-footer-r124-20261011/java"
JAVA_PINS = {
    "client/src/java/org/emulationstation/frontend/station/StationGraphicsPreferences.java":
        "0327cb2f25e05162e19f81b50128c478ebbc298e063d219fd391572b30199b52",
    "client/src/java/org/emulationstation/frontend/station/StationGraphicsPanel.java":
        "7b8483c4775e2f1c2c543f74308be153a4b5b601d1edde3f00881721d0e96654",
    "netplay-src/org/emulationstation/frontend/netplay/StationSinglePassVideo720.java":
        "dde13ca08170e98354a22a764a42f9a6a98e032389aba48e81fb5aab3d9e1673",
}
VIDEO_SHA = "f88f90d04a0da17ab96d4278f2b77ed60f071dcae715c7709bb840d5198a56e5"
GRAPHICS_SHA = "fb266e78ad9daffdf3742b0e3967bfbec7124930997afabc1a8a241cb6cd703d"
NATIVE_SCOPE = b'''#pragma once
// This is a launch scope, not another graphics mask or a per-frame preference.
static bool stationPlatformVideoLoopRequested(bool systems,bool folders){
 return systems&&!folders;
}
'''

PREFERENCES = (
    ("    private volatile State state;\n",
     "    private volatile State state;\n    private volatile boolean platformVideoLoop;\n"),
    ("        saved = context.getSharedPreferences(FILE, Context.MODE_PRIVATE);\n",
     "        saved = context.getSharedPreferences(FILE, Context.MODE_PRIVATE);\n"
     "        platformVideoLoop = saved.getBoolean(\"platform_video_loop\", true);\n"),
    ("    public long revision() { return state.revision; }\n",
     "    public long revision() { return state.revision; }\n"
     "    public boolean platformVideoLoop() { return platformVideoLoop; }\n"
     "    public void setPlatformVideoLoop(boolean loop) {\n"
     "        synchronized (this) {\n"
     "            if (platformVideoLoop == loop) return;\n"
     "            platformVideoLoop = loop;\n"
     "            saved.edit().putBoolean(\"platform_video_loop\", loop).apply();\n"
     "        }\n"
     "        announce(state);\n"
     "    }\n"),
)

PANEL_RENDER = '''        private void renderVideoLoop(StationGraphicsPreferences.State state){
            boolean enabled=state.isEnabled(StationGraphicsPreferences.VIDEO);
            videoLoopModes.check(LOOP_ID+(preferences.platformVideoLoop()?1:0));
            for(int i=0;i<videoLoopModes.getChildCount();i++){
                RadioButton button=(RadioButton)videoLoopModes.getChildAt(i);button.setEnabled(enabled);
                button.setTextColor(button.isChecked()?WHITE:MUTED);button.setTypeface(null,button.isChecked()?Typeface.BOLD:Typeface.NORMAL);
                button.setContentDescription("Vídeo principal "+button.getText()+(button.isChecked()?", selecionado":"")+(!enabled?", vídeos desligados":""));
            }
            videoLoopHint.setText(!enabled?"Escolha salva; vídeos desligados.":"Só o vídeo em destaque nas plataformas. Coleções sempre sem loop.");
        }
        @Override public void onCheckedChanged(RadioGroup group,int id){
            if(group==videoLoopModes&&!updating&&id>=LOOP_ID&&id<=LOOP_ID+1)
                preferences.setPlatformVideoLoop(id==LOOP_ID+1);
        }
'''

PANEL = (
    ("private static final class Content extends LinearLayout implements StationGraphicsPreferences.Listener, StationCarouselStylePreferences.Listener {",
     "private static final class Content extends LinearLayout implements StationGraphicsPreferences.Listener, StationCarouselStylePreferences.Listener, RadioGroup.OnCheckedChangeListener {"),
    ("        private static final int MODE_ID=0x118100, STYLE_ID=0x123100;\n",
     "        private static final int MODE_ID=0x118100, STYLE_ID=0x123100, LOOP_ID=0x130100;\n"),
    ("        private final TextView status,backgroundHint,carouselHint;\n",
     "        private final TextView status,backgroundHint,carouselHint,videoLoopHint;\n"),
    ("        private final RadioGroup backgrounds,carouselStyles;\n",
     "        private final RadioGroup backgrounds,carouselStyles,videoLoopModes;\n"),
    ("            for(int i=0;i<effects.length;i++){\n",
     '''            videoLoopModes=new RadioGroup(owner);videoLoopModes.setOrientation(HORIZONTAL);
            videoLoopModes.addView(choice(LOOP_ID+1,"Com loop","Vídeo principal com loop"),choiceSize(0));
            videoLoopModes.addView(choice(LOOP_ID,"Sem loop","Vídeo principal sem loop"),choiceSize(1));
            videoLoopModes.setOnCheckedChangeListener(this);
            videoLoopHint=text("",10,MUTED);videoLoopHint.setMaxLines(2);videoLoopHint.setPadding(dp(4),0,dp(4),dp(4));
            for(int i=0;i<effects.length;i++){
'''),
    ("                effectsList.addView(option(effects[i],labels[i],hints[i]),new LinearLayout.LayoutParams(-1,-2));\n",
     '''                effectsList.addView(option(effects[i],labels[i],hints[i]),new LinearLayout.LayoutParams(-1,-2));
                if(effects[i]==StationGraphicsPreferences.VIDEO){
                    effectsList.addView(videoLoopModes,new LinearLayout.LayoutParams(-1,-2));
                    effectsList.addView(videoLoopHint,new LinearLayout.LayoutParams(-1,-2));
                }
'''),
    ("                renderCarouselStyle(state);\n",
     "                renderCarouselStyle(state);\n                renderVideoLoop(state);\n"),
    ("        private void renderCarouselStyle(StationGraphicsPreferences.State state){\n",
     PANEL_RENDER + "        private void renderCarouselStyle(StationGraphicsPreferences.State state){\n"),
)

AFTER_SEEK = '''    private static void afterEndSeek(Session s){
        if(!current(s)||!s.finishing)return;
        if(!s.loopSeeking){completeHold(s);return;}
        s.loopSeeking=false;
        if(s.seekTimeout!=null)worker().removeCallbacks(s.seekTimeout);
        if(!s.visible||!s.loopRequested||!s.preferences.platformVideoLoop()){
            // A human disabled looping, or this clip was hidden during the seek.
            // Complete the original hold path; never restart a hidden decoder.
            s.finishing=false;finishEarly(s,false);return;
        }
        try{
            // Same MediaPlayer, Surface and decoder; no new prepare or asset IO.
            s.player.start();s.parked=false;s.finishing=false;s.keepPreviousFrame=false;
            s.lastFrame=SystemClock.uptimeMillis();scheduleEnd(s);armWatchdog();
        }catch(RuntimeException e){fail(s,"loop resume failed");}
    }
'''

PLAYER = (
    ("import java.util.concurrent.atomic.AtomicReferenceArray;\n",
     "import java.util.concurrent.atomic.AtomicReferenceArray;\n"
     "import org.emulationstation.frontend.station.StationGraphicsPreferences;\n"),
    ("/** Focused 720p30 clip, one pass. Native retains the image two frames before the last frame, then stop(). */",
     "/** One focused decoder. Collections hold once; platform looping reuses its worker/player. */"),
    ("        final int slot; final String asset;\n",
     "        final int slot; final String asset;\n"
     "        final boolean loopRequested; final StationGraphicsPreferences preferences;\n"),
    ("        boolean prepared,parked,counted,surfacesReleased;\n",
     "        boolean prepared,parked,counted,surfacesReleased,loopSeeking;\n"),
    ("        Session(int slot,int textureId,String asset,boolean visible){\n"
     "            this.slot=slot;this.asset=asset;this.visible=visible;\n",
     "        Session(int slot,int textureId,String asset,boolean visible,boolean loopRequested,StationGraphicsPreferences preferences){\n"
     "            this.slot=slot;this.asset=asset;this.visible=visible;\n"
     "            this.loopRequested=loopRequested;this.preferences=preferences;\n"),
    ("    private static void finishEarly(Session s,boolean playbackEnded){\n",
     AFTER_SEEK + "    private static void finishEarly(Session s,boolean playbackEnded){\n"),
    ("            if(!playbackEnded)s.player.pause();s.parked=true;\n",
     "            if(!playbackEnded)s.player.pause();s.parked=true;\n"
     "            s.loopSeeking=s.loopRequested&&s.visible&&s.preferences.platformVideoLoop();\n"),
    ("s.seekTimeout=()->{if(current(s)&&!s.completed){s.keepPreviousFrame=true;s.frame.set(false);completeHold(s);Log.w(TAG,\"End-frame seek timed out; previous image retained\");}};",
     "s.seekTimeout=()->{if(current(s)&&!s.completed){s.loopSeeking=false;s.keepPreviousFrame=true;s.frame.set(false);completeHold(s);Log.w(TAG,\"End-frame seek timed out; previous image retained\");}};"),
    ("            s.player.seekTo(s.holdPosition,MediaPlayer.SEEK_CLOSEST);\n",
     "            s.player.seekTo(s.loopSeeking?0L:s.holdPosition,MediaPlayer.SEEK_CLOSEST);\n"),
    ("        }catch(RuntimeException e){s.keepPreviousFrame=true;completeHold(s);}\n",
     "        }catch(RuntimeException e){s.loopSeeking=false;s.keepPreviousFrame=true;completeHold(s);}\n"),
    ("    public static boolean start(Activity a,int slot,int textureId,String asset,boolean visible){\n",
     "    public static boolean start(Activity a,int slot,int textureId,String asset,boolean visible){\n"
     "        return start(a,slot,textureId,asset,visible,false);\n"
     "    }\n"
     "    public static boolean start(Activity a,int slot,int textureId,String asset,boolean visible,boolean loopRequested){\n"),
    ("try{s=new Session(slot,textureId,asset,visible);}catch(RuntimeException e){return false;}",
     "try{s=new Session(slot,textureId,asset,visible,loopRequested,StationGraphicsPreferences.get(a));}catch(RuntimeException e){return false;}"),
    ("player.setOnSeekCompleteListener(mp->{if(current(s)&&s.finishing)completeHold(s);});",
     "player.setOnSeekCompleteListener(mp->{if(current(s)&&s.finishing)afterEndSeek(s);});"),
)

VIDEO_REPLACEMENTS = (
    ("#include \"sony_system_video720_assets.h\"\n",
     "#include \"native_platform_video_loop.h\"\n#include \"sony_system_video720_assets.h\"\n"),
    ('video720Start=env->GetStaticMethodID(video720Class,"start","(Landroid/app/Activity;IILjava/lang/String;Z)Z");',
     'video720Start=env->GetStaticMethodID(video720Class,"start","(Landroid/app/Activity;IILjava/lang/String;ZZ)Z");'),
    ("env->CallStaticBooleanMethod(video720Class,video720Start,a,slot,(jint)v.texture,asset,(jboolean)true);",
     "env->CallStaticBooleanMethod(video720Class,video720Start,a,slot,(jint)v.texture,asset,(jboolean)true,(jboolean)stationPlatformVideoLoopRequested(systemsMode,folderMode));"),
)


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def apply_exact(raw: bytes, replacements: tuple, checksum: str | None = None) -> bytes:
    if checksum is not None and digest(raw) != checksum:
        raise ValueError("Pinned video-loop source changed")
    eol = "\r\n" if b"\r\n" in raw else "\n"
    text = raw.decode("utf-8").replace("\r\n", "\n")
    for old, new in replacements:
        if text.count(old) != 1 or new in text:
            raise ValueError("Exact video-loop anchor changed: " + old[:100])
        text = text.replace(old, new, 1)
    result = text.replace("\n", eol).encode("utf-8")
    check_inverse(raw, result, replacements)
    return result


def check_inverse(original: bytes, changed: bytes, replacements: tuple) -> None:
    eol = "\r\n" if b"\r\n" in original else "\n"
    text = changed.decode("utf-8").replace("\r\n", "\n")
    for old, new in reversed(replacements):
        if text.count(new) != 1:
            raise ValueError("A video-loop replacement is missing or duplicated")
        text = text.replace(new, old, 1)
    if text.replace("\n", eol).encode("utf-8") != original:
        raise ValueError("An unrelated source byte changed")


def transform_java_sources(repo: Path = REPO) -> tuple[dict[str, bytes], dict]:
    """Return exactly three transformed productive sources, with no output IO.

    Client sources must compile before the player. Their resulting JAR precedes
    the old client.jar on the player's classpath. No new Java/anonymous type or
    lambda is introduced; the builder verifies the actual donor class set.
    """
    changes = (PREFERENCES, PANEL, PLAYER)
    sources = {}
    details = {}
    for (name, checksum), replacements in zip(JAVA_PINS.items(), changes, strict=True):
        original = (repo / BASE / name).read_bytes()
        changed = apply_exact(original, replacements, checksum)
        if original.count(b"->") != changed.count(b"->"):
            raise ValueError("The loop overlay must not add a lambda")
        sources[name] = changed
        details[name] = {"sourceSha256": checksum, "patchedSha256": digest(changed),
                         "exactInverse": True, "replacementCount": len(replacements)}
    return sources, {
        "sources": details,
        "allowedDex28Families": [
            "Lorg/emulationstation/frontend/station/StationGraphicsPanel;",
            "Lorg/emulationstation/frontend/station/StationGraphicsPreferences;"],
        "allowedDex35Families": [
            "Lorg/emulationstation/frontend/netplay/StationSinglePassVideo720;"],
        "newJavaTypes": False, "newLambdas": False,
        "classSetVerificationRequired": True,
        "compileClientBeforePlayer": True,
        "clientOverlayJarMustPrecedeOldClientJar": True,
        "originalGraphicsStateAndMaskContractUnchanged": True,
        "newPreference": {"file": "station_graphics_r117", "key": "platform_video_loop", "default": True},
        "preferenceIOPerFrameAdded": False, "preferenceReadPerFrameAdded": False,
        "loopUsesExistingWorkerAndDecoder": True,
        "playerSetLoopingRemainsFalse": True,
        "originalStopTwoFramesEarlyTimingUnchanged": True,
        "collectionLoopEnabled": False,
        "backgroundLifecycleAndWatchdogUnchanged": True,
        "physicalPlaybackValidated": False, "thermalReductionMeasured": False,
    }


def patch(native_source: bytes, sony_video_header: bytes,
          original_graphics_header: bytes) -> tuple[bytes, dict[str, bytes], dict]:
    """Return the native source and two generated, explicitly selected headers.

    Apply after sony_media.sourceTransform. Put the generated headers in the
    final native output directory, before prepared media in the include search.
    The original native graphics header is identity-checked but not modified.
    """
    if digest(original_graphics_header) != GRAPHICS_SHA:
        raise ValueError("The existing graphics snapshot contract changed")
    header = apply_exact(sony_video_header, VIDEO_REPLACEMENTS, VIDEO_SHA)
    replaces = (('#include "sony_native_system_video720.h"',
                 '#include "loop_native_system_video720.h"'),)
    cpp = apply_exact(native_source, replaces)
    headers = {"loop_native_system_video720.h": header,
               "native_platform_video_loop.h": NATIVE_SCOPE}
    return cpp, headers, {
        "sourceSha256": digest(native_source), "patchedSha256": digest(cpp),
        "videoSourceSha256": VIDEO_SHA, "graphicsSourceSha256": GRAPHICS_SHA,
        "headers": {name: digest(raw) for name, raw in headers.items()},
        "nativeCppExactInverse": True, "nativeVideoExactInverse": True,
        "onlyNativeIncludeAndVideoStartArgumentChanges": True,
        "nativeGraphicsHeaderByteIdentical": True,
        "nativeVideoCompletionAndRetirementByteIdentical": True,
        "retireBeforeStartPolicyByteIdentical": True,
        "decoderCapacityChanged": False, "maximumRenderFPSChanged": False,
        "ledCacheAndPreloadChanged": False, "graphicsSnapshotABIChanged": False,
        "jniCallsPerFrameAdded": False, "preferenceIOPerFrameAdded": False,
        "platformScope": "systemsMode && !folderMode, focused asset only",
        "collectionLoopEnabled": False, "physicalPlaybackValidated": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=REPO)
    for name in ("native-source", "video-header", "graphics-header", "out"):
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        raise ValueError("Use a new isolated generated-source directory")
    cpp, headers, native_check = patch(args.native_source.read_bytes(),
        args.video_header.read_bytes(), args.graphics_header.read_bytes())
    sources, java_check = transform_java_sources(args.repo)
    args.out.mkdir()
    (args.out / "native_carousel.cpp").write_bytes(cpp)
    for name, raw in headers.items():
        (args.out / name).write_bytes(raw)
    for name, raw in sources.items():
        path = args.out / "java" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
    report = {"schemaVersion": 1, "revision": "R130", "passed": True,
              "recipeSha256": digest(Path(__file__).read_bytes()),
              "native": native_check, "java": java_check,
              "sourcePreparationOnly": True, "apkProduced": False}
    (args.out / "video-loop.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"revision": "R130", "sourcePreparationOnly": True, "out": str(args.out)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
