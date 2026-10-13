"""Candidate only: bind canonical private core options in exact original R139 Launch."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil

OWNER = "Lorg/emulationstation/frontend/netplay/StationRetroLaunch;"
RELATIVE = "org/emulationstation/frontend/netplay/StationRetroLaunch.smali"
ORIGINAL_CLASS_SHA = "6c855d7a920b39c757356eaded726480e27247368047da8d59a6136d35ae4094"
METHOD = ".method static prepare(Landroid/content/Context;Lorg/emulationstation/frontend/netplay/StationOnlineGame;Lorg/json/JSONObject;Lorg/json/JSONObject;Lorg/emulationstation/frontend/station/StationApi$Cancellation;)Ljava/lang/String;"
SETTINGS = (("global_core_options", "true"), ("game_specific_options", "false"))
ANCHOR = ('    .line 30\n'
          '    new-instance v2, Ljava/lang/StringBuilder;\n\n'
          '    invoke-direct {v2}, Ljava/lang/StringBuilder;-><init>()V\n')


def need(ok, text):
    if not ok:
        raise ValueError(text)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def normalize(raw):
    text = raw.decode("utf-8")
    eol = "\r\n" if "\r\n" in text else "\n"
    need("\r" not in text.replace("\r\n", ""), "Unexpected line endings")
    return text.replace("\r\n", "\n"), eol


def inserted():
    block = "\n"
    for key, value in SETTINGS:
        block += ('    const-string v3, "' + key + '"\n\n'
                  '    const-string v4, "' + value + '"\n\n'
                  '    invoke-static {v2, v3, v4}, ' + OWNER + '->set(Ljava/lang/StringBuilder;Ljava/lang/String;Ljava/lang/String;)V\n\n')
    # One final newline: preserve the donor separator after assembler formatting.
    return block.rstrip("\n") + "\n"


def span(text):
    need(text.count(METHOD + "\n") == 1, "Exact donor prepare() declaration required")
    start = text.index(METHOD + "\n")
    end = text.index(".end method", start) + len(".end method")
    return start, end


def inverse(raw):
    text, eol = normalize(raw)
    start, end = span(text)
    method = text[start:end]
    need(method.count(ANCHOR + inserted()) == 1, "Only the exact two binding calls are accepted")
    original = (text[:start] + method.replace(ANCHOR + inserted(), ANCHOR) + text[end:]).replace("\n", eol).encode("utf-8")
    need(digest(original) == ORIGINAL_CLASS_SHA, "All original fields/methods/instructions must be recovered exactly")
    return original


def patch(raw):
    need(digest(raw) == ORIGINAL_CLASS_SHA, "Exact original R139 Launch required; diagnostic donor is forbidden")
    text, eol = normalize(raw)
    need("StationStartupLogging" not in text and all('"' + key + '"' not in text for key, _ in SETTINGS), "Logging or binding overlay already present")
    start, end = span(text)
    method = text[start:end]
    need(method.count(ANCHOR) == 1, "Unique builder anchor required")
    # v3 is overwritten in both mask branches; v4 is overwritten by the platform
    # iget before its next read. Register count and all existing branches stay exact.
    following = method[method.index(ANCHOR) + len(ANCHOR):]
    need(following.startswith("\n    if-eqz v8, :cond_f\n"), "Dead-register insertion point moved")
    output = (text[:start] + method.replace(ANCHOR, ANCHOR + inserted()) + text[end:]).replace("\n", eol).encode("utf-8")
    need(inverse(output) == raw, "Exact source inverse proof failed")
    return output


def verify(donor, candidate):
    before = {p.relative_to(donor).as_posix(): p.read_bytes() for p in donor.rglob("*.smali")}
    after = {p.relative_to(candidate).as_posix(): p.read_bytes() for p in candidate.rglob("*.smali")}
    need(len(before) == len(after) == 608 and set(before) == set(after), "No added/removed/synthetic classes allowed")
    need({n for n in before if before[n] != after[n]} == {RELATIVE}, "Only Launch may change")
    need(inverse(after[RELATIVE]) == before[RELATIVE], "Existing class/method projection changed")
    return dict(originalClassCount=608, finalClassCount=608, unchangedClasses=607, modifiedClasses=[OWNER],
                modifiedMethods=[METHOD], addedClasses=[], removedClasses=[], inversePassed=True,
                changedCfgKeys=dict(SETTINGS))


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--donor-smali", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--verify", action="store_true")
    a = p.parse_args()
    if a.verify:
        print(json.dumps(verify(a.donor_smali, a.out)))
    else:
        need(not a.out.exists(), "New isolated candidate output required")
        shutil.copytree(a.donor_smali, a.out)
        target = a.out / RELATIVE
        target.write_bytes(patch(target.read_bytes()))
        print(json.dumps(verify(a.donor_smali, a.out)))
