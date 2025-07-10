import discord
from discord.ext import commands
from discord import app_commands
import logging
import vertexai
from vertexai.preview.generative_models import GenerativeModel, Image
from PIL import Image as PILImage
import io

from main import TRANSLATIONS, get_localized_name # VERTEX_AI_PROJECT_IDとVERTEX_AI_LOCATIONをインポート

logger = logging.getLogger('discord')

class AICommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # vertexai.init()はGOOGLE_APPLICATION_CREDENTIALS環境変数から認証情報を自動的に読み取る
        try:
            vertexai.init()
            self.gemini_model = GenerativeModel("gemini-1.5-pro-preview-0514") # Gemini 2.5 Pro
            self.imagen_model = GenerativeModel("imagen-004") # Imagen 4
        except Exception as e:
            logger.error(f"Failed to initialize Vertex AI: {e}. AI commands will not function.")
            self.gemini_model = None
            self.imagen_model = None

    @app_commands.command(
        name=TRANSLATIONS['en-US']["ask_command_name"],
        description=TRANSLATIONS['en-US']["ask_command_description"],
        name_localizations=get_localized_name("ask_command_name"),
        description_localizations=get_localized_name("ask_command_description"),
    )
    @app_commands.describe(question=TRANSLATIONS['en-US']["ask_option_question_description"])
    async def ask(self, interaction: discord.Interaction, question: str):
        locale = interaction.locale if interaction.locale in TRANSLATIONS else discord.Locale.english_us
        messages = TRANSLATIONS.get(str(locale).replace('_', '-'), TRANSLATIONS['en-US'])

        if not self.gemini_model:
            await interaction.response.send_message(messages["ask_error_response"], ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True) # 処理に時間がかかるためdefer

        try:
            response = await self.gemini_model.generate_content_async(question)
            await interaction.followup.send(response.text)
            logger.info(f"Ask command used by {interaction.user.display_name}. Question: {question}")
        except Exception as e:
            logger.error(f"Error in ask command: {e}")
            await interaction.followup.send(messages["ask_error_response"], ephemeral=True)

    @app_commands.command(
        name=TRANSLATIONS['en-US']["imagine_command_name"],
        description=TRANSLATIONS['en-US']["imagine_command_description"],
        name_localizations=get_localized_name("imagine_command_name"),
        description_localizations=get_localized_name("imagine_command_description"),
    )
    @app_commands.describe(prompt=TRANSLATIONS['en-US']["imagine_option_prompt_description"])
    async def imagine(self, interaction: discord.Interaction, prompt: str):
        locale = interaction.locale if interaction.locale in TRANSLATIONS else discord.Locale.english_us
        messages = TRANSLATIONS.get(str(locale).replace('_', '-'), TRANSLATIONS['en-US'])

        if not self.imagen_model:
            await interaction.response.send_message(messages["imagine_error_response"], ephemeral=True)
            return

        await interaction.response.defer() # 画像生成に時間がかかるためdefer

        try:
            image_response = await self.imagen_model.generate_content_async(prompt)
            # 生成された画像をPIL Imageオブジェクトに変換
            pil_image = PILImage.open(io.BytesIO(image_response.images[0]._image_bytes))

            # Discordに送信するためにBytesIOに保存
            with io.BytesIO() as image_binary:
                pil_image.save(image_binary, 'PNG')
                image_binary.seek(0)
                file = discord.File(fp=image_binary, filename='generated_image.png')
                await interaction.followup.send(messages["imagine_success_response"].format(prompt=prompt), file=file)
            logger.info(f"Imagine command used by {interaction.user.display_name}. Prompt: {prompt}")
        except Exception as e:
            logger.error(f"Error in imagine command: {e}")
            await interaction.followup.send(messages["imagine_error_response"], ephemeral=True)

async def setup(bot):
    await bot.add_cog(AICommands(bot))
