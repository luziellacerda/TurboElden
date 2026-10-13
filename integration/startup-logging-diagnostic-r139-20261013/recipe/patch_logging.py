"""Insert startup logging into exact R139 methods; prove the inverse byte for byte."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import shutil

PACKAGE = "org/emulationstation/frontend/netplay/"
PINS = {
    "StationRetroActivity": "653ffc33cd875efd04b08321ac21435aeac55be4c30318a1878dc33ad9920d17",
    "StationRetroLaunch": "6c855d7a920b39c757356eaded726480e27247368047da8d59a6136d35ae4094",
}
HEADS = {
    "StationRetroActivity": ".method public onCreate(Landroid/os/Bundle;)V",
    "StationRetroLaunch": ".method static prepare(Landroid/content/Context;Lorg/emulationstation/frontend/netplay/StationOnlineGame;Lorg/json/JSONObject;Lorg/json/JSONObject;Lorg/emulationstation/frontend/station/StationApi$Cancellation;)Ljava/lang/String;",
}
HELPER = "L" + PACKAGE + "StationStartupLogging;"


def need(ok, message):
    if not ok:
        raise ValueError(message)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def normalized(raw):
    text = raw.decode("utf-8")
    eol = "\r\n" if "\r\n" in text else "\n"
    need("\r" not in text.replace("\r\n", ""), "Mixed or invalid line endings")
    return text.replace("\r\n", "\n"), eol


def additions(name):
    if name == "StationRetroActivity":
        anchor = ('    :try_start_1\n'
                  '    invoke-static {v13}, Ljava/lang/System;->loadLibrary(Ljava/lang/String;)V\n')
        inserted = '\n    invoke-static/range {p0 .. p0}, ' + HELPER + '->begin(Landroid/content/Context;)V\n'
        return [(anchor, inserted)]
    anchor = ('    .line 30\n'
              '    new-instance v2, Ljava/lang/StringBuilder;\n\n'
              '    invoke-direct {v2}, Ljava/lang/StringBuilder;-><init>()V\n')
    inserted = "\n"
    for key, value in (("log_verbosity", "true"), ("frontend_log_level", "3"), ("libretro_log_level", "3")):
        inserted += ('    const-string v3, "' + key + '"\n\n'
                     '    const-string v4, "' + value + '"\n\n'
                     '    invoke-static {v2, v3, v4}, L' + PACKAGE + 'StationRetroLaunch;->set(Ljava/lang/StringBuilder;Ljava/lang/String;Ljava/lang/String;)V\n\n')
    # v3 is assigned by both arms of the following mask branch; v4 is assigned
    # by the following platform iget before any read. No register count changes.
    write = '    invoke-static {v5, v2}, L' + PACKAGE + 'StationRetroLaunch;->write(Ljava/io/File;Ljava/lang/String;)V\n'
    receipt = '\n    invoke-static {}, ' + HELPER + '->cfgWritten()V\n'
    return [(anchor, inserted), (write, receipt)]


def method_span(text, name):
    head = HEADS[name]
    need(text.count(head + "\n") == 1, "Exact original method required: " + name)
    start = text.index(head + "\n")
    end = text.index(".end method", start) + len(".end method")
    return start, end


def patch(name, raw):
    need(digest(raw) == PINS[name], "Exact R139 class projection required: " + name)
    text, eol = normalized(raw)
    need(HELPER not in text, "Diagnostics already present")
    start, end = method_span(text, name)
    method = text[start:end]
    for anchor, inserted in additions(name):
        need(method.count(anchor) == 1, "Unique insertion anchor required: " + name)
        method = method.replace(anchor, anchor + inserted)
    output = (text[:start] + method + text[end:]).replace("\n", eol).encode("utf-8")
    need(inverse(name, output) == raw, "Source inverse differs")
    return output


def inverse(name, raw):
    text, eol = normalized(raw)
    start, end = method_span(text, name)
    method = text[start:end]
    for anchor, inserted in reversed(additions(name)):
        need(method.count(anchor + inserted) == 1, "Exact diagnostic insertion required: " + name)
        method = method.replace(anchor + inserted, anchor)
    original = (text[:start] + method + text[end:]).replace("\n", eol).encode("utf-8")
    need(digest(original) == PINS[name], "Original class not recovered after inverse: " + name)
    return original


def verify(donor, working):
    before = {p.relative_to(donor).as_posix(): p.read_bytes() for p in donor.rglob("*.smali")}
    after = {p.relative_to(working).as_posix(): p.read_bytes() for p in working.rglob("*.smali")}
    helper = PACKAGE + "StationStartupLogging.smali"
    need(len(before) == 608 and set(after) == set(before) | {helper}, "Only one new helper class allowed")
    changed = {PACKAGE + n + ".smali" for n in PINS}
    need({n for n in before if before[n] != after[n]} == changed, "Only Activity and Launch may change")
    for name in PINS:
        key = PACKAGE + name + ".smali"
        need(inverse(name, after[key]) == before[key], "Existing method/class projection changed")
    return dict(originalClassCount=608, finalClassCount=609, unchangedClasses=606,
                modifiedMethods={name: HEADS[name] for name in PINS},
                insertedClass="L" + PACKAGE + "StationStartupLogging;", inversePassed=True)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--donor", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--verify", action="store_true")
    a = p.parse_args()
    if a.verify:
        print(json.dumps(verify(a.donor, a.out)))
    else:
        need(not a.out.exists(), "New isolated destination required")
        shutil.copytree(a.donor, a.out)
        for name in PINS:
            path = a.out / (PACKAGE + name + ".smali")
            path.write_bytes(patch(name, path.read_bytes()))
        print(json.dumps({"patchedMethods": HEADS, "compiled": False}))
