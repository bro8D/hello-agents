# from dotenv import load_dotenv
# # 加载 .env 文件中的环境变量
# load_dotenv()
#
# import os
# import serpapi
# from typing import Dict, Any
#
#
# def search(query: str) -> str:
#     """
#     一个基于SerpApi的实战网页搜索引擎工具。
#     """
#     print(f"🔍 正在执行 [SerpApi] 网页搜索: {query}")
#     try:
#         api_key = os.getenv("SERPAPI_API_KEY")
#         if not api_key:
#             return "错误：SERPAPI_API_KEY 未在 .env 文件中配置。"
#
#         # 1. 实例化 Client
#         client = serpapi.Client(api_key=api_key)
#
#         # 2. 调用 client.search 传入参数字典
#         results = client.search({
#             "engine": "google",
#             "q": query,
#             "gl": "cn",
#             "hl": "zh-cn",
#         })
#
#         # 智能解析：优先寻找最直接的答案
#         if "answer_box_list" in results:
#             return "\n".join(results["answer_box_list"])
#         if "answer_box" in results and "answer" in results["answer_box"]:
#             return results["answer_box"]["answer"]
#         if "knowledge_graph" in results and "description" in results["knowledge_graph"]:
#             return results["knowledge_graph"]["description"]
#         if "organic_results" in results and results["organic_results"]:
#             snippets = [
#                 f"[{i + 1}] {res.get('title', '')}\n{res.get('snippet', '')}"
#                 for i, res in enumerate(results["organic_results"][:3])
#             ]
#             return "\n\n".join(snippets)
#
#         return f"对不起，没有找到关于 '{query}' 的信息。"
#
#     except Exception as e:
#         return f"搜索时发生错误: {e}"
#
# from typing import Dict, Any
#
# class ToolExecutor:
#     """
#     一个工具执行器，负责管理和执行工具。
#     """
#     def __init__(self):
#         self.tools: Dict[str, Dict[str, Any]] = {}
#
#     def registerTool(self, name: str, description: str, func: callable):
#         """
#         向工具箱中注册一个新工具。
#         """
#         if name in self.tools:
#             print(f"警告：工具 '{name}' 已存在，将被覆盖。")
#
#         self.tools[name] = {"description": description, "func": func}
#         print(f"工具 '{name}' 已注册。")
#
#     def getTool(self, name: str) -> callable:
#         """
#         根据名称获取一个工具的执行函数。
#         """
#         return self.tools.get(name, {}).get("func")
#
#     def getAvailableTools(self) -> str:
#         """
#         获取所有可用工具的格式化描述字符串。
#         """
#         return "\n".join([
#             f"- {name}: {info['description']}"
#             for name, info in self.tools.items()
#         ])
#
#
# # --- 工具初始化与使用示例 ---
# if __name__ == '__main__':
#     # 1. 初始化工具执行器
#     toolExecutor = ToolExecutor()
#
#     # 2. 注册我们的实战搜索工具
#     search_description = "一个网页搜索引擎。当你需要回答关于时事、事实以及在你的知识库中找不到的信息时，应使用此工具。"
#     toolExecutor.registerTool("Search", search_description, search)
#
#     # 3. 打印可用的工具
#     print("\n--- 可用的工具 ---")
#     print(toolExecutor.getAvailableTools())
#
#     # 4. 智能体的Action调用，这次我们问一个实时性的问题
#     print("\n--- 执行 Action: Search['英伟达最新的GPU型号是什么'] ---")
#     tool_name = "Search"
#     tool_input = "英伟达最新的GPU型号是什么"
#
#     tool_function = toolExecutor.getTool(tool_name)
#     if tool_function:
#         observation = tool_function(tool_input)
#         print("--- 观察 (Observation) ---")
#         print(observation)
#     else:
#         print(f"错误：未找到名为 '{tool_name}' 的工具。")


import os
from typing import Any, Callable, Dict, List, Union
from dotenv import load_dotenv
import serpapi

# 加载 .env 文件中的环境变量
load_dotenv()


def search(query: str) -> str:
    """一个基于SerpApi的实战网页搜索引擎工具。"""
    print(f"🔍 正在执行 [SerpApi] 网页搜索: {query}")
    try:
        api_key = os.getenv("SERPAPI_API_KEY")
        if not api_key:
            return "错误：SERPAPI_API_KEY 未在 .env 文件中配置。"

        # 1. 实例化 Client
        client = serpapi.Client(api_key=api_key)

        # 2. 调用 client.search 传入参数字典
        results = client.search({
            "engine": "google",
            "q": query,
            "gl": "cn",
            "hl": "zh-cn",
        })

        # 智能解析：优先寻找最直接的答案
        if "answer_box_list" in results:
            return "\n".join(results["answer_box_list"])
        if "answer_box" in results and "answer" in results["answer_box"]:
            return results["answer_box"]["answer"]
        if (
            "knowledge_graph" in results
            and "description" in results["knowledge_graph"]
        ):
            return results["knowledge_graph"]["description"]
        if "organic_results" in results and results["organic_results"]:
            snippets = [
                f"[{i + 1}] {res.get('title', '')}\n{res.get('snippet', '')}"
                for i, res in enumerate(results["organic_results"][:3])
            ]
            return "\n\n".join(snippets)

        return f"对不起，没有找到关于 '{query}' 的信息。"

    except Exception as e:
        return f"搜索时发生错误: {e}"


class ToolExecutor:
    """一个工具执行器，负责管理和执行工具，并提供原生 Function Calling 所需的 Schema。"""

    def __init__(self):
        self.tools: Dict[str, Dict[str, Any]] = {}
        self.tools_schema: List[Dict[str, Any]] = (
            []
        )  # 存储原生 Function Calling Schema

    def registerTool(
        self,
        name: str,
        description_or_schema: Union[str, Dict[str, Any]],
        func: Callable,
        schema: Dict[str, Any] = None,
    ):
        """向工具箱中注册一个新工具。

        支持三种注册形式：
        1. 传入名称、JSON Schema 字典、函数：registerTool("Search", search_schema, search)
        2. 传入名称、字符串描述、函数、JSON Schema 字典：registerTool("Search", "描述...", search,
        search_schema)
        3. 仅传入名称、字符串描述、函数（旧版兼容）：registerTool("Search", "描述...", search)
        """
        if name in self.tools:
            print(f"警告：工具 '{name}' 已存在，将被覆盖。")

        # 判断 description_or_schema 的类型
        if isinstance(description_or_schema, dict):
            # 如果第二个参数直接传的是 Schema 字典
            actual_schema = description_or_schema
            desc_text = actual_schema.get("function", {}).get(
                "description", name
            )
        else:
            desc_text = str(description_or_schema)
            # 如果单独提供了 schema 参数则使用，否则生成默认极简 Schema
            actual_schema = schema or {
                "type": "function",
                "function": {
                    "name": name,
                    "description": desc_text,
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "工具调用的输入参数",
                            }
                        },
                        "required": ["query"],
                    },
                },
            }

        # 保存工具函数和描述
        self.tools[name] = {"description": desc_text, "func": func}

        # 维护 Function Calling 的 Schema 列表
        # 如果已经存在同名工具，先更新 Schema
        self.tools_schema = [
            s
            for s in self.tools_schema
            if s.get("function", {}).get("name") != name
        ]
        self.tools_schema.append(actual_schema)

        print(f"工具 '{name}' 已成功注册。")

    def getTool(self, name: str) -> Callable:
        """根据名称获取一个工具的执行函数。"""
        return self.tools.get(name, {}).get("func")

    def getAvailableTools(self) -> str:
        """获取所有可用工具的格式化描述字符串（兼容旧版 Prompt 方式）。"""
        return "\n".join([
            f"- {name}: {info['description']}"
            for name, info in self.tools.items()
        ])

    def get_tools_schema(self) -> List[Dict[str, Any]]:
        """获取所有已注册工具的原生 Function Calling Schema 列表。"""
        return self.tools_schema


# --- 工具初始化与使用示例 ---
if __name__ == "__main__":
    toolExecutor = ToolExecutor()

    # 1. 定义标准的 OpenAI Function Calling Schema
    search_schema = {
        "type": "function",
        "function": {
            "name": "Search",
            "description": (
                "一个网页搜索引擎。当你需要回答关于时事、事实以及在你的知识库中找不到的信息时，应使用此工具。"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "需要在搜索引擎中查询的关键词或短语",
                    }
                },
                "required": ["query"],
            },
        },
    }

    # 2. 包装 search 函数以接受关键词参数（也可直接定义为 def search_wrapper(query: str): return search(query)）
    def search_wrapper(query: str):
        return search(query)

    # 3. 注册工具（传入 Schema 字典）
    toolExecutor.registerTool("Search", search_schema, search_wrapper)

    # 4. 测试获取 Schema (专供 ReActAgent 使用)
    print("\n--- 导出的 原生 Function Calling Schema ---")
    import json

    print(json.dumps(toolExecutor.get_tools_schema(), indent=2, ensure_ascii=False))

    # 5. 测试执行工具
    print("\n--- 执行 Action: Search(query='英伟达最新的GPU型号是什么') ---")
    tool_name = "Search"
    tool_args = {"query": "英伟达最新的GPU型号是什么"}

    tool_function = toolExecutor.getTool(tool_name)
    if tool_function:
        observation = tool_function(**tool_args)
        print("\n--- 观察 (Observation) ---")
        print(observation)
    else:
        print(f"错误：未找到名为 '{tool_name}' 的工具。")