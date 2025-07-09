import discord
from discord.ext import commands
from discord import app_commands
import logging

from main import TRANSLATIONS, get_localized_name # TRANSLATIONSとget_localized_nameをインポート

logger = logging.getLogger('discord')

# ボタンのViewクラス
class ButtonView(discord.ui.View):
    def __init__(self, locale):
        super().__init__(timeout=180) # タイムアウトを設定
        self.messages = TRANSLATIONS.get(str(locale).replace('_', '-'), TRANSLATIONS['en-US'])
        self.add_item(discord.ui.Button(label=self.messages["button_label"], style=discord.ButtonStyle.primary, emoji="👋", custom_id="my_button"))

    @discord.ui.button(custom_id="my_button")
    async def button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(self.messages["button_response"], ephemeral=True)
        logger.info(f"Button clicked by {interaction.user.display_name}")

# セレクトメニューのViewクラス
class SelectView(discord.ui.View):
    def __init__(self, locale):
        super().__init__(timeout=180)
        self.messages = TRANSLATIONS.get(str(locale).replace('_', '-'), TRANSLATIONS['en-US'])

        options=[
            discord.SelectOption(label=self.messages["select_option_red"], value="red", emoji="🔴"),
            discord.SelectOption(label=self.messages["select_option_blue"], value="blue", emoji="🔵"),
            discord.SelectOption(label=self.messages["select_option_green"], value="green", emoji="🟢"),
        ]
        self.add_item(discord.ui.Select(placeholder=self.messages["select_placeholder"], min_values=1, max_values=1, options=options, custom_id="my_select"))

    @discord.ui.select(custom_id="my_select")
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        selected_color = select.values[0]
        # 選択された色をローカライズ
        localized_color = self.messages[f"select_option_{selected_color}"]
        await interaction.response.send_message(self.messages["select_response"].format(color=localized_color), ephemeral=True)
        logger.info(f"Select menu used by {interaction.user.display_name}: {selected_color}")

# モーダルのクラス
class MyModal(discord.ui.Modal):
    def __init__(self, locale):
        super().__init__(title=TRANSLATIONS['en-US']["modal_title"], custom_id="my_modal")
        self.messages = TRANSLATIONS.get(str(locale).replace('_', '-'), TRANSLATIONS['en-US'])

        self.name = discord.ui.TextInput(
            label=self.messages["modal_name_label"],
            placeholder=self.messages["modal_name_placeholder"],
            max_length=50,
            required=True,
            custom_id="name_input"
        )
        self.add_item(self.name)

        self.age = discord.ui.TextInput(
            label=self.messages["modal_age_label"],
            placeholder=self.messages["modal_age_placeholder"],
            max_length=3,
            required=False,
            custom_id="age_input"
        )
        self.add_item(self.age)

    async def on_submit(self, interaction: discord.Interaction):
        age_value = self.age.value if self.age.value else self.messages["modal_response_age_empty"]
        await interaction.response.send_message(self.messages["modal_response"].format(name=self.name.value, age=age_value), ephemeral=True)
        logger.info(f"Modal submitted by {interaction.user.display_name}: Name={self.name.value}, Age={self.age.value}")

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message(self.messages["modal_error"], ephemeral=True)
        logger.error(f"Modal submission error: {error}")

class InteractiveUI(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name=TRANSLATIONS['en-US']["button_test_command_name"],
        description=TRANSLATIONS['en-US']["button_test_command_description"],
        name_localizations=get_localized_name("button_test_command_name"),
        description_localizations=get_localized_name("button_test_command_description"),
    )
    async def button_test(self, interaction: discord.Interaction):
        locale = interaction.locale if interaction.locale in TRANSLATIONS else discord.Locale.english_us
        messages = TRANSLATIONS.get(str(locale).replace('_', '-'), TRANSLATIONS['en-US'])
        await interaction.response.send_message(messages["button_test_message"], view=ButtonView(interaction.locale))
        logger.info(f"Button test command used by {interaction.user.display_name}")

    @app_commands.command(
        name=TRANSLATIONS['en-US']["select_test_command_name"],
        description=TRANSLATIONS['en-US']["select_test_command_description"],
        name_localizations=get_localized_name("select_test_command_name"),
        description_localizations=get_localized_name("select_test_command_description"),
    )
    async def select_test(self, interaction: discord.Interaction):
        locale = interaction.locale if interaction.locale in TRANSLATIONS else discord.Locale.english_us
        messages = TRANSLATIONS.get(str(locale).replace('_', '-'), TRANSLATIONS['en-US'])
        await interaction.response.send_message(messages["select_test_message"], view=SelectView(interaction.locale))
        logger.info(f"Select test command used by {interaction.user.display_name}")

    @app_commands.command(
        name=TRANSLATIONS['en-US']["modal_test_command_name"],
        description=TRANSLATIONS['en-US']["modal_test_command_description"],
        name_localizations=get_localized_name("modal_test_command_name"),
        description_localizations=get_localized_name("modal_test_command_description"),
    )
    async def modal_test(self, interaction: discord.Interaction):
        await interaction.response.send_modal(MyModal(interaction.locale))
        logger.info(f"Modal test command used by {interaction.user.display_name}")

async def setup(bot):
    await bot.add_cog(InteractiveUI(bot))
