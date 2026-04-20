import requests
from bs4 import BeautifulSoup
import csv
import os
import json
from urllib.parse import urljoin

URL = "https://remoteok.com/api"
CSV_PATH = "jobs.csv"
JSON_PATH = "jobs.json"
CONFIG_PATH = "config.json"

headers = {
    "User-Agent": "Mozilla/5.0"
}

# -----------------------
# CONFIG
# -----------------------
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = json.load(f)

exclude = [e.lower() for e in config.get("exclude", [])]

print(f"\n🚫 Exclude base: {exclude}\n")

# -----------------------
# FILTRO DURO
# -----------------------
def is_hard_excluded(text):
    text = text.lower()
    return any(e in text for e in exclude)

# -----------------------
# PENALIZACIÓN
# -----------------------
def domain_penalty(text):
    text = text.lower()
    penalty = 0

    non_tech = [
        "retail", "store", "sales",
        "marketing", "hr", "human resources",
        "finance", "accounting",
        "nurse", "health",
        "purchasing", "logistics",
        "operations", "culture"
    ]

    for w in non_tech:
        if w in text:
            penalty -= 2

    return penalty

# -----------------------
# SCORING
# -----------------------
def calculate_score(text):
    text = text.lower()
    score = 0

    strong_tech = [
        "qa", "tester", "testing", "quality assurance",
        "automation", "selenium",
        "test engineer", "qa engineer", "qa analyst"
    ]
    for k in strong_tech:
        if k in text:
            score += 4

    mid_tech = [
        "developer", "engineer", "software",
        "backend", "frontend", "fullstack",
        "git", "docker", "ci", "cd", "python"
    ]
    for k in mid_tech:
        if k in text:
            score += 2

    entry = [
        "junior", "entry level", "intern",
        "trainee", "remote", "work from home",
        "no experience", "0 experience"
    ]
    for k in entry:
        if k in text:
            score += 2

    if "remote" in text:
        score += 1

    return score

# -----------------------
# EXISTENTES
# -----------------------
existing = set()

if os.path.exists(CSV_PATH):
    try:
        with open(CSV_PATH, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader, None)
            for row in reader:
                if len(row) > 1:
                    existing.add(row[1])
    except:
        print("⚠️ Error leyendo CSV")

# -----------------------
# API REQUEST
# -----------------------
response = requests.get(URL, headers=headers)

if response.status_code != 200:
    print("❌ Error API")
    exit()

data = response.json()
jobs = data[1:]  # RemoteOK devuelve metadata en [0]

print(f"TOTAL JOBS: {len(jobs)}\n")

top, good, ok, low = [], [], [], []
evaluados = 0

# -----------------------
# CSV WRITE
# -----------------------
try:
    file_exists = os.path.exists(CSV_PATH)

    with open(CSV_PATH, "a", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)

        if not file_exists or os.stat(CSV_PATH).st_size == 0:
            writer.writerow(["empresa", "titulo", "url", "score"])

        for job in jobs:
            title = job.get("position", "")
            company = job.get("company", "")
            raw_url = job.get("url", "")

            # ✅ FIX robusto de URL
            if raw_url.startswith("http"):
                url = raw_url
            else:
                url = urljoin("https://remoteok.com", raw_url)

            text = f"{title} {company}"

            if is_hard_excluded(text):
                continue

            score = calculate_score(text)
            score += domain_penalty(text)

            evaluados += 1

            job_data = {
                "empresa": company,
                "titulo": title,
                "url": url,
                "score": score
            }

            # -----------------------
            # CLASIFICACIÓN
            # -----------------------
            if score >= 8:
                top.append(job_data)
            elif score >= 6:
                good.append(job_data)
            elif score >= 4:
                ok.append(job_data)
            else:
                low.append(job_data)

            # guardar CSV solo relevantes
            if url and title and title not in existing and score >= 1:
                writer.writerow([company, title, url, score])

except PermissionError:
    print("❌ Cierra jobs.csv (Excel abierto)")
    exit()

# -----------------------
# ORDENAR
# -----------------------
for lst in [top, good, ok, low]:
    lst.sort(key=lambda x: x["score"], reverse=True)

# -----------------------
# OUTPUT
# -----------------------
def print_section(name, jobs, emoji):
    print(f"\n{emoji} {name} ({len(jobs)})")
    print("-" * 40)
    for j in jobs:
        print(f"{j['empresa']} - {j['titulo']} | score: {j['score']}")
        print(j["url"])
        print()

print(f"📊 Jobs evaluados: {evaluados}")

print_section("TOP JOBS", top, "🔥")
print_section("BUENOS", good, "🟢")
print_section("ACEPTABLES", ok, "🟡")
print_section("BAJOS", low, "⚪")

# -----------------------
# JSON SAVE
# -----------------------
all_jobs = top + good + ok + low

if os.path.exists(JSON_PATH):
    try:
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            existing_json = json.load(f)
    except:
        existing_json = []
else:
    existing_json = []

existing_json.extend(all_jobs)

existing_json.sort(key=lambda x: x.get("score", 0), reverse=True)

with open(JSON_PATH, "w", encoding="utf-8") as f:
    json.dump(existing_json, f, indent=4, ensure_ascii=False)

# -----------------------
# SUMMARY
# -----------------------
print("----------------------")
print(f"🔥 TOP: {len(top)}")
print(f"🟢 GOOD: {len(good)}")
print(f"🟡 OK: {len(ok)}")
print(f"⚪ LOW: {len(low)}")
