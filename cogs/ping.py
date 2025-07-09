import discord
from discord.ext import commands
from discord import app_commands
import platform
import psutil
import datetime
import logging

from main import TRANSLATIONS, get_localized_name # TRANSLATIONSとget_localized_nameをインポート

logger = logging.getLogger('discord')

class Ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = datetime.datetime.now()

    @app_commands.command(
        name=TRANSLATIONS['en-US']["ping_command_name"],
        description=TRANSLATIONS['en-US']["ping_command_description"],
        name_localizations=get_localized_name("ping_command_name"),
        description_localizations=get_localized_name("ping_command_description"),
    )
    async def ping(self, interaction: discord.Interaction):
        locale = interaction.locale if interaction.locale in TRANSLATIONS else discord.Locale.english_us
        messages = TRANSLATIONS.get(str(locale).replace('_', '-'), TRANSLATIONS['en-US'])

        latency = self.bot.latency * 1000

        uptime = datetime.datetime.now() - self.start_time
        hours, remainder = divmod(int(uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        uptime_str = f"{hours}時間 {minutes}分 {seconds}秒"

        memory = psutil.virtual_memory()
        total_memory = memory.total / (1024**3)
        used_memory = memory.used / (1024**3)
        memory_percent = memory.percent

        cpu_percent = psutil.cpu_percent(interval=1)

        python_version = platform.python_version()
        discord_py_version = discord.__version__

        system_info = platform.system()
        release_info = platform.release()
        version_info = platform.version()

        embed = discord.Embed(
            title=messages["ping_embed_title"],
            description=messages["ping_embed_description"],
            color=discord.Color.blue()
        )
        embed.add_field(name=messages["ping_field_latency"], value=f"{latency:.2f}ms", inline=False)
        embed.add_field(name=messages["ping_field_uptime"], value=uptime_str, inline=False)
        embed.add_field(name=messages["ping_field_memory_usage"], value=f"{used_memory:.2f}GB / {total_memory:.2f}GB ({memory_percent:.2f}%)", inline=False)
        embed.add_field(name=messages["ping_field_cpu_usage"], value=f"{cpu_percent:.2f}%", inline=False)
        embed.add_field(name=messages["ping_field_python_version"], value=python_version, inline=False)
        embed.add_field(name=messages["ping_field_pycord_version"], value=discord_py_version, inline=False)
        embed.add_field(name=messages["ping_field_os_info"], value=f"{system_info} {release_info} ({version_info})", inline=False)
        embed.set_footer(text=messages["ping_footer_requested_by"].format(user_display_name=interaction.user.display_name), icon_url=interaction.user.avatar.url if interaction.user.avatar else interaction.user.default_avatar.url)

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Ping(bot))
