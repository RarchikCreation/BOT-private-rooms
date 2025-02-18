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
    message_content=True,
    voice_states=True
)

bot = commands.InteractionBot(intents=intents)

def init_db():
    if not os.path.exists("database.db"):
        open("database.db", "w").close()
    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
        cursor.execute('''
                  CREATE TABLE IF NOT EXISTS voice_channels (
                      id INTEGER PRIMARY KEY AUTOINCREMENT,
                      channel_id INTEGER UNIQUE,
                      owner_id INTEGER,
                      name TEXT,
                      created_at TEXT,
                      is_private INTEGER DEFAULT 0,
                      is_hidden INTEGER DEFAULT 0,
                      user_limit INTEGER DEFAULT 0,
                      last_active TEXT
                  )
              ''')

        cursor.execute("PRAGMA table_info(voice_channels);")
        existing_columns = [row[1] for row in cursor.fetchall()]

        if "last_active" not in existing_columns:
            cursor.execute("ALTER TABLE voice_channels ADD COLUMN last_active TEXT;")
        if "user_limit" not in existing_columns:
            cursor.execute("ALTER TABLE voice_channels ADD COLUMN user_limit INTEGER DEFAULT 0;")
        if "is_private" not in existing_columns:
            cursor.execute("ALTER TABLE voice_channels ADD COLUMN is_private INTEGER DEFAULT 0;")
        if "is_hidden" not in existing_columns:
            cursor.execute("ALTER TABLE voice_channels ADD COLUMN is_hidden INTEGER DEFAULT 0;")

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
