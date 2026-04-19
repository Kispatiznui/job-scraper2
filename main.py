import requests
from bs4 import BeautifulSoup
import csv
import os
import json

URL = "https://remoteok.com/remote-dev-jobs"
CSV_PATH = "jobs.csv"
CONFIG_PATH = "config.json"

headers = {
    "User-Agent": "Mozilla/5.0"
}

# -----------------------
# Cargar config
# -----------------------
with open(CONFIG_PATH) as f:
    config = json.load(f)

keywords = [k.lower() for k in config["keywords"]]

def match_keywords(text):
    text = text.lower()
    return any(k in text for k in keywords)

# -----------------------
# Cargar existentes
# -----------------------
existing = set()

if os.path.exists(CSV_PATH):
    with open(CSV_PATH, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader, None)
        for row in reader:
            existing.add(row[1])  # título

# -----------------------
# Scraping
# -----------------------
response = requests.get(URL, headers=headers)

if response.status_code != 200:
    print("Error al acceder a RemoteOK")
    exit()

soup = BeautifulSoup(response.text, "html.parser")
jobs = soup.find_all("tr", class_="job")

# -----------------------
# Guardar resultados
# -----------------------
file_exists = os.path.isfile(CSV_PATH)

with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)

    if not file_exists:
        writer.writerow(["empresa", "titulo"])

    nuevos = 0

    for job in jobs:
        title = job.find("h2")
        company = job.find("h3")

        if title and company:
            job_title = title.text.strip()
            company_name = company.text.strip()

            text = job_title + " " + company_name

            if job_title not in existing and match_keywords(text):
                writer.writerow([company_name, job_title])
                nuevos += 1

    print(f"✅ Nuevos trabajos guardados: {nuevos}")
