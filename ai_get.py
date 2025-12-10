import os
import cv2
import numpy as np
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

# 优先读取 GOOGLE_API_KEY（google-genai 官方约定）。缺失则给出清晰错误。
_API_KEY = os.getenv("GOOGLE_API_KEY")
if not _API_KEY:
    raise RuntimeError("缺少 GOOGLE_API_KEY 环境变量，无法调用 Gemini API。请在 .env 或部署环境中设置。")

_client = genai.Client(api_key=_API_KEY)
_PROMPT = os.getenv("CAPTCHA_PROMPT", "识别这张验证码图片中的字符或数字，只输出结果，不要其他文字。")


def recognize_captcha_from_array(image_array: np.ndarray) -> str:
    """输入图像数组，返回识别结果。"""
    _, img_bytes = cv2.imencode('.png', image_array)
    response = _client.models.generate_content(
        model='gemini-2.5-flash',
        contents=[
            types.Part.from_bytes(data=img_bytes.tobytes(), mime_type='image/png'),
            _PROMPT
        ]
    )
    return response.text.strip()
