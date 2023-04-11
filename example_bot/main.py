import asyncio
import os

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
import openai

bot_token = "5736824530:AAETLlte0-e1jeCfHzhTGderPfdLpnrhXyU"
openai.api_key = "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"
bot = Bot(token=bot_token)
dp = Dispatcher(bot)

# Dictionary to store conversation contexts
conversations = {}


@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.reply(
        "Привет! Я бот, который умеет отвечать на вопросы и давать советы. Просто напиши мне свой вопрос, и я постараюсь дать на него ответ."
    )


@dp.message_handler(content_types=["text"])
async def handle_text(message: types.Message):
    user_id = message.from_user.id

    # If the user has no existing conversation context, create one
    if user_id not in conversations:
        conversations[user_id] = {"prompt": "", "response": ""}

    # Add the user's message to the current conversation context
    conversations[user_id]["prompt"] += message.text + "\n"

    # Call the OpenAI model to get a response to the user's question
    response = openai.Completion.create(
        model="text-davinci-002",
        prompt=conversations[user_id]["prompt"],
        temperature=0.9,
        max_tokens=2000,
        top_p=1,
        frequency_penalty=0.0,
        presence_penalty=0.6,
        stop=["\n\n", "Human:", "AI:"],
    )

    # Add the model's response to the current conversation context
    conversations[user_id]["response"] = response.choices[0].text.strip()

    # Send the response to the user
    await message.answer(conversations[user_id]["response"])


@dp.message_handler(content_types=["photo"])
async def handle_photo(message: types.Message):
    # Get the object with information about the photo
    photo_obj = message.photo[-1]

    # Download the photo
    photo_path = await photo_obj.download()

    # Send a confirmation message with the photo
    await message.answer_photo(photo_obj.file_id, caption="Фотография получена.")

    # Remove the photo file
    os.remove(photo_path)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
