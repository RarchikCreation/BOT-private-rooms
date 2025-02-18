import disnake
from disnake.ext import commands
import sqlite3
import datetime
from config import control_role_id, category_id


class CreateCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(description="Создать приватную голосовую комнату")
    async def create_room(self, inter: disnake.ApplicationCommandInteraction):
        await inter.response.defer(ephemeral=True)

        if not any(role.id in control_role_id for role in inter.author.roles):
            await inter.response.send_message("У вас нет доступа к этой команде.", ephemeral=True)
            return

        category = inter.guild.get_channel(category_id)
        if not category or not isinstance(category, disnake.CategoryChannel):
            return

        channel_name = f"Комната {inter.author.display_name}"
        voice_channel = await category.create_voice_channel(name=channel_name)

        created_at = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        with sqlite3.connect("database.db") as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO voice_channels (channel_id, owner_id, name, created_at) VALUES (?, ?, ?, ?)",
                           (voice_channel.id, inter.author.id, channel_name, created_at))
            conn.commit()

        await inter.response.send_message(f"Голосовой канал {channel_name} создан!", ephemeral=True)


def setup(bot):
    bot.add_cog(CreateCog(bot))
