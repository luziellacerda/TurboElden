"""Generate presentation metadata by exact published Station identity, offline.

No network, title matching, ROM reads, or changes to existing sources. Inputs are
pinned to the audited catalog revision. To relocate inputs, use --help. The
metadata-only XMLs preserve the original source SHA and one-based ordinal.
"""
from pathlib import Path, PurePosixPath
import argparse
import collections
import csv
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
import hashlib
import io
import json
import posixpath
import re
import subprocess
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent
SERVER_COMMIT = '100e4bbd92aa4c85cda10a633e6463fbb24ae8ab'
SERVER_PATH = 'docs/station-android/biblioteca-neogeocd-20261005/catalogo-completo.tsv'
CATALOG_SHA = '3dae0cfa3877fba31b9a347b58795fe0df95333aea628b9ea8be597b7ccfed6e'
IDENTITIES_SHA = 'e94db5ef1d55e3f8b92f03282563a401c79ec4ea424304c09b90078e9ced6c7f'
FROZEN_XML = {
    '7e3a7dcedb814114d465b6e9c3f0b0e2119b7de8656def37857afa4969e817c9':
        '574648480e6db75d7cbf06ffd02f5c1448a2adc23b6895586de358a99b7fdc4c',
    'f459dfd5b5960e13bf1d989b6d107e29759d6d8da15e9d0d1efbc3525b583ee1':
        '73b1a11347e530e3096d1100e7a370e8e7441756c71f083a7e6ba0420a5211ce',
}
PATH_XML = {
    'n64': 'ed9e30df64ab33e0bf13105bf44b1c50098b6e12c9f3675aeaa2b4c911bf7ea1',
    'neogeo': '555672bfb311bcef62a5f5409e81a199b37e32eb082f2b04c5a1619bbcbe5463',
}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def checked_bytes(path, expected, role):
    raw = Path(path).read_bytes()
    require(sha(raw) == expected, role + ' differs from the audited source')
    return raw


def xml_root(raw):
    require(b'<!DOCTYPE' not in raw.upper() and b'<!ENTITY' not in raw.upper(),
            'XML entities are not supported')
    return ET.fromstring(raw)


def players_text(value):
    value = value.strip()
    require(len(value) <= 40 and all(ord(c) >= 32 and ord(c) != 127 for c in value),
            'Invalid player metadata')
    # Count/range syntax found in these inputs; never infer counts from prose.
    require(not value or re.fullmatch(r'[1-9][0-9]*(?:-[1-9][0-9]*|\+)?', value),
            'Unsupported player metadata')
    return value


def rating_thousandths(value):
    value = value.strip()
    if not value:
        return -1
    try:
        score = Decimal(value)
    except InvalidOperation as error:
        raise ValueError('Invalid catalog rating') from error
    require(score.is_finite() and Decimal(0) <= score <= Decimal(1),
            'Catalog rating must be within zero and one')
    return int((score * 1000).quantize(Decimal(1), rounding=ROUND_HALF_UP))


def stable_station_id(platform, xml_path):
    normalized = xml_path.replace('\\', '/')
    require(normalized and not normalized.startswith('/') and ':' not in normalized,
            'XML path must be relative')
    relative = posixpath.normpath(normalized)
    require(relative != '.' and '..' not in PurePosixPath(relative).parts,
            'XML path leaves its platform')
    actual_platform = platform + 'br' if 'pt-br' in PurePosixPath(relative).parts else platform
    return 'station_' + sha((actual_platform + ':' + relative).encode('utf-8'))[:32]


def read_catalog(args):
    if args.catalog_tsv:
        raw = Path(args.catalog_tsv).read_bytes()
    else:
        repo = Path(args.server_repo)
        raw = subprocess.check_output([
            'git', '-c', 'safe.directory=' + repo.as_posix(), '-C', str(repo),
            'show', SERVER_COMMIT + ':' + SERVER_PATH,
        ])
    require(sha(raw) == CATALOG_SHA, 'Catalog differs from the audited revision')
    rows = [r for r in csv.DictReader(io.StringIO(raw.decode('utf-8-sig')), delimiter='\t')
            if r['catalogVisible'] == 'yes']
    require(len(rows) == 2212, 'Unexpected catalog size')
    by_id = {}
    for row in rows:
        identity = row['itemId']
        require(re.fullmatch(r'[A-Za-z0-9_-]{8,64}', identity), 'Invalid catalog identity')
        require(identity not in by_id, 'Duplicate catalog identity')
        by_id[identity] = row
    return by_id


def build_records(args):
    catalog = read_catalog(args)
    base = Path(args.metadata_dir)
    identities = json.loads(checked_bytes(base / 'station-synopses.json', IDENTITIES_SHA,
                                          'Frozen identity map'))
    require(len(identities) == 1816, 'Unexpected frozen identity map size')
    originals = {}
    matches = {}
    for source_sha, asset_sha in FROZEN_XML.items():
        root = xml_root(checked_bytes(base / 'xml' / (source_sha + '.xml'), asset_sha,
                                      'Frozen metadata XML'))
        require(root.get('sourceSha256') == source_sha, 'Wrong original XML identity')
        games = {}
        for game in root.findall('game'):
            ordinal = int(game.attrib['sourceOrdinal'])
            require(ordinal > 0 and ordinal not in games, 'Duplicate source ordinal')
            games[ordinal] = game
        originals[source_sha] = games
    for record in identities:
        identity = record['itemId']
        row = catalog.get(identity)
        require(row is not None and row['platform'] == record['platform']
                and row['name'] == record['name'], 'Frozen identity no longer matches catalog')
        # Supplemental description origins are deliberately not metadata origins.
        source_sha, ordinal = record['sourceSha256'], int(record['sourceOrdinal'])
        game = originals[source_sha][ordinal]
        require(game.findtext('name', '') == row['name'], 'Wrong original XML ordinal')
        require(identity not in matches, 'Duplicate metadata identity')
        matches[identity] = (game, {
            'method': 'published-item-id-and-original-xml-ordinal',
            'sourceSha256': source_sha, 'sourceOrdinal': ordinal,
        })
    for platform, source_sha in PATH_XML.items():
        root = xml_root(checked_bytes(getattr(args, platform + '_xml'), source_sha,
                                      platform + ' original XML'))
        observed = set()
        for ordinal, game in enumerate(root.findall('game'), 1):
            identity = stable_station_id(platform, game.findtext('path', ''))
            require(identity not in observed, 'Duplicate exact XML path identity')
            observed.add(identity)
            row = catalog.get(identity)
            if row is None:
                continue
            require(row['platform'] == platform, 'XML identity platform mismatch')
            require(identity not in matches, 'Conflicting metadata identity')
            matches[identity] = (game, {
                'method': 'published-item-id-and-server-sha256-path-rule',
                'sourceSha256': source_sha, 'sourceOrdinal': ordinal,
                'displayNameMatches': game.findtext('name', '') == row['name'],
            })
    records = []
    for identity, row in sorted(catalog.items()):
        match = matches.get(identity)
        game, provenance = match if match else (None, None)
        server_players = players_text(row['players'])
        xml_players = players_text(game.findtext('players', '')) if game is not None else ''
        players = server_players or xml_players
        rating = rating_thousandths(game.findtext('rating', '')) if game is not None else -1
        records.append({
            'itemId': identity, 'platform': row['platform'], 'players': players,
            'playersSource': 'published-catalog' if server_players else
                             'exact-xml' if xml_players else 'missing',
            'ratingThousandths': rating, 'xmlIdentity': provenance,
        })
    return records


def header_bytes(records):
    lines = [
        '#pragma once',
        '// Generated by generate_game_details.py; exact published item IDs only.',
        '// players: empty means unknown. ratingThousandths: -1 unknown; 0 is explicit zero.',
        '// XML rating is a catalog score in [0,1], not an average of user reviews.',
        'struct StationGameDetails { const char* id; const char* players; int ratingThousandths; };',
        'static const StationGameDetails stationGameDetails[] = {',
    ]
    for record in records:
        lines.append('{' + json.dumps(record['itemId']) + ',' +
                     json.dumps(record['players']) + ',' + str(record['ratingThousandths']) + '},')
    lines.extend([
        '};',
        'static constexpr int NSTATIONGAMEDETAILS = sizeof(stationGameDetails) / sizeof(stationGameDetails[0]);',
        'static const StationGameDetails* findStationGameDetails(const char* id) {',
        ' if (!id || !*id) return nullptr;',
        ' int first = 0, last = NSTATIONGAMEDETAILS;',
        ' while (first < last) {',
        '  int middle = first + (last - first) / 2;',
        '  if (strcmp(id, stationGameDetails[middle].id) > 0) first = middle + 1;',
        '  else last = middle;',
        ' }',
        ' return first < NSTATIONGAMEDETAILS && strcmp(id, stationGameDetails[first].id) == 0',
        '     ? &stationGameDetails[first] : nullptr;',
        '}',
        '',
    ])
    return '\n'.join(lines).encode('utf-8')


def make_report(records, header):
    counts = collections.Counter()
    platforms = collections.defaultdict(collections.Counter)
    for record in records:
        for target in (counts, platforms[record['platform']]):
            target['items'] += 1
            target['playersKnown'] += bool(record['players'])
            target['playersMissing'] += not record['players']
            target['playersFromServer'] += record['playersSource'] == 'published-catalog'
            target['playersFromExactXml'] += record['playersSource'] == 'exact-xml'
            target['xmlMatched'] += record['xmlIdentity'] is not None
            target['ratingKnown'] += record['ratingThousandths'] >= 0
            target['ratingMissing'] += record['ratingThousandths'] < 0
            target['ratingExplicitZero'] += record['ratingThousandths'] == 0
    return {
        'generator': 'generate_game_details.py', 'schema': 1,
        'catalogCommit': SERVER_COMMIT, 'catalogRepositoryPath': SERVER_PATH,
        'inputSha256': {'catalog': CATALOG_SHA, 'identityMap': IDENTITIES_SHA,
                        'frozenXmlAssets': FROZEN_XML, 'originalPathXml': PATH_XML},
        'headerSha256': sha(header), 'headerBytes': len(header),
        'counts': dict(counts), 'platforms': {k: dict(v) for k, v in sorted(platforms.items())},
        'playersPolicy': 'Published nonempty value, then XML of exact item identity, then unknown.',
        'ratingPolicy': 'Catalog XML score [0,1], multiplied by 1000 and rounded half up; -1 absent; zero preserved.',
        'ratingIsUserAverage': False,
        'identityPolicy': 'Exact published IDs only; original XML ordinal or reproduced server path hash; no title fallback.',
        'missingXml': {'n64': 1, 'neogeocd': 50},
    }


def arguments(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--catalog-tsv', type=Path, help='Optional exported TSV of the pinned catalog commit')
    parser.add_argument('--server-repo', type=Path,
                        default=Path(r'E:\ESTUDO APK\work\server-auth-handoff\Servidor-pix-implementar-faltas-20261002'))
    parser.add_argument('--metadata-dir', type=Path,
                        default=Path(r'E:\ESTUDO APK\work\station-visual-covers-20261003\assets\station-metadata'))
    parser.add_argument('--n64-xml', type=Path, default=Path(r'G:\TURBORAMA\RetroBat\roms\n64\gamelist.xml'))
    parser.add_argument('--neogeo-xml', type=Path, default=Path(r'G:\TURBORAMA\RetroBat\roms\neogeo\gamelist.xml'))
    parser.add_argument('--output', type=Path, default=ROOT / 'native' / 'station_game_details.h')
    parser.add_argument('--evidence-dir', type=Path, default=ROOT / 'evidence')
    return parser.parse_args(argv)


def main(argv=None):
    args = arguments(argv)
    records = build_records(args)
    header = header_bytes(records)
    report = make_report(records, header)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.evidence_dir.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(header)
    for name, value in [('game-details-records.json', records), ('game-details-build.json', report)]:
        (args.evidence_dir / name).write_text(json.dumps(value, ensure_ascii=True, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'headerSha256': report['headerSha256'], 'counts': report['counts']}, sort_keys=True))


if __name__ == '__main__':
    main()
