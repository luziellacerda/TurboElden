"""Offline data/provenance/regression checks for the frozen R37 synopsis index."""
from pathlib import Path
import collections, copy, importlib.util, io, json, sys, unittest
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('synopsis_generator',ROOT/'generate_synopses_r37.py')
g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
NEO=Path(r'G:\TURBORAMA\RetroBat\roms\neogeo\gamelist.xml')
SNES=Path(r'E:\ESTUDO APK\work\native-carousel\implementation\metadata-sources\catalog-xml\34-snes.xml')

class SynopsisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw=(ROOT/'data/synopses-catalog-14.tsv').read_bytes()
        cls.rows=g.parse_catalog(cls.raw)
        cls.neo=NEO.read_bytes();cls.snes=SNES.read_bytes()
        cls.edits=json.loads((ROOT/'data/synopses-editorial.json').read_text('utf8'))
        cls.records=json.loads((ROOT/'data/synopses-complete.json').read_text('utf8'))
        cls.by_id={r['itemId']:r for r in cls.records}
        cls.catalog={r['itemId']:r for r in cls.rows}
    def build(self,rows=None,edits=None):
        return g.make_records(self.rows if rows is None else rows,self.neo,self.snes,self.edits if edits is None else edits)
    def test_01_exact_catalog_scope(self):
        self.assertEqual(2212,len(self.records));self.assertEqual(2212,len(self.by_id))
        self.assertEqual(set(self.catalog),set(self.by_id))
        self.assertEqual(g.EXPECTED,dict(collections.Counter(r['platform'] for r in self.records)))
        for identity,r in self.by_id.items():
            self.assertEqual(self.catalog[identity]['platform'],r['platform'])
            self.assertEqual(self.catalog[identity]['name'],r['name'])
            self.assertEqual(g.LABELS[r['platform']],r['label'])
            self.assertEqual(14,r['catalogRevision'])
    def test_02_reproducible_records_and_header(self):
        self.assertEqual(self.records,self.build())
        self.assertEqual(g.header(self.records),(ROOT/'native/station_game_infos.h').read_text('utf8'))
    def test_03_complete_sorted_usable_descriptions(self):
        self.assertEqual(sorted(self.by_id),[r['itemId'] for r in self.records])
        for r in self.records:
            self.assertGreaterEqual(len(r['description'].strip()),30,r['itemId'])
            self.assertNotRegex(r['description'].lower(),r'sinopse ainda|sinopse n.o dispon.vel|no description available')
            self.assertNotIn('\ufffd',r['description'])
            self.assertNotIn('\f',r['description'])
            self.assertEqual(g.sha(r['description'].encode('utf8')),r['descriptionSha256'])
            self.assertEqual(g.sha(r['serverDescription'].encode('utf8')),r['serverDescriptionSha256'])
    def test_04_source_counts_and_preservation(self):
        self.assertEqual({'server-catalog':2168,'exact-xml':27,'editorial':17},dict(collections.Counter(r['sourceKind'] for r in self.records)))
        overwritten=[]
        for r in self.records:
            old=self.catalog[r['itemId']]['description']
            self.assertEqual(old,r['serverDescription'])
            if r['sourceKind']=='server-catalog':
                self.assertEqual(old,r['description']);self.assertTrue(r['provenance']['preservedVerbatim'])
            elif old.strip():overwritten.append(r['itemId'])
        self.assertEqual(['ab9773189dbfc1571ca0d56adb13ff32'],overwritten)
    def test_05_exact_xml_identity_and_disclosure(self):
        games=g.xml_games(self.neo)
        for r in self.records:
            if r['sourceKind']!='exact-xml':continue
            p=r['provenance'];original=games[p['sourceOrdinal']-1]
            self.assertEqual(r['itemId'],g.stable_id('neogeo',original.findtext('path','')))
            self.assertEqual(original.findtext('desc',''),p['sourceDescription'])
            self.assertEqual(g.NEOGEO_SHA,p['sourceSha256'])
            if r['itemId'] in g.BOOTLEGS:
                self.assertIn('variante não oficial (bootleg)',r['description'])
                self.assertTrue(r['description'].endswith(p['sourceDescription']))
            else:self.assertEqual(p['sourceDescription'],r['description'])
    def test_06_editorial_provenance_and_language(self):
        local=web=0
        for e in self.edits:
            self.assertEqual('pt-BR',e['language']);self.assertTrue(e['identityNotes'])
            self.assertEqual('2026-10-05',e['reviewDate'])
            for s in e['sources']:
                if s['kind']=='web':
                    web+=1;self.assertTrue(s['url'].startswith('https://'));self.assertEqual('2026-10-05',s['accessed'])
                else:
                    local+=1;self.assertEqual(g.SNES_SOURCE_SHA,s['sourceSha256']);self.assertGreater(s['sourceOrdinal'],0)
        self.assertEqual(6,local);self.assertGreaterEqual(web,14)
    def test_07_battletoads_regression(self):
        r=self.by_id['826da6daebe9edbebffb3721f83abf12']
        self.assertEqual('snes',r['platform']);self.assertEqual('editorial',r['sourceKind'])
        self.assertIn('Rash e Pimple',r['description']);self.assertIn('Gamescape',r['description'])
    def test_08_variant_claim_boundaries(self):
        self.assertIn('ROM hack',self.by_id['station_4edf8e2a65d21b8485a9869f7ad77749']['description'])
        self.assertIn('ROM alternativa',self.by_id['station_23c83c0af84a554b338c8eac2876cd8c']['description'])
        self.assertNotRegex(self.by_id['station_79ad81b885f85b3f3948eeef9531c054']['description'],r'19\d\d|20\d\d')
    def test_09_reject_catalog_changes(self):
        with self.assertRaisesRegex(ValueError,'Pinned catalog changed'):g.parse_catalog(self.raw+b'\n')
    def test_10_reject_source_changes(self):
        with self.assertRaisesRegex(ValueError,'Neo Geo source changed'):g.make_records(self.rows,self.neo+b'\n',self.snes,self.edits)
        with self.assertRaisesRegex(ValueError,'SNES source changed'):g.make_records(self.rows,self.neo,self.snes+b'\n',self.edits)
    def test_11_reject_wrong_platform_or_title(self):
        for field,value in [('platform','n64'),('name','Unrelated title')]:
            edits=copy.deepcopy(self.edits);edits[0][field]=value
            with self.assertRaisesRegex(ValueError,'Curated identity mismatch'):self.build(edits=edits)
    def test_12_reject_duplicate_editorial_id(self):
        edits=copy.deepcopy(self.edits);edits[1]['itemId']=edits[0]['itemId']
        with self.assertRaisesRegex(ValueError,'Expected 17 curated titles'):self.build(edits=edits)
    def test_13_reject_unreviewed_overwrite(self):
        rows=copy.deepcopy(self.rows)
        next(r for r in rows if r['itemId']==self.edits[0]['itemId'])['description']='A newly published full server synopsis.'
        with self.assertRaisesRegex(ValueError,'Unexpected overwrite'):self.build(rows=rows)
    def test_14_reject_changed_old_towers_value(self):
        rows=copy.deepcopy(self.rows)
        next(r for r in rows if r['itemId']=='ab9773189dbfc1571ca0d56adb13ff32')['description']='Old Towers revised synopsis from server.'
        with self.assertRaisesRegex(ValueError,'Unexpected overwrite'):self.build(rows=rows)
    def test_15_reject_wrong_xml_ordinal(self):
        edits=copy.deepcopy(self.edits)
        source=next(s for e in edits for s in e['sources'] if s['kind']=='local-xml')
        source['sourceOrdinal']=1
        with self.assertRaisesRegex(ValueError,'SNES editorial source mismatch'):self.build(edits=edits)
    def test_16_reject_missing_provenance(self):
        edits=copy.deepcopy(self.edits);edits[0]['sources']=[]
        with self.assertRaisesRegex(ValueError,'Incomplete provenance'):self.build(edits=edits)
    def test_17_reject_placeholders_and_invalid_text(self):
        for description in ['','Sinopse ainda não disponível nesta edição.','Valid description with broken Unicode \ufffd symbol.']:
            edits=copy.deepcopy(self.edits);edits[0]['description']=description
            with self.assertRaises(ValueError):self.build(edits=edits)
    def test_18_reject_unknown_unresolved_item(self):
        rows=copy.deepcopy(self.rows)
        next(r for r in rows if r['itemId']==self.edits[0]['itemId'])['itemId']='future_unknown_id'
        with self.assertRaisesRegex(ValueError,'Unresolved description'):self.build(rows=rows)
    def test_19_reject_xml_entities_and_escaping_paths(self):
        with self.assertRaisesRegex(ValueError,'XML entities'):g.xml_games(b'<!DOCTYPE gameList><gameList/>')
        for path in ['../../rom.zip','/rom.zip','C:/rom.zip','']:
            with self.assertRaises(ValueError):g.stable_id('neogeo',path)
    def test_20_artifact_hashes_match_build_report(self):
        report=json.loads((ROOT/'evidence/synopses-build.json').read_text('utf8'))
        for key,path in [('outputHeaderSha256','native/station_game_infos.h'),('completeDataSha256','data/synopses-complete.json'),('editorialSha256','data/synopses-editorial.json')]:
            self.assertEqual(report[key],g.sha((ROOT/path).read_bytes()))
        self.assertEqual(0,report['missing']);self.assertEqual(0,report['placeholders']);self.assertEqual(0,report['duplicates'])
        self.assertIn('not a live HTTP',report['scope'])

if __name__=='__main__':
    capture=io.StringIO();result=unittest.TextTestRunner(stream=capture,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(SynopsisTests))
    text=capture.getvalue();print(text)
    report={'suite':'R37 offline synopses','testsRun':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'successful':result.wasSuccessful(),'coverage':'Exact frozen revision 14 / 2212 IDs only; no live catalog or phone tested.','log':text}
    g.dump(ROOT/'evidence/synopses-tests-python.json',report)
    sys.exit(0 if result.wasSuccessful() else 1)