import discord
from discord.ext import commands, tasks
import requests
import os
import datetime

# 讀取環境變數
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
CWB_API_KEY = os.getenv("CWB_API_KEY")
CITY_NAME = "臺中市"

# 天氣 API URL
CWB_API_URL = (
    f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001"
    f"?Authorization={CWB_API_KEY}&locationName={CITY_NAME}"
)

# 初始化 bot，開啟 message content intent
intents = discord.Intents.default()
intents.message_content = True  # ⚠️ 必須開啟才能接收指令
bot = commands.Bot(command_prefix="!", intents=intents)

# 取得天氣資訊函式
def fetch_taichung_weather():
    try:
        response = requests.get(CWB_API_URL)
        data = response.json()
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

# 機器人上線後事件
@bot.event
async def on_ready():
    print(f"✅ Bot 已上線：{bot.user}")
    send_daily_weather.start()

# 指令：!天氣
@bot.command()
async def 天氣(ctx):
    report = fetch_taichung_weather()
    await ctx.send(report)

# 每天早上 8:00 自動發送天氣
@tasks.loop(minutes=1.0)
async def send_daily_weather():
    now = datetime.datetime.now()
    if now.hour == 8 and now.minute == 0:
        channel = bot.get_channel(CHANNEL_ID)
        if channel:
            report = fetch_taichung_weather()
            await channel.send(report)

# 啟動 Bot
bot.run(DISCORD_TOKEN)
