from tkinter import *
from tkinter import filedialog, ttk
import ttkbootstrap as tb
from ttkbootstrap.dialogs import Messagebox
from ttkbootstrap.scrolled import ScrolledText
import openai
from moviepy.editor import *
import os.path

root = tb.Window(themename="cyborg")
root.title("AI Video Transcriber")
root.iconbitmap("assets/images/video.ico")
root.iconbitmap(default="assets/images/video.ico")
root.geometry("700x450")
root.resizable(width=False, height=False)

global VIDEO_FILE_PATH, AUDIO_FILE_PATH


def open_video():
    global VIDEO_FILE_PATH
    my_file = filedialog.askopenfilename(
        title="Open Video File", filetypes=[("MP4 Video", ".mp4"), ("All Files", "*.*")]
    )
    if my_file:
        VIDEO_FILE_PATH = my_file
        sz = os.path.getsize(my_file) / 1000000
        my_text.delete(1.0, END)
        my_text.insert(END, f"File To Convert:\n{my_file}\n\nFile Size:\n{sz:.2f} MB")
        save_mp3_button.config(state="normal")


def save_mp3():
    global AUDIO_FILE_PATH
    my_file = filedialog.asksaveasfilename(
        title="Save MP3 File",
        filetypes=(("mp3 Audio", "*.mp3"),),
        defaultextension=".mp3",
    )
    if my_file:
        AUDIO_FILE_PATH = my_file
        MP4ToMP3(VIDEO_FILE_PATH, AUDIO_FILE_PATH)
        sz = os.path.getsize(my_file) / 1000000
        my_text.insert(
            END,
            f"\n\n\nSaving Audio File As:\n{AUDIO_FILE_PATH}\n\nFile Size:\n{sz:.2f} MB",
        )
        if sz <= 25:
            my_text.insert(
                END,
                "\n\n\nYour File Is Ready To Transcribe!\nClick The 'Transcribe' Button Below...",
            )
            transcribe_button.config(state="normal")
        else:
            my_text.insert(
                END,
                "\n\n\nYour File Is Too Large!\nIt Must Be Less Than 25MB In Size...",
            )


def transcribe_it():
    try:
        my_text.delete(1.0, END)
        openai.api_key = "YOUR_API_KEY_HERE"
        audio_file = open(AUDIO_FILE_PATH, "rb")
        transcript = openai.Audio.transcribe("whisper-1", audio_file)

        sentences = transcript.txt.split(".")
        timestamp = 0

        for sentence in sentences:
            sentence = sentence.strip()
            if sentence:
                timestamp_str = f"{timestamp // 60:02d}:{timestamp % 60:02d}"
                my_text.insert(END, f"{timestamp_str} : {sentence.strip()}\n")
                timestamp += (
                    len(sentence.split()) // 3
                )  # Adjust the timestamp based on the number of words

    except openai.error.RateLimitError:
        my_text.insert(
            END, "Rate limit exceeded. Please check your API plan and billing details."
        )


def copy_it():
    root.clipboard_clear()
    root.clipboard_append(my_text.get(1.0, END))
    mb = Messagebox.ok("The Text Has Been Copied To Your Clipboard!", "Copy Complete!")


def save_text():
    my_file = filedialog.askopenfilename(
        title="Save Transcript",
        filetypes=[("Text Files .txt", ".txt")],
        defaultextension=".txt",
    )
    if my_file:
        text_file = open(my_file, "w")
        text_file.write(my_text.get(1.0, END))
        text_file.close()
        mb = Messagebox.ok("The Text Has Been Saved!", "Save Complete!")


def clear_screen():
    my_mb = Messagebox.okcancel("Are you sure?!", "Clear Transcribed Text")
    if my_mb == "OK":
        my_text.delete(1.0, END)
        save_mp3_button.config(state="disabled")
        transcribe_button.config(state="disabled")


my_text = ScrolledText(root, height=20, width=110, wrap=WORD, autohide=False)
my_text.pack(pady=15)

my_frame = Frame(root)
my_frame.pack()

open_button = tb.Button(
    my_frame, bootstyle="light", text="Convert Video To MP3", command=open_video
)
open_button.grid(row=0, column=0)

save_mp3_button = tb.Button(
    my_frame,
    bootstyle="light",
    text="Save MP3 As...",
    state="disabled",
    command=save_mp3,
)
save_mp3_button.grid(row=0, column=1, padx=30)

copy_button = tb.Button(
    my_frame, bootstyle="light", text="Copy Text To Clipboard", command=copy_it
)
copy_button.grid(row=0, column=2)

save_button = tb.Button(
    my_frame, bootstyle="light", text="Save Text", command=save_text
)
save_button.grid(row=0, column=3, padx=(30, 0))

clear_button = tb.Button(
    my_frame, bootstyle="light", text="Clear Screen", command=clear_screen
)
clear_button.grid(row=0, column=4, padx=(30, 0))

transcribe_button = tb.Button(
    root,
    bootstyle="primary",
    text="Transcribe Video!",
    width=108,
    state="disabled",
    command=transcribe_it,
)
transcribe_button.pack(pady=20)


def MP4ToMP3(mp4, mp3):
    try:
        FILETOCONVERT = AudioFileClip(mp4)
        FILETOCONVERT.write_audiofile(mp3)
        FILETOCONVERT.close()
    except:
        my_text.insert(END, "\n\nThere was a Problem, Please Try Again...")


root.mainloop()
