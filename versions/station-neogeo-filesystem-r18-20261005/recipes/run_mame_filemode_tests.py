"""Test the real bridge methods and compile both Java files; no APK/DEX/ADB.

All generated sources, classes, fixtures and reports stay in the explicit E: test
directory. The input sources in this script's java/ directory are read only.
"""
from pathlib import Path
import hashlib
import json
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / 'java/org/emulationstation/frontend'
OUTPUT = Path(r'E:\ESTUDO APK\work\station-neogeo-access-20261005\tests')
JDK = Path(r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin')
ANDROID = Path(r'G:\Android\Sdk\platforms\android-34\android.jar')
DONOR = Path(r'E:\ESTUDO APK\work\native-carousel\implementation\mame-current\donor-decoded\smali\com\seleuco\mame4droid')


def extract_method(source, signature):
    start = source.index(signature)
    cursor = source.index('{', start) + 1
    depth = 1
    while depth:
        if source[cursor] == '{':
            depth += 1
        elif source[cursor] == '}':
            depth -= 1
        cursor += 1
    return source[start:cursor]


def run(*args):
    result = subprocess.run([str(arg) for arg in args], capture_output=True,
                            text=True, encoding='utf-8', errors='replace')
    if result.returncode:
        raise RuntimeError(result.stdout + result.stderr)
    return result.stdout + result.stderr


bootstrap = (SOURCE / 'MameBootstrap.java').read_text(encoding='utf-8-sig')
entry = (SOURCE / 'MameEntryActivity.java').read_text(encoding='utf-8-sig')
original_bootstrap = Path(r'E:\ESTUDO APK\work\station-emulators-r15-20261005\mame\java\org\emulationstation\frontend\MameBootstrap.java').read_text(encoding='utf-8-sig')

checks = 0


def check(value):
    global checks
    checks += 1
    assert value, f'contract check {checks}'


# Read-only upstream contracts. Native quote behavior was additionally audited
# in libMAME4droid.so: myosd_droid_main VA 0x0a0725f8..0x0a0727a8 recognizes
# delimiter 0x27 (apostrophe), space 0x20 outside quotes, no escape syntax.
prefs = (DONOR / 'helpers/PrefsHelper.smali').read_text(encoding='utf-8')
activity = (DONOR / 'MAME4droid.smali').read_text(encoding='utf-8')
worker = (DONOR / 'Emulator$4.smali').read_text(encoding='utf-8')
pref_method = prefs.split('.method public getROMsDIR()')[1].split('.end method')[0]
check('"PREF_ROMsDIR_2"' in pref_method)
init = activity.split('.method protected initMame4droid()')[1].split('.end method')[0]
check('->getROMsDIR()' in init and 'if-nez v0, :cond_0' in init)
check('->length()' not in init)
check('const-string v1, ""' in init and '->setROMsDIR' in init)
check('->length()I' in worker and 'if-eqz v7, :cond_6' in worker)
check('const-string v9, "cli_params"' in worker)
check(worker.index('->init(Ljava/lang/String;Ljava/lang/String;II)V')
      < worker.index('const/4 v6, 0x5') < worker.index('->runT()V'))
check('i.putExtra("cli_params",MameBootstrap.cliParamsFor(game));' in entry)
check(entry.index('if(settings){') < entry.index('i.putExtra("cli_params"'))
check('if(!settings&&(rom==null||!rom.isFile()||!rom.canRead()))' in entry)
check('i.setAction(Intent.ACTION_VIEW);' in entry)
check('i.setDataAndType(Uri.fromFile(rom),mimeFor(game));' in entry)
check('startActivityForResult(i,41);' in entry)
check('Thread.sleep' not in bootstrap + entry)
check('MessageDigest' not in bootstrap + entry)

harness = r'''import java.io.*;
import java.util.*;
import java.nio.file.*;
public class MameFileModeTest {
 static File ROMS_ROOT;
 static int checks;
 static void check(boolean value){checks++;if(!value)throw new AssertionError("check "+checks);}
 interface Throwing {void run() throws Exception;}
 static void rejects(Throwing action)throws Exception {boolean failed=false;try{action.run();}catch(IllegalArgumentException e){failed=true;}check(failed);}
 static class Context {File dir;Context(File p){dir=p;}File getFilesDir(){return dir;}}
 static class SharedPreferences {
  Map<String,String> data=new HashMap<>();boolean commitSucceeds=true;
  String getString(String key,String fallback){return data.getOrDefault(key,fallback);}
  Editor edit(){return new Editor();}
  class Editor {
   Map<String,String> pending=new HashMap<>();Set<String> removed=new HashSet<>();
   Editor putString(String key,String value){if(value==null)return remove(key);pending.put(key,value);removed.remove(key);return this;}
   Editor remove(String key){pending.remove(key);removed.add(key);return this;}
   boolean commit(){if(!commitSucceeds)return false;for(String key:removed)data.remove(key);data.putAll(pending);return true;}
  }
 }
 static class PreferenceManager {static SharedPreferences prefs=new SharedPreferences();static SharedPreferences getDefaultSharedPreferences(Context context){return prefs;}}
 static class Log {static void i(String tag,String value){}}
 static boolean upstreamUsesSaf(){String dir=PreferenceManager.prefs.getString("PREF_ROMsDIR_2",null);return dir!=null&&dir.length()!=0;}
 static boolean upstreamNeedsPicker(){return PreferenceManager.prefs.getString("PREF_INSTALLATION_DIR",null)==null||PreferenceManager.prefs.getString("PREF_ROMsDIR_2",null)==null;}
 // Port of the audited native CLI token rules for this fixed argument shape.
 // This is a host contract test, not execution of the ARM64 native engine.
 static List<String> nativeTokens(String input){
  List<String> tokens=new ArrayList<>();int at=0;
  while(at<input.length()){
   while(at<input.length()&&input.charAt(at)==' ')at++;
   if(at==input.length())break;
   if(input.charAt(at)=='\''){
    int start=++at;while(at<input.length()&&input.charAt(at)!='\'')at++;
    if(at==input.length())throw new IllegalArgumentException("unclosed quote");
    tokens.add(input.substring(start,at++));
   }else{
    int start=at;while(at<input.length()&&input.charAt(at)!=' ')at++;
    tokens.add(input.substring(start,at));
   }
  }
  return tokens;
 }
'''
for signature in ['static File romDirFor(', 'static String quoteCliPath(',
                  'static String cliParamsFor(', 'public static File files(',
                  'public static void seed(Context c,String path)']:
    harness += extract_method(bootstrap, signature).replace('android.util.Log.i', 'Log.i') + '\n'
harness += extract_method(entry, 'private static String mimeFor(') + '\n'
harness += extract_method(original_bootstrap, 'public static void seed(Context c,String path)').replace('public static void seed(', 'public static void r15Seed(').replace('android.util.Log.i', 'Log.i') + '\n'
harness += r'''
 public static void main(String[] args)throws Exception {
  Path root=Paths.get(args[0]);Files.createDirectories(root);ROMS_ROOT=root.resolve("roms").toFile();ROMS_ROOT.mkdirs();
  Context context=new Context(root.resolve("private").toFile());context.dir.mkdirs();
  SharedPreferences prefs=PreferenceManager.prefs;
  prefs.data.put("unrelated_setting","keep");
  String initialInstallation=null;
  for(String platform:new String[]{"neo-geo","mame","cps1","cps2","cps3","neo-geo-cd"}){
   Path content=root.resolve("roms/.station-v2/"+platform+"/station_fixture/install-123/content com espaco");Files.createDirectories(content);
   Path game=content.resolve("game.zip");Path bios=content.resolve("neogeo.zip");Files.write(game,new byte[]{1,2,3});Files.write(bios,new byte[]{4,5,6});
   prefs.data.put("PREF_ROMsDIR","old");prefs.data.put("PREF_ROMsDIR_2","old");prefs.data.put("PREF_SAF_URI","content://old/tree");
   r15Seed(context,game.toString());
   check(upstreamUsesSaf());check(!prefs.data.containsKey("PREF_SAF_URI"));check(!upstreamNeedsPicker());
   check(romDirFor(game.toString()).equals(content.toFile().getAbsoluteFile()));
   seed(context,game.toString());
   check(prefs.data.containsKey("PREF_ROMsDIR_2"));
   check(prefs.data.get("PREF_ROMsDIR_2").isEmpty());
   check(!prefs.data.containsKey("PREF_ROMsDIR"));
   check(!prefs.data.containsKey("PREF_SAF_URI"));
   check(new File(prefs.data.get("PREF_INSTALLATION_DIR")).isDirectory());
   if(initialInstallation==null)initialInstallation=prefs.data.get("PREF_INSTALLATION_DIR");
   check(initialInstallation.equals(prefs.data.get("PREF_INSTALLATION_DIR")));
   List<String> tokens=nativeTokens(cliParamsFor(game.toString()));
   check(tokens.size()==2);check(tokens.get(0).equals("-rompath"));check(tokens.get(1).equals(content.toAbsolutePath().toString()));
   check(Arrays.equals(Files.readAllBytes(game),new byte[]{1,2,3}));check(Arrays.equals(Files.readAllBytes(bios),new byte[]{4,5,6}));
   check(prefs.data.get("unrelated_setting").equals("keep"));
   check(prefs.data.get("PREF_ROMsDIR_2")!=null); // skips upstream first-run picker
   check(prefs.data.get("PREF_ROMsDIR_2").length()==0); // skips upstream SAF block
   check(!upstreamUsesSaf());check(!upstreamNeedsPicker());
  }
  Path custom=root.resolve("custom-saves");Files.createDirectories(custom);Path save=custom.resolve("save.nv");Files.write(save,new byte[]{7,8,9});
  prefs.data.put("PREF_INSTALLATION_DIR",custom.toString());prefs.data.put("PREF_OLD_INSTALLATION_DIR",custom.toString());
  for(int n=0;n<3;n++){seed(context,null);check(prefs.data.get("PREF_INSTALLATION_DIR").equals(custom.toString()));check(prefs.data.get("PREF_OLD_INSTALLATION_DIR").equals(custom.toString()));check(Arrays.equals(Files.readAllBytes(save),new byte[]{7,8,9}));check(prefs.data.get("PREF_ROMsDIR_2").equals(""));}
  prefs.data.put("PREF_INSTALLATION_DIR",root.resolve("missing").toString());seed(context,null);
  check(prefs.data.get("PREF_INSTALLATION_DIR").equals(initialInstallation));check(prefs.data.get("PREF_OLD_INSTALLATION_DIR").equals(custom.toString()));
  prefs.commitSucceeds=false;boolean failed=false;try{seed(context,null);}catch(IllegalStateException expected){failed=true;}check(failed);prefs.commitSucceeds=true;
  rejects(()->cliParamsFor(null));rejects(()->cliParamsFor(root.resolve("absent.zip").toString()));rejects(()->cliParamsFor(root.toString()));
  for(String path:new String[]{"/storage/emulated/0/EmulationStation/roms/content","/root/dir with spaces/content","/root/ação/日本/content","/root/a\"b/content","E:\\fixture with space\\content"}){
   List<String> tokens=nativeTokens("-rompath "+quoteCliPath(path));check(tokens.size()==2);check(tokens.get(0).equals("-rompath"));check(tokens.get(1).equals(path));
  }
  for(String path:new String[]{"", "a'b", "a;b", "a\nb", "a\rb", "a\tb", "a\u0000b", "a\u007fb"})rejects(()->quoteCliPath(path));
  rejects(()->quoteCliPath(null));
  check(nativeTokens("-rompath \"parent with space\"").size()>2);
  check(mimeFor("game.ZIP").equals("application/zip"));check(mimeFor("game.chd").equals("application/octet-stream"));check(mimeFor("game.cue").equals("text/plain"));
  System.out.println("PASS "+checks+" real-method filesystem mode, CLI quoting, path, settings, saves and failure checks");
 }
}
'''

OUTPUT.mkdir(parents=True, exist_ok=True)
work = Path(tempfile.mkdtemp(prefix='filemode-', dir=OUTPUT))
generated = work / 'MameFileModeTest.java'
generated.write_text(harness, encoding='utf-8')
host_classes = work / 'host-classes'
android_classes = work / 'android-classes'
host_classes.mkdir()
android_classes.mkdir()
logs = [run(JDK / 'javac.exe', '-encoding', 'UTF-8', '-d', host_classes, generated)]
logs.append(run(JDK / 'java.exe', '-cp', host_classes, 'MameFileModeTest', work / 'fixture with spaces'))
logs.append(run(JDK / 'javac.exe', '-encoding', 'UTF-8', '-source', '8', '-target', '8',
                '-classpath', ANDROID, '-d', android_classes,
                SOURCE / 'MameBootstrap.java', SOURCE / 'MameEntryActivity.java'))
report = {
    'sourceDirectory': str(SOURCE), 'outputDirectory': str(work),
    'contractChecks': checks, 'hostOutput': logs[1].strip(),
    'androidCompile': 'API34 Java8', 'nativeExecuted': False, 'apkBuilt': False,
    'deviceTested': False,
    'sourceSha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                     for p in [SOURCE / 'MameBootstrap.java', SOURCE / 'MameEntryActivity.java']},
    'quoteContract': 'MAME4droid 1.41.2 myosd_droid_main: apostrophe 0x27; spaces outside quotes; no escape assumed',
}
(OUTPUT / 'result.log').write_text(''.join(logs), encoding='utf-8')
(OUTPUT / 'result.json').write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
print(json.dumps(report, indent=2, ensure_ascii=False))
