import disnake
from disnake.ext import commands
import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TOKEN")

intents = disnake.Intents(
    guilds=True,
    messages=True,
    members=True,
    message_content=True
)

bot = commands.InteractionBot(intents=intents)

def init_db():
    if not os.path.exists("database.db"):
        open("database.db", "w").close()
    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS voice_channels (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            channel_id INTEGER,
                            owner_id INTEGER,
                            name TEXT,
                            created_at TEXT
                          )''')
        conn.commit()

@bot.event
async def on_ready():
    print(f"{bot.user}")

def load_cogs():
    for root, _, files in os.walk("cogs"):
        for file in files:
            if file.endswith(".py") and not file.startswith("_"):
                cog = f"{root.replace(os.sep, '.')}.{file[:-3]}"
                if cog not in bot.extensions:
                    try:
                        bot.load_extension(cog)
                        print(f"{cog}")
                    except Exception as e:
                        print(f"{cog}: {e}")

if __name__ == "__main__":
    init_db()
    load_cogs()
    bot.run(TOKEN)
