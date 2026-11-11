#!/usr/bin/env python3
"""Salin jadwal aplikasi checklist (gist) ke Kalender & Reminders "Skripsi" di Mac (iCloud → ikut ke iPhone).

Yang disalin:
  - S.jadwal (Kalender aplikasi)                     → acara sepanjang hari + pengingat
  - tenggat poin masukan bimbingan (poin.due)        → acara "Masukan: …" + pengingat 20.00 sehari sebelumnya
  - bimbingan berikutnya (next, nextJam, nextTempat) → acara (berjam bila ada jam) + pengingat

Acara/pengingat yang dibuat skrip ini diberi penanda "ckid:<kunci>" di catatan, jadi menjalankan ulang
hanya mengubah yang berubah. Acara lama tanpa penanda yang judul & tanggalnya sama akan diberi penanda
(tidak dibuat dobel). Acara buatan sendiri tanpa penanda tidak disentuh.

Pakai:  GH_TOKEN=$(gh auth token) python3 tools/kalender_mac.py [--dry-run]
"""
import datetime as dt, json, os, subprocess, sys

CAL = "Skripsi"
DATA_FILE = "checklist-skripsi.json"
EMO = {"terbang": "✈️", "tulis": "📝", "tenggat": "⚠️", "bimbingan": "👩‍🏫", "sidang": "🎓", "lain": "📌"}
JAM = {"terbang": 5, "tenggat": 20}           # jam pengingat; lainnya 07.00
DRY = "--dry-run" in sys.argv


def gh(path):
    out = subprocess.run(["curl", "-sf", "-H", "Authorization: Bearer " + os.environ["GH_TOKEN"],
                          "-H", "Accept: application/vnd.github+json", "https://api.github.com" + path],
                         capture_output=True, check=True).stdout
    return json.loads(out)


def load_data():
    gists = [g for g in gh("/gists?per_page=100") if DATA_FILE in g["files"]]
    if not gists:
        sys.exit("tidak ada gist data aplikasi di akun ini")
    gid = max(gists, key=lambda g: g["updated_at"])["id"]          # sama dengan pilihan otomatis di aplikasi
    g = gh("/gists/" + gid)
    f = g["files"][DATA_FILE]
    txt = f["content"] if not f["truncated"] else subprocess.run(["curl", "-sf", f["raw_url"]], capture_output=True, check=True).stdout.decode()
    return gid, json.loads(txt)["data"]


def poin_check_id(d, b, p):
    t = p.get("target")
    if t and any(c["id"] == t["cid"] for c in d.get("custom", {}).get(t["gid"], [])):
        return f'{t["gid"]}:c:{t["cid"]}'
    return f'bim:{b["id"]}:{p["id"]}'


def desired(d):
    """Daftar acara yang seharusnya ada: kunci, judul, mulai, selesai, sepanjang hari, lokasi, pengingat, selesai?"""
    out = []
    day = lambda s: dt.datetime.fromisoformat(s)
    for j in d.get("jadwal", []):
        if j.get("deleted"):
            continue
        s = day(j["date"])
        rem = s.replace(hour=JAM.get(j["type"], 7)) - (dt.timedelta(days=1) if j["type"] == "tenggat" else dt.timedelta())
        out.append(dict(key="j:" + j["id"], title=f'{EMO.get(j["type"], "📌")} {j["title"]}', start=s, end=s + dt.timedelta(days=1),
                        allday=True, loc="", rem=rem, done=bool(j.get("done"))))
    checks = d.get("checks", {})
    for b in d.get("bimbingan", []):
        if b.get("deleted"):
            continue
        for p in b.get("poin", []):
            if p.get("due"):
                s = day(p["due"])
                out.append(dict(key="p:" + p["id"], title="📝 Masukan: " + p["text"], start=s, end=s + dt.timedelta(days=1), allday=True,
                                loc="", rem=s.replace(hour=20) - dt.timedelta(days=1), done=bool(checks.get(poin_check_id(d, b, p)))))
        if b.get("next"):
            s = day(b["next"])
            title = f'👩‍🏫 Bimbingan {b.get("dosen", "")}' + (f' · {b["nextTempat"]}' if b.get("nextTempat") else "")
            if b.get("nextJam"):
                hh, mm = map(int, b["nextJam"].split(":"))
                s = s.replace(hour=hh, minute=mm)
                out.append(dict(key="b:" + b["id"], title=title, start=s, end=s + dt.timedelta(hours=1), allday=False,
                                loc=b.get("nextTempat", ""), rem=s - dt.timedelta(hours=1), done=False))
            else:
                out.append(dict(key="b:" + b["id"], title=title, start=s, end=s + dt.timedelta(days=1), allday=True,
                                loc=b.get("nextTempat", ""), rem=s.replace(hour=7), done=False))
    return out


def osa(script):
    r = subprocess.run(["osascript", "-"], input=script.encode(), capture_output=True)
    if r.returncode:
        sys.exit("AppleScript gagal: " + r.stderr.decode())
    return r.stdout.decode()


def q(s):
    return '"' + str(s).replace("\\", "\\\\").replace('"', '\\"') + '"'


def asdate(t):
    return f"(my mkdate({t.year}, {t.month}, {t.day}, {t.hour}, {t.minute}))"


MKDATE = """on mkdate(y, m, d, hh, mm)
  set t to current date
  set day of t to 1
  set year of t to y
  set month of t to m
  set day of t to d
  set time of t to hh * 3600 + mm * 60
  return t
end mkdate
on iso(t)
  return ((year of t) as string) & "-" & text -2 thru -1 of ("0" & ((month of t) as integer)) & "-" & text -2 thru -1 of ("0" & (day of t)) & "T" & text -2 thru -1 of ("0" & (hours of t)) & ":" & text -2 thru -1 of ("0" & (minutes of t))
end iso
"""

READ = MKDATE + f"""
set out to ""
tell application "Calendar"
  repeat with e in (every event of calendar {q(CAL)})
    set ds to description of e
    if ds is missing value then set ds to ""
    set out to out & "EV" & tab & (uid of e) & tab & (summary of e) & tab & my iso(start date of e) & tab & ds & linefeed
  end repeat
end tell
tell application "Reminders"
  repeat with r in (every reminder of list {q(CAL)})
    set bd to body of r
    if bd is missing value then set bd to ""
    set dd to ""
    try
      set dd to my iso(due date of r)
    end try
    set out to out & "RM" & tab & (id of r) & tab & (name of r) & tab & dd & tab & bd & tab & (completed of r) & linefeed
  end repeat
end tell
return out
"""


def main():
    gid, d = load_data()
    want = desired(d)
    ev, rm = [], []
    for line in osa(READ).splitlines():
        p = line.split("\t")
        if p[0] == "EV" and len(p) >= 5:
            ev.append(dict(uid=p[1], title=p[2], start=p[3], desc=p[4]))
        elif p[0] == "RM" and len(p) >= 6:
            rm.append(dict(id=p[1], title=p[2], due=p[3], body=p[4], done=p[5] == "true"))
    tag = lambda k: "ckid:" + k
    iso = lambda t: t.strftime("%Y-%m-%dT%H:%M")
    acts, log, used = [], [], set()   # used: acara/pengingat lama yang sudah dipasangkan (judul sama bisa >1)
    keys = {w["key"] for w in want}
    for w in want:
        T = tag(w["key"])
        # --- acara kalender ---
        mine = [e for e in ev if T in e["desc"]]
        legacy = [e for e in ev if "ckid:" not in e["desc"] and e["uid"] not in used and e["title"] == w["title"] and e["start"] == iso(w["start"])]
        if len(mine) == 1 and mine[0]["title"] == w["title"] and mine[0]["start"] == iso(w["start"]):
            pass
        elif not mine and legacy:
            used.add(legacy[0]["uid"])
            acts.append(f'tell application "Calendar" to set description of (first event of calendar {q(CAL)} whose uid is {q(legacy[0]["uid"])}) to {q(T)}')
            log.append("tandai  " + w["title"])
        else:
            for e in mine:
                acts.append(f'tell application "Calendar" to delete (every event of calendar {q(CAL)} whose uid is {q(e["uid"])})')
            props = f'summary:{q(w["title"])}, start date:{asdate(w["start"])}, end date:{asdate(w["end"])}, allday event:{str(w["allday"]).lower()}, description:{q(T)}'
            if w["loc"]:
                props += f', location:{q(w["loc"])}'
            acts.append(f'tell application "Calendar" to tell calendar {q(CAL)} to make new event with properties {{{props}}}')
            log.append(("ubah   " if mine else "tambah ") + w["title"])
        # --- pengingat ---
        rmine = [r for r in rm if T in r["body"]]
        rleg = sorted([r for r in rm if "ckid:" not in r["body"] and r["id"] not in used and r["title"] == w["title"]],
                      key=lambda r: r["due"] != iso(w["rem"]))   # utamakan yang tanggalnya sama
        if len(rmine) == 1 and rmine[0]["title"] == w["title"] and rmine[0]["due"] == iso(w["rem"]):
            if w["done"] and not rmine[0]["done"]:
                acts.append(f'tell application "Reminders" to set completed of (first reminder of list {q(CAL)} whose id is {q(rmine[0]["id"])}) to true')
                log.append("selesai " + w["title"])
        elif not rmine and rleg:
            used.add(rleg[0]["id"])
            acts.append(f'tell application "Reminders" to set body of (first reminder of list {q(CAL)} whose id is {q(rleg[0]["id"])}) to {q(T)}')
            if rleg[0]["due"] != iso(w["rem"]):
                acts.append(f'tell application "Reminders" to set due date of (first reminder of list {q(CAL)} whose id is {q(rleg[0]["id"])}) to {asdate(w["rem"])}')
        else:
            for r in rmine:
                acts.append(f'tell application "Reminders" to delete (every reminder of list {q(CAL)} whose id is {q(r["id"])})')
            acts.append(f'tell application "Reminders" to tell list {q(CAL)} to make new reminder with properties '
                        f'{{name:{q(w["title"])}, due date:{asdate(w["rem"])}, remind me date:{asdate(w["rem"])}, body:{q(T)}, completed:{str(w["done"]).lower()}}}')
    # buang yang dulu dibuat skrip ini tapi sudah tidak ada di aplikasi
    for e in ev:
        if "ckid:" in e["desc"] and e["desc"].split("ckid:")[1].split()[0] not in keys:
            acts.append(f'tell application "Calendar" to delete (every event of calendar {q(CAL)} whose uid is {q(e["uid"])})')
            log.append("hapus  " + e["title"])
    for r in rm:
        if "ckid:" in r["body"] and r["body"].split("ckid:")[1].split()[0] not in keys:
            acts.append(f'tell application "Reminders" to delete (every reminder of list {q(CAL)} whose id is {q(r["id"])})')
    print(f"gist {gid}: {len(want)} item, {len(acts)} perubahan")
    print("\n".join(log) or "(tidak ada yang berubah di kalender)")
    if acts and not DRY:
        osa(MKDATE + "\n".join(acts) + '\ntell application "Calendar" to reload calendars\nreturn "ok"')
        print("selesai")


if __name__ == "__main__":
    main()
