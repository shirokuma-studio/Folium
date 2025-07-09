import discord
from discord.ext import commands
from discord import app_commands # app_commandsをインポート
import platform
import psutil
import datetime

class Ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = datetime.datetime.now()

    @app_commands.command(name="ping", description="ボットのレイテンシとシステム情報を表示します。") # スラッシュコマンドに変更
    async def ping(self, interaction: discord.Interaction): # interactionに変更
        # レイテンシの計算
        latency = self.bot.latency * 1000  # msに変換

        # 稼働時間の計算
        uptime = datetime.datetime.now() - self.start_time
        hours, remainder = divmod(int(uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        uptime_str = f"{hours}時間 {minutes}分 {seconds}秒"

        # メモリ使用量
        memory = psutil.virtual_memory()
        total_memory = memory.total / (1024**3)  # GB
        used_memory = memory.used / (1024**3)  # GB
        memory_percent = memory.percent

        # CPU使用率
        cpu_percent = psutil.cpu_percent(interval=1) # 1秒間のCPU使用率

        # PythonとPycordのバージョン
        python_version = platform.python_version()
        discord_py_version = discord.__version__

        # OS情報
        system_info = platform.system()
        release_info = platform.release()
        version_info = platform.version()

        embed = discord.Embed(
            title="🏓 Pong!",
            description="ボットの現在の状態です。",
            color=discord.Color.blue()
        )
        embed.add_field(name="🌐 レイテンシ", value=f"{latency:.2f}ms", inline=False)
        embed.add_field(name="⏰ 稼働時間", value=uptime_str, inline=False)
        embed.add_field(name="🧠 メモリ使用量", value=f"{used_memory:.2f}GB / {total_memory:.2f}GB ({memory_percent:.2f}%)", inline=False)
        embed.add_field(name="💻 CPU使用率", value=f"{cpu_percent:.2f}%", inline=False)
        embed.add_field(name="🐍 Pythonバージョン", value=python_version, inline=False)
        embed.add_field(name="📚 Pycordバージョン", value=discord_py_version, inline=False)
        embed.add_field(name="🖥️ OS情報", value=f"{system_info} {release_info} ({version_info})", inline=False)
        embed.set_footer(text=f"Requested by {interaction.user.display_name}", icon_url=interaction.user.avatar.url if interaction.user.avatar else interaction.user.default_avatar.url) # interaction.userに変更

        await interaction.response.send_message(embed=embed) # interaction.response.send_messageに変更

async def setup(bot):
    await bot.add_cog(Ping(bot))
