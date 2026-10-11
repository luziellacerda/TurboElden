"""Pinned donor and instruction-order probes; not an Android/gameplay test."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("dolphin_recipe", HERE / "recipe/patch_dolphin_smali.py")
recipe = importlib.util.module_from_spec(spec); spec.loader.exec_module(recipe)
checks = 0

def check(value, label):
    global checks
    if not value:
        raise AssertionError(label)
    checks += 1

def body(text, signature):
    found = re.findall(r"(?ms)^\.method[^\n]* " + re.escape(signature) + r"\n.*?^\.end method$", text)
    check(len(found) == 1, "one method " + signature)
    return found[0]

def rejects(action, label):
    try:
        action()
    except ValueError:
        check(True, label)
        return
    raise AssertionError(label)

def main():
    p=argparse.ArgumentParser();p.add_argument("--base-apk",type=Path,required=True);p.add_argument("--core",type=Path,required=True);p.add_argument("--bootstrap",type=Path,required=True);p.add_argument("--receipt",type=Path,required=True);a=p.parse_args()
    sources={"core":a.core,"bootstrap":a.bootstrap}
    initial={group:recipe.tree(source) for group,source in sources.items()}
    changes,planned=recipe.plan(sources,a.base_apk);again=recipe.plan(sources,a.base_apk)
    check((changes,planned)==again,"deterministic plan");check(len(planned)==5,"exact five donor changes")
    texts={Path(relative).name:data.decode().replace("\r\n","\n") for (_,relative),data in planned.items()}
    app=body(texts["DolphinApplication.smali"],"onCreate()V")
    check(app.index("->libraryName(")<app.index("->loadLibrary("),"select library before native load")
    check('const-string v0, "dolp"' not in app,"online library selection replaces only literal")
    net=texts["NetplaySession.smali"]
    boot=body(net,"onBootGame(Ljava/lang/String;J)V")
    check(boot.index("->bootSessionDataPointer:J")<boot.index("->onBootGame("),"preserve boot pointer before consuming callback")
    check(boot.index("->onBootGame(")<boot.index("->_stopGame:"),"Station consumes independent native lobby path")
    for signature,hook in [("onStopGame()V","onNativeStop"),("onConnectionLost()V","onConnectionLost"),("onConnectionError(Ljava/lang/String;)V","onConnectionError")]:
        b=body(net,signature);check(b.index("->"+hook+"(")<b.index("iget-object"),"callback before object register reused");check("if-eqz v0" in b and "return-void" in b,"online consumes, offline falls through")
    for signature in ["closeBlocking()V","releaseNativeResources()V"]:
        b=body(net,signature);check("->allowClose(Ljava/lang/Object;)Z" in b,"real close paths guarded");check(b.index("->allowClose(")<min(x for x in [b.find("monitor-enter"),b.find("iget-wide")] if x>=0),"guard before monitor/resource reads")
    check("->releaseNativeResources()V" in body(net,"finalize()V"),"finalize delegates into guarded resource release")
    game=texts["EmulationActivity.smali"]
    for signature,hook in [("onCreate(Landroid/os/Bundle;)V","onGameCreate"),("onResume()V","onGameResume"),("onDestroy()V","onGameDestroy")]:
        b=body(game,signature);check("invoke-static/range {p0 .. p0}" in b,"safe lifecycle register encoding");check(b.index("->"+hook+"(")<b.index("invoke-super"),"real Activity captured before original mutation")
    pause=body(game,"onPause()V");check("->onGamePause(Landroid/app/Activity;)V" in pause and "invoke-super {p0}" in pause,"inherited pause preserves super and Station visibility")
    menu=body(game,"handleMenuAction(I)V");check(menu.index("->allowMenuAction(")<menu.index("->onMenuAction(")<menu.index("move-object/from16 v0, p0"),"authorize allowed menu before original action")
    check(menu.count("invoke-static/range {p0 .. p1}")==2,"large-locals menu uses range invoke")
    long_back=body(game,"onKeyLongPress(ILandroid/view/KeyEvent;)Z")
    check(long_back.index("if-ne p1, v0, :cond_0")<long_back.index("->onMenuAction(")<long_back.index("iget-object p0"),"only validated BACK long authorizes before Activity is overwritten")
    check(long_back.index("->onMenuAction(")<long_back.index("->StopEmulation("),"long human BACK exit authorizes before original stop")
    check(long_back.index("->onMenuAction(")<long_back.index("\n    :cond_0\n")<long_back.index("invoke-super {p0, p1, p2}"),"other long key codes retain original super implementation")
    save=body(game,"onSaveInstanceState(Landroid/os/Bundle;)V");check(save.index("->allowSaveState(")<save.index("->SaveStateAs("),"temporary save guarded")
    check(save.index(":station_dolphin_skip_temporary_state",save.index("->SaveStateAs("))<save.index('const-string v0, "SelectedGames"'),"Bundle persistence after skipped native save")
    original=recipe.fs(a.core/"org/dolphinemu/dolphinemu/activities/EmulationActivity.smali").read_text().replace("\r\n","\n")
    orig_save=body(original,"onSaveInstanceState(Landroid/os/Bundle;)V")
    check(save[save.index('const-string v0, "SelectedGames"'):]==orig_save[orig_save.index('const-string v0, "SelectedGames"'):],"all original Bundle/state restoration logic retained")
    bootstrap=texts["DolphinBootstrap.smali"]
    for method_name,kind in [("userDirectory","User"),("internalDirectory","Internal"),("cacheDirectory","Cache")]:
        b=body(bootstrap,method_name+"(Landroid/content/Context;)Ljava/io/File;")
        check(f'const-string v0, "{kind}"' in b and "->directory(" in b,"typed isolated directory");check("if-eqz v0" in b and "return-object v0" in b,"null preserves original offline directory")
    check("->skipLegacySaves(Landroid/content/Context;)Z" in body(bootstrap,"migrateLegacySaves(Landroid/content/Context;)V"),"no offline save import in online session")
    entry=body(texts["DolphinEntryActivity.smali"],"onCreate(Landroid/os/Bundle;)V")
    check(entry.index("invoke-super")<entry.index("->rejectOfflineLaunch(")<entry.index("->getWindow("),"normal launch rejection follows super but precedes UI/boot")
    check("return-void" in entry[entry.index("->rejectOfflineLaunch("):entry.index("->getWindow(")],"online normal entry does not dispatch game")
    for name,patcher in recipe.PATCHERS.items():
        original_file=next(relative for group in recipe.EXPECTED_FILES.values() for relative in group if Path(relative).name==name)
        group="core" if original_file.startswith("org/dolphinemu") else "bootstrap"
        raw=recipe.fs(sources[group]/original_file).read_text().replace("\r\n","\n")
        rejects(lambda p=patcher,r=raw:p(r.replace(".method", ".removed_method")),"invalid input anchors rejected")
    check({group:recipe.tree(source) for group,source in sources.items()}==initial,"both full donor trees unchanged")
    # Exact source declarations required by emitted invocations; compiled javap
    # is a separate build check, not fabricated by these textual probes.
    apis={"StationDolphinSelector":["libraryName","directory","skipLegacySaves","rejectOfflineLaunch"],"StationDolphinSession":["onGameCreate","onGameResume","onGamePause","onGameDestroy","allowMenuAction","onMenuAction","allowSaveState","onBootGame","onNativeStop","onConnectionLost","onConnectionError","allowClose"]}
    for cls,names in apis.items():
        source=(HERE/f"java/org/emulationstation/frontend/netplay/{cls}.java").read_text()
        for name in names:check(re.search(r"public static(?: synchronized)? [\w<>]+ "+name+r"\(",source) is not None,"public static API "+name)
    receipt={"schema":"station-dolphin-smali-probe-v1","checks":checks,"modifiedFiles":changes,"requiredPublicStaticApis":apis,"donorModified":False,"scope":"Pinned full source trees, real donor anchors/instruction order, hook declaration checks; independent DEX assembly reported separately","physicalGameplayValidated":False}
    a.receipt.parent.mkdir(parents=True,exist_ok=True);a.receipt.write_text(json.dumps(receipt,indent=2)+"\n",encoding="utf-8");print(json.dumps({"checks":checks,"receipt":str(a.receipt)}))

if __name__=="__main__":main()
