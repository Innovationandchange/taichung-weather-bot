import discord
import requests
import asyncio
import datetime

import os
import os
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
# OpenWeatherMap API
WEATHER_API_KEY = "你的 OpenWeatherMap API Key"
CITY_NAME = "Taichung,tw"
API_URL = f"http://api.openweathermap.org/data/2.5/weather?q={CITY_NAME}&appid={WEATHER_API_KEY}&units=metric&lang=zh_tw"

intents = discord.Intents.default()
client = discord.Client(intents=intents)

async def fetch_weather():
    response = requests.get(API_URL)
    data = response.json()
    description = data['weather'][0]['description']
    temp = data['main']['temp']
    feels_like = data['main']['feels_like']
    humidity = data['main']['humidity']
    return f"🌤️ 今日台中天氣：{description}\n🌡️ 溫度：{temp}°C（體感 {feels_like}°C）\n💧 濕度：{humidity}%"

async def daily_weather_task():
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)
    while not client.is_closed():
        now = datetime.datetime.now()
        # 每天早上 8 點發送
        if now.hour == 8 and now.minute == 0:
            weather_report = await fetch_weather()
            await channel.send(weather_report)
            await asyncio.sleep(60)  # 避免重複發送
        await asyncio.sleep(30)

@client.event
async def on_ready():
    print(f'已登入為 {client.user}')
    client.loop.create_task(daily_weather_task())

client.run(DISCORD_TOKEN)
