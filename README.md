# Telegram Video Uniqueizer Bot

This Telegram bot is designed to make videos unique using various processing methods.

## Functionality

The bot provides the following video processing functions:

1. 🔄 Change bitrate: reduces the video bitrate by 30%.
2. 🪞 Mirror horizontally: flips the video horizontally.
3. 🖼 Add picture: overlays a selected image on the video.
4. 🗑 Remove metadata: removes metadata from the video.
5. 🌫 Add noise: adds random noise to the video.

## Requirements

- Python 3.7+
- FFmpeg
- OpenCV
- Telethon
- python-decouple

## Installation

1. Clone the repository:
2. Install dependencies:

- pip install -r requirements.txt

3. Install FFmpeg if it's not already installed on your system.

4. Create a `.env` file in the project root directory and add the following variables:

- API_ID=your_api_id
- API_HASH=your_api_hash
- BOT_TOKEN=your_bot_token

## Running the Bot

1. Ensure you have a `best_offer.png` file in the same directory as the script (used for the picture overlay function).

2. Run the bot:

- python bot.py

## Usage

1. Start a chat with the bot on Telegram and send the `/start` command.
2. Use the `/menu` command to bring up the menu with action selection buttons.
3. Choose the desired action by pressing the corresponding button.
4. Send a video to the bot for processing.
5. The bot will process the video and send the result back.

## Code Overview

### Main Variables

- `API_ID`: Telegram API ID
- `API_HASH`: Telegram API Hash
- `BOT_TOKEN`: Telegram Bot Token
- `picture_path`: Path to the overlay image (default: `"best_offer.png"`)
- `user_states`: Dictionary to store user states

### Key Functions

- `start(event)`: Handles the `/start` command
- `menu(event)`: Displays the menu with action buttons
- `set_state(event)`: Sets the user's chosen action
- `handle_message(event)`: Processes incoming messages and videos
- `mirror_horizontal(event, video_path, input_format)`: Flips the video horizontally
- `add_a_picture(event, video_path, input_format)`: Adds an overlay image to the video
- `change_bitrate(event, video_path, input_format)`: Reduces the video bitrate
- `remove_metadata(event, video_path, input_format)`: Removes metadata from the video
- `add_noise(event, video_path, input_format)`: Adds noise to the video

## Notes

- The bot preserves the input video format during processing.
- Temporary files are deleted after processing.
- Ensure the bot has sufficient permissions to send files in the chat.

## Support

If you encounter any issues or have suggestions for improvements, please create an issue in the project repository.
