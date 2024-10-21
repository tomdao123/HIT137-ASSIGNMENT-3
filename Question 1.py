import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox, Scale
from functools import wraps
import cv2
from PIL import Image, ImageTk
import threading
import time

# Decorator Example
def log_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__} with arguments {args} and {kwargs}")
        return func(*args, **kwargs)
    return wrapper

# Base Class for the Application
class BaseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Youtube Like Interface Application")
        self.setup_ui()

    def setup_ui(self):
        raise NotImplementedError("Must override setup_ui in subclasses")

# Main Application Class using Inheritance and Encapsulation
class MainApp(BaseApp):
    def __init__(self, root):
        self.__video_loaded = False  # Encapsulated attribute
        self.video_path = None
        self.cap = None
        self.is_playing = False
        self.play_thread = None
        super().__init__(root)

    # Overriding Base Class Method
    def setup_ui(self):
        self.label = tk.Label(self.root, text="Welcome to the Youtube Like Interface Application")
        self.label.pack()

        self.load_button = tk.Button(self.root, text="Load Video", command=self.load_video)
        self.load_button.pack()

        self.play_button = tk.Button(self.root, text="Play Video", command=self.play_video)
        self.play_button.pack()

        self.pause_button = tk.Button(self.root, text="Pause Video", command=self.pause_video)
        self.pause_button.pack()

        self.like_button = tk.Button(self.root, text="Like", command=self.like_video)
        self.like_button.pack()

        self.comment_button = tk.Button(self.root, text="Comment", command=self.add_comment)
        self.comment_button.pack()

        self.fullscreen_button = tk.Button(self.root, text="Fullscreen", command=self.toggle_fullscreen)
        self.fullscreen_button.pack()

        self.volume_scale = Scale(self.root, from_=0, to=100, orient=tk.HORIZONTAL, label="Volume")
        self.volume_scale.pack()
        self.volume_scale.set(50)

        self.like_count_label = tk.Label(self.root, text="Likes: 0")
        self.like_count_label.pack()
        self.like_count = 0

        self.video_panel = tk.Label(self.root)
        self.video_panel.pack()

        self.progress_label = tk.Label(self.root, text="Progress: 0%")
        self.progress_label.pack()

    @log_decorator  # Decorator usage
    def load_video(self):
        self.video_path = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4;*.avi;*.mov")])
        if self.video_path:
            self.__video_loaded = True
            self.cap = cv2.VideoCapture(self.video_path)
            self.label.config(text="Video Loaded Successfully!")

    @log_decorator  # Decorator usage
    def play_video(self):
        if self.__video_loaded and not self.is_playing:
            self.is_playing = True
            self.play_thread = threading.Thread(target=self.play_video_thread)
            self.play_thread.start()
        elif not self.__video_loaded:
            self.label.config(text="Please load a video first.")

    def play_video_thread(self):
        fps = self.cap.get(cv2.CAP_PROP_FPS)
        delay = 1 / fps if fps > 0 else 0.03
        while self.cap.isOpened() and self.is_playing:
            start_time = time.time()
            ret, frame = self.cap.read()
            if not ret:
                break
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(frame)
            image_tk = ImageTk.PhotoImage(image=image)
            self.video_panel.config(image=image_tk)
            self.video_panel.image = image_tk
            self.update_progress()
            elapsed_time = time.time() - start_time
            sleep_time = max(0, delay - elapsed_time)
            time.sleep(sleep_time)
        self.is_playing = False

    @log_decorator  # Decorator usage
    def pause_video(self):
        if self.__video_loaded:
            self.is_playing = False
            self.label.config(text="Video is paused.")
        else:
            self.label.config(text="Please load a video first.")

    @log_decorator  # Decorator usage
    def like_video(self):
        self.like_count += 1
        self.like_count_label.config(text=f"Likes: {self.like_count}")
        self.label.config(text="You liked the video!")

    @log_decorator  # Decorator usage
    def add_comment(self):
        comment = simpledialog.askstring("Comment", "Enter your comment:")
        if comment:
            print(f"Comment added: {comment}")
            messagebox.showinfo("Comment Added", f"Your comment: {comment}")

    @log_decorator
    def toggle_fullscreen(self):
        self.root.attributes("-fullscreen", not self.root.attributes("-fullscreen"))

    def update_progress(self):
        if self.cap:
            current_frame = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
            total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            progress = (current_frame / total_frames) * 100 if total_frames else 0
            self.progress_label.config(text=f"Progress: {progress:.2f}%")

# Multiple Inheritance Example
class FileHandler:
    def open_file(self):
        file_path = filedialog.askopenfilename()
        print(f"File selected: {file_path}")

class YoutubeApp(MainApp, FileHandler):
    def __init__(self, root):
        super().__init__(root)
        self.file_button = tk.Button(self.root, text="Open File", command=self.open_file)
        self.file_button.pack()

if __name__ == "__main__":
    root = tk.Tk()
    app = YoutubeApp(root)
    root.mainloop()
