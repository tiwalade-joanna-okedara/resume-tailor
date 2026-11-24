# resume-tailor ✂️

**One profile, a tailored resume for every job.** Keep all your experience in one JSON file, with tags on each bullet. Paste a job description and it picks the closest title, keeps the most relevant bullets for each role, shows the job's top keywords, flags what the ad asks for that your profile doesn't mention, writes the resume (HTML, or PDF with Playwright), and logs the application in `tracker.csv`.

```text
$ python tailor.py profile.example.json job.example.txt --company Acme --role "SEO Lead"
Title: SEO and AI Search Lead
Top job keywords: seo, search, growth, content, ...
In the job ad but nowhere in your profile: technical, schema
  (Only add these if they're true.)
Wrote out/acme-seo-lead.html
```

## Why

During a job search I was tailoring my resume for every application, by hand. This is the generalised version of the script I ended up writing. It deliberately **never writes new claims**: it only chooses and orders what's already true in your profile, and tells you about gaps so you can decide.

## Use it

```bash
cp profile.example.json profile.json    # fill in your real experience and tags
python tailor.py profile.json job.txt --company Acme --role "Content Lead" --pdf
python test_tailor.py
```

No dependencies except Python 3.9+. PDF output needs `pip install playwright && playwright install chromium`.

Keep your real `profile.json` out of Git (it's in `.gitignore`).

---
Made by [Tiwalade Joanna Okedara-Kalu](https://github.com/tiwalade-joanna-okedara) · MIT licence
