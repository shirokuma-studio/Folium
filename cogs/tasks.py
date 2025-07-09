import discord
from discord.ext import commands, tasks
import logging

logger = logging.getLogger('discord')

class ScheduledTasks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.my_periodic_task.start() # タスクを開始

    def cog_unload(self):
        self.my_periodic_task.cancel() # Cogがアンロードされたときにタスクをキャンセル

    @tasks.loop(seconds=60) # 60秒ごとに実行
    async def my_periodic_task(self):
        # ボットが準備完了状態になるまで待機
        await self.bot.wait_until_ready()
        logger.info("定期タスクが実行されました！")
        # ここに定期的に実行したい処理を記述

    @my_periodic_task.before_loop
    async def before_my_periodic_task(self):
        logger.info("定期タスクの開始を待機中...")

async def setup(bot):
    await bot.add_cog(ScheduledTasks(bot))
