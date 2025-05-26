import os
import sqlite3
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from dotenv import load_dotenv

load_dotenv()
TELEGRAM_BOT_KEY = os.getenv("TELEGRAM_BOT_KEY")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")

DB_NAME = 'database.db'
conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    description TEXT,
    budget TEXT,
    applications INTEGER,
    category TEXT,
    language TEXT,
    date_posted TEXT,
    UNIQUE(title, date_posted)
)
""")
conn.commit()

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_KEY}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHANNEL_ID, "text": message}
    requests.post(url, data=payload)

def scrape_jobs():
    url = "https://www.mql5.com/en/job"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    
    job_items = soup.find_all("div", class_="job-item")
    new_jobs = []

    for job in job_items:
        title = job.find("div", class_="job-item__title").get_text(strip=True)
        description = job.find("div", class_="job-item__text").get_text(strip=True)
        budget = job.find("span", class_="budget").get_text(strip=True)
        applications = int(job.find("div", class_="job-item__count").strong.get_text(strip=True))
        category = job.find("span", class_="job-item__list-category-item").get_text(strip=True) if job.find("span", class_="job-item__list-category-item") else "N/A"
        language = job.find("span", class_="job-item__lang").get_text(strip=True)
        date_posted = job.find("time").get("datetime")

        try:
            cursor.execute("""
            INSERT INTO jobs (title, description, budget, applications, category, language, date_posted)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (title, description, budget, applications, category, language, date_posted))
            conn.commit()
            new_jobs.append(f"New Job: {title}\nDescription: {description}\nBudget: {budget}\nCategory: {category}\nLanguage: {language}")
        except sqlite3.IntegrityError:
            pass

    if new_jobs:
        for job_message in new_jobs:
            send_telegram_message(job_message)

scheduler = BlockingScheduler()
scheduler.add_job(scrape_jobs, "interval", seconds=30)

if __name__ == "__main__":
    scheduler.start()