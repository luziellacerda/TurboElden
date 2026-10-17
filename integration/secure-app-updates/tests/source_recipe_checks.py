#!/usr/bin/env python3
import importlib.util
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

MODULE=Path(__file__).resolve().parents[1]
def module(name):
    spec=importlib.util.spec_from_file_location(name,MODULE/'recipe'/(name+'.py'))
    value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value
hooks=module('patch_sources');manifest=module('merge_manifest')

class Recipes(unittest.TestCase):
    def test_get_hook_does_not_change_current_accessor(self):
        original='        return instance;\r\n    }\r\n    static StationAndroid current(){return instance;}\r\n'
        result=hooks.patch('StationAndroid.java',original)
        self.assertIn('current(){return instance;}',result)
        self.assertEqual(result.replace('        '+hooks.MARKER+'\r\n        StationAppUpdateUi.install(instance,context);\r\n',''),original)
    def test_duplicate_or_installed_hooks_refused(self):
        for text in ('        return instance;\n'*2,hooks.MARKER+'\n        return instance;'):
            with self.assertRaises(ValueError):hooks.patch('StationAndroid.java',text)
    def test_api_outside_added_methods_identical(self):
        original='prefix\r\n    private JSONObject signed(body) { keep(); }\r\n'
        result=hooks.patch('StationApi.java',original)
        self.assertEqual(result.replace(hooks.API.replace('\n','\r\n')+'\r\n',''),original)
    def test_http_preserves_non_update_allowlist(self):
        original='if ("POST".equals(method)) return path.equals("/v1/station/downloads/authorize");\n        if (!"GET".equals(method)) return false;\nkeepRedirectAndPinRules();'
        result=hooks.patch('StationHttp.java',original)
        self.assertIn('keepRedirectAndPinRules();',result)
        self.assertIn('path.equals("/v1/station/downloads/authorize")',result)
        self.assertIn('path.startsWith("/v1/station/updates/artifacts/")',result)
    def source(self):
        return b'<manifest xmlns:android="http://schemas.android.com/apk/res/android" package="org.turboramastation.frontend" android:versionCode="100" android:versionName="Existing"><uses-sdk android:minSdkVersion="28" android:targetSdkVersion="28"/><uses-permission android:name="android.permission.INTERNET"/><application android:appComponentFactory="keep.Factory"><activity android:name="keep.Existing" android:exported="true"/><service android:name="keep.Service"/></application></manifest>'
    def test_manifest_preserves_sdk_existing_components_and_factory(self):
        result=ET.fromstring(manifest.merge(self.source(),101,'Update 101'));a=manifest.attr
        self.assertEqual(result.find('uses-sdk').attrib,{a('minSdkVersion'):'28',a('targetSdkVersion'):'28'})
        self.assertEqual(result.find('application').get(a('appComponentFactory')),'keep.Factory')
        self.assertEqual(result.find('application/activity').get(a('name')),'keep.Existing')
        self.assertEqual(result.find('application/service').get(a('name')),'keep.Service')
        components=[e for e in result.find('application') if 'StationAppUpdate' in e.get(a('name'),'')]
        self.assertEqual(len(components),3);self.assertTrue(all(e.get(a('exported'))=='false' for e in components))
    def test_version_rollback_refused(self):
        for version in (100,99,0,2100000001):
            with self.assertRaises(ValueError):manifest.merge(self.source(),version,'Invalid')
    def test_wrong_package_refused(self):
        with self.assertRaises(ValueError):manifest.merge(self.source().replace(b'org.turboramastation.frontend',b'other.package'),101,'Invalid')
    def test_later_manifest_merge_does_not_duplicate_components(self):
        first=manifest.merge(self.source(),101,'One');second=ET.fromstring(manifest.merge(first,102,'Two'))
        self.assertEqual(len(second.findall('uses-permission')),4)
        self.assertEqual(len(list(second.find('application'))),5)

if __name__=='__main__':unittest.main()
