import disnake
from disnake.ext import commands
import sqlite3
from config import control_role_id


class DeleteRoomCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(description="Удалить голосовую комнату")
    async def delete_room(self, inter: disnake.ApplicationCommandInteraction, channel: disnake.VoiceChannel):
        await inter.response.defer(ephemeral=True)

        with sqlite3.connect("database.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT owner_id FROM voice_channels WHERE channel_id = ?", (channel.id,))
            row = cursor.fetchone()

            if not row:
                await inter.edit_original_response("Этот канал не зарегистрирован как приватная комната.")
                return

            is_owner = row[0] == inter.author.id
            is_admin = any(role.id in control_role_id for role in inter.author.roles)

            if not (is_owner or is_admin):
                await inter.edit_original_response("Вы не владелец этой комнаты и не являетесь администратором.")
                return

            cursor.execute("DELETE FROM voice_channels WHERE channel_id = ?", (channel.id,))
            conn.commit()

        await channel.delete()
        await inter.edit_original_response(f"Комната {channel.name} удалена.")


def setup(bot):
    bot.add_cog(DeleteRoomCog(bot))
