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
import pytz
import ctypes

sys.stdout.reconfigure(encoding='utf-8')

# Suppress ALSA errors
def suppress_alsa_errors():
    try:
        ERROR_HANDLER_FUNC = ctypes.CFUNCTYPE(None, ctypes.c_char_p, ctypes.c_int,
                                               ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p)
        def py_error_handler(filename, line, function, err, fmt): pass
        c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)
        asound = ctypes.cdll.LoadLibrary('libasound.so.2')
        asound.snd_lib_error_set_handler(c_error_handler)
    except:
        pass
suppress_alsa_errors()

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
    os.system(f"ffplay -nodisp -autoexit -loglevel quiet {file}")
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
            try:
                speak_sync(entry.title)
                count += 1
                if count == 3:
                    return
            except:
                pass
    speak_sync("No fresh news found today.")

# -------------------------
# CLOCK WINDOW
# -------------------------
def time_window():
    try:
        root = tk.Tk()
        root.title("Meera Mirror")
        label = tk.Label(root, font=("Arial", 30), fg="white", bg="black")
        label.pack()
        def update():
            IST = pytz.timezone("Asia/Kolkata")
            now = datetime.now(IST).strftime("%d %B %Y\n%H:%M:%S")
            label.config(text=now)
            label.after(1000, update)
        update()
        root.mainloop()
    except Exception as e:
        print(f"GUI not available: {e}")
        while True:
            IST = pytz.timezone("Asia/Kolkata")
            now = datetime.now(IST).strftime("%d %B %Y | %H:%M:%S")
            print(f"\r{now}", end="")
            time.sleep(1)

threading.Thread(target=time_window, daemon=True).start()

# -------------------------
# SPEECH RECOGNITION
# -------------------------
recognizer = sr.Recognizer()
mic = sr.Microphone(device_index=3, sample_rate=44100, chunk_size=1024)

speak_sync("Meera system is ready. Say activate.")

# -------------------------
# MAIN LOOP
# -------------------------
while True:
    with mic as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        try:
            audio = recognizer.listen(source, timeout=15, phrase_time_limit=10)
        except:
            continue

    try:
        command = recognizer.recognize_google(audio).lower()
        print("Heard:", command)

        if "activate" in command:
            speak_sync("Hi, I am Meera, your personalized mirror.")

        elif "time" in command:
            IST = pytz.timezone("Asia/Kolkata")
            now = datetime.now(IST).strftime("%d %B %Y %H:%M")
            speak_sync(f"The current time is {now}")

        elif "weather" in command:
            speak_sync("Please tell me the city name")
            with mic as source:
                audio = recognizer.listen(source, timeout=10, phrase_time_limit=5)
                city = recognizer.recognize_google(audio)
                get_weather(city)

        elif "news" in command:
            speak_sync("Here are today's top news")
            read_news()

    except sr.UnknownValueError:
        pass
    except sr.RequestError:
        speak_sync("Internet connection problem.")
    except Exception as e:
        print("Mic error:", e)
        continue
