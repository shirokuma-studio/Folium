import discord
from discord.ext import commands
from discord import app_commands
import os
import yaml
import logging
import logging.handlers
import json
from dotenv import load_dotenv # load_dotenvをインポート

from database import Database

# .envファイルを読み込む
load_dotenv()

logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)

handler = logging.handlers.RotatingFileHandler(
    filename='logs/discord.log',
    encoding='utf-8',
    maxBytes=32 * 1024 * 1024,
    backupCount=5,
)
dt_fmt = '%Y-%m-%d %H:%M:%S'
formatter = logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', dt_fmt, style='{')
handler.setFormatter(formatter)
logger.addHandler(handler)

TOKEN = os.getenv('DISCORD_BOT_TOKEN')

with open('config.yaml', 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

# Function to override config with environment variables
def override_config_with_env(cfg, prefix=""):
    for key, value in cfg.items():
        env_var_name = f"{prefix}{key.upper()}"
        if isinstance(value, dict):
            override_config_with_env(value, f"{env_var_name}_")
        else:
            env_value = os.getenv(env_var_name)
            if env_value is not None:
                # Attempt to convert env_value to the original type
                if isinstance(value, int):
                    try:
                        cfg[key] = int(env_value)
                    except ValueError:
                        logger.warning(f"Environment variable {env_var_name} has invalid integer value: {env_value}")
                elif isinstance(value, bool):
                    cfg[key] = env_value.lower() in ('true', '1', 't', 'y', 'yes')
                else:
                    cfg[key] = env_value
                logger.info(f"Overridden config['{key}'] with environment variable {env_var_name}: {cfg[key]}")

# Apply environment variable overrides
override_config_with_env(config)

# 翻訳ファイルを読み込む
def load_translations():
    translations = {}
    for lang_dir in os.listdir('locales'):
        lang_path = os.path.join('locales', lang_dir)
        if os.path.isdir(lang_path):
            messages_file = os.path.join(lang_path, 'messages.json')
            if os.path.exists(messages_file):
                with open(messages_file, 'r', encoding='utf-8') as f:
                    translations[lang_dir] = json.load(f)
    return translations

TRANSLATIONS = load_translations()

def get_localized_name(key: str) -> dict[discord.Locale, str]:
    localizations = {}
    for lang_code, messages in TRANSLATIONS.items():
        if key in messages:
            try:
                locale = discord.Locale(lang_code.replace('-', '_').lower()) # en-US -> en_us
                localizations[locale] = messages[key]
            except ValueError:
                # DiscordのLocaleに存在しない言語コードはスキップ
                pass
    return localizations

class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True

        super().__init__(intents=intents) # command_prefixを削除
        self.tree = app_commands.CommandTree(self)
        self.initial_extensions = [
            "cogs.ping",
            "cogs.settings",
            "cogs.interactive_ui",
            "cogs.tasks",
        ]

        # データベース接続情報を取得し、Databaseインスタンスを作成
        db_config = config['database']
        if db_config['type'] == "sqlite":
            db_url = f"sqlite+aiosqlite:///{db_config['path']}"
        elif db_config['type'] == "postgresql":
            db_url = f"postgresql+asyncpg://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['dbname']}"
        else:
            raise ValueError("Unsupported database type in config.yaml")
        self.db = Database(db_url)

    async def setup_hook(self):
        await self.db.init_db()
        for extension in self.initial_extensions:
            await self.load_extension(extension)
        await self.tree.sync()
        logger.info(f"Logged in as {self.user} (ID: {self.user.id})")
        logger.info("------")

    async def on_ready(self):
        logger.info(f"Bot is ready. Latency: {self.latency * 1000:.2f}ms")

        @self.tree.error
        async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
            # エラーメッセージもローカライズ
            locale = interaction.locale if interaction.locale in TRANSLATIONS else discord.Locale.english_us
            messages = TRANSLATIONS.get(str(locale).replace('_', '-'), TRANSLATIONS['en-US'])

            if isinstance(error, app_commands.CommandNotFound):
                await interaction.response.send_message(messages["error_command_not_found"], ephemeral=True)
            elif isinstance(error, app_commands.MissingPermissions):
                await interaction.response.send_message(messages["error_missing_permissions"], ephemeral=True)
            elif isinstance(error, app_commands.BotMissingPermissions):
                await interaction.response.send_message(messages["error_bot_missing_permissions"], ephemeral=True)
            elif isinstance(error, app_commands.CommandOnCooldown):
                await interaction.response.send_message(messages["error_command_on_cooldown"].format(retry_after=error.retry_after), ephemeral=True)
            elif isinstance(error, app_commands.CheckFailure):
                await interaction.response.send_message(messages["error_unexpected"], ephemeral=True) # CheckFailureは汎用エラーメッセージ
            else:
                logger.error(f"予期せぬスラッシュコマンドエラーが発生しました: {error}")
                await interaction.response.send_message(messages["error_unexpected"], ephemeral=True)

if TOKEN is None:
    logger.error("Error: DISCORD_BOT_TOKEN environment variable not set.")
    logger.error("Please set the DISCORD_BOT_TOKEN environment variable before running the bot.")
else:
    bot = MyBot()
    bot.run(TOKEN)
