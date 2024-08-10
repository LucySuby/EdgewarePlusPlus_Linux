import random
from tkinter import Label, Tk

from features.popup import Popup
from PIL import Image, ImageFilter
from utils import utils
from utils.pack import Pack
from utils.settings import Settings
from widgets.image_label import GifLike, ImageLabel


class ImagePopup(Popup):
    def __init__(self, root: Tk, settings: Settings, pack: Pack):
        super().__init__(root, settings, pack)

        self.denial = utils.roll(settings.denial_chance)

        image = Image.open(self.pack.random_image())

        self.set_size_and_position(image.width, image.height)
        ImageLabel(self, self.try_subliminal(image), (self.width, self.height), self.try_denial_filter()).pack()

        self.try_denial_text()
        self.init_finish()

    def try_subliminal(self, image: Image.Image) -> Image.Image | GifLike:
        single_frame = not hasattr(image, "n_frames") or image.n_frames == 1
        if utils.roll(self.settings.subliminal_chance) and single_frame:
            blend_image = image.convert("RGBA")
            subliminal = Image.open(self.pack.random_subliminal())

            if hasattr(subliminal, "n_frames") and subliminal.n_frames > 1:
                frames = []
                for i in range(subliminal.n_frames):
                    subliminal.seek(i)
                    blend_frame = subliminal.resize(image.size).convert("RGBA")
                    frame = Image.blend(blend_image, blend_frame, self.settings.subliminal_opacity)
                    frames.append((frame, subliminal.info["duration"]))

                return GifLike(frames)
            else:
                blend_subliminal = subliminal.resize(image.size).convert("RGBA")
                return Image.blend(blend_image, blend_subliminal, self.settings.subliminal_opacity)
        else:
            return image

    def try_denial_filter(self) -> ImageFilter.Filter:
        if self.denial:
            return random.choice([
                ImageFilter.GaussianBlur(5),
                ImageFilter.GaussianBlur(10),
                ImageFilter.GaussianBlur(20),
                ImageFilter.BoxBlur(5),
                ImageFilter.BoxBlur(10),
                ImageFilter.BoxBlur(20),
            ])  # fmt: skip
        else:
            return None

    def try_denial_text(self) -> None:
        if self.denial:
            label = Label(self, text=self.pack.random_denial(), wraplength=self.width)
            label.place(relx=0.5, rely=0.5, anchor="c")
