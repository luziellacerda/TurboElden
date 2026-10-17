#!/usr/bin/env python3
"""Merge updater declarations into the current decoded Manifest, preserving its SDK.

This writes XML for the existing private packaging recipe; it does not replace
binary Manifest/resources in an APK and never signs or installs a package.
"""
import argparse
from pathlib import Path
import xml.etree.ElementTree as ET

ANDROID='http://schemas.android.com/apk/res/android'
ET.register_namespace('android',ANDROID)
def attr(name):return '{'+ANDROID+'}'+name

def merge(source,version,name):
    root=ET.fromstring(source)
    if root.get('package')!='org.turboramastation.frontend':raise ValueError('Wrong package')
    before=int(root.get(attr('versionCode'),'0'))
    if not before<version<=2100000000 or not 1<=len(name)<=100 or any(ord(c)<32 for c in name):raise ValueError('Version must increase and have a valid name')
    application=root.find('application')
    if application is None:raise ValueError('Missing original application')
    root.set(attr('versionCode'),str(version));root.set(attr('versionName'),name)
    for permission in ('REQUEST_INSTALL_PACKAGES','FOREGROUND_SERVICE','FOREGROUND_SERVICE_DATA_SYNC'):
        full='android.permission.'+permission
        existing=[p for p in root.findall('uses-permission') if p.get(attr('name'))==full]
        if len(existing)>1:raise ValueError('Duplicate existing permission')
        if not existing:root.insert(0,ET.Element('uses-permission',{attr('name'):full}))
        elif existing[0].get(attr('maxSdkVersion')) is not None:raise ValueError('Updater permission is limited by the current manifest; review required')
    for tag,suffix in (('activity','Activity'),('service','Service'),('receiver','Receiver')):
        full='org.emulationstation.frontend.station.StationAppUpdate'+suffix
        existing=[p for p in application.findall(tag) if p.get(attr('name'))==full]
        if len(existing)>1:raise ValueError('Duplicate updater component')
        component=existing[0] if existing else ET.SubElement(application,tag,{attr('name'):full})
        component.set(attr('exported'),'false')
        if tag=='service':component.set(attr('foregroundServiceType'),'dataSync')
    return ET.tostring(root,encoding='utf-8',xml_declaration=True)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest',required=True,type=Path)
    parser.add_argument('--version-code',required=True,type=int)
    parser.add_argument('--version-name',required=True)
    parser.add_argument('--out',required=True,type=Path)
    args=parser.parse_args()
    result=merge(args.manifest.read_bytes(),args.version_code,args.version_name)
    with args.out.open('xb') as output:output.write(result)

if __name__=='__main__':main()
