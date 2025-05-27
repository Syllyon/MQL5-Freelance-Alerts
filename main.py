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

DB_NAME = 'mql5-freelance.db'
conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

def setup_database():
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        description TEXT,
        budget TEXT,
        applications INTEGER,
        date_posted TEXT,
        UNIQUE(title, date_posted)
    )
    """)
    conn.commit()

def scrape_jobs():
    url = "https://www.mql5.com/en/job"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    
    job_items = soup.find_all("div", class_="job-item")
    new_jobs = []

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    for job in job_items:
        title        = job.find("div", class_="job-item__title").get_text(strip=True)
        href         = job.find("a").get('href')
        full_link    = f"https://www.mql5.com{href}"
        description  = job.find("div", class_="job-item__text").get_text(strip=True)
        budget       = job.find("span", class_="budget").get_text(strip=True)
        date_posted  = job.find("time").get("datetime")

        try:
            cursor.execute("""
            INSERT INTO jobs (title, description, budget, date_posted)
            VALUES (?, ?, ?, ?)
            """, (title, description, budget, date_posted))
            conn.commit()
            new_jobs.append(f"New Job: {title}\n\nDescription: {description}\n\nBudget: {budget}\n\nPosted: {date_posted}\n\nLink: {full_link}")

        except sqlite3.IntegrityError:
            print("Job post already added... Ending loop")
            break

    if new_jobs:
        for job_message in new_jobs:
            send_telegram_message(job_message)

    new_jobs.clear()

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_KEY}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHANNEL_ID, "text": message}
    requests.post(url, data=payload)

scheduler = BlockingScheduler()
scheduler.add_job(scrape_jobs, "interval", minutes=1)

if __name__ == "__main__":    
    print("Starting application!")
    setup_database()
    scrape_jobs()
    scheduler.start()