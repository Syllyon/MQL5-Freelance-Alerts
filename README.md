## 🎯 Project Description
This project's primary objective is to test if I can be the first MetaQuotes developers to apply for a freelance job from the MQL5 website, since other developers often flood these positions minutes after they are published.
This code notifies Telegram of any new, real-time Job postings for MQL5 Freelance In order to accomplish this, you must first set up the Telegram Bot using Botfather, then make a public or private Telegram channel and grant the bot permission to send messages.

You can see the bot in action in my Telegram Channel: https://t.me/mql5freelancejobs

## Results after 3 days of use: 
I've applied for 11 jobs in 3 days using these notifications, and I was accepted for 2 of them, meaning I had an 18.18% chance of being chosen. Other factors include: 
- Customers forgetting about their freelance job posting.
- Customers prefers developers with more reviews and projects overall; my profile has ⭐⭐⭐⭐⭐ (5 stars, 1 project/feedback).

## 🌟 Features
- **Automated notifications**: Yep.
- **Simplicity**: I'm just making stuff up at this point.
- **Filters**: Currently ommiting any "personal job" post since these are usually created for a designated developer.
  
## 💻 Technologies Used
- **Language**: Python
- **Database**: SQLite
- **Communication & Notifications**: Telegram Bot API

## 🛠️ Installation
Follow these steps to set up the project locally:
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/Syllyon/MQL5-Freelance-Alerts.git
   cd MQL5-Freelance-Alerts
2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
3. **Set Up Environment Variables: Create a .env file in the root directory and add the following**:
   ```text
   TELEGRAM_BOT_KEY = your_telegram_bot_token
   TELEGRAM_CHANNEL_ID = your_telegram_channel_id
3. **Set Up .gitignore: You don't want to be uploading your API keys or database, would you?**:
   ```text
   .env
   mql5-freelance.db
4. **Run the Application**:
   ```bash
   python main.py

## 🧪 Usage
1. Launch the application.
2. Stop manually refreshing the website and get real-time notifications :)

## 🧪 To-do List
1. Deploy this as a background service.
2. Add more notification methods.
