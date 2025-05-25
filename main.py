import discord
import requests
import asyncio
import datetime
import os
from discord.ext import commands
import pytz

# 環境變數
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
CWB_API_KEY = os.getenv("CWB_API_KEY")
CITY_NAME = "臺中市"

# 建立 bot
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# 中央氣象局 API URL
CWB_API_URL = f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001?Authorization={CWB_API_KEY}&locationName={CITY_NAME}"

# 天氣資料取得函式
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

# !天氣 指令
@bot.command()
async def 天氣(ctx):
    report = await fetch_taichung_weather()
    await ctx.send(report)

# 自動每日發送
async def daily_weather_task():
    await bot.wait_until_ready()
    channel = bot.get_channel(CHANNEL_ID)
    tz = pytz.timezone('Asia/Taipei')  # 台灣時區
    while not bot.is_closed():
        now = datetime.datetime.now(tz)
        if now.hour == 8 and now.minute == 0:
            report = await fetch_taichung_weather()
            await channel.send(report)
            await asyncio.sleep(60)  # 等 1 分鐘避免重複發送
        await asyncio.sleep(30)

# Bot 上線事件
@bot.event
async def on_ready():
    print(f"✅ Bot 上線：{bot.user}")
    # 啟動每日排程
    bot.loop.create_task(daily_weather_task())
    # 第一次上線時傳送測試訊息
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        await channel.send("🚀 Bot 上線完成，輸入 `!天氣` 試試看吧！")

# 啟動 bot
bot.run(DISCORD_TOKEN)
