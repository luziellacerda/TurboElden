"""Strict whole-class guard for the actual postassembly DEX10 decode.

Caller must bind the decoded directory to its actual compiled DEX checksum and
prove the other 4,990 classes independently. This guard admits only the fixed
canonical four-method projection and must recover the complete donor class.
"""
from pathlib import Path
import argparse
import json
import re
import audit_ownership as a
import prepare_ownership as p

ROOT = Path(__file__).resolve().parent
CANONICAL_SHA = 'ed45e5272b1d554d26e702b6d168b1e49ce1f14144b25451858e8cc78c542690'


def verify(raw):
    assert a.sha(raw) == CANONICAL_SHA, 'Exact canonical ownership class required'
    before = (ROOT / 'evidence/baseline-NetplaySession.smali.txt').read_bytes()
    assert a.sha(before) == a.DONOR_SHA
    proposed = (ROOT / 'evidence/canonical-proposed-NetplaySession.smali.txt').read_bytes()
    assert a.sha(proposed) == CANONICAL_SHA and raw == proposed
    original, candidate = before.decode('utf-8'), raw.decode('utf-8')
    old_fields = re.findall(r'^\.field[^\r\n]+', original, re.M)
    new_fields = re.findall(r'^\.field[^\r\n]+', candidate, re.M)
    assert old_fields == new_fields and len(old_fields) == 40
    old_methods, new_methods = p.methods(original), p.methods(candidate)
    assert old_methods.keys() == new_methods.keys() and len(old_methods) == 63
    assert {signature for signature in old_methods if old_methods[signature] != new_methods[signature]} == set(p.SIGNATURES)
    inverse = candidate
    for signature in reversed(p.SIGNATURES):
        body = a.method(inverse, signature)
        assert inverse.count(body) == 1
        inverse = inverse.replace(body, a.method(original, signature), 1)
    assert inverse.encode('utf-8') == before, 'Whole class metadata/method/field inverse failed'
    return {'canonicalClassSha256': CANONICAL_SHA, 'inverseClassSha256': a.DONOR_SHA,
            'inverseWholeClassPassed': True, 'unchangedFields': 40, 'originalMethodCount': 63,
            'finalMethodCount': 63, 'changedMethods': p.SIGNATURES, 'unchangedMethods': 59,
            'newMethods': [], 'newFields': [], 'newClasses': []}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--class', dest='candidate', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(verify(args.candidate.read_bytes()), ensure_ascii=False))
