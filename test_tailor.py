import json, tailor
p = json.load(open("profile.example.json")); jd = open("job.example.txt").read()
t = tailor.tailor(p, jd)
assert t["title"] == "SEO and AI Search Lead", t["title"]
assert "ai search" in " ".join(t["jobs"][0]["bullets"][0]["tags"]) or "seo" in t["jobs"][0]["bullets"][0]["tags"]
assert "<li>" in tailor.render(p, t)
print("All tests passed")
