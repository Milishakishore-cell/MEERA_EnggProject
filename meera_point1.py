# import speech_recognition as sr
# import asyncio
# import edge_tts
# import os
# import requests
# import feedparser
# from datetime import datetime, date
# import tkinter as tk
# import threading
# import time
# import sys
# from playsound import playsound

# sys.stdout.reconfigure(encoding='utf-8')

# # -------------------------
# # CONFIG
# # -------------------------
# API_KEY = "1c192646db0e072537706f539e68aa71"
# WEATHER_URL = "http://api.openweathermap.org/data/2.5/weather?"
# VOICE = "en-IN-NeerjaNeural"

# # -------------------------
# # EDGE TTS
# # -------------------------
# async def speak(text):
#     file = "meera.mp3"
#     communicate = edge_tts.Communicate(text, VOICE)
#     await communicate.save(file)

#     playsound(file)
#     os.remove(file)

# def speak_sync(text):
#     asyncio.run(speak(text))

# # -------------------------
# # WEATHER
# # -------------------------
# def get_weather(city):
#     try:
#         url = f"{WEATHER_URL}q={city},IN&appid={API_KEY}&units=metric"
#         data = requests.get(url).json()

#         if data["cod"] != 200:
#             speak_sync("Sorry, I could not find that city.")
#             return

#         temp = data["main"]["temp"]
#         desc = data["weather"][0]["description"]

#         speak_sync(f"The temperature in {city} is {temp} degree Celsius with {desc}")

#     except:
#         speak_sync("Weather service is not available right now.")

# # -------------------------
# # NEWS
# # -------------------------
# rss_feeds = [
#     "https://news.abplive.com/news/india/feed",
#     "https://www.ndtv.com/rss",
#     "https://indianexpress.com/section/india/feed"
# ]

# def read_news():
#     count = 0

#     for feed_url in rss_feeds:
#         feed = feedparser.parse(feed_url)

#         for entry in feed.entries:
#             try:
#                 speak_sync(entry.title)
#                 count += 1

#                 if count == 3:
#                     return

#             except:
#                 pass

#     speak_sync("No fresh news found today.")

# # -------------------------
# # CLOCK WINDOW
# # -------------------------
# def time_window():
#     root = tk.Tk()
#     root.title("Meera Mirror")

#     label = tk.Label(root, font=("Arial", 30))
#     label.pack()

#     def update():
#         label.config(text=time.strftime("%d %B %Y\n%H:%M:%S"))
#         label.after(1000, update)

#     update()
#     root.mainloop()

# #threading.Thread(target=time_window, daemon=True).start()

# # -------------------------
# # SPEECH RECOGNITION
# # -------------------------
# recognizer = sr.Recognizer()

# # USB microphone stable config
# mic = sr.Microphone(device_index=2)

# speak_sync("Meera system is ready. Say activate.")

# while True:

#     with mic as source:

#         recognizer.adjust_for_ambient_noise(source, duration=0.5)

#         try:
#             audio = recognizer.listen(source, timeout=5, phrase_time_limit=4)
#         except:
#             continue

#     try:
#         command = recognizer.recognize_google(audio).lower()

#         print("Heard:", command)

#         if "activate" in command:

#             speak_sync("Hi, I am Meera, your personalized mirror.")

#         elif "time" in command:

#             now = datetime.now().strftime("%d %B %Y %H:%M")

#             speak_sync(f"The current time is {now}")

#         elif "weather" in command:

#             speak_sync("Please tell me the city name")

#             with mic as source:

#                 audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)

#                 city = recognizer.recognize_google(audio)

#                 get_weather(city)

#         elif "news" in command:

#             speak_sync("Here are today's top news")

#             read_news()

#     except sr.UnknownValueError:
#         pass

#     except sr.RequestError:
#         speak_sync("Internet connection problem.")
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
# SPEAK (STABLE)
# -------------------------
async def speak(text):
    file = "meera.mp3"
    communicate = edge_tts.Communicate(text, VOICE)
    await communicate.save(file)
    os.system(f"mpg123 {file} > /dev/null 2>&1")
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
            speak_sync(entry.title)
            count += 1
            if count == 3:
                return

# -------------------------
# GUI (TIME DISPLAY)
# -------------------------
def time_window():
    try:
        root = tk.Tk()
        root.title("Meera Mirror")

        label = tk.Label(root, font=("Arial", 30), fg="white", bg="black")
        label.pack(fill="both", expand=True)

        def update():
            now = time.strftime("%d %B %Y\n%H:%M:%S")
            label.config(text=now)
            root.after(1000, update)

        update()
        root.mainloop()

    except:
        print("GUI not supported")

# start GUI
threading.Thread(target=time_window, daemon=True).start()

# -------------------------
# MIC SETUP (FINAL FIX)
# -------------------------
recognizer = sr.Recognizer()
recognizer.energy_threshold = 400
recognizer.pause_threshold = 0.8

mic = sr.Microphone(device_index=2)

speak_sync("Meera system is ready")

# -------------------------
# MAIN LOOP
# -------------------------
while True:
    try:
        with mic as source:
            print("Listening...")
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=4)

        command = recognizer.recognize_google(audio).lower()
        print("Heard:", command)

        if "activate" in command:
            speak_sync("Hello, I am Meera")

        elif "time" in command:
            now = datetime.now().strftime("%d %B %Y %H:%M")
            speak_sync(f"Time is {now}")

        elif "weather" in command:
            speak_sync("Tell city name")
            with mic as source:
                audio = recognizer.listen(source, timeout=5)
                city = recognizer.recognize_google(audio)
                get_weather(city)

        elif "news" in command:
            speak_sync("Top news")
            read_news()

    except Exception as e:
        print("Error:", e)
        continue
