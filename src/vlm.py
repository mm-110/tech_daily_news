import base64
from enum import Enum
from typing import Literal

from src.prompts import describe_website_portion_screenshot_prompt
from src.models import PageInfoOutput, BoundingBoxInfo

from dotenv import load_dotenv

load_dotenv()


class ModelType(Enum):
    OPENAI = "gpt-4o"
    LLAMA = "llama3.2-vision:latest"


class VLM:
    def __init__(self, model: ModelType):
        self.model = model

        if self.model == ModelType.OPENAI:
            from langchain_openai import ChatOpenAI

            self.llm = ChatOpenAI(model=model.value, temperature=0)
        elif self.model == ModelType.LLAMA:
            pass
            # import ollama

            # self.ollama = ollama
        else:
            raise ValueError(f"Unsupported model: {model}")

    def convert_to_base64(self, file_path: str) -> str:
        from PIL import Image
        from io import BytesIO

        pil_image = Image.open(file_path)
        buffered = BytesIO()
        pil_image.save(buffered, format="JPEG")
        return base64.b64encode(buffered.getvalue()).decode("utf-8")

    def describe_image(
        self, file_path: str, page_info: PageInfoOutput, bounding_box: BoundingBoxInfo
    ) -> str:
        variables = {
            "page_type": page_info.page_type,
            "url": page_info.url,
            "page_width": page_info.width,
            "page_height": page_info.height,
            "page_area": (
                page_info.area()
                if hasattr(page_info, "area")
                else page_info.width * page_info.height
            ),
            "x": bounding_box.x,
            "y": bounding_box.y,
            "width": bounding_box.width,
            "height": bounding_box.height,
            "bbox_area": (
                bounding_box.area()
                if hasattr(bounding_box, "area")
                else bounding_box.width * bounding_box.height
            ),
            "css_selector": bounding_box.css_selector,
            "tag_html": bounding_box.tag,
        }
        prompt = describe_website_portion_screenshot_prompt.format(**variables)

        if self.model == ModelType.OPENAI:
            from langchain_core.messages import HumanMessage

            image_base64 = self.convert_to_base64(file_path)
            image_url = f"data:image/jpeg;base64,{image_base64}"

            message = HumanMessage(
                content=[
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": image_url}},
                ]
            )
            response = self.llm.invoke([message])
            return response.content

        elif self.model == ModelType.LLAMA:
            import ollama
            response = ollama.chat(
                model=self.model.value,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                        "images": [file_path],
                    }
                ],
            )
            return response["message"]["content"]
