# import re
# from llm_client import HelloAgentsLLM
# from tools import ToolExecutor, search
#
# # (此处省略 REACT_PROMPT_TEMPLATE 的定义)
# REACT_PROMPT_TEMPLATE = """
# 请注意，你是一个有能力调用外部工具的智能助手。
#
# 可用工具如下：
# {tools}
#
# 请严格按照以下格式进行回应：
#
# Thought: 你的思考过程，用于分析问题、拆解任务和规划下一步行动。
# Action: 你决定采取的行动，必须是以下格式之一：
# - `{{tool_name}}[{{tool_input}}]`：调用一个可用工具。
# - `Finish[最终答案]`：当你认为已经获得最终答案时。
# - 当你收集到足够的信息，能够回答用户的最终问题时，你必须在`Action:`字段后使用 `Finish[最终答案]` 来输出最终答案。
#
#
# 现在，请开始解决以下问题：
# Question: {question}
# History: {history}
# """
#
# class ReActAgent:
#     def __init__(self, llm_client: HelloAgentsLLM, tool_executor: ToolExecutor, max_steps: int = 5):
#         self.llm_client = llm_client
#         self.tool_executor = tool_executor
#         self.max_steps = max_steps
#         self.history = []
#
#     def run(self, question: str):
#         self.history = []
#         current_step = 0
#
#         while current_step < self.max_steps:
#             current_step += 1
#             print(f"\n--- 第 {current_step} 步 ---")
#
#             tools_desc = self.tool_executor.getAvailableTools()
#             history_str = "\n".join(self.history)
#             prompt = REACT_PROMPT_TEMPLATE.format(tools=tools_desc, question=question, history=history_str)
#
#             messages = [{"role": "user", "content": prompt}]
#             response_text = self.llm_client.think(messages=messages)
#             if not response_text:
#                 print("错误：LLM未能返回有效响应。"); break
#
#             thought, action = self._parse_output(response_text)
#             if thought: print(f"🤔 思考: {thought}")
#             if not action: print("警告：未能解析出有效的Action，流程终止。"); break
#
#             if action.startswith("Finish"):
#                 # 如果是Finish指令，提取最终答案并结束
#                 final_answer = self._parse_action_input(action)
#                 print(f"🎉 最终答案: {final_answer}")
#                 return final_answer
#
#             tool_name, tool_input = self._parse_action(action)
#             if not tool_name or not tool_input:
#                 self.history.append("Observation: 无效的Action格式，请检查。"); continue
#
#             print(f"🎬 行动: {tool_name}[{tool_input}]")
#             tool_function = self.tool_executor.getTool(tool_name)
#             observation = tool_function(tool_input) if tool_function else f"错误：未找到名为 '{tool_name}' 的工具。"
#
#             print(f"👀 观察: {observation}")
#             self.history.append(f"Action: {action}")
#             self.history.append(f"Observation: {observation}")
#
#         print("已达到最大步数，流程终止。")
#         return None
#
#     def _parse_output(self, text: str):
#         # Thought: 匹配到 Action: 或文本末尾
#         thought_match = re.search(r"Thought:\s*(.*?)(?=\nAction:|$)", text, re.DOTALL)
#         # Action: 匹配到文本末尾
#         action_match = re.search(r"Action:\s*(.*?)$", text, re.DOTALL)
#         thought = thought_match.group(1).strip() if thought_match else None
#         action = action_match.group(1).strip() if action_match else None
#         return thought, action
#
#     def _parse_action(self, action_text: str):
#         match = re.match(r"(\w+)\[(.*)\]", action_text, re.DOTALL)
#         return (match.group(1), match.group(2)) if match else (None, None)
#
#     def _parse_action_input(self, action_text: str):
#         match = re.match(r"\w+\[(.*)\]", action_text, re.DOTALL)
#         return match.group(1) if match else ""
#
# if __name__ == '__main__':
#     llm = HelloAgentsLLM()
#     tool_executor = ToolExecutor()
#     search_desc = "一个网页搜索引擎。当你需要回答关于时事、事实以及在你的知识库中找不到的信息时，应使用此工具。"
#     tool_executor.registerTool("Search", search_desc, search)
#     agent = ReActAgent(llm_client=llm, tool_executor=tool_executor)
#     question = "华为最新的手机是哪一款？它的主要卖点是什么？"
#     agent.run(question)
# 弃用正则表达式，改为function calling （实际就是让大模型直接输出我们想要的格式，这里是json）
import json
from llm_client import HelloAgentsLLM
from tools import ToolExecutor, search


class ReActAgent:
    def __init__(self, llm_client: HelloAgentsLLM, tool_executor: ToolExecutor, max_steps: int = 5):
        self.llm_client = llm_client
        self.tool_executor = tool_executor
        self.max_steps = max_steps

    def run(self, question: str):
        current_step = 0

        # 1. 初始化标准对话历史消息队列（不再把 History 拼接到字符串 Prompt 中）
        messages = [
            {"role": "system", "content": "你是一个能够调用外部工具解决问题的智能助手。"},
            {"role": "user", "content": question}
        ]

        # 2. 获取注册工具的原生 JSON Schema 描述（Function Calling 所需的声明）
        tools_schema = self.tool_executor.get_tools_schema()

        while current_step < self.max_steps:
            current_step += 1
            print(f"\n--- 第 {current_step} 步 ---")

            # 3. 将工具声明和消息历史直接传给 LLM API
            response = self.llm_client.think(messages=messages, tools=tools_schema)
            if not response:
                print("错误：LLM未能返回有效响应。")
                break

            # 如果模型给出了思考/文本回答内容，直接输出
            if response.content:
                print(f"🤔 思考/回复: {response.content}")

            # 4. 检查模型是否发起了 Function Calling（原生工具调用请求）
            if not response.tool_calls:
                # 当模型没有再调用工具，而是直接返回文本时，说明任务完成，输出最终答案
                print(f"\n🎉 最终答案: {response.content}")
                return response.content

            # 将 LLM 的响应（包含 tool_calls）追加到对话历史中
            # messages.append(response.to_message())
            messages.append(response.model_dump())
            # 5. 处理模型请求调用的工具（原生支持单步多工具调用，这里逐个处理）
            for tool_call in response.tool_calls:
                tool_name = tool_call.function.name
                # 原生 API 已经自动将参数解析为 JSON/字典，无需正则！
                tool_args = json.loads(tool_call.function.arguments) if isinstance(tool_call.function.arguments,
                                                                                   str) else tool_call.function.arguments

                print(f"🎬 行动（调用工具）: {tool_name}({tool_args})")

                # 执行工具
                tool_function = self.tool_executor.getTool(tool_name)
                if tool_function:
                    try:
                        observation = tool_function(**tool_args)
                    except Exception as e:
                        observation = f"工具执行异常: {str(e)}"
                else:
                    observation = f"错误：未找到名为 '{tool_name}' 的工具。"

                print(f"👀 观察（工具返回）: {observation}")

                # 6. 将工具执行结果作为 'tool' 角色的消息喂回给大模型
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": tool_name,
                    "content": str(observation)
                })

        print("已达到最大步数，流程终止。")
        return None


if __name__ == '__main__':
    llm = HelloAgentsLLM()
    tool_executor = ToolExecutor()

    # 原生 Function Calling 需要标准的工具 Schema 定义（OpenAI / JSON Schema 格式）
    search_schema = {
        "type": "function",
        "function": {
            "name": "Search",
            "description": "一个网页搜索引擎。当你需要回答关于时事、事实以及在你的知识库中找不到的信息时，应使用此工具。",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "需要在搜索引擎中查询的关键词或问题"
                    }
                },
                "required": ["query"]
            }
        }
    }


    # 包装原 search 函数以适配参数解包
    def search_wrapper(query: str):
        return search(query)


    tool_executor.registerTool("Search", search_schema, search_wrapper)

    agent = ReActAgent(llm_client=llm, tool_executor=tool_executor)
    question = "华为最新的手机是哪一款？它的主要卖点是什么？"
    agent.run(question)