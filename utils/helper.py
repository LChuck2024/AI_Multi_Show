# Qwen3-32B
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

system = '你是一个助手'
prompt = '请用中文回答：'

# 定义提示模板
prompt_template = ChatPromptTemplate.from_messages([
    ("system", system),
    ("human", "{user_input}")
])

llm = ChatOpenAI(
    openai_api_base='https://ms-ens-51dda1d6-fa99.api-inference.modelscope.cn/v1',
    openai_api_key='2fd43260-bee2-44df-998d-7c8b24495b59',
    model_name='unsloth/Qwen3-32B-GGUF',
    streaming=True
)

chat = prompt_template | llm | StrOutputParser()

response = chat.stream({"user_input": prompt})
response_content = ""
for chunk in response:
    print(chunk)
    response_content += chunk
    print(chunk.content, end='', flush=True)
print(response_content)