"""Read-only source/provenance checks plus exact C++ lookup coverage."""
from pathlib import Path
import importlib.util
import json
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('game_details_generator', ROOT / 'generate_game_details.py')
generator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(generator)


class GameDetailsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.args = generator.arguments([])
        cls.records = generator.build_records(cls.args)
        cls.by_id = {x['itemId']: x for x in cls.records}
        cls.catalog = generator.read_catalog(cls.args)
        cls.header = generator.header_bytes(cls.records)
        cls.report = generator.make_report(cls.records, cls.header)

    def test_all_published_identities_and_platforms(self):
        self.assertEqual(2212, len(self.records))
        self.assertEqual(set(self.catalog), set(self.by_id))
        self.assertEqual(sorted(self.by_id), [x['itemId'] for x in self.records])
        for identity, record in self.by_id.items():
            self.assertEqual(self.catalog[identity]['platform'], record['platform'])

    def test_all_nonempty_server_players_are_preserved(self):
        for identity, row in self.catalog.items():
            if row['players'].strip():
                self.assertEqual(row['players'].strip(), self.by_id[identity]['players'])
                self.assertEqual('published-catalog', self.by_id[identity]['playersSource'])

    def test_fallback_uses_exact_xml_only(self):
        fallback = [x for x in self.records if x['playersSource'] == 'exact-xml']
        self.assertEqual(27, len(fallback))
        for row in fallback:
            self.assertFalse(self.catalog[row['itemId']]['players'])
            self.assertEqual('neogeo', row['platform'])
            self.assertEqual('published-item-id-and-server-sha256-path-rule', row['xmlIdentity']['method'])
            self.assertEqual(generator.PATH_XML['neogeo'], row['xmlIdentity']['sourceSha256'])

    def test_no_unknown_default_or_alias_guess(self):
        alternative = self.by_id['station_23c83c0af84a554b338c8eac2876cd8c']
        self.assertEqual('', alternative['players'])
        self.assertEqual(-1, alternative['ratingThousandths'])
        self.assertIsNone(alternative['xmlIdentity'])
        for row in self.records:
            if row['playersSource'] == 'missing':
                self.assertEqual('', row['players'])
            if row['xmlIdentity'] is None:
                self.assertEqual(-1, row['ratingThousandths'])

    def test_rating_zero_is_known_and_missing_is_distinct(self):
        self.assertEqual(-1, generator.rating_thousandths(''))
        self.assertEqual(0, generator.rating_thousandths('0'))
        self.assertEqual(0, generator.rating_thousandths('0.000'))
        self.assertEqual(850, generator.rating_thousandths('0.85'))
        self.assertEqual(1000, generator.rating_thousandths('1'))
        self.assertEqual(124, generator.rating_thousandths('0.1235'))
        self.assertEqual(9, sum(x['ratingThousandths'] == 0 for x in self.records))
        self.assertEqual(226, sum(x['ratingThousandths'] == -1 for x in self.records))
        for row in self.records:
            self.assertTrue(-1 <= row['ratingThousandths'] <= 1000)

    def test_invalid_ratings_rejected(self):
        for value in ('NaN', 'Infinity', '-0.01', '1.01', '4/5', 'unrated'):
            with self.subTest(value=value), self.assertRaises(ValueError):
                generator.rating_thousandths(value)

    def test_players_ranges_preserved_and_invalid_values_rejected(self):
        for value in ('', '1', '2', '1-2', '1-16', '8+'):
            self.assertEqual(value, generator.players_text(value))
        for value in ('0', 'players', '1\x00', '1\n2', 'https://example.test/2'):
            with self.subTest(value=value), self.assertRaises(ValueError):
                generator.players_text(value)

    def test_path_identity_matches_server_without_title_input(self):
        self.assertEqual('station_c16309c829ad81a41da0b4cb7236a4fb',
                         generator.stable_station_id('n64', './007 - The World is Not Enough.zip'))
        self.assertEqual('station_939cf663599c63ae2141d93a198e7163',
                         generator.stable_station_id('neogeo', './2020bb.zip'))
        self.assertEqual(generator.stable_station_id('neogeo', './folder/game.zip'),
                         generator.stable_station_id('neogeo', '.\\folder\\game.zip'))
        self.assertNotEqual(generator.stable_station_id('neogeo', './game.zip'),
                            generator.stable_station_id('n64', './game.zip'))
        self.assertNotEqual(generator.stable_station_id('neogeo', './game.zip'),
                            generator.stable_station_id('neogeo', './folder/game.zip'))

    def test_paths_outside_source_are_rejected(self):
        for value in ('', '../game.zip', '/game.zip', 'C:/game.zip', 'https://x/game.zip'):
            with self.subTest(value=value), self.assertRaises(ValueError):
                generator.stable_station_id('n64', value)

    def test_coverage(self):
        self.assertEqual({
            'items': 2212, 'playersKnown': 2148, 'playersMissing': 64,
            'playersFromServer': 2121, 'playersFromExactXml': 27, 'xmlMatched': 2161,
            'ratingKnown': 1986, 'ratingMissing': 226, 'ratingExplicitZero': 9,
        }, self.report['counts'])
        self.assertFalse(self.report['ratingIsUserAverage'])

    def test_generated_header_contains_each_exact_value(self):
        generated = []
        for line in self.header.decode('utf-8').splitlines():
            if line.startswith('{"'):
                generated.append(json.loads('[' + line[1:-2] + ']'))
        self.assertEqual([[x['itemId'], x['players'], x['ratingThousandths']]
                          for x in self.records], generated)
        self.assertEqual(self.header, (ROOT / 'native' / 'station_game_details.h').read_bytes())

    def test_evidence_is_reproducible_and_contains_no_source_urls(self):
        persisted = json.loads((ROOT / 'evidence' / 'game-details-records.json').read_text('utf-8'))
        report = json.loads((ROOT / 'evidence' / 'game-details-build.json').read_text('utf-8'))
        self.assertEqual(self.records, persisted)
        self.assertEqual(self.report, report)
        payload = json.dumps([persisted, report])
        self.assertNotIn('https://', payload)
        self.assertNotIn('http://', payload)
        self.assertNotIn('artifactFileName', payload)


if __name__ == '__main__':
    unittest.main(verbosity=2)
