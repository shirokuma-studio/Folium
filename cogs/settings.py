import discord
from discord.ext import commands
from discord import app_commands
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models import Guild
import logging

from main import TRANSLATIONS, get_localized_name # TRANSLATIONSとget_localized_nameをインポート

logger = logging.getLogger('discord')

class Settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name=TRANSLATIONS['en-US']["setprefix_command_name"],
        description=TRANSLATIONS['en-US']["setprefix_command_description"],
        name_localizations=get_localized_name("setprefix_command_name"),
        description_localizations=get_localized_name("setprefix_command_description"),
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def set_prefix(self, interaction: discord.Interaction, prefix: str):
        locale = interaction.locale if interaction.locale in TRANSLATIONS else discord.Locale.english_us
        messages = TRANSLATIONS.get(str(locale).replace('_', '-'), TRANSLATIONS['en-US'])

        if not interaction.guild:
            await interaction.response.send_message(messages["setprefix_response_guild_only"], ephemeral=True)
            return

        async with self.bot.db.get_session() as session:
            stmt = select(Guild).where(Guild.guild_id == str(interaction.guild.id))
            result = await session.execute(stmt)
            guild_data = result.scalar_one_or_none()

            if guild_data:
                guild_data.prefix = prefix
                await interaction.response.send_message(messages["setprefix_response_success"].format(prefix=prefix), ephemeral=True)
            else:
                new_guild = Guild(guild_id=str(interaction.guild.id), prefix=prefix)
                session.add(new_guild)
                await interaction.response.send_message(messages["setprefix_response_success"].format(prefix=prefix), ephemeral=True)
            await session.commit()
            logger.info(f"Guild {interaction.guild.id} prefix set to {prefix}")

    @app_commands.command(
        name=TRANSLATIONS['en-US']["getprefix_command_name"],
        description=TRANSLATIONS['en-US']["getprefix_command_description"],
        name_localizations=get_localized_name("getprefix_command_name"),
        description_localizations=get_localized_name("getprefix_command_description"),
    )
    async def get_prefix(self, interaction: discord.Interaction):
        locale = interaction.locale if interaction.locale in TRANSLATIONS else discord.Locale.english_us
        messages = TRANSLATIONS.get(str(locale).replace('_', '-'), TRANSLATIONS['en-US'])

        if not interaction.guild:
            await interaction.response.send_message(messages["getprefix_response_guild_only"], ephemeral=True)
            return

        async with self.bot.db.get_session() as session:
            stmt = select(Guild).where(Guild.guild_id == str(interaction.guild.id))
            result = await session.execute(stmt)
            guild_data = result.scalar_one_or_none()

            if guild_data:
                await interaction.response.send_message(messages["getprefix_response_current"].format(prefix=guild_data.prefix), ephemeral=True)
            else:
                await interaction.response.send_message(messages["getprefix_response_no_custom"].format(default_prefix=self.bot.command_prefix), ephemeral=True)

async def setup(bot):
    await bot.add_cog(Settings(bot))
