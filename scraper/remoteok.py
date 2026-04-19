import requests
from bs4 import BeautifulSoup

URL = "https://remoteok.com/remote-dev-jobs"

def get_jobs():
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(URL, headers=headers)

    soup = BeautifulSoup(response.text, "html.parser")
    jobs = soup.find_all("tr", class_="job")

    results = []

    for job in jobs:
        title = job.find("h2")
        company = job.find("h3")

        if title and company:
            results.append({
                "title": title.text.strip(),
                "company": company.text.strip()
            })

    return results
