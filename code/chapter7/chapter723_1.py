# from dotenv import load_dotenv
# from chapter723_my_llm import MyAutoLLM
#
# load_dotenv()
#
# # 无需传入 provider，框架会自动检测
# llm = MyAutoLLM()
# # 框架内部日志会显示检测到 provider 为 'ollama'
#
# # 后续调用方式完全不变
# messages = [{"role": "user", "content": "你好！"}]
# for chunk in llm.think(messages):
#     print(chunk, end="")

from dotenv import load_dotenv
from hello_agents import HelloAgentsLLM

load_dotenv()

# 无需传入 provider，框架会自动检测
llm = HelloAgentsLLM()
# 框架内部日志会显示检测到 provider 为 'ollama'

# 后续调用方式完全不变
messages = [{"role": "user", "content": "你好！"}]
for chunk in llm.think(messages):
    print(chunk, end="")

# 原来折腾了一大圈，就是原代码中少了一句
# http_client=httpx.Client(
#     trust_env=False
# )
