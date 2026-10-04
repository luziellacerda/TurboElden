from pathlib import Path
import collections,csv,hashlib,json,re,unittest,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parent
class MetadataTests(unittest.TestCase):
 def setUp(self):
  self.rows=json.loads((ROOT/'assets/station-metadata/station-synopses.json').read_text('utf8'))
 def test_exact_counts(self):
  self.assertEqual(len(self.rows),1816)
  self.assertEqual(sum(bool(r['description']) for r in self.rows),1804)
  self.assertEqual(collections.Counter(r['platform'] for r in self.rows),{'snes':644,'snesbr':191,'megadrive':887,'megadrivebr':94})
 def test_identity_binary_search_order(self):
  ids=[r['itemId'] for r in self.rows]
  self.assertEqual(ids,sorted(ids));self.assertEqual(len(set(ids)),len(ids))
  self.assertTrue(all(re.fullmatch(r'[A-Za-z0-9_-]{8,64}',i) for i in ids))
 def test_source_exact_name_and_ordinal(self):
  roots={k:ET.parse(Path(r'G:\TURBORAMA\RetroBat\roms')/k/'gamelist.xml').getroot().findall('game') for k in ['snes','megadrive']}
  for r in self.rows:
   g=roots[r['sourcePlatform']][r['sourceOrdinal']-1]
   self.assertEqual(g.findtext('name'),r['name'])
 def test_published_production_identity(self):
  path=ROOT/'server-inputs/catalogo-conciliado-jogos-capas-downloads-20261003.tsv'
  self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),'3542803f0887a3595bfcae6f2c1bd5e860b5ab81df32f308c2f3ac1fbd071f12')
  rows=[r for r in csv.DictReader(path.read_text('utf-8-sig').splitlines(),delimiter='\t') if r['catalogVisible']=='yes']
  expected={(r['itemId'],r['platform'],r['name'],r['sourcePlatform'],int(r['sourceXmlEntry'])) for r in rows}
  actual={(r['itemId'],r['platform'],r['name'],r['sourcePlatform'],r['sourceOrdinal']) for r in self.rows}
  self.assertEqual(actual,expected)
 def test_preserved_id_from_phone(self):
  byid={r['itemId']:r for r in self.rows}
  row=byid['bba0ae28b358b6581357f6dff15799af']
  self.assertEqual(row['name'],'Clay Fighter');self.assertTrue(row['description'])
  row=byid['826da6daebe9edbebffb3721f83abf12']
  self.assertEqual(row['name'],'Battletoads in Battlemaniacs (USA)')
  self.assertFalse(row['description'])
 def test_diagnostic_export_only_when_identity_changes(self):
  s=(ROOT/'native/native_carousel.cpp').read_text('utf8')
  self.assertIn('if(identityChanged)exportCatalog(real);',s)
  self.assertLess(s.index('bool identityChanged='),s.index('syncedRevision=rev;'))
 def test_missing_explicit(self):
  missing=json.loads((ROOT/'assets/station-metadata/missing-station-synopses.json').read_text('utf8'))
  self.assertEqual(len(missing),12);self.assertTrue(all(not r['description'] for r in missing))
 def test_supplemental_sources_exact(self):
  report=json.loads((ROOT/'evidence/missing-synopses-exact-search.json').read_text('utf8'))
  self.assertEqual(report['counts'],{'unique-description':29,'missing':6,'ambiguous':6})
  byid={r['itemId']:r for r in self.rows}
  for item in report['items']:
   row=byid[item['itemId']]
   if item['status']!='unique-description':self.assertFalse(row['description']);continue
   self.assertEqual(len({m['description'] for m in item['matches']}),1)
   self.assertEqual(row['description'],item['matches'][0]['description'])
   for match in item['matches']:
    self.assertEqual(match['platform'],row['sourcePlatform'])
    self.assertTrue(match['name']==row['name'] or (match['stem'] and match['stem']==item['originalStem']))
 def test_native_fallback_utf8(self):
  source=(ROOT/'native/native_info.h').read_text('utf8')
  self.assertIn('Sinopse ainda n\u00e3o localizada para esta edi\u00e7\u00e3o.',source)
  self.assertNotIn('n\u00c3\u00a3o',source)
  header=(ROOT/'native/station_game_infos.h').read_text('utf8')
  self.assertIn('Sinopse ainda n\u00e3o dispon\u00edvel nesta edi\u00e7\u00e3o.',header)
 def test_asset_xml_metadata_only(self):
  files=list((ROOT/'assets/station-metadata/xml').glob('*.xml'));self.assertEqual(len(files),167)
  forbidden=('http://','https://','miami.sambox','drawers.json','Bearer ','?e=','?s=')
  for file in files:
   text=file.read_text('utf8');root=ET.fromstring(text)
   self.assertEqual(root.attrib.get('metadataOnly'),'true')
   for game in root.findall('game'):
    self.assertTrue(all(c.tag in ('name','desc','genre','developer','publisher','players','releasedate','rating') for c in game))
   self.assertFalse(any(x in text for x in forbidden),file.name)
 def test_legacy_data_preserved(self):
  original=Path(r'E:\ESTUDO APK\work\station-mega-explus-20261003\native\game_infos.h')
  self.assertEqual(original.read_bytes(),(ROOT/'native/game_infos.h').read_bytes())
 def test_shader_equations_preserved(self):
  original=Path(r'G:\TURBORAMA\RetroBat\emulationstation\.emulationstation\themes\TURBORAMAx\_theme_inc\premium-magazine-led.glsl').read_text('utf-8-sig')
  mobile=(ROOT/'native/premium-magazine-led-android.glsl').read_text('utf8')
  mobile=mobile.replace('    if(region(p)<=0.0) return 0.0; // Equivalent zero mask; saves texture reads.\n','')
  self.assertIn('precision highp float;\nprecision highp int;',mobile)
  mobile=mobile.replace('precision highp int;\n','')
  self.assertEqual(original,mobile)
 def test_only_hero_scope_and_clock(self):
  source=(ROOT/'native/native_formation.h').read_text('utf8')
  self.assertIn('mappingHero=!systemsMode&&pos==at<int>(p,0xf0)',source)
  self.assertIn('if(mappingHero&&drawMagazineCover',source)
  light=(ROOT/'native/native_magazine.h').read_text('utf8')
  self.assertIn('((U)now*60u)/1000u',light)
  self.assertIn('g.UseProgram((unsigned)original)',light)
 def test_synopsis_clock_survives_cover_batches(self):
  source=(ROOT/'native/native_info.h').read_text('utf8')
  self.assertIn('if(nextInfo!=gameInfo){pageStarted=tick;oldPage=-1;}',source)
  self.assertNotIn('else{pageStarted=tick;oldPage=-1;gameInfo=nullptr;}',source)
 def test_power_policy_unchanged(self):
  original=Path(r'E:\ESTUDO APK\work\station-mega-explus-20261003\native\native_menu_power.h')
  self.assertEqual(original.read_bytes(),(ROOT/'native/native_menu_power.h').read_bytes())
 def test_console_alpha_and_memory(self):
  from PIL import Image
  for key in ['snes','megadrive']:
   image=Image.open(ROOT/f'assets/turbo-console/{key}.png')
   self.assertEqual(image.mode,'RGBA');self.assertLessEqual(max(image.size),512)
   self.assertLess(image.getextrema()[3][0],255)
  source=(ROOT/'native/native_console.h').read_text('utf8')
  self.assertIn('if(!texture.id)',source);self.assertIn('if(texture.context!=context)',source)
  self.assertIn('s.BindTexture(0x0de1,(unsigned)originalTexture)',source)
if __name__=='__main__':unittest.main()
