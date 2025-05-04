from typing import Final
import os
import yt_dlp
import discord
import re
import subprocess
import uuid
from dotenv import load_dotenv
from discord import Intents, Client, Message
from Response import get_response

load_dotenv()
TOKEN: Final[str] = os.getenv("DISCORD_TOKEN")
print(TOKEN)

intents: Intents = Intents.default()
intents.message_content = True 
client: Client = Client(intents=intents)


# reencodes the video to h.264 in order for it to be viweable on discord
def reencode(input_file: str, output_file: str):
    cmd = [
        'ffmpeg',
        '-y',                      # Overwrite output without asking
        '-i', input_file,          # Input file
        '-c:v', 'libx264',         # Encode video to H.264
        '-c:a', 'aac',             # Encode audio to AAC
        '-b:v', '2M',           # Set video bitrate to 5000 kbps
        '-b:a', '128k',            # Set audio bitrate to 192 kbps
        '-movflags', '+faststart', # Important for web/discord preview
        output_file                # Output file with .mp4
    ]
    subprocess.run(cmd, check=True)

async def send_message(message: Message, user_message: str) -> None:
    if not user_message:
        print('No message to send')
    if is_private := user_message[0] == '?':
        user_message = user_message[1:]

    try:
        response: str = get_response(user_message)
        await message.author.send(response) if is_private else await message.channel.send(response)
    except Exception as e:
        print(f"Error: {e}")


# function for downloading videos
async def get_video(message: Message, url: str):
    try:
        # Generate unique filenames for each download
        unique_id = str(uuid.uuid4())
        file_path = f"downloaded_video_{unique_id}.%(ext)s"
        final_path = f"final_video_{unique_id}.mp4"

        # yt_dlp options with unique output template
        ydl_opts = {
            'outtmpl': file_path,  # Use unique filename
            'format': 'bestvideo+bestaudio/best',
            'merge_output_format': 'mp4',
        }

        # Download the video
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            downloaded_file_path = ydl.prepare_filename(info)

        # Rename to .mp4 if needed
        if not downloaded_file_path.endswith(".mp4"):
            renamed_file_path = os.path.splitext(downloaded_file_path)[0] + ".mp4"
            os.rename(downloaded_file_path, renamed_file_path)
        else:
            renamed_file_path = downloaded_file_path

        # Re-encode the video
        reencode(renamed_file_path, final_path)

        # Send the final video to the Discord channel
        await message.channel.send(file=discord.File(final_path))

        # Clean up temporary files
        os.remove(renamed_file_path)
        os.remove(final_path)

    except Exception as e:
        # Handle exceptions and notify the user
        await message.channel.send("❌ Failed to process the video.")
        print(f"Error processing video: {e}")


# event for getting the links 
@client.event
async def on_message(message:Message) -> None:
    if message.author == client.user:
        return
    user_message = message.content 

    url_patterns = {
        'facebook': r'(https?://(?:www\.)?(facebook\.com/reel|fb\.reel)/[^\s]+)',
        'instagram': r'(https?://(?:www\.)?(instagram\.com/reels|instagram\.com/reel)/[^\s]+)',
        'twitter': r'(https?://(?:www\.)?(x\.com)/[^\s]+)',
        'youtube': r'(https?://(?:www\.)?(youtube\.com/shorts)/[^\s]+)',
        'tiktok': r'(https?://(?:www\.)?(tiktok\.com)/[^\s]+)'
    }

    for platform, pattern in url_patterns.items():
        match = re.search(pattern, user_message)
        if match:
            await get_video(message, match.group(1))
            await message.delete()  # Delete the original message
            return
        
    await send_message(message, user_message)


def main() -> None:
    client.run(token=TOKEN)

if __name__ == '__main__':
    main()


# @client.event
# async def on_message(message: Message) -> None:
#     if message.author == client.user:
#         return
    
#     user_message = message.content
#     fb_url_match  = re.search(r'(https?://(?:www\.)?(facebook\.com/reel|fb\.reel)/[^\s]+)', user_message)
#     insta_url_match  = re.search(r'(https?://(?:www\.)?(instagram\.com/reels)/[^\s]+)', user_message)
#     twitter_url_match  = re.search(r'(https?://(?:www\.)?(x\.com)/[^\s]+)', user_message)
#     youtube_url_match  = re.search(r'(https?://(?:www\.)?(youtube\.com/shorts)/[^\s]+)', user_message)
#     tiktok_url_match  = re.search(r'(https?://(?:www\.)?(tiktok\.com)/[^\s]+)', user_message)



#     if fb_url_match:
#         await get_video(message, fb_url_match.group(1))
#         return
    
#     if insta_url_match:
#         await get_video(message, insta_url_match.group(1))
#         return
    
#     if twitter_url_match:
#         await get_video(message, twitter_url_match.group(1))
#         return
    
#     if youtube_url_match:
#         await get_video(message, youtube_url_match.group(1))
#         return
    
#     if tiktok_url_match:
#         await get_video(message, tiktok_url_match.group(1))
#         return

#     await send_message(message, user_message)