# import os
# from openai import OpenAI
# from dotenv import load_dotenv
# from typing import List, Dict
#
# # 加载 .env 文件中的环境变量
# load_dotenv()
#
# class HelloAgentsLLM:
#     """
#     为本书 "Hello Agents" 定制的LLM客户端。
#     它用于调用任何兼容OpenAI接口的服务，并默认使用流式响应。
#     """
#     def __init__(self, model: str = None, apiKey: str = None, baseUrl: str = None, timeout: int = None):
#         """
#         初始化客户端。优先使用传入参数，如果未提供，则从环境变量加载。
#         """
#         self.model = model or os.getenv("LLM_MODEL_ID")
#         apiKey = apiKey or os.getenv("LLM_API_KEY")
#         baseUrl = baseUrl or os.getenv("LLM_BASE_URL")
#         timeout = timeout or int(os.getenv("LLM_TIMEOUT", 60))
#
#         if not all([self.model, apiKey, baseUrl]):
#             raise ValueError("模型ID、API密钥和服务地址必须被提供或在.env文件中定义。")
#
#         self.client = OpenAI(api_key=apiKey, base_url=baseUrl, timeout=timeout)
#
#     def think(self, messages: List[Dict[str, str]], temperature: float = 0) -> str:
#         """
#         调用大语言模型进行思考，并返回其响应。
#         """
#         print(f"🧠 正在调用 {self.model} 模型...")
#         try:
#             response = self.client.chat.completions.create(
#                 model=self.model,
#                 messages=messages,
#                 temperature=temperature,
#                 stream=True,
#             )
#
#             # 处理流式响应
#             print("✅ 大语言模型响应成功:")
#             collected_content = []
#             for chunk in response:
#                 if not chunk.choices:
#                     continue
#                 content = chunk.choices[0].delta.content or ""
#                 print(content, end="", flush=True)
#                 collected_content.append(content)
#             print()  # 在流式输出结束后换行
#             return "".join(collected_content)
#
#         except Exception as e:
#             print(f"❌ 调用LLM API时发生错误: {e}")
#             return None
#
# # --- 客户端使用示例 ---
# if __name__ == '__main__':
#     try:
#         llmClient = HelloAgentsLLM()
#
#         exampleMessages = [
#             {"role": "system", "content": "You are a helpful assistant that writes Python code."},
#             {"role": "user", "content": "写一个快速排序算法"}
#         ]
#
#         print("--- 调用LLM ---")
#         responseText = llmClient.think(exampleMessages)
#         if responseText:
#             print("\n\n--- 完整模型响应 ---")
#             print(responseText)
#
#     except ValueError as e:
#         print(e)

import os
from typing import Any, Dict, List, Optional, Union
from dotenv import load_dotenv
from openai import OpenAI
from openai.types.chat import ChatCompletionMessage

# 加载 .env 文件中的环境变量
load_dotenv()


class HelloAgentsLLM:
    """为本书 "Hello Agents" 定制的 LLM 客户端。

    支持常规对话（流式）以及原生 Function Calling（工具调用）。
    """

    def __init__(
        self,
        model: str = None,
        apiKey: str = None,
        baseUrl: str = None,
        timeout: int = None,
    ):
        """初始化客户端。优先使用传入参数，如果未提供，则从环境变量加载。"""
        self.model = model or os.getenv("LLM_MODEL_ID")
        apiKey = apiKey or os.getenv("LLM_API_KEY")
        baseUrl = baseUrl or os.getenv("LLM_BASE_URL")
        timeout = timeout or int(os.getenv("LLM_TIMEOUT", 60))

        if not all([self.model, apiKey, baseUrl]):
            raise ValueError(
                "模型ID、API密钥和服务地址必须被提供或在.env文件中定义。"
            )

        self.client = OpenAI(api_key=apiKey, base_url=baseUrl, timeout=timeout)

    def think(
        self,
        messages: List[Dict[str, Any]],
        temperature: float = 0,
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> Union[ChatCompletionMessage, str, None]:
        """调用大语言模型进行思考，并返回响应。

        :param messages: 对话历史消息列表
        :param temperature: 采样温度
        :param tools: 可选的工具 Schema 列表 (用于 Function Calling)
        :return: 传入 tools 时返回 ChatCompletionMessage 对象，未传 tools 时返回生成的文本字符串
        """
        print(f"🧠 正在调用 {self.model} 模型...")
        try:
            # 模式 A: 传了 tools，使用原生 Function Calling (采用非流式模式，确保 tool_calls 参数完整解析)
            if tools:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    tools=tools,
                    stream=False,  # 工具调用时推荐非流式，避免手动拼装参数 chunk
                )
                message = response.choices[0].message
                print("✅ 大语言模型响应成功 (Function Calling)")
                return message

            # 模式 B: 未传 tools，执行普通对话 (保持原有流式响应体验)
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                stream=True,
            )

            # 处理流式响应
            print("✅ 大语言模型响应成功:")
            collected_content = []
            for chunk in response:
                if not chunk.choices:
                    continue
                content = chunk.choices[0].delta.content or ""
                print(content, end="", flush=True)
                collected_content.append(content)
            print()  # 在流式输出结束后换行
            return "".join(collected_content)

        except Exception as e:
            print(f"❌ 调用LLM API时发生错误: {e}")
            return None


# --- 客户端使用示例 ---
if __name__ == "__main__":
    try:
        llmClient = HelloAgentsLLM()

        # 示例 1: 普通对话测试
        print("--- 示例 1: 普通文本调用 ---")
        exampleMessages = [
            {
                "role": "system",
                "content": "You are a helpful assistant that writes Python code.",
            },
            {"role": "user", "content": "写一个快速排序算法"},
        ]
        responseText = llmClient.think(exampleMessages)

        # 示例 2: 原生 Function Calling 测试
        print("\n--- 示例 2: 原生 Function Calling 调用 ---")
        tools_schema = [{
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "获取指定城市的天气状况",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "城市名称，例如：北京、上海",
                        }
                    },
                    "required": ["location"],
                },
            },
        }]

        toolMessages = [
            {"role": "user", "content": "北京今天天气怎么样？"}
        ]

        responseMsg = llmClient.think(toolMessages, tools=tools_schema)
        if responseMsg and responseMsg.tool_calls:
            print(
                f"\n🎉 成功触发工具调用: {responseMsg.tool_calls[0].function.name}"
            )
            print(f"📌 工具参数: {responseMsg.tool_calls[0].function.arguments}")

    except ValueError as e:
        print(e)