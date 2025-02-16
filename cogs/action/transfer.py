import disnake
from disnake.ext import commands
import sqlite3


class TransferOwnershipCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(description="Передать владельца голосовой комнаты")
    async def transfer_room(self, inter: disnake.ApplicationCommandInteraction, channel: disnake.VoiceChannel,
                            member: disnake.Member):
        await inter.response.defer(ephemeral=True)

        with sqlite3.connect("database.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT owner_id FROM voice_channels WHERE channel_id = ?", (channel.id,))
            row = cursor.fetchone()

            if not row or row[0] != inter.author.id:
                await inter.edit_original_response("Вы не являетесь владельцем этой комнаты.")
                return

            cursor.execute("UPDATE voice_channels SET owner_id = ? WHERE channel_id = ?", (member.id, channel.id))
            conn.commit()

            await inter.edit_original_response(f"Теперь {member.mention} владелец комнаты {channel.name}.")


def setup(bot):
    bot.add_cog(TransferOwnershipCog(bot))
