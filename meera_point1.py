import speech_recognition as sr
import asyncio
import edge_tts
import os
import requests
import feedparser
from datetime import datetime
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
# GUI SETUP
# -------------------------
root = tk.Tk()
root.title("Meera Mirror")
root.configure(bg="black")
root.attributes("-fullscreen", True)

time_label = tk.Label(root, font=("Arial", 35, "bold"), fg="white", bg="black")
time_label.pack(pady=20)

info_label = tk.Label(root, font=("Arial", 20), fg="cyan", bg="black",
                      wraplength=460, justify="center")
info_label.pack(pady=20)

# Clock activated flag
clock_running = False

def update_clock():
    if clock_running:
        now = datetime.now().strftime("%d %B %Y\n%H:%M:%S")
        time_label.config(text=now)
    root.after(1000, update_clock)

update_clock()

def start_clock():
    global clock_running
    clock_running = True

def show_news(text):
    info_label.config(text=f"📰 {text}", fg="cyan")

def clear_news():
    info_label.config(text="")

# -------------------------
# SPEAK
# -------------------------
async def speak(text):
    file = "meera.mp3"
    communicate = edge_tts.Communicate(text, VOICE)
    await communicate.save(file)
    os.system(f"mpg123 -q {file}")
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
            speak_sync("City not found")
            return
        temp = data["main"]["temp"]
        desc = data["weather"][0]["description"]
        speak_sync(f"{city} temperature is {temp} degree with {desc}")
    except:
        speak_sync("Weather error")

# -------------------------
# NEWS
# -------------------------
rss_feeds = [
    "https://news.abplive.com/news/india/feed",
    "https://www.ndtv.com/rss"
]

def read_news():
    count = 0
    for url in rss_feeds:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            show_news(entry.title)
            root.update()
            speak_sync(entry.title)
            count += 1
            if count == 3:
                clear_news()
                return

# -------------------------
# MIC THREAD
# -------------------------
def meera_thread():
    recognizer = sr.Recognizer()
    mic = sr.Microphone(device_index=3, sample_rate=44100, chunk_size=1024)

    speak_sync("Meera system is ready")

    while True:
        try:
            with mic as source:
                print("Listening...")
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = recognizer.listen(source, timeout=15, phrase_time_limit=10)

            command = recognizer.recognize_google(audio).lower()
            print("Heard:", command)

            if "activate" in command:
                start_clock()
                speak_sync("Hello, I am Meera,Your personalised companion")

            elif "time" in command:
                now = datetime.now().strftime("%d %B %Y %H:%M")
                speak_sync(f"Time is {now}")

            elif "weather" in command:
                speak_sync("Tell city name")
                with mic as source:
                    audio = recognizer.listen(source, timeout=10)
                    city = recognizer.recognize_google(audio)
                    get_weather(city)

            elif "news" in command:
                speak_sync("Top news")
                read_news()
              elif "deactivate" in command:
    speak_sync("Meera is deactivating. Goodbye!")
    break

        except Exception as e:
            print("Error:", e)
            continue

# Mic thread start
threading.Thread(target=meera_thread, daemon=True).start()

# GUI main loop
root.mainloop()
