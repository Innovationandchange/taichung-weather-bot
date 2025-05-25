import discord
import requests
import asyncio
import datetime
import os

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
CWB_API_KEY = os.getenv("CWB_API_KEY")
CITY_NAME = "臺中市"

intents = discord.Intents.default()
client = discord.Client(intents=intents)

CWB_API_URL = f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001?Authorization={CWB_API_KEY}&locationName={CITY_NAME}"

async def fetch_taichung_weather():
    response = requests.get(CWB_API_URL)
    data = response.json()
    try:
        location = data['records']['location'][0]
        weather_elements = location['weatherElement']
        wx = weather_elements[0]['time'][0]['parameter']['parameterName']
        pop = weather_elements[1]['time'][0]['parameter']['parameterName']
        minT = weather_elements[2]['time'][0]['parameter']['parameterName']
        maxT = weather_elements[4]['time'][0]['parameter']['parameterName']

        return (
            f"📍 **{CITY_NAME} 今日天氣預報**\n"
            f"🌤️ 天氣狀況：{wx}\n"
            f"🌡️ 氣溫：{minT}°C - {maxT}°C\n"
            f"🌧️ 降雨機率：{pop}%"
        )
    except Exception as e:
        return "⚠️ 無法取得天氣資料"

async def daily_weather_task():
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)
    while not client.is_closed():
        now = datetime.datetime.now()
        if now.hour == 8 and now.minute == 0:
            report = await fetch_taichung_weather()
            await channel.send(report)
            await asyncio.sleep(60)
        await asyncio.sleep(30)

@client.event
async def on_ready():
    print(f"✅ Bot 上線：{client.user}")
    client.loop.create_task(daily_weather_task())

client.run(DISCORD_TOKEN)
