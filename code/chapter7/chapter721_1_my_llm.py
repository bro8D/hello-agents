import os
from typing import Optional

from openai import OpenAI
from hello_agents import HelloAgentsLLM


class MyLLM(HelloAgentsLLM):

    def __init__(
            self,
            model: Optional[str] = None,
            api_key: Optional[str] = None,
            base_url: Optional[str] = None,
            provider: Optional[str] = "auto",
            **kwargs
    ):

        # ==============================
        # Ollama 本地模型
        # ==============================
        if provider == "ollama":

            print("正在使用本地 Ollama")

            super().__init__(
                model=model or "qwen2.5:3b",
                api_key="ollama",
                base_url=base_url or "http://localhost:11434/v1",
                provider="ollama",
                temperature=kwargs.get(
                    "temperature",
                    0.7
                ),
                max_tokens=kwargs.get(
                    "max_tokens",
                    2048
                ),
                timeout=kwargs.get(
                    "timeout",
                    60
                )
            )

            self.provider = "ollama"


        # ==============================
        # ModelScope
        # ==============================
        elif provider == "modelscope":

            print("正在使用自定义 ModelScope Provider")


            self.provider = "modelscope"


            self.api_key = (
                api_key
                or os.getenv("MODELSCOPE_API_KEY")
            )


            if not self.api_key:
                raise ValueError(
                    "ModelScope API key not found"
                )


            self.base_url = (
                base_url
                or os.getenv("LLM_BASE_URL")
                or "https://api-inference.modelscope.cn/v1/"
            )


            self.model = (
                model
                or os.getenv("LLM_MODEL_ID")
                or "Qwen/Qwen2.5-VL-72B-Instruct"
            )


            self.temperature = kwargs.get(
                "temperature",
                0.7
            )


            # 不设置None
            self.max_tokens = kwargs.get(
                "max_tokens",
                2048
            )


            self.timeout = kwargs.get(
                "timeout",
                60
            )


            self._client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
                timeout=self.timeout
            )


        # ==============================
        # 其他模型
        # ==============================
        else:

            super().__init__(
                model=model,
                api_key=api_key,
                base_url=base_url,
                provider=provider,
                **kwargs
            )