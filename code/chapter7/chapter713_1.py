from hello_agents import SimpleAgent, HelloAgentsLLM
from chapter721_1_my_llm import MyLLM
from dotenv import load_dotenv
import os

# print(os.path.exists(r"D:\py_project\hello-agents\.env"))
# print(os.path.exists(r"D:\py_project\hello-agents\code\chapter7\.env"))

# print("当前目录:")
# print(os.getcwd())

# env_path = r"D:\py_project\hello-agents\code\chapter7\.env"

# 加载环境变量
# load_dotenv(env_path)

# print("API KEY:")
# print(os.getenv("MODELSCOPE_API_KEY"))
# 云端大模型
# llm = MyLLM(provider="modelscope")
# 用本地部署的 qwen
llm = MyLLM(
    provider="ollama",
    model="qwen2.5:3b",
    api_key="ollama",
    base_url="http://localhost:11434/v1"
)

messages = [{"role": "user", "content": "please introduce u self"}]

# 更正：（但这个也违背了流式返回的初衷，直接一次性全打印了，没了那种动态的感觉）
response_stream = llm.think(messages)

answer = ""

for chunk in response_stream:
    answer += chunk

print(answer)
# 这样的流式返回的结果不能直接打印
# response_stream = llm.think(messages)
#
# print(response_stream)
# for chunk in response_stream:
#     print(chunk)

# 如下
# II
# 'm'm
#  Deep Deep
# SeSe
# ekek
# ,,
#  an an
#  AI AI
#  assistant assistant
#  created created
#  by by
#  Deep Deep
# SeSe
# ekek
#  ( (
# 深度深度
# 求求
# 索索
# ))



