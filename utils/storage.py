import csv
import os

def load_existing(file_path):
    existing = set()

    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader, None)
            for row in reader:
                existing.add(row[1])

    return existing


def save_jobs(file_path, jobs):
    file_exists = os.path.isfile(file_path)

    with open(file_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        if not file_exists:
            writer.writerow(["empresa", "titulo"])

        for job in jobs:
            writer.writerow([job["company"], job["title"]])
