import shutil, sys

p = '/root/archive_daily_v3.py'
bak = p + '.bak-1110'

s = open(p).read()

i = s.find('r = requests.post(f"{SUPABASE_URL}/rest/v1/memory_events", json=rows, headers={')
if i < 0:
    print('!! 没找到目标行，未改动')
    sys.exit(1)

end_marker = 'r.raise_for_status()\n    return len(rows)'
j = s.find(end_marker, i)
if j < 0:
    print('!! 没找到结尾行，未改动')
    sys.exit(1)

shutil.copy(p, bak)

new = '''ok, failed = 0, []
    for row in rows:
        rr = requests.post(f"{SUPABASE_URL}/rest/v1/memory_events", json=row, headers={
            "apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json", "Prefer": "return=minimal",
        })
        if rr.status_code in (200, 201):
            ok += 1
        else:
            failed.append((row.get("title"), rr.status_code, rr.text[:300]))
    for _t, _sc, _tx in failed:
        print("  X single-fail [%s] %s :: %s" % (_sc, _t, _tx))
    if not ok:
        raise RuntimeError("all %d rows failed" % len(rows))
    if failed:
        print("!! %d rows failed, %d rows saved" % (len(failed), ok))
    return ok'''

s2 = s[:i] + new + s[j + len(end_marker):]
open(p, 'w').write(s2)
print('OK patched. backup =', bak)
print('---- 改后这一段 ----')
k = s2.find('ok, failed = 0, []')
print(s2[k - 40:k + 780])
