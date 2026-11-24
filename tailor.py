#!/usr/bin/env python3
"""Tailor a resume to a job description.

    python tailor.py profile.json job.txt --company Acme --role "SEO Lead" [--pdf]

Scores every bullet in your profile against the job description, keeps the most
relevant ones, picks the closest title, writes resume HTML (and a PDF if Playwright
is installed), and logs the application in tracker.csv.
Nothing is invented: it only selects and orders what is already in your profile.
"""
import argparse, csv, datetime, html, json, os, re, sys
from collections import Counter

STOP = set("""a an and are as at be by for from has have in is it its of on or our that the this to we will with you your
who what when where which while about across into more most other over such than their them they very work working
role team teams years year experience strong ability able including within using use help new also well
hiring hire looking lead own set track plus you'll we're join great love""".split())

def words(text):
    ws = (w.strip(".-") for w in re.findall(r"[a-z][a-z0-9+#.\-']*", text.lower()))
    return [w for w in ws if w not in STOP and len(w) > 2]

def keywords(jd, top=40):
    ws = words(jd)
    bigrams = [f"{a} {b}" for a, b in zip(ws, ws[1:])]
    c = Counter(ws) + Counter({k: v * 2 for k, v in Counter(bigrams).items() if v > 1})
    return dict(c.most_common(top))

def score(bullet, kw):
    text = (bullet["text"] + " " + " ".join(bullet.get("tags", []))).lower()
    return sum(w for k, w in kw.items() if k in text)

def pick_title(titles, jd):
    jd = jd.lower()
    best = max(((k, sum(jd.count(w) for w in k.split())) for k in titles if k != "default"), key=lambda x: x[1], default=("default", 0))
    return titles[best[0]] if best[1] else titles["default"]

def tailor(profile, jd, per_job=3):
    kw = keywords(jd)
    jobs = []
    for i, job in enumerate(profile["experience"]):
        ranked = sorted(job["bullets"], key=lambda b: -score(b, kw))
        keep = ranked[: per_job + (1 if i == 0 else 0)]
        jobs.append({**job, "bullets": keep, "score": sum(score(b, kw) for b in keep)})
    all_text = " ".join(b["text"] + " " + " ".join(b.get("tags", [])) for j in profile["experience"] for b in j["bullets"]).lower()
    all_text += " " + " ".join(profile.get("skills", {}).values()).lower() + " " + profile.get("summary", "").lower()
    gaps = [k for k in list(kw)[:20] if " " not in k and k not in all_text]
    return {"title": pick_title(profile["titles"], jd), "jobs": jobs, "keywords": list(kw)[:15], "gaps": gaps}

CSS = """body{font-family:Helvetica,Arial,sans-serif;color:#111;max-width:760px;margin:32px auto;font-size:12.5px;line-height:1.5}
h1{margin:0;font-size:26px}.t{color:#1f5eff;font-weight:600;margin:2px 0 4px}.c{color:#555}h2{font-size:12px;letter-spacing:.12em;border-bottom:1px solid #ddd;padding-bottom:4px;margin-top:20px}
.jh{display:flex;justify-content:space-between}.org{color:#555;margin-bottom:4px}ul{margin:4px 0 12px 18px;padding:0}.sk b{display:inline-block;width:90px}"""

def render(profile, t):
    e = html.escape
    jobs = "".join(f'<div class="jh"><b>{e(j["title"])}</b><span>{e(j["dates"])}</span></div><div class="org">{e(j["org"])}</div><ul>'
                   + "".join(f"<li>{e(b['text'])}</li>" for b in j["bullets"]) + "</ul>" for j in t["jobs"])
    skills = "".join(f"<div class='sk'><b>{e(k)}</b> {e(v)}</div>" for k, v in profile["skills"].items())
    return f"""<!doctype html><html><head><meta charset="utf-8"><title>{e(profile['name'])}</title><style>{CSS}</style></head><body>
<h1>{e(profile['name'])}</h1><div class="t">{e(t['title'])}</div><div class="c">{' · '.join(e(c) for c in profile['contact'])}</div>
<h2>PROFILE</h2><p>{e(profile['summary'])}</p><h2>EXPERIENCE</h2>{jobs}<h2>SKILLS</h2>{skills}
<h2>EDUCATION</h2><p>{e(profile.get('education',''))}</p></body></html>"""

def to_pdf(html_path, pdf_path):
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Playwright not installed: pip install playwright && playwright install chromium"); return False
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(); pg.goto("file://" + os.path.abspath(html_path))
        pg.pdf(path=pdf_path, format="A4", print_background=True); b.close()
    return True

def log(company, role, out, tracker="tracker.csv"):
    new = not os.path.exists(tracker)
    with open(tracker, "a", newline="") as f:
        w = csv.writer(f)
        if new: w.writerow(["date", "company", "role", "resume", "status", "notes"])
        w.writerow([datetime.date.today().isoformat(), company, role, out, "applied", ""])

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("profile"); ap.add_argument("job")
    ap.add_argument("--company", default="company"); ap.add_argument("--role", default="role")
    ap.add_argument("--pdf", action="store_true"); ap.add_argument("--no-log", action="store_true")
    a = ap.parse_args()
    profile = json.load(open(a.profile)); jd = open(a.job).read()
    t = tailor(profile, jd)
    slug = re.sub(r"[^a-z0-9]+", "-", f"{a.company}-{a.role}".lower()).strip("-")
    os.makedirs("out", exist_ok=True); out = f"out/{slug}.html"
    open(out, "w").write(render(profile, t))
    if a.pdf and to_pdf(out, out[:-5] + ".pdf"): out = out[:-5] + ".pdf"
    if not a.no_log: log(a.company, a.role, out)
    print(f"Title: {t['title']}\nTop job keywords: {', '.join(t['keywords'][:10])}")
    if t["gaps"]: print(f"In the job ad but nowhere in your profile: {', '.join(t['gaps'][:10])}\n  (Only add these if they're true.)")
    print(f"Wrote {out}")

if __name__ == "__main__":
    main()
