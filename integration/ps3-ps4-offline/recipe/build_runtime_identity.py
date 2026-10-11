"""Renew existing online identities for the exact shared R128 offline additions.

Only the shared bundle binding changes: the PSX/N64/Dolphin cores, controller
profiles, options, frame loop, authority and protocol stay those of R127.
PS3 and PS4 are external offline routes and never get an online engine record.
"""
import argparse
import json
from pathlib import Path
import sys
from pipeline_common import load_psx, offline_sources, sha, SHARED_ADDITIONS

OFFLINE_PAYLOADS = {
    'AndroidManifest.xml': 'AndroidManifest.xml',
    'classes28.dex': 'classes28.dex',
    'classes39.dex': 'classes39.dex',
    'libturbo_carousel.so': 'lib/arm64-v8a/libturbo_carousel.so',
}

def verify_offline_compilation(receipt_path, payloads):
    receipt = json.loads(receipt_path.read_bytes())
    if receipt.get('passed') is not True or receipt.get('offlineOnly') is not True:
        raise ValueError('Successful offline-only compilation receipt required')
    compiled = {'offline/' + name: value for name, value in receipt['sourceSha256'].items()}
    if compiled != offline_sources():
        raise ValueError('Offline sources changed after compilation')
    if set(receipt['payloads']) != set(OFFLINE_PAYLOADS):
        raise ValueError('Exact four compiled offline payloads required')
    for name, target in OFFLINE_PAYLOADS.items():
        path = payloads[target]
        record = receipt['payloads'][name]
        if sha(path) != record['sha256'] or path.stat().st_size != record['bytes']:
            raise ValueError('Offline payload differs from its compilation: ' + name)
    return receipt

def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--offline-receipt', type=Path, required=True)
    own, remaining = parser.parse_known_args()
    payload_parser = argparse.ArgumentParser(add_help=False)
    payload_parser.add_argument('--payload', action='append', required=True)
    selected, _ = payload_parser.parse_known_args(remaining)
    module = load_psx('build_runtime_identity')
    module.PAYLOADS |= set(SHARED_ADDITIONS)
    payloads = module.mapping(selected.payload)
    verify_offline_compilation(own.offline_receipt, payloads)
    current = module.source_pins
    def sources(receipt):
        verify_offline_compilation(own.offline_receipt, payloads)
        java, transforms = current(receipt)
        return java, {**transforms, **offline_sources()}
    module.source_pins = sources
    original = sys.argv
    try:
        sys.argv = [original[0], *remaining]
        module.main()
    finally:
        sys.argv = original

if __name__ == '__main__':
    main()
