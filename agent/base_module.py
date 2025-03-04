import os
import io
from google.cloud import vision
from .model_zoo.shared_model import SharedModel


class BaseModule():
    """Tool that adds the capability to locate image region with a natural language query."""

    name = "Base Module"
    description = (
        "illustration of tool"
    )
    visual_inputs_number = 0
    core_model = None

    def __init__(self, ):
        self.llm = None
        self.preprocess = None

    def _run(self, **kwargs):
        # TODO: revise to (query, visual_inputs, history)
        """Use the tool."""
        return {}

    def _test(self) -> dict:
        """Test the tool."""
        return {}
        
    def check_input(self, **kwargs) -> str:
        """Check if the input is valid."""
        return ""

    def check_output(self, output) -> str:
        """Check if the output is valid."""
        return ""

    def _check_input_video_only(self, image, video, error_msg) -> str:
        if image:
            error_msg += f"{self.name} does not support image input. "

        if video.duration > 60:
            error_msg += f"{self.name} only supports video input with duration less than 60 seconds. " \
                         "You need to ground the video to short clip first."
        return error_msg

    def _check_input_image_only(self, image, video, error_msg, duration=60) -> str:
        if video.duration < duration:
            error_msg += f"{self.name} only supports video input with duration less than {duration} seconds. " \
                         "You need to ground the video to short clip first."
        return error_msg

    def _check_input_video_number(self, image, video, error_msg) -> str:
        number = self.visual_inputs_number
        if number == 1:
            if type(video) is list:
                if len(video) > number:
                    error_msg += f"{self.name} only supports one video input. "
        else:
            if type(video) is list:
                if len(video) != number:
                    error_msg += f"{self.name} only supports {number} video input. "
            else:
                error_msg += f"{self.name} only supports {number} video input. "

        return error_msg

    def _check_subtitle(self, image, video, error_msg):
        if video.subtitle is None:
            error_msg += "You should call ASR Module to got subtitle."
        return error_msg

    def crop_video(self, input_video, start_time, end_time):
        # Create the subclip using the subclip method
        subclip = input_video.video.subclip(start_time, end_time)
        # from IPython.core.debugger import Pdb
        # Pdb().set_trace()
        video_name = input_video.video_path.split('/')[-1].split('.')[0]
        video_path = os.path.join(input_video.cache_dir, f"{video_name}-{start_time}-{end_time}.mp4")
        subclip.write_videofile(video_path)

        # if input_video.subtitle:
        #     cropped_subtitle = self.crop_audio(input_video.subtitle, start_time, end_time)
        # else:
        cropped_subtitle = None

        out = {"video_path": video_path,
               "video": subclip,
               "tensor": None,
               "subtitle": cropped_subtitle,
               'cache_dir': input_video.cache_dir}
        return out

    def get_ocr(self, image_path):
        with io.open(image_path, 'rb') as image_file:
            content = image_file.read()

        image = vision.Image(content=content)

        # Perform OCR using the API
        response = self.client.text_detection(image=image)
        texts = response.text_annotations

        # Extract the full text from the response
        if texts:
            full_text = texts[0].description
            return f" OCR on the frame ({full_text})"
        else:
            return ""

    def __call__(self, **kwargs):
        error_msg = self.check_input(image=kwargs.get("input_image", None), video=kwargs.get("input_video", None))
        if error_msg != "":
            return {"text": error_msg}
        else:
            return self._run(**kwargs)
