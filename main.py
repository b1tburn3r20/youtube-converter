import os
import threading
from tkinter import Tk, ttk, StringVar
from pytube import YouTube
from moviepy.editor import VideoFileClip, AudioFileClip

def sanitize_filename(title):
    """Sanitizes a string to be safe for use as a filename."""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        title = title.replace(char, '_')
    return title[:200]  # Trim filename length if necessary

def on_download_complete(file_path):
    """Updates the UI when the download and merge are complete."""
    status_label.config(text=f"Download Complete. Check the folder: {file_path}")
    url_entry.delete(0, 'end')  # Clear the URL entry field
    download_button.config(state="normal")  # Re-enable the download button

def merge_video_audio(video_path, audio_path, output_path, title):
    """Merges video and audio into a single MP4 file using moviepy."""
    video_clip = VideoFileClip(video_path)
    audio_clip = AudioFileClip(audio_path)
    final_clip = video_clip.set_audio(audio_clip)
    status_label.config(text=f"Merging video and audio for {title}...")
    final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")
    video_clip.close()
    audio_clip.close()
    os.remove(video_path)  # Remove the original video file
    os.remove(audio_path)  # Remove the original audio file
    on_download_complete(output_path)

def merge_audio(audio_path, output_path, title):
    """Merges audio into a single MP3 file using moviepy."""
    audio_clip = AudioFileClip(audio_path)
    status_label.config(text=f"Merging audio for {title}...")
    audio_clip.write_audiofile(output_path, codec="mp3")
    audio_clip.close()
    os.remove(audio_path)  # Remove the original audio file
    on_download_complete(output_path)

def download():
    """Handles the downloading of video and audio streams."""
    url = url_entry.get()
    format_choice = format_var.get()
    download_button.config(state="disabled")  # Disable the button while downloading
    
    def threaded_download():
        try:
            youtube = YouTube(url)
            video_title.set(youtube.title)  # Set the video title in the UI
            status_label.config(text="Preparing download...")
            output_path = os.path.join(os.getcwd(), "converted_videos")
            os.makedirs(output_path, exist_ok=True)

            if format_choice == 'mp4':
                status_label.config(text=f"Downloading video and audio for {youtube.title}...")
                video_stream = youtube.streams.filter(progressive=False, file_extension='mp4').order_by('resolution').desc().first()
                audio_stream = youtube.streams.get_audio_only()
                video_path = video_stream.download(output_path=output_path, filename_prefix="video_")
                audio_path = audio_stream.download(output_path=output_path, filename_prefix="audio_")
                final_title = sanitize_filename(youtube.title)
                final_path = os.path.join(output_path, f"{final_title}.mp4")
                merge_video_audio(video_path, audio_path, final_path, youtube.title)

            elif format_choice == 'mp3':
                status_label.config(text=f"Downloading audio for {youtube.title}...")
                audio_stream = youtube.streams.get_audio_only()
                audio_path = audio_stream.download(output_path=output_path, filename_prefix="audio_")
                final_title = sanitize_filename(youtube.title)
                final_path = os.path.join(output_path, f"{final_title}.mp3")
                merge_audio(audio_path, final_path, youtube.title)

        except Exception as e:
            status_label.config(text=f"Error: {e}")
            download_button.config(state="normal")

    threading.Thread(target=threaded_download).start()

app = Tk()
app.title("YouTube Downloader")

style = ttk.Style(app)
style.theme_use('clam')

# Font, color configurations, and padding
style.configure('TLabel', background='seashell', foreground='#061139', font=('Helvetica', 12), padding=20)
style.configure('TEntry', font=('Helvetica', 12), padding=10)
style.configure('TButton', font=('Helvetica', 12), padding=20, borderwidth=0)
style.configure('TRadiobutton', background='seashell', foreground='#061139', font=('Helvetica', 12), padding=20)

app.configure(bg='seashell')

# UI layout
ttk.Label(app, text="YouTube URL:", style='TLabel').pack(padx=20, pady=10)
url_entry = ttk.Entry(app, font=('Helvetica', 12), width=50)
url_entry.pack(padx=20, pady=10)

video_title = StringVar(app, value="")  # Initialize the video title variable
video_title_label = ttk.Label(app, textvariable=video_title, style='TLabel')  # Label to display the video title
video_title_label.pack(padx=20, pady=5)

format_var = StringVar(app)
ttk.Radiobutton(app, text="MP4 (Video)", variable=format_var, value="mp4", style='TRadiobutton').pack(padx=20, pady=10)
ttk.Radiobutton(app, text="MP3 (Audio)", variable=format_var, value="mp3", style='TRadiobutton').pack(padx=20, pady=10)

download_button = ttk.Button(app, text="Download", command=download, style='TButton')
download_button.pack(padx=20, pady=20)

status_label = ttk.Label(app, text="", style='TLabel')
status_label.pack(padx=20, pady=10)

app.mainloop()
