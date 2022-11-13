"""monkeyShot is an application thar can be used for making screenshots and video recording
"""

from subprocess import PIPE
from subprocess import Popen
from subprocess import getoutput
try:
    from subprocess import CREATE_NO_WINDOW
except ImportError:
    CREATE_NO_WINDOW = 134217728

from shutil import move

from re import sub
from re import search
from re import findall

from os import remove
from os.path import join
from os.path import isfile
from os.path import dirname
from os.path import abspath
from os.path import realpath
from os.path import expanduser

from tkinter import Tk
from tkinter import Label
from tkinter import Frame
from tkinter import Canvas
from tkinter import Button
from tkinter import Toplevel
from tkinter import TclError
from tkinter import StringVar
from tkinter import OptionMenu
from tkinter.filedialog import asksaveasfilename

from typing import Tuple

from pyautogui import size
from pyautogui import position
from pyautogui import screenshot

from keyboard import is_pressed
from sounddevice import query_devices

from PIL import ImageTk

from idlelib.tooltip import Hovertip

WORKING_DIR = dirname(abspath(__file__))

IMAGES = [
    ('JPEG Image', '*.jpg'),
    ('PNG Image', '*.png'),
    ('TIFF Image', '*.tif'),
    ('WEBP Image', '*.webp'),
    ('BMP Image', '*.bmp'),
    ('GIF Image', '*.gif'),
    ('All Image Formats', '*.*'),
]

VIDEOS = [
    ('MP4 Video', '*.mp4'),
    ('AVI Video', '*.avi'),
    ('MKV Video', '*.mkv'),
    ('WEBM Video', '*.webm'),
    ('WMV Video', '*.wmv'),
    ('All Video Formats', '*.*'),
]

def wait_for_key(key_: str):
    """Wait for key to be pressed

    Args:
        key_ (str): Key to wait for
    """
    run_ = True
    while run_:
        if is_pressed(key_):
            run_ = False

def get_video_devices() -> Tuple[str, list]:
    """Get video devices

    Returns:
        tuple:
            str: Camera Name,
            list: Camera Device List
    """
    list_devices = getoutput('ffmpeg -list_devices true -f dshow -i dummy').replace('\n', '%%%')
    video_regex = "(DirectShow video devices)(.*?)(DirectShow audio devices)"
    video_devicces = search(video_regex, list_devices).group(2).replace('%%%', '\n')
    camera_regex = '(]  ")(.*?)(")'
    video_devs = []
    for dev in findall(camera_regex, video_devicces):
        video_devs.append(dev[1])
    camera = findall(camera_regex, video_devicces)[0][1]
    video_devs.remove(camera)
    return camera, video_devs

def get_audio_devices() -> Tuple[str, list]:
    """Get audio devices

    Returns:
        tuple:
            str: Default Audio Device Name,
            list: Audio Device List
    """
    audio_devices_raw = query_devices()
    audio_devices = []
    default_input_device = "None"
    for audio_device in f"{audio_devices_raw}".split('\n'):
        device_name = audio_device[4:].split(", ")[0].strip()
        if '>' in audio_device:
            default_input_device = device_name
        elif device_name not in audio_devices and ")" in device_name and "0 in" not in audio_device:
            audio_devices.append(device_name)

    default_audio = None
    for audio_device in f"{audio_devices_raw}".split('\n'):
        if default_input_device in audio_device:
            default_audio = audio_device[4:].split(", ")[0].strip()

    if default_audio in audio_devices:
        audio_devices.remove(default_audio)

    return default_audio, audio_devices

class MonkeyHouse:
    """GUI for MonkeyShot
    """
    def __init__(self):
        self.last_click_x = 0
        self.last_click_y = 0
        self.region = None
        self.settings_w = None
        self._init_settings()
        self.main_window()

    @staticmethod
    def read_settings_file() -> dict:
        # TODO: Change settings to json
        """Read the settings.xml file and return the settings as a dictionary

        Returns:
            dict: Dictionary with the settings
        """
        settings_dict = {}
        if isfile(join(WORKING_DIR, "settings.xml")):
            with open(join(WORKING_DIR, "settings.xml"), "r", encoding="utf-8") as settings_file:
                content = settings_file.read()
            settings_dict["Audio Device"] = search(
                r"(<AudioDevice>[\r\n \t]*)(.*?)([\r\n \t]*</AudioDevice>)",
                content
            ).group(2)
            settings_dict["Video Device"] = search(
                r"(<VideoDevice>[\r\n \t]*)(.*?)([\r\n \t]*</VideoDevice>)",
                content
            ).group(2)

        return settings_dict

    @staticmethod
    def _init_settings():
        if not isfile(join(WORKING_DIR, "settings.xml")):
            with open(join(WORKING_DIR, "settings.xml"), "w", encoding="utf-8") as settings_file:
                settings_file.write("<Settings>\n")
                settings_file.write(f"    <AudioDevice>{get_audio_devices()[0]}</AudioDevice>\n")
                settings_file.write(f"    <VideoDevice>{get_video_devices()[0]}</VideoDevice>\n")
                settings_file.write("</Settings>")

    def save_settings_file(self, settings_dict: dict):
        # TODO:
        """Save settings to file

        Args:
            settings_dict (dict): Dictionary with the settings to be saved
        """
        with open(join(WORKING_DIR, "settings.xml"), "r", encoding="utf-8") as settings_file:
            content = settings_file.read()
        if "Audio Device" in settings_dict:
            content = sub(
                r"(<AudioDevice>[\r\n \t]*)(.*?)([\r\n \t]*</AudioDevice>)",
                fr"\1{settings_dict['Audio Device']}\3",
                content
            )
        if "Video Device" in settings_dict:
            content = sub(
                r"(<VideoDevice>[\r\n \t]*)(.*?)([\r\n \t]*</VideoDevice>)",
                fr"\1{settings_dict['Video Device']}\3",
                content
            )
        with open(join(WORKING_DIR, "settings.xml"), "w", encoding="utf-8") as settings_file:
            settings_file.write(content)

    def settings_window(self):
        """Settings Window
        """

        def on_enter(e):
            e.widget.config(foreground="red")

        def on_leave(e):
            e.widget.config(foreground='white')

        if self.settings_w is None:
            self.settings_w = Toplevel(self.window)
            x_main = self.window.winfo_x()
            y_main = self.window.winfo_y()
            self.settings_w.title("Settings")
            if self.window.winfo_x() + 400 + 1000 <= size()[0]:
                self.settings_w.geometry(f"1000x400+{x_main + 400}+{y_main}")
            else:
                self.settings_w.geometry(f"1000x400+{x_main - 600}+{y_main + 100}")
            self.settings_w.configure(bg='black')
            self.settings_w.resizable(False, False)
            self.settings_w.overrideredirect(True)
            self.settings_w.attributes('-alpha', 0.8, '-topmost', 1)
            title_bar = Frame(self.settings_w, bg='black', highlightthickness=0)
            title_bar.pack(expand=0, fill='x')
            close_button = Button(
                title_bar,
                image=self.close_button_img,
                command=self.settings_w.destroy,
                bg="black",
                padx=2,
                pady=2,
                bd=0,
                font="bold",
                fg='red',
                highlightthickness=0
            )
            close_button.pack(side='right')
            audio_label = Label(
                self.settings_w,
                text="Audio Device",
                bg='#000001',
                fg='white'
            )
            video_label = Label(
                self.settings_w,
                text="Video Device",
                bg='#000001',
                fg='white'
            )
            audio_label.place(x=10, y=40)
            video_label.place(x=10, y=80)

            audio_var = StringVar(self.settings_w)
            video_var = StringVar(self.settings_w)

            current_settings_dict = self.read_settings_file()

            default_audio_device, audio_devices_list = get_audio_devices()
            default_video_device, video_devices_list = get_video_devices()

            if "Audio Device" not in current_settings_dict:
                audio_var.set(default_audio_device)
            else:
                audio_var.set(current_settings_dict['Audio Device'])

            if "Video Device" not in current_settings_dict:
                video_var.set(default_video_device)
            else:
                video_var.set(current_settings_dict['Video Device'])

            audio_dropdown = OptionMenu(self.settings_w, audio_var, default_audio_device, *audio_devices_list)
            video_dropdown = OptionMenu(self.settings_w, video_var, default_video_device, *video_devices_list)
            audio_dropdown.config(
                bg='#000001',
                fg='white',
                bd=0,
                highlightthickness=0,
                activebackground="#000001",
                activeforeground="#AA0000",
            )
            video_dropdown.config(
                bg='#000001',
                fg='white',
                bd=0,
                highlightthickness=0,
                activebackground="#000001",
                activeforeground="red",
            )
            audio_dropdown["menu"].config(
                bg="#000001",
                selectcolor="#AA0000",
                activebackground="#000001",
                activeforeground="red",
                fg='white',
                bd=0,
            )
            video_dropdown["menu"].config(
                bg="#000001",
                selectcolor="red",
                activebackground="#000001",
                activeforeground="red",
                fg='white',
                bd=0,
            )
            audio_dropdown.place(x=250, y=40)
            video_dropdown.place(x=250, y=80)

            bottom_frame = Frame(self.settings_w, bg='black', highlightthickness=0)
            bottom_frame.pack(side='bottom', fill='x', expand='no')
            save_settings_button = Button(
                bottom_frame,
                text="Save & Close",
                bg='black',
                fg="white",
                command=lambda: [
                    self.save_settings_file(
                        {
                            'Audio Device': audio_var.get(),
                            'Video Device': video_var.get(),
                        }
                    ),
                    self.settings_w.destroy()
                ]
            )
            apply_settings_button = Button(
                bottom_frame,
                text="Apply",
                bg='black',
                fg="white",
                command=lambda: self.save_settings_file(
                    {
                        'Audio Device': audio_var.get(),
                        'Video Device': video_var.get(),
                    }
                )
            )

            close_settings_button = Button(
                bottom_frame,
                text="Close",
                bg='black',
                fg="white",
                command=self.settings_w.destroy
            )
            save_settings_button.pack(side='left', expand='yes')
            apply_settings_button.pack(side='left', expand='yes')
            close_settings_button.pack(side='left', expand='yes')

            save_settings_button.bind('<Enter>', on_enter)
            save_settings_button.bind('<Leave>', on_leave)

            apply_settings_button.bind('<Enter>', on_enter)
            apply_settings_button.bind('<Leave>', on_leave)

            close_settings_button.bind('<Enter>', on_enter)
            close_settings_button.bind('<Leave>', on_leave)

    def sync_windows(self, event=None):
        """Sync Windows

        Args:
            event
        """
        if self.settings_w is not None:
            try:
                x_main = self.window.winfo_x()
                y_main = self.window.winfo_y()
                if self.window.winfo_x() + 400 + 1000 <= size()[0]:
                    self.settings_w.geometry(f"1000x400+{x_main + 400}+{y_main}")
                else:
                    self.settings_w.geometry(f"1000x400+{x_main - 600}+{y_main + 100}")
            except TclError:
                self.settings_w = None

    def main_window(self):
        """Main window
        """
        self.window = Tk()
        self.window.overrideredirect(True)
        self.window.title('MonkeyHouse')
        self.window.configure(bg='black')
        # self.window.wm_attributes('-transparentcolor', self.window['bg'])
        self.window.wm_attributes('-transparentcolor', '#000001')
        self.window.resizable(False, False)
        self.window.geometry('400x100+200+200')

        self.title_bar = Frame(self.window, bg='black', highlightthickness=0)

        self.close_button_img = ImageTk.PhotoImage(
            file=join(
                dirname(realpath(__file__)),
                "img",
                "close_button_24px_#AA0000.png"
            )
        )

        self.close_button = Button(
            self.title_bar,
            image=self.close_button_img,
            command=self.window.destroy,
            bg="black",
            padx=2,
            pady=2,
            bd=0,
            font="bold",
            fg='red',
            highlightthickness=0
        )

        self.canvas = Canvas(self.window, bg='black', highlightthickness=0)
        self.window.attributes('-alpha', 0.8, '-topmost', 1)

        self.title_bar.pack(expand=1, fill='x')
        self.close_button.pack(side='right')

        self.static_screenshot_button_img = ImageTk.PhotoImage(
            file=join(
                dirname(realpath(__file__)),
                "img",
                "static_screenshot_button_48px_#AA0000.png"
            )
        )

        self.dynamic_screenshot_button_img = ImageTk.PhotoImage(
            file=join(
                dirname(realpath(__file__)),
                "img",
                "dynamic_screenshot_button_48px_#AA0000.png"
            )
        )

        self.record_button_img = ImageTk.PhotoImage(
            file=join(
                dirname(realpath(__file__)),
                "img",
                "record_button_48px_#AA0000.png"
            )
        )

        self.region_record_button_img = ImageTk.PhotoImage(
            file=join(
                dirname(realpath(__file__)),
                "img",
                "region_record_button_48px_#AA0000.png"
            )
        )

        self.streamer_button_img = ImageTk.PhotoImage(
            file=join(
                dirname(realpath(__file__)),
                "img",
                "streamer_button_48px_#AA0000.png"
            )
        )

        self.settings_button_img = ImageTk.PhotoImage(
            file=join(
                dirname(realpath(__file__)),
                "img",
                "settings_button_48px_#AA0000.png"
            )
        )

        self.static_screenshot_button = Button(
            self.canvas,
            image=self.static_screenshot_button_img,
            command=self.monkey_shot,
            bg="black",
            padx=5,
            pady=5,
            bd=0,
            highlightthickness=10
        )
        self.dynamic_screenshot_button = Button(
            self.canvas,
            image=self.dynamic_screenshot_button_img,
            command=lambda: self.monkey_shot('dynamic'),
            bg="black",
            padx=5,
            pady=5,
            bd=0,
            highlightthickness=10
        )
        self.record_button = Button(
            self.canvas,
            image=self.record_button_img,
            command=self.monkey_see,
            bg="black",
            padx=5,
            pady=5,
            bd=0,
            highlightthickness=10
        )
        self.region_record_button = Button(
            self.canvas,
            image=self.region_record_button_img,
            command=lambda: self.monkey_see(mode='region'),
            bg="black",
            padx=5,
            pady=5,
            bd=0,
            highlightthickness=10
        )
        self.streamer_button = Button(
            self.canvas,
            image=self.streamer_button_img,
            command=lambda: self.monkey_see(mode='streaming'),
            bg="black",
            padx=5,
            pady=5,
            bd=0,
            highlightthickness=10
        )
        self.settings_button = Button(
            self.canvas,
            image=self.settings_button_img,
            command=self.settings_window,
            bg="black",
            padx=5,
            pady=5,
            bd=0,
            highlightthickness=10
        )

        self.static_screenshot_button.pack(side='left')
        self.dynamic_screenshot_button.pack(side='left')
        self.record_button.pack(side='left')
        self.region_record_button.pack(side='left')
        self.streamer_button.pack(side='left')
        self.settings_button.pack(side='right')

        Hovertip(
            self.static_screenshot_button,
            'Static Screenshot using Crosshair'
        )
        Hovertip(
            self.dynamic_screenshot_button,
            'Dynamic Screenshot using Crosshair'
        )
        Hovertip(
            self.record_button,
            'Fullscreen recording'
        )
        Hovertip(
            self.region_record_button,
            'Specific region recording'
        )
        Hovertip(
            self.streamer_button,
            'Streaming Recording (Desktop Recording with Web Camera recording overlay)'
        )
        Hovertip(
            self.settings_button,
            'Settings'
        )

        self.canvas.pack(expand=1, fill='both')

        self.title_bar.bind('<Button-1>', self._save_last_click)
        self.title_bar.bind('<B1-Motion>', self._window_moving)

        self.window.bind("<Configure>", self.sync_windows)

        self.window.mainloop()

    def monkey_shot(self, mode: str = 'static'):
        """Call screenshot function

        Args:
            mode (str, optional): Screenshot mode. Defaults to 'static'.
        """
        self.window.withdraw()
        if self.settings_w is not None:
            self.settings_w.withdraw()
        screenshot_session = MonkeyShot()
        monkey_screenshot = screenshot_session.shoot(mode)
        self.window.deiconify()
        if self.settings_w is not None:
            self.settings_w.deiconify()
        try:
            monkey_screenshot.save(asksaveasfilename(filetypes=IMAGES, defaultextension=IMAGES))
        except ValueError:
            pass

    def monkey_see(self, mode: str = 'fullscreen'):
        """Call video recording function

        Args:
            fullscreen (bool, optional): Fullscreen recording. Defaults to True.
        """
        self.window.withdraw()
        if self.settings_w is not None:
            self.settings_w.withdraw()
        video_recorder = MonkeyShot()
        if mode == 'fullscreen':
            video_recorder.record()
        if mode == 'streaming':
            video_recorder.streaming_record()
        elif mode == 'region':
            video_recorder.shoot(mode='video')
        self.window.deiconify()
        if self.settings_w is not None:
            self.settings_w.deiconify()
        monkey_recording = asksaveasfilename(filetypes=VIDEOS, defaultextension=VIDEOS)
        if isfile(monkey_recording):
            remove(monkey_recording)

        try:
            move("Video_recording.mp4", monkey_recording)
        except FileNotFoundError:
            raise Exception("No recording found") from None

    def _save_last_click(self, event):
        self.last_click_x = event.x
        self.last_click_y = event.y

    def _window_moving(self, event):
        x, y = event.x - self.last_click_x + self.window.winfo_x(), event.y - self.last_click_y + self.window.winfo_y()
        self.window.geometry(f'+{x}+{y}')

class MonkeyShot(Toplevel):
    """Take screenshot of specific region, using a croshair for selection
    """
    def __init__(self):
        self._clicks = 0
        self._points = []
        self.filename = join(expanduser("~/Desktop"), "cyberMonkeyScreenShort.jpg")
        self.monkey_screenshot = None
        self.mode = None
        self.window = Tk()
        self.canvas = None

    def shoot(self, mode: str = 'static'):
        """Take the screenshot

        Args:
            mode (str, optional): Screenshot mode, can be static or dynamic.
            - Static mode: first take a screenshot of complete screen that draw crosshair on top.
              This mode provides a clearer view of what is behind, but cannot be used to capture live images from videos.
            - Dynamic mode: uses transparency. But the image is a more fuzzy and the corsshair is also partially transparent.
              This mode can be used to capture live images from videos.
            Defaults to 'static'.
        """
        if mode == 'static':
            transparency = 1
            self.mode = 'screenshot'
        elif mode == 'dynamic':
            transparency = 0.4
            self.mode = 'screenshot'
        elif mode == 'video':
            transparency = 1
            self.mode = 'video'
        # self.window = Toplevel()  # Tk()
        self.window.attributes('-fullscreen', True, '-alpha', transparency)
        self.window.configure(bg='black')

        self.canvas = Canvas(
            self.window,
            width=self.window.winfo_screenwidth(),
            height=self.window.winfo_screenheight(),
            cursor="crosshair"
        )
        self.canvas.configure(highlightthickness=0, bg='black')
        self.canvas.bind("<Button-1>", self._two_clicks)
        self.canvas.pack()

        if mode in ('static', 'video'):
            self.canvas.image = ImageTk.PhotoImage(screenshot())
            self.canvas.create_image(0, 0, image=self.canvas.image, anchor='nw')

        self.window.after(1, self._crosshair, None, None, None)
        self.window.mainloop()
        return self.monkey_screenshot

    def record(self, region=None, audio: str = None) -> None:
        """Record a video of the screen

        Args:
            region (list, optional): Region to record. Defaults to None.
            audio (str, optional): Audio to record. Defaults to None.

        Returns:
            None
        """
        ffmpeg = abspath(".//3rd//ffmpeg.exe")
        width, height = size()
        resolution = f'{width}x{height}'
        if region is not None:
            resolution = f'{region[2]}x{region[3]}'

        filename = "Video_recording.mp4"
        default_input_device = "None"
        if audio is None:
            audio_devices_raw = query_devices()
            audio_devices = []
            default_input_device = "None"
            for audio_device in f"{audio_devices_raw}".split('\n'):
                device_name = audio_device[4:].split(", ")[0].strip()
                if '>' in audio_device:
                    default_input_device = device_name
                elif device_name not in audio_devices and ")" in device_name and "0 in" not in audio_device:
                    audio_devices.append(device_name)

            default_audio = None
            for audio_device in f"{audio_devices_raw}".split('\n'):
                if default_input_device in audio_device:
                    default_audio = audio_device[4:].split(", ")[0].strip()

            audio = f'-f dshow -channel_layout stereo  -thread_queue_size 1024 -i audio="{default_audio}"' \
                if default_input_device != "None" else ''

        offset_x = 0
        offset_y = 0
        if region is not None:
            offset_x = region[0]
            offset_y = region[1]

        cmd = f'"{ffmpeg}" -y \
                -rtbufsize 200M \
                -f gdigrab \
                -thread_queue_size 1024 \
                -probesize 10M \
                -hide_banner \
                -r 10 \
                -draw_mouse 1 \
                -video_size {resolution} \
                -offset_x {offset_x} \
                -offset_y {offset_y} \
                -i desktop \
                {audio} \
                -c:v libx264 \
                -r 10 -preset ultrafast \
                -tune zerolatency \
                -crf 25 \
                -pix_fmt yuv420p \
                -c:a aac \
                -strict -2 -ac 2 -b:a 128k \
                -vf "pad=ceil(iw/2)*2:ceil(ih/2)*2" "{filename}" '.replace("                ", "")
        print(f"cmd = {cmd}")
        #with Popen(cmd, shell=True, stdin=PIPE, creationflags=CREATE_NO_WINDOW) as ffmpeg_process:
        with Popen(cmd, shell=True, stdin=PIPE) as ffmpeg_process:
            wait_for_key('esc')
            ffmpeg_process.stdin.write(b'q')  # send q to end ffmpeg process
            # ffmpeg_process.stdin.close()  # send q to end ffmpeg process

    def streaming_record(self, region=None, audio: str = None) -> None:
        """Record a video of the screen

        Args:
            region (list, optional): Region to record. Defaults to None.
            audio (str, optional): Audio to record. Defaults to None.

        Returns:
            None
        """
        ffmpeg = abspath(".//3rd//ffmpeg.exe")
        width, height = size()
        resolution = f'{width}x{height}'
        if region is not None:
            resolution = f'{region[2]}x{region[3]}'

        filename = "Video_recording.mp4"
        default_input_device = "None"
        if audio is None:
            audio_devices_raw = query_devices()
            audio_devices = []
            default_input_device = "None"
            for audio_device in f"{audio_devices_raw}".split('\n'):
                device_name = audio_device[4:].split(", ")[0].strip()
                if '>' in audio_device:
                    default_input_device = device_name
                elif device_name not in audio_devices and ")" in device_name and "0 in" not in audio_device:
                    audio_devices.append(device_name)

            default_audio = None
            for audio_device in f"{audio_devices_raw}".split('\n'):
                if default_input_device in audio_device:
                    default_audio = audio_device[4:].split(", ")[0].strip()

            audio = f':audio="{default_audio}"' if default_input_device != "None" else ''

        camera = get_video_devices()[0]
        offset_x = 0
        offset_y = 0
        if region is not None:
            offset_x = region[0]
            offset_y = region[1]

        cmd = f'{ffmpeg} -f gdigrab \
            -rtbufsize 100M \
            -probesize 20M \
            -framerate 24 \
            -draw_mouse 1 \
            -video_size {resolution} \
            -offset_x {offset_x} \
            -offset_y {offset_y} \
            -i desktop \
            -f dshow \
            -rtbufsize 100M \
            -probesize 20M \
            -i video="{camera}"{audio} \
            -filter_complex "[0:v] scale=1920x1080[desktop]; \
            [1:v] scale=320x240 [webcam]; \
            [desktop][webcam] overlay=x=W-w-50:y=H-h-50" \
            "{filename}"'.replace("            ", "")
        print(f"cmd = {cmd}")

        with Popen(cmd, shell=False, stdin=PIPE, creationflags=CREATE_NO_WINDOW) as ffmpeg_process:
            wait_for_key('esc')
            ffmpeg_process.stdin.write(b'q')  # send q to end ffmpeg process

    def set_filename(self, fname: str):
        """Set name of the image

        Args:
            nam (str): Filename for the screenshot
        """
        self.filename = fname

    @staticmethod
    def _points_to_region(pt1: list, pt2: list) -> tuple:
        x_1, y_1 = pt1
        x_2, y_2 = pt2

        if x_1 > x_2 and y_1 < y_2:
            top_left_x = x_2
            top_left_y = y_1
            width = x_1 - x_2
            height = y_2 - y_1
        elif x_1 < x_2 and y_1 < y_2:
            top_left_x = x_1
            top_left_y = y_1
            width = x_2 - x_1
            height = y_2 - y_1
        elif x_1 < x_2 and y_1 > y_2:
            top_left_x = x_1
            top_left_y = y_2
            width = x_2 - x_1
            height = y_1 - y_2
        elif x_1 > x_2 and y_1 > y_2:
            top_left_x = x_2
            top_left_y = y_2
            width = x_1 - x_2
            height = y_1 - y_2

        return (top_left_x, top_left_y, width, height)

    def _run(self):
        reg = self._points_to_region(self._points[0], self._points[1])
        if self.mode == 'video':
            self.record(reg)
        elif self.mode == 'screenshot':
            self.monkey_screenshot = screenshot(region=reg)
        self.window.quit()

    def _crosshair(self, vertical, horizontal, rectangle):
        if self._clicks == 0:
            x_point, y_point = position()

            self.canvas.delete(vertical)
            self.canvas.delete(horizontal)

            vertical = self.canvas.create_line(
                x_point,
                self.window.winfo_screenheight(),
                x_point,
                0,
                fill='red'
            )
            horizontal = self.canvas.create_line(
                0,
                y_point,
                self.window.winfo_screenwidth(),
                y_point,
                fill='red'
            )
        elif self._clicks == 1:
            self.canvas.delete(vertical)
            self.canvas.delete(horizontal)
            self.canvas.delete(rectangle)
            rectangle = self.canvas.create_rectangle(
                self._points[0][0],
                self._points[0][1],
                position()[0],
                position()[1],
                outline='red'
            )

        self.window.after(1, self._crosshair, vertical, horizontal, rectangle)

    def _two_clicks(self, event):
        self._clicks += 1
        self._points.append((event.x, event.y))
        if self._clicks == 2:
            self.window.destroy()
            self._run()

if __name__ == '__main__':
    MonkeyHouse()
