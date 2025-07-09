import discord
from discord.ext import commands
import os

# 環境変数からトークンを読み込む
TOKEN = os.getenv('DISCORD_BOT_TOKEN')

class MyBot(commands.Bot):
    def __init__(self):
        # 必要なインテントを有効にする
        intents = discord.Intents.default()
        intents.message_content = True # メッセージ内容を読み取るために必要
        intents.guilds = True # ギルド情報を取得するために必要

        super().__init__(command_prefix='!', intents=intents)
        self.initial_extensions = [
            "cogs.ping",
        ]

    async def setup_hook(self):
        # ここでCogをロードする
        for extension in self.initial_extensions:
            await self.load_extension(extension)
        print(f"Logged in as {self.user} (ID: {self.user.id})")
        print("------")

    async def on_ready(self):
        print(f"Bot is ready. Latency: {self.latency * 1000:.2f}ms")

if TOKEN is None:
    print("Error: DISCORD_BOT_TOKEN environment variable not set.")
    print("Please set the DISCORD_BOT_TOKEN environment variable before running the bot.")
else:
    bot = MyBot()
    bot.run(TOKEN)
