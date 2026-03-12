# =========================
# MEERA – PERSONALIZED MIRROR
# =========================

import speech_recognition as sr
import asyncio
import edge_tts
import playsound
import os
import requests
import feedparser
from datetime import datetime, date
import tkinter as tk
import threading
import time
import sys

sys.stdout.reconfigure(encoding='utf-8')

# -------------------------
# CONFIG
# -------------------------
API_KEY = "1c192646db0e072537706f539e68aa71"
WEATHER_URL = "http://api.openweathermap.org/data/2.5/weather?"
VOICE = "en-IN-NeerjaNeural"

# -------------------------
# EDGE TTS
# -------------------------
async def speak(text):
    file = "meera.mp3"
    communicate = edge_tts.Communicate(text, VOICE)
    await communicate.save(file)
    playsound.playsound(file)
    os.remove(file)

def speak_sync(text):
    asyncio.run(speak(text))

# -------------------------
# WEATHER
# -------------------------
def get_weather(city):
    try:
        url = f"{WEATHER_URL}q={city},IN&appid={API_KEY}&units=metric"
        data = requests.get(url).json()

        if data["cod"] != 200:
            speak_sync("Sorry, I could not find that city.")
            return

        temp = data["main"]["temp"]
        desc = data["weather"][0]["description"]

        speak_sync(f"The temperature in {city} is {temp} degree Celsius with {desc}")

    except:
        speak_sync("Weather service is not available right now.")

# -------------------------
# NEWS
# -------------------------
rss_feeds = [
    "https://news.abplive.com/news/india/feed",
    "https://www.ndtv.com/rss",
    "https://indianexpress.com/section/india/feed"
]

def read_news():
    count = 0
    for feed_url in rss_feeds:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries:
            published = entry.get("published", "")
            try:
                pub_date = datetime.strptime(published[:16], "%a, %d %b %Y").date()
            except:
                continue

            if pub_date == date.today():
                speak_sync(entry.title)
                count += 1
                if count == 3:
                    return

    speak_sync("No fresh news found today.")

# -------------------------
# TIME WINDOW (TKINTER)
# -------------------------
def time_window():
    root = tk.Tk()
    root.title("Meera Mirror – Time")

    label = tk.Label(root, font=("Arial", 32))
    label.pack()

    def update():
        label.config(text=time.strftime("%d %B %Y\n%H:%M:%S"))
        label.after(1000, update)

    update()
    root.mainloop()

threading.Thread(target=time_window, daemon=True).start()

# -------------------------
# SPEECH RECOGNITION
# -------------------------
r = sr.Recognizer()
mic = sr.Microphone()

speak_sync("Meera system is ready. Say activate.")

while True:
    with mic as source:
        r.adjust_for_ambient_noise(source, duration=0.5)
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=4)
        except:
            continue

    try:
        command = r.recognize_google(audio).lower()
        print("Heard:", command)

        if "activate" in command:
            speak_sync("Hi, I am Meera, your personalized mirror.")

        elif "time" in command:
            now = datetime.now().strftime("%d %B %Y %H:%M")
            speak_sync(f"The current time is {now}")

        elif "weather" in command:
            speak_sync("Please tell me the city name")
            with mic as source:
                audio = r.listen(source, timeout=5, phrase_time_limit=5)
                city = r.recognize_google(audio)
                get_weather(city)

        elif "news" in command:
            speak_sync("Here are today's top news")
            read_news()

    except:
        pass
