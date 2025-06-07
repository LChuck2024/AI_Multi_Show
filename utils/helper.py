from openai import OpenAI

openai_api_key = "EMPTY"
openai_api_base = "http://direct.virtaicloud.com:25595/v1"

client = OpenAI(
    api_key=openai_api_key,
    base_url=openai_api_base,
)

chat_response = client.chat.completions.create(
    model="Medical_Qwen3_8B_Large_Language_Model",
    messages=[
        {"role": "system", "content": "你是一个很有用的助手。"},
        {"role": "user", "content": "中华人民共和国的首都是哪里？"},
    ]
)
print("Chat response:", chat_response)