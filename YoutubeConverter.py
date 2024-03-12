import os
import threading
from tkinter import Tk, ttk, StringVar, Label
from PIL import Image, ImageTk
from pytube import YouTube
import requests
from io import BytesIO
from moviepy.editor import *


def sanitize_filename(title):
    """Sanitizes a string to be safe for use as a filename."""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        title = title.replace(char, '_')
    return title[:200]  # Trim filename length if necessary

def on_download_complete(file_path):
    """Updates the UI when the download is complete."""
    status_label.config(text=f"Download Complete. Check the folder: {file_path}")
    url_entry.delete(0, 'end')  # Clear the URL entry field
    download_button.config(state="normal")  # Re-enable the download button

def update_thumbnail(url):
    """Fetches and updates the thumbnail in the UI."""
    def fetch_and_update():
        try:
            response = requests.get(url)
            img_data = response.content
            img = Image.open(BytesIO(img_data))
            img = img.resize((200, 200), Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            thumbnail_label.config(image=photo)
            thumbnail_label.image = photo  # Keep a reference
            if not thumbnail_label.winfo_ismapped():
                thumbnail_label.pack(padx=20, pady=10, before=video_title_label)
        except Exception as e:
            print(f"Failed to update thumbnail: {e}")

    app.after(0, fetch_and_update)


def download():
    """Handles the downloading and conversion of audio streams to MP3."""
    url = url_entry.get()
    download_button.config(state="disabled")  # Disable the button while downloading

    def threaded_download():
        try:
            youtube = YouTube(url)
            video_title.set(youtube.title)  # Set the video title in the UI
            status_label.config(text="Preparing download...")
            update_thumbnail(youtube.thumbnail_url)
            output_path = os.path.join(os.getcwd(), "downloaded_audios")
            os.makedirs(output_path, exist_ok=True)

            status_label.config(text=f"Downloading audio for {youtube.title}...")
            audio_stream = youtube.streams.get_audio_only()
            audio_path = audio_stream.download(output_path=output_path)
            final_title = sanitize_filename(youtube.title)
            final_path = os.path.join(output_path, f"{final_title}.mp3")

            # Convert the downloaded file to MP3
            status_label.config(text=f"Converting to MP3: {final_title}...")
            audio_clip = AudioFileClip(audio_path)
            audio_clip.write_audiofile(final_path)
            audio_clip.close()

            # Optionally, remove the original download if it's not in MP3 format
            if not audio_path.endswith(".mp3"):
                os.remove(audio_path)

            on_download_complete(final_path)

        except Exception as e:
            status_label.config(text=f"Error: {e}")
            download_button.config(state="normal")

    threading.Thread(target=threaded_download).start()


app = Tk()
app.title("YouTube Audio Downloader")

style = ttk.Style(app)
style.theme_use('clam')

# Font, color configurations, and padding
style.configure('TLabel', background='seashell', foreground='#061139', font=('Helvetica', 12), padding=20)
style.configure('TEntry', font=('Helvetica', 12), padding=10)
style.configure('TButton', font=('Helvetica', 12), padding=20, borderwidth=0)

app.configure(bg='seashell')

# UI layout
ttk.Label(app, text="YouTube URL:", style='TLabel').pack(padx=20, pady=10)
url_entry = ttk.Entry(app, font=('Helvetica', 12), width=50)
url_entry.pack(padx=20, pady=10)

video_title = StringVar(app, value="")  # Initialize the video title variable
video_title_label = ttk.Label(app, textvariable=video_title, style='TLabel')  # Label to display the video title
video_title_label.pack(padx=20, pady=5)

thumbnail_label = Label(app)  # Initialize the thumbnail label but don't pack it yet

download_button = ttk.Button(app, text="Download Audio", command=download, style='TButton')
download_button.pack(padx=20, pady=20)

status_label = ttk.Label(app, text="", style='TLabel')
status_label.pack(padx=20, pady=10)

app.mainloop()
