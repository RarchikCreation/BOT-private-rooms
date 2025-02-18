import disnake
from disnake.ext import commands, tasks
import sqlite3
import datetime

class AutoDeleteRoomsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_inactive_rooms.start()

    def cog_unload(self):
        self.check_inactive_rooms.cancel()

    @tasks.loop(hours=1)
    async def check_inactive_rooms(self):
        now = datetime.datetime.utcnow()
        threshold = now - datetime.timedelta(days=7)
        threshold_str = threshold.strftime("%Y-%m-%d %H:%M:%S")

        with sqlite3.connect("database.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT channel_id FROM voice_channels WHERE last_active < ?", (threshold_str,))
            channels_to_delete = cursor.fetchall()

            for (channel_id,) in channels_to_delete:
                try:
                    channel = await self.bot.fetch_channel(channel_id)
                    if channel:
                        await channel.delete()
                        cursor.execute("DELETE FROM voice_channels WHERE channel_id = ?", (channel_id,))
                        print(f"Канал {channel_id} удален за неактивность.")
                except Exception as e:
                    print(f"{channel_id}: {e}")

            conn.commit()

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if after.channel and (not before.channel or before.channel.id != after.channel.id):
            with sqlite3.connect("database.db") as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT channel_id FROM voice_channels WHERE channel_id = ?", (after.channel.id,))
                row = cursor.fetchone()

                if row:
                    print(f"{member.display_name} зашел в голосовой канал {after.channel.name}, таймер сброшен.")
                    cursor.execute("UPDATE voice_channels SET last_active = ? WHERE channel_id = ?",
                                   (datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"), after.channel.id))
                    conn.commit()


def setup(bot):
    bot.add_cog(AutoDeleteRoomsCog(bot))
