import smtplib
import datetime
import requests
import os
from dotenv import load_dotenv
from datetime import timedelta

import sqlite3


load_dotenv()

today = datetime.date.today()
yesterday = today - timedelta(days = 1)
API_KEY = os.getenv("AUTHTOKEN")
PASSWORD = os.getenv("EMAILPASSWORD")
EMAIL = os.getenv("EMAIL")

def send(message, to_address):
    connection = smtplib.SMTP("smtp.gmail.com")
    connection.starttls()

    connection.login(user=EMAIL,password=PASSWORD)
    connection.sendmail(from_addr=EMAIL, to_addrs=f"{to_address}",
                        msg=message)


db = sqlite3.connect("login.db", check_same_thread=False)
cursor = db.cursor()
emails = cursor.execute("SELECT email, id FROM login_information;")
for i, j in emails.fetchall():

    message = "Hi! \nYour daily update is here!!\n\n"
    topics = cursor.execute("SELECT topic FROM news_topics WHERE id = ?", (j,)).fetchall()
    dates = cursor.execute("SELECT dates, occasion FROM important_dates WHERE id = ?", (j,)).fetchall()
    has_personal = False

    for l in dates:
        # extract date from string collected from database
        dat = datetime.date(int(l[0][0:4]), int(l[0][5:7]), int(l[0][8:10]))
        if dat.day == today.day and dat.month == today.month:
            if not has_personal:
                message += "\nYour personal updates:\n"
            has_personal = True
            message += f"{l[1]}\n"

    for k in topics:
        # get news from API
        thingy = requests.get(f"https://newsapi.org/v2/everything?q={k[0]}&from={yesterday}&sortBy=popularity&language=en&apiKey={API_KEY}").json()
        if thingy["articles"] == []:
            message += f"sorry there was no news on the topic {k[0]}"
        else:
            count = 0
            for m in thingy["articles"]:
                message += f"Source:  {m['source']['name']}\n"
                message += f"title: {m['title']}\n"
                message += f'description:  {m["description"]}\n'
                message += f'url:  {m["url"]}\n'
                message += "\n"
                count += 1
                if count == 10:
                    break
        print(thingy)

    message = 'Subject: {}\n\n{}'.format("Daily Updates", message)
    send(message.encode('utf-8'), i)
    print("done")



