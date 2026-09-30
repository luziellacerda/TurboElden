from pathlib import Path
import subprocess,shutil,hashlib,json,urllib.request,os
P=Path(r'E:\ESTUDO APK\work\native-carousel\implementation')
S=P/'platform-media-refresh/psvita';R=P/'emulator-completion/vita-rar-diagnosis'
N=Path(r'E:\TurboEdenEngine\android-ndk-r28c/toolchains/llvm/prebuilt/windows-x86_64')
source=S/'archive/libarchive-3.8.9/libarchive/archive_read_support_format_rar5.c'
text=source.read_text();old='ret = do_unpack(a, rar5, buff, size, offset);\n\tif(ret != ARCHIVE_OK) {'
assert text.count(old)==1
new='''ret = do_unpack(a, rar5, buff, size, offset);
\t/* RAR5 may finish with an output-empty block. Persist EOF and verify
\t * checksums only when the declared input and output are complete.
\t * Based on libarchive PR 3361 revision 317730a. */
\tif(ret == ARCHIVE_EOF && rar5->file.bytes_remaining == 0 &&
\t    rar5->cstate.last_write_ptr == rar5->file.unpacked_size)
\t\tret = ARCHIVE_OK;
\tif(ret != ARCHIVE_OK) {'''
patched=R/source.name;patched.write_text(text.replace(old,new),encoding='utf-8')
shutil.copy2(source,R/'original-rar5.c')
cmd=[str(N/'bin/clang.exe'),'--target=aarch64-linux-android26','--sysroot='+str(N/'sysroot'),'-DHAVE_CONFIG_H','-DLIBARCHIVE_STATIC','-D__LIBARCHIVE_ENABLE_VISIBILITY','-DANDROID','-fdata-sections','-ffunction-sections','-funwind-tables','-fstack-protector-strong','-D_FORTIFY_SOURCE=2','-fvisibility=hidden','-O3','-DNDEBUG','-fPIC']
cmd+=['-I'+str(x) for x in [S/'archive/libarchive-3.8.9/libarchive',S/'archive/build',S/'archive/libarchive-3.8.9/contrib/android/include']]
obj=R/'archive_read_support_format_rar5.c.o'
subprocess.run(cmd+['-c',str(patched),'-o',str(obj)],check=True)
lib=R/'libarchive-rar5-eof.a';shutil.copy2(S/'archive/build/libarchive/libarchive.a',lib)
subprocess.run([str(N/'bin/llvm-ar.exe'),'r',str(lib),str(obj)],check=True)
subprocess.run([str(N/'bin/clang.exe'),'--target=aarch64-linux-android26','--sysroot='+str(N/'sysroot'),'-O2','-fPIE','-pie','-I'+str(S/'archive/libarchive-3.8.9/libarchive'),str(R/'read_only_archive.c'),str(lib),'-lz','-lm','-o',str(R/'read-only-archive-fixed')],check=True)
record={'reference':'https://github.com/libarchive/libarchive/pull/3361','upstream_status':'open, not merged at review','revision_basis':'317730a guarded EOF finalization','change':'rar5_read_data: promote ARCHIVE_EOF only when compressed input consumed and declared output size complete; reaches existing checksum validation; preserve negative errors and incomplete EOF behavior','original_source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'patched_source_sha256':hashlib.sha256(patched.read_bytes()).hexdigest(),'original_static_sha256':hashlib.sha256((S/'archive/build/libarchive/libarchive.a').read_bytes()).hexdigest(),'patched_static_sha256':hashlib.sha256(lib.read_bytes()).hexdigest()}
(R/'patch-record.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
adb=Path(__file__).parent/'work/android-tools/platform-tools/adb.exe';os.environ['ADB_USB_LEGACY']='1';target='/data/local/tmp/turborama-read-only-archive-fixed'
subprocess.run([str(adb),'push',str(R/'read-only-archive-fixed'),target],check=True)
subprocess.run([str(adb),'shell','chmod','700',target],check=True)
game='/sdcard/EmulationStation/roms/psvita/Mortal Kombat [PCSE00023].psvita.rar'
try:
 result=subprocess.run([str(adb),'shell',target+" '"+game+"'"],capture_output=True,timeout=300)
 output=result.stdout.decode(errors='replace')+result.stderr.decode(errors='replace')
 (R/'archive-read-fixed.log').write_text(output,encoding='utf-8');print(output)
 assert result.returncode==0
finally:subprocess.run([str(adb),'shell','rm','-f',target],check=True)
