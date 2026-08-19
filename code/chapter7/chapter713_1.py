from chapter721_1_my_llm import MyLLM


llm = MyLLM(
    provider="ollama",
    model="qwen2.5:3b",
    base_url="http://localhost:11434/v1"
)


messages = [
    {
        "role": "user",
        "content": "你好，介绍一下自己"
    }
]


response_stream = llm.think(messages)


for chunk in response_stream:
    pass