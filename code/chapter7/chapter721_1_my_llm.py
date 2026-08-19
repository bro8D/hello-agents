import os
from typing import Optional, Iterator
import httpx
from openai import OpenAI
from hello_agents import HelloAgentsLLM
from hello_agents import HelloAgentsException


class MyLLM(HelloAgentsLLM):
    def __init__(
            self,
            model: Optional[str] = None,
            api_key: Optional[str] = None,
            base_url: Optional[str] = None,
            provider: Optional[str] = "auto",
            **kwargs
    ):
        # =====================================================
        # Ollama 本地模型
        # =====================================================
        if provider == "ollama":
            print("正在使用本地 Ollama")
            # 不调用父类初始化
            # 避免 HelloAgentsLLM 内部创建client
            self.provider = "ollama"
            self.model = (
                model
                or "qwen2.5:3b"
            )
            self.api_key = "ollama"
            self.base_url = (
                base_url
                or "http://localhost:11434/v1"
            )
            self.temperature = kwargs.get(
                "temperature",
                0.7
            )
            self.max_tokens = kwargs.get(
                "max_tokens",
                None
            )
            self.timeout = kwargs.get(
                "timeout",
                60
            )
            # 关键：
            # 和你 test_openai_exact.py 保持完全一致
            self._client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
                http_client=httpx.Client(
                    trust_env=False
                ),
                timeout=self.timeout
            )
        # =====================================================
        # ModelScope 云端模型
        # =====================================================
        elif provider == "modelscope":
            print("正在使用 ModelScope")
            self.provider = "modelscope"
            self.api_key = (
                api_key
                or os.getenv(
                    "MODELSCOPE_API_KEY"
                )
            )
            if not self.api_key:
                raise ValueError(
                    "缺少 MODELSCOPE_API_KEY"
                )
            self.base_url = (
                base_url
                or "https://api-inference.modelscope.cn/v1/"
            )
            self.model = (
                model
                or "Qwen/Qwen2.5-VL-72B-Instruct"
            )
            self.temperature = kwargs.get(
                "temperature",
                0.7
            )
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
        # =====================================================
        # 其他provider
        # =====================================================
        else:
            super().__init__(
                model=model,
                api_key=api_key,
                base_url=base_url,
                provider=provider,
                **kwargs
            )
        print("初始化完成")
        print("provider:", self.provider)
        print("model:", self.model)
        print("base_url:", self.base_url)
    # =====================================================
    # 流式调用
    # =====================================================
    def think(
            self,
            messages: list[dict[str, str]],
            temperature: Optional[float] = None
    ) -> Iterator[str]:
        print(
            f"🧠 正在调用 {self.model} 模型..."
        )
        try:
            params = {
                "model": self.model,
                "messages": messages,
                "stream": True
            }
            if temperature is not None:
                params["temperature"] = temperature
            if self.max_tokens is not None:
                params["max_tokens"] = self.max_tokens
            response = (
                self._client
                .chat
                .completions
                .create(
                    **params
                )
            )
            print(
                "✅ 大语言模型响应成功:"
            )
            for chunk in response:
                content = (
                    chunk
                    .choices[0]
                    .delta
                    .content
                )
                if content:
                    print(
                        content,
                        end="",
                        flush=True
                    )
                    yield content
            print()
        except Exception as e:
            print(
                f"❌ 调用LLM API时发生错误: {e}"
            )
            raise HelloAgentsException(
                f"LLM调用失败: {str(e)}"
            )
    def invoke(
            self,
            messages: list[dict[str, str]],
            **kwargs
    ) -> str:
        try:
            params = {
                "model": self.model,
                "messages": messages
            }
            if self.temperature is not None:
                params["temperature"] = (
                    kwargs.get(
                        "temperature",
                        self.temperature
                    )
                )
            if self.max_tokens is not None:
                params["max_tokens"] = (
                    kwargs.get(
                        "max_tokens",
                        self.max_tokens
                    )
                )
            response = (
                self._client
                .chat
                .completions
                .create(
                    **params
                )
            )
            return (
                response
                .choices[0]
                .message
                .content
            )
        except Exception as e:
            raise HelloAgentsException(
                f"LLM调用失败: {str(e)}"
            )