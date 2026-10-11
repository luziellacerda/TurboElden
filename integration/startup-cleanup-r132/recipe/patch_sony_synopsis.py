"""Add two Sony platform fiches through a byte-pinned R131 include overlay.

Apply before other R132 C++ transformations. This recipe does not compile,
package, edit the frozen R124/R131 inputs, or mutate a signed game catalogue.
The same original Nintendo synopsis/collection consumers keep their bodies.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
SOURCE_SHA256 = {
    # Final R130 platform-loop source, whose binary is retained by R131.
    "native_carousel.cpp": "eb9a7e14bc50e7fac66fee14f9a98ef8b7f109860720c6564ab5da34dea7723b",
    "native_info.h": "f1e4a86b23bb04898a1bff3de5c13fa2627e6bf101db29f27e80b2c6eb950905",
    "native_folders.h": "71fa0864f7833c1e2cf29eac8c7a0bf97ff15115625fd55789819a69d23b1944",
    "collection_presentation.h": "fd6e3af8310481f72b7bd3c4618b56c84ead1f77e50f3b3057194716e902d82e",
    "system_infos.h": "96327b84b58981343a0eadfe1817504f9dcf561b550334dd400b28fc97021e68",
}
ROWS_SHA256 = "80f24440749e1b0eb47428ecb1d6a5cd09646b6b70a758bc8bf9e1ce78a78bc9"
SONY_KEYS = ("Playstation 3", "Playstation 4")
SOURCES = (
    "https://www.playstation.com/pt-br/playstation-history/2007-ps3-ps-vita/",
    "https://www.playstation.com/pt-br/playstation-history/2013-ps4-ps-vr/",
)


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def replace_once(raw: bytes, old: bytes, new: bytes) -> bytes:
    if raw.count(old) != 1 or new in raw:
        raise ValueError("Sony synopsis include anchor changed")
    result = raw.replace(old, new, 1)
    if result.count(new) != 1 or result.replace(new, old, 1) != raw:
        raise ValueError("Sony synopsis include inverse differs")
    return result


def patch(native_cpp: bytes, native_info: bytes, native_folders: bytes,
          collection_presentation: bytes, system_infos: bytes
          ) -> tuple[bytes, dict[str, bytes], dict]:
    """Return C++ bytes, five fresh overlay headers, and checked source receipt."""
    inputs = dict(zip(SOURCE_SHA256, (
        native_cpp, native_info, native_folders,
        collection_presentation, system_infos,
    )))
    for name, raw in inputs.items():
        if sha(raw) != SOURCE_SHA256[name]:
            raise ValueError("Exact retained R131 synopsis input required: " + name)

    rows = (ROOT / "native/sony_system_info_rows.h").read_bytes()
    if sha(rows) != ROWS_SHA256:
        raise ValueError("Sony editorial source changed; review and renew its pin")
    original_keys = re.findall(rb'^\{"([^"\r\n]+)",', system_infos, re.M)
    new_keys = re.findall(rb'^\{"([^"\r\n]+)",', rows, re.M)
    if len(original_keys) != 52 or len(set(original_keys)) != 52:
        raise ValueError("Original system synopsis table changed")
    if new_keys != [key.encode("utf-8") for key in SONY_KEYS]:
        raise ValueError("Exactly the two signed presentation keys are required")
    if any(key.lower() in {old.lower() for old in original_keys} for key in new_keys):
        raise ValueError("Sony platform synopsis already exists")
    # No URL/link, numeric player claim or executable behaviour belongs in a fiche.
    if b"https:" in rows or b"http:" in rows or rows.count(b"\\n\\n") != 2:
        raise ValueError("Historical two-paragraph Sony editorial scope changed")

    info_old = b'#include "native_info.h"'
    info_new = b'#include "r132_native_info.h"'
    folders_old = b'#include "native_folders.h"'
    folders_new = b'#include "r132_native_folders.h"'
    changed_cpp = replace_once(native_cpp, info_old, info_new)
    changed_cpp = replace_once(changed_cpp, folders_old, folders_new)
    inverse_cpp = changed_cpp.replace(folders_new, folders_old, 1).replace(info_new, info_old, 1)
    if inverse_cpp != native_cpp:
        raise ValueError("C++ outside two explicit includes changed")

    system_old = b'#include "system_infos.h"'
    system_new = b'#include "r132_system_infos.h"'
    collection_old = b'#include "collection_presentation.h"'
    collection_new = b'#include "r132_collection_presentation.h"'
    # Quoted nested includes otherwise resolve next to the frozen R124 consumer,
    # regardless of an earlier -I. Every edge in that include chain is explicit.
    info_header = replace_once(native_info, system_old, system_new)
    folders_header = replace_once(native_folders, collection_old, collection_new)
    collection_header = replace_once(collection_presentation, system_old, system_new)
    table_old = b'};\r\nstatic constexpr int NINFOS='
    table_new = b'#include "r132_sony_system_info_rows.h"\r\n};\r\nstatic constexpr int NINFOS='
    table_header = replace_once(system_infos, table_old, table_new)
    headers = {
        "r132_native_info.h": info_header,
        "r132_native_folders.h": folders_header,
        "r132_collection_presentation.h": collection_header,
        "r132_system_infos.h": table_header,
        "r132_sony_system_info_rows.h": rows,
    }
    inverse_headers = (
        info_header.replace(system_new, system_old, 1) == native_info,
        folders_header.replace(collection_new, collection_old, 1) == native_folders,
        collection_header.replace(system_new, system_old, 1) == collection_presentation,
        table_header.replace(table_new, table_old, 1) == system_infos,
    )
    if not all(inverse_headers):
        raise ValueError("Frozen synopsis or collection consumer changed")

    receipt = {
        "schemaVersion": 1,
        "revision": "R132",
        "retainedBaseExecutableSourceCommit": "8503c2e32d7487d3bb31397ba9533dc7e1bfe981",
        "retainedBaseCarouselSha256": "45e8131c0fc59f5c4627950c3aaed7b05dee1b519704d173698d5f56644fb806",
        "inputSha256": dict(SOURCE_SHA256),
        "nativeCppSha256": sha(changed_cpp),
        "overlayHeaderSha256": {name: sha(raw) for name, raw in headers.items()},
        "recipeSha256": sha(Path(__file__).read_bytes()),
        "sonyEditorialSha256": ROWS_SHA256,
        "sonyPresentationKeys": list(SONY_KEYS),
        "originalSystemFichesRetained": 52,
        "addedSystemFiches": 2,
        "resultingSystemFiches": 54,
        "nativeCppExactInverse": True,
        "allFourConsumerOrTableHeadersExactInverse": True,
        "includeOverlayExplicit": True,
        "sameNativeSynopsisPanelAndLayout": True,
        "allGamesCollectionUsesSameTable": True,
        "gameAndDemoSynopsesChanged": False,
        "signedCatalogChanged": False,
        "emulatorRoutesChanged": False,
        "videoLedCacheEconomyLifecycleMethodsChanged": False,
        "backgroundWorkAdded": False,
        "editorialPrimarySources": list(SOURCES),
        "historicalConsoleFactsOnly": True,
        "compiledByThisRecipe": False,
        "physicalValidation": False,
    }
    return changed_cpp, headers, receipt


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--native-cpp", type=Path, required=True)
    parser.add_argument("--r124-d0", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True,
                        help="New empty build directory; existing paths are refused")
    args = parser.parse_args()
    result, headers, receipt = patch(
        args.native_cpp.read_bytes(),
        (args.r124_d0 / "native_info.h").read_bytes(),
        (args.r124_d0 / "native_folders.h").read_bytes(),
        (args.r124_d0 / "collection_presentation.h").read_bytes(),
        (args.r124_d0 / "system_infos.h").read_bytes(),
    )
    args.out.mkdir(parents=True, exist_ok=False)
    (args.out / "native_carousel.cpp").write_bytes(result)
    for name, raw in headers.items():
        (args.out / name).write_bytes(raw)
    (args.out / "sony-synopsis-receipt.json").write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"result": "source-overlay-prepared", "addedSystemFiches": 2,
                      "nativeCppExactInverse": True}))


if __name__ == "__main__":
    main()
