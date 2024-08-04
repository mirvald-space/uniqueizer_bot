import mimetypes
import os
import subprocess
import uuid

import cv2
from decouple import config
from telethon import TelegramClient, events
from telethon.tl.types import KeyboardButton, KeyboardButtonRow, ReplyKeyboardMarkup

API_ID = config("API_ID")
API_HASH = config("API_HASH")
BOT_TOKEN = config("BOT_TOKEN")

bot = TelegramClient("bot", API_ID, API_HASH).start(bot_token=BOT_TOKEN)

picture_path = "offer.png"

user_states = {}

START_MESSAGE = """
Привет, это бот уникализатор видео. 
Для выбора режима уникализации введи /menu,
"""


@bot.on(events.NewMessage(pattern="/start"))
async def start(event):
    await event.respond(START_MESSAGE)


@bot.on(events.NewMessage(pattern="/menu"))
async def menu(event):
    keyboard = ReplyKeyboardMarkup([
        KeyboardButtonRow([
            KeyboardButton(text="🔄 Изменить битрейт"),
            KeyboardButton(text="🪞 Отзеркалить")
        ]),
        KeyboardButtonRow([
            KeyboardButton(text="🖼 Наложить картинку"),
            KeyboardButton(text="🗑 Удалить метаданные")
        ]),
        KeyboardButtonRow([
            KeyboardButton(text="🌫 Наложить шум")
        ])
    ])
    await event.respond("Выбери действие:", buttons=keyboard)


@bot.on(events.NewMessage(pattern="(🔄 Изменить битрейт|🪞 Отзеркалить|🖼 Наложить картинку|🗑 Удалить метаданные|🌫 Наложить шум)"))
async def set_state(event):
    global user_states

    user_id = event.sender_id
    new_state = event.pattern_match.group(1)

    if "Изменить битрейт" in new_state:
        current_state = "change_bitrate"
    elif "Отзеркалить" in new_state:
        current_state = "mirror_horizontal"
    elif "Наложить картинку" in new_state:
        current_state = "add_a_picture"
    elif "Удалить метаданные" in new_state:
        current_state = "remove_metadata"
    elif "Наложить шум" in new_state:
        current_state = "add_noise"

    user_states[user_id] = current_state
    await event.respond(f"Выбрано действие: {new_state}\nТеперь отправь видео для уникализации.")


@bot.on(events.NewMessage)
async def handle_message(event):
    global user_states

    user_id = event.sender_id
    current_state = user_states.get(user_id)

    if current_state in ["change_bitrate", "mirror_horizontal", "add_a_picture", "remove_metadata", "add_noise"]:
        if event.media and hasattr(event.media, "document") and "video" in event.media.document.mime_type:
            video = await event.client.download_media(event.media.document)

            # Определяем формат входящего видео
            input_format = os.path.splitext(
                event.media.document.attributes[-1].file_name)[1]

            if current_state == "change_bitrate":
                await change_bitrate(event, video, input_format)
            elif current_state == "mirror_horizontal":
                await mirror_horizontal(event, video, input_format)
            elif current_state == "add_a_picture":
                await add_a_picture(event, video, input_format)
            elif current_state == "remove_metadata":
                await remove_metadata(event, video, input_format)
            elif current_state == "add_noise":
                await add_noise(event, video, input_format)


async def mirror_horizontal(event, video_path, input_format):
    unique_filename = f"{str(uuid.uuid4())}{input_format}"
    unique_video_path = os.path.join(unique_filename)

    ffmpeg_cmd = [
        "ffmpeg",
        "-i",
        video_path,
        "-vf",
        "hflip",
        "-map_metadata",
        "-1",
        "-c:a",
        "copy",
        unique_video_path,
    ]
    subprocess.call(ffmpeg_cmd)

    mime_type, _ = mimetypes.guess_type(unique_video_path)

    await event.client.send_file(event.chat_id, unique_video_path, mime_type=mime_type)

    os.remove(video_path)
    os.remove(unique_video_path)


async def add_a_picture(event, video_path, input_format):
    global picture_path

    unique_filename = f"{str(uuid.uuid4())}{input_format}"
    unique_video_path = os.path.join(unique_filename)

    ffmpeg_cmd = [
        "ffmpeg",
        "-i",
        video_path,
        "-i",
        picture_path,
        "-filter_complex",
        f"[0:v][1:v]overlay=W-w-10:H-h-10[v]",
        "-map",
        "[v]",
        "-map",
        "0:a",
        "-map_metadata",
        "-1",
        "-c:v",
        "libx264",
        "-c:a",
        "copy",
        unique_video_path,
    ]
    subprocess.call(ffmpeg_cmd)

    mime_type, _ = mimetypes.guess_type(unique_video_path)

    await event.client.send_file(event.chat_id, unique_video_path, mime_type=mime_type)

    os.remove(video_path)
    os.remove(unique_video_path)


async def change_bitrate(event, video_path, input_format):
    unique_filename = f"{str(uuid.uuid4())}{input_format}"
    unique_video_path = os.path.join(unique_filename)

    cap = cv2.VideoCapture(video_path)
    duration = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) / \
        int(cap.get(cv2.CAP_PROP_FPS))
    file_size = os.path.getsize(video_path)
    bitrate = (file_size * 8) / duration

    target_bitrate = int(bitrate * 0.7)

    ffmpeg_cmd = [
        "ffmpeg",
        "-i",
        video_path,
        "-b:v",
        str(target_bitrate),
        "-map_metadata",
        "-1",
        unique_video_path,
    ]
    subprocess.call(ffmpeg_cmd)

    mime_type, _ = mimetypes.guess_type(unique_video_path)

    await event.client.send_file(event.chat_id, unique_video_path, mime_type=mime_type)

    os.remove(video_path)
    os.remove(unique_video_path)


async def remove_metadata(event, video_path, input_format):
    unique_filename = f"{str(uuid.uuid4())}{input_format}"
    unique_video_path = os.path.join(unique_filename)

    ffmpeg_cmd = [
        "ffmpeg",
        "-i",
        video_path,
        "-map_metadata",
        "-1",
        "-c:v",
        "copy",
        "-c:a",
        "copy",
        unique_video_path,
    ]
    subprocess.call(ffmpeg_cmd)

    mime_type, _ = mimetypes.guess_type(unique_video_path)

    await event.client.send_file(event.chat_id, unique_video_path, mime_type=mime_type)

    os.remove(video_path)
    os.remove(unique_video_path)


async def add_noise(event, video_path, input_format):
    unique_filename = f"{str(uuid.uuid4())}{input_format}"
    unique_video_path = os.path.join(unique_filename)

    ffmpeg_cmd = [
        "ffmpeg",
        "-i",
        video_path,
        "-vf",
        "noise=alls=10:allf=t+u",
        "-c:a",
        "copy",
        "-map_metadata",
        "-1",
        unique_video_path,
    ]
    subprocess.call(ffmpeg_cmd)

    mime_type, _ = mimetypes.guess_type(unique_video_path)

    await event.client.send_file(event.chat_id, unique_video_path, mime_type=mime_type)

    os.remove(video_path)
    os.remove(unique_video_path)


def main():
    bot.run_until_disconnected()


if __name__ == "__main__":
    main()
