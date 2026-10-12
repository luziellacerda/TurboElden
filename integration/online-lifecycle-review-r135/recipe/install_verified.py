"""Update one explicitly authorized idle USB phone with the fully verified R135."""
from pathlib import Path
import argparse,datetime,json,re,subprocess,os
from release_common import *

HELPER_SHA='98fde21e001000d7ec2013e5d1b7899c3735869d08a4e7c97d45c6cfa26272e1'

def installation_helper():
    path=REPO/'tooling/release/install_current.py'
    require(sha(path)==HELPER_SHA,'Retained installation/idle parser changed')
    require(sha(path.with_name('compile_current.py'))=='0009341406e25b578a44e387c3c9f79c4b36fbaea405e4fe97336d773a95a4ac','Retained release/manifest helper changed')
    return module(path,'r135_retained_installation')

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('base','apk','freeze','identity','verification','tools','receipt'):parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--serial',required=True);parser.add_argument('--expected-model',required=True)
    parser.add_argument('--expected-installed-sha256',required=True)
    parser.add_argument('--allow-update',action='store_true');parser.add_argument('--launch',action='store_true')
    args=parser.parse_args()
    require(re.fullmatch('[A-Za-z0-9._-]+',args.serial) and '._tcp' not in args.serial,'Explicit USB device required')
    require(re.fullmatch('[0-9a-f]{64}',args.expected_installed_sha256),'Explicit inspected installed SHA256 required')
    require(not args.receipt.exists(),'Never overwrite an installation receipt')
    assembly=module(ROOT/'recipe/assemble_apk.py','r135_install_source_guard')
    _,runtime,_,_,_=assembly.inputs(args.base,args.freeze,args.identity)
    final=read(args.verification)
    require(final.get('revision')=='R135' and final['sourceCommit']==runtime['sourceCommit'] and final['freezeSha256']==sha(args.freeze) and final['identityReceiptSha256']==sha(args.identity) and final['replacementCount']==5 and final['additionCount']==0 and final['completeAggregateEntryHashMaps'] is True,'R135 final package/source proof required')
    helper=installation_helper()
    temporary=args.freeze.resolve().parent/'release-temp'
    temporary.mkdir(exist_ok=True)
    helper.release.env_for_tools=lambda context=None:{**os.environ,'TMP':str(temporary),'TEMP':str(temporary),'JAVA_TOOL_OPTIONS':'-Djava.io.tmpdir='+str(temporary),'PYTHONDONTWRITEBYTECODE':'1'}
    context={'current':{'revision':'R135','sourceCommit':runtime['sourceCommit'],'bytes':final['apkBytes'],'sha256':final['apkSha256']},'apk':args.apk,'final':final,'repo':REPO,'tools':args.tools}
    helper.local_preflight(context)
    adb=helper.Adb(args.tools/'platform-tools/adb.exe',args.serial)
    require(adb('get-state').strip()=='device' and adb('get-serialno').strip()==args.serial,'Explicit USB phone not authorized')
    require(adb('shell','am','get-current-user').strip()=='0','Only authorized Android user0 supported')
    model=adb('shell','getprop','ro.product.model').strip()
    require(model.casefold()==args.expected_model.strip().casefold(),'Phone model changed')
    idle=helper.idle_snapshot(adb)
    history={row['task'] for row in idle['records'] if helper.stale_gallery(row,idle,invisible_required=True)}
    before,previous=helper.device_identity(adb),helper.installed_sha(adb)
    require(previous in (args.expected_installed_sha256,final['apkSha256']),'Installed APK differs from explicitly inspected baseline')
    record={'schemaVersion':1,'revision':'R135','package':helper.PACKAGE,'deviceModel':model,'sourceCommit':runtime['sourceCommit'],'startedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'apkSHA256':final['apkSha256'],'apkBytes':final['apkBytes'],'previousAPK_SHA256':previous,'currentResolvedFromExplicitFinalProof':True,'androidUser':0,'activeEmulatorBeforeInstall':False,'activeDownloadBeforeInstall':False,'signatureCertificateSHA256':CERT,'originalInstallerCertificateVerified':True,'installed':False,'installPerformed':False,'launchRequested':False,'officialFrontendObserved':False,'authenticatedSessionChecked':False,'serverActivationVerified':False,'physicalGameplayValidated':False,'externalEmulatorsInstalledByThisProcedure':False,'uninstalledOrClearedData':False,'deviceSettingsChanged':False,'tasksRemoved':False,'appForceStopped':False,'containsDeviceSerialOrPersonalSessionData':False}
    helper.save(args.receipt,record)
    if previous!=final['apkSha256']:
        require(args.allow_update,'Human update authorization flag required')
        assembly.inputs(args.base,args.freeze,args.identity)
        require(read(args.verification)==final and sha(args.apk)==final['apkSha256'] and helper.device_identity(adb)==before,'Package/source/device changed before update')
        fresh=helper.idle_snapshot(adb)
        history|={row['task'] for row in fresh['records'] if helper.stale_gallery(row,fresh,invisible_required=True)}
        result=adb('install','--streaming','--no-incremental','-r','--user','0',args.apk,timeout=600)
        require(re.search('^Success\\s*$',result,re.M),'Android update did not succeed')
        record['installPerformed']=True
    after,actual=helper.device_identity(adb),helper.installed_sha(adb)
    require(all(before[k]==after[k] for k in ('uid','firstInstallTime','dataDir')),'Original installed identity/data preservation failed')
    require(actual==final['apkSha256'],'Device integral APK differs from final verified package')
    record.update(installed=True,deviceAPK_SHA256=actual,installedAPKHashMatchesPackage=True,originalUIDPreserved=True,originalInstallTimePreserved=True,dataDirectoryPreserved=True,dataPreserved=True,sameSigningIdentityAcceptedByAndroid=True,directStreamingUpdate=record['installPerformed'],extraAPKCopyOnPhone=False,completedUTC=datetime.datetime.now(datetime.timezone.utc).isoformat())
    helper.save(args.receipt,record)
    if args.launch:
        fresh=helper.idle_snapshot(adb)
        history|={row['task'] for row in fresh['records'] if helper.stale_gallery(row,fresh,invisible_required=True)}
        record['launchRequested']=True;helper.save(args.receipt,record)
        try:record.update(helper.official_launch(adb,30,history))
        except (ValueError,subprocess.TimeoutExpired):record.update(launchOutcome='unobserved',officialFrontendObserved=False,launchOperationFailed=True)
        record['entryObservationCompletedUTC']=datetime.datetime.now(datetime.timezone.utc).isoformat();helper.save(args.receipt,record)
    print(json.dumps({'revision':'R135','deviceModel':model,'installed':record['installed'],'installPerformed':record['installPerformed'],'officialFrontendObserved':record['officialFrontendObserved'],'launchOutcome':record.get('launchOutcome','not-requested')}))

if __name__=='__main__':main()
