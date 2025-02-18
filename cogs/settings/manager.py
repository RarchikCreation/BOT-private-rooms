import disnake
from disnake.ext import commands
from disnake.ui import Button, View, Select, TextInput
import sqlite3

class RoomManagementCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conn = sqlite3.connect("database.db")
        self.cursor = self.conn.cursor()
        self.path = "assets/setting.png"

    def get_room(self, room_id):
        self.cursor.execute("SELECT * FROM voice_channels WHERE channel_id = ?", (room_id,))
        return self.cursor.fetchone()

    def get_user_rooms(self, user_id):
        self.cursor.execute("SELECT * FROM voice_channels WHERE owner_id = ?", (user_id,))
        return self.cursor.fetchall()

    def update_room(self, room_id, **kwargs):
        set_clause = ", ".join([f"{key} = ?" for key in kwargs.keys()])
        values = list(kwargs.values())
        values.append(room_id)
        self.cursor.execute(f"UPDATE voice_channels SET {set_clause} WHERE channel_id = ?", values)
        self.conn.commit()

    @commands.slash_command(description="Управление вашей приватной комнатой")
    async def edit_room(self, inter: disnake.ApplicationCommandInteraction):
        await inter.response.defer(ephemeral=True)

        user_id = str(inter.author.id)
        user_rooms = self.get_user_rooms(user_id)

        if not user_rooms:
            await inter.followup.send("У вас нет приватных комнат.", ephemeral=True)
            return

        room_select = Select(
            placeholder="Выберите комнату",
            custom_id="select_room",
            options=[
                disnake.SelectOption(
                    label=room[3],
                    value=str(room[1]))
                for room in user_rooms
            ]
        )

        view = View()
        view.add_item(room_select)

        embed_edit = disnake.Embed(
            description=f"Выберите комнату для управления:",
            color=disnake.Color.blurple()
        )

        file = disnake.File(self.path, filename="setting.png")
        embed_edit.set_author(name="Управление комнатой", icon_url=f"attachment://setting.png")

        await inter.followup.send(embed=embed_edit, view=view, ephemeral=True, file=file)

    @commands.Cog.listener()
    async def on_dropdown(self, inter: disnake.MessageInteraction):
        if inter.component.custom_id == "select_room":
            room_id = inter.values[0]
            room = self.get_room(room_id)
            access_button = Button(
                emoji="<:access:1334968385242533922>",
                style=disnake.ButtonStyle.secondary,
                custom_id=f"access_{room_id}"
            )
            limit_button = Button(
                emoji="<:limited:1334968388300177480>",
                style=disnake.ButtonStyle.secondary,
                custom_id=f"limit_{room_id}"
            )
            rename_button = Button(
                emoji="<:rename:1334968393152856074>",
                style=disnake.ButtonStyle.secondary,
                custom_id=f"rename_{room_id}"
            )
            kick_button = Button(
                emoji="<:kick:1334968386731380868>",
                style=disnake.ButtonStyle.secondary,
                custom_id=f"kick_{room_id}"
            )
            voice_button = Button(
                emoji="<:voice:1334968396181274634>",
                style=disnake.ButtonStyle.secondary,
                custom_id=f"voice_{room_id}"
            )

            view = View()
            view.add_item(access_button)
            view.add_item(limit_button)
            view.add_item(rename_button)
            view.add_item(kick_button)
            view.add_item(voice_button)

            embed = disnake.Embed(
                description=f"Измените конфигурацию вашей комнаты с помощью панели управления.\n\n"
                           f"<:access:1334968385242533922> — ограничить/выдать доступ к комнате\n"
                           f"<:limited:1334968388300177480> — задать новый лимит участников\n"
                           f"<:rename:1334968393152856074> — изменить название комнаты\n"
                           f"<:kick:1334968386731380868> — выгнать участника из комнаты\n"
                           f"<:voice:1334968396181274634> — ограничить/выдать право говорить",
                color=disnake.Color.blurple()
            )
            file = disnake.File(self.path, filename="setting.png")
            embed.set_author(name=f"Управление комнатой {room[3]}", icon_url=f"attachment://setting.png")

            await inter.response.send_message(embed=embed, view=view, ephemeral=True, file=file)

    @commands.Cog.listener()
    async def on_button_click(self, inter: disnake.MessageInteraction):
        custom_id = inter.component.custom_id
        match custom_id.split("_"):
            case ["rename", room_id]:
                modal = disnake.ui.Modal(
                    title="Изменение названия комнаты",
                    custom_id=f"rename_room_modal_{room_id}",
                    components=[
                        TextInput(
                            label="Новое название",
                            custom_id="new_name",
                            placeholder="Введите новое название",
                            max_length=50
                        )
                    ]
                )
                await inter.response.send_modal(modal)

            case ["limit", room_id]:
                modal = disnake.ui.Modal(
                    title="Установка лимита пользователей",
                    custom_id=f"set_limit_modal_{room_id}",
                    components=[
                        TextInput(
                            label="Новый лимит",
                            custom_id="new_limit",
                            placeholder="Введите новый лимит (от 1 до 99)",
                            max_length=2
                        )
                    ]
                )
                await inter.response.send_modal(modal)

            case ["access", room_id]:
                modal = disnake.ui.Modal(
                    title="Ограничить/открыть доступ к комнате",
                    custom_id=f"access_modal_{room_id}",
                    components=[
                        TextInput(
                            label="ID пользователя",
                            custom_id="user_id",
                            placeholder="Введите ID пользователя",
                            max_length=20
                        )
                    ]
                )
                await inter.response.send_modal(modal)

            case ["kick", room_id]:
                modal = disnake.ui.Modal(
                    title="Выгнать участника из комнаты",
                    custom_id=f"kick_modal_{room_id}",
                    components=[
                        TextInput(
                            label="ID пользователя",
                            custom_id="user_id",
                            placeholder="Введите ID пользователя",
                            max_length=20
                        )
                    ]
                )
                await inter.response.send_modal(modal)

            case ["voice", room_id]:
                modal = disnake.ui.Modal(
                    title="Управление микрофоном",
                    custom_id=f"voice_modal_{room_id}",
                    components=[
                        TextInput(
                            label="ID пользователя",
                            custom_id="user_id",
                            placeholder="Введите ID пользователя",
                            max_length=20
                        )
                    ]
                )
                await inter.response.send_modal(modal)

    @commands.Cog.listener()
    async def on_modal_submit(self, inter: disnake.ModalInteraction):
        match inter.custom_id.split("_"):
            case ["rename", "room", "modal", room_id]:
                new_name = inter.text_values["new_name"]

                self.update_room(room_id, name=new_name)

                voice_channel = inter.guild.get_channel(int(room_id))
                if voice_channel:
                    await voice_channel.edit(name=new_name)

                await inter.response.send_message(f"Название комнаты изменено на **{new_name}**.", ephemeral=True)

            case ["set", "limit", "modal", room_id]:
                new_limit = int(inter.text_values["new_limit"])

                if new_limit < 1 or new_limit > 99:
                    await inter.response.send_message("Лимит пользователей должен быть от 1 до 99.", ephemeral=True)
                    return

                self.update_room(room_id, user_limit=new_limit)

                voice_channel = inter.guild.get_channel(int(room_id))
                if voice_channel:
                    await voice_channel.edit(user_limit=new_limit)

                await inter.response.send_message(f"Лимит пользователей изменен на **{new_limit}**.", ephemeral=True)

            case ["access", "modal", room_id]:
                user_id = inter.text_values["user_id"]

                voice_channel = inter.guild.get_channel(int(room_id))
                if voice_channel:
                    member = inter.guild.get_member(int(user_id))
                    if member:
                        overwrites = voice_channel.overwrites_for(member)
                        if overwrites.connect is False:
                            await voice_channel.set_permissions(member, connect=True, speak=True)
                            await inter.response.send_message(f"Доступ к комнате открыт для <@{user_id}>.",
                                                              ephemeral=True)
                        else:
                            await voice_channel.set_permissions(member, connect=False, speak=False)
                            await inter.response.send_message(f"Доступ к комнате ограничен для <@{user_id}>.",
                                                              ephemeral=True)

            case ["kick", "modal", room_id]:
                user_id = inter.text_values["user_id"]
                voice_channel = inter.guild.get_channel(int(room_id))

                if voice_channel:
                    member = inter.guild.get_member(int(user_id))

                    if member:
                        if member.voice and member.voice.channel == voice_channel:
                            await member.move_to(None)
                            await inter.response.send_message(f"Пользователь <@{user_id}> выгнан из комнаты.",
                                                              ephemeral=True)
                        else:
                            await inter.response.send_message("Пользователь не находится в этой комнате.",
                                                              ephemeral=True)
                    else:
                        await inter.response.send_message("Пользователь не найден.", ephemeral=True)
                else:
                    await inter.response.send_message("Голосовой канал не найден.", ephemeral=True)

            case ["voice", "modal", room_id]:
                user_id = inter.text_values["user_id"]

                voice_channel = inter.guild.get_channel(int(room_id))
                if voice_channel:
                    member = inter.guild.get_member(int(user_id))
                    if member:
                        overwrites = voice_channel.overwrites_for(member)
                        if overwrites.speak is False:
                            await voice_channel.set_permissions(member, speak=True)
                            await inter.response.send_message(f"Микрофон включен для <@{user_id}>.", ephemeral=True)
                        else:
                            await voice_channel.set_permissions(member, speak=False)
                            await inter.response.send_message(f"Микрофон выключен для <@{user_id}>.", ephemeral=True)
def setup(bot):
    bot.add_cog(RoomManagementCog(bot))