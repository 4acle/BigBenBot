import discord
import asyncio
import datetime
from discord.ext import commands, tasks
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Replace with your bot's token
TOKEN = os.getenv('DISCORD_BOT_TOKEN')  # Use environment variable for token

# Bot setup with necessary intents
intents = discord.Intents.default()
intents.voice_states = True  # Allows tracking of voice channels
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    logging.info(f"🔔 Big Ben Bot is online! Logged in as {bot.user}")
    big_ben_chime.start()  # Start the hourly chime loop

def get_largest_vc():
    """Find the most populated voice channel in all servers."""
    largest_vc = None
    max_members = 0

    for guild in bot.guilds:
        for vc in guild.voice_channels:
            if len(vc.members) > max_members:
                largest_vc = vc
                max_members = len(vc.members)

    return largest_vc

async def play_audio(vc, file_name):
    """Helper function to play an audio file from the assets folder in a voice channel."""
    if vc:
        try:
            vc_client = await vc.connect()  # Connect to VC
            file_path = f"assets/{file_name}"  # Correct path to assets folder
            source = discord.FFmpegPCMAudio(file_path)

            vc_client.play(source)
            while vc_client.is_playing():
                await asyncio.sleep(1)

            await vc_client.disconnect()
        except Exception as e:
            logging.error(f"⚠️ Error playing audio ({file_name}): {e}")

async def play_hourly_chime(vc, hour):
    """Play the quarter chime first, then the hourly chime the correct number of times."""
    if vc:
        logging.info(f"🔔 Playing Quarter Chime in {vc.name}")
        await play_audio(vc, "quarterChime.mp3")  # Play quarter chime first
        
        logging.info(f"🔔 Playing {hour} Hourly Chimes in {vc.name}")
        for _ in range(hour):  # Play hourly chime the correct number of times
            await play_audio(vc, "hourlyChime.mp3")
            await asyncio.sleep(1)  # Small delay between chimes

@tasks.loop(minutes=1)
async def big_ben_chime():
    """Check the time and play chimes every hour on the hour."""
    now = datetime.datetime.now()

    if now.minute == 0:  # Only run at the start of the hour
        hour = now.hour % 12  # Convert to 12-hour format
        hour = 12 if hour == 0 else hour  # Ensure 12 AM/PM rings 12 chimes

        vc = get_largest_vc()
        if vc:
            await play_hourly_chime(vc, hour)
        else:
            logging.info("🚫 No active voice channels found.")

bot.run(TOKEN)
