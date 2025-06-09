import streamlit as st
import os
from utils.load_info import load_info
from langchain_openai import ChatOpenAI
from langchain_deepseek import ChatDeepSeek
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# 项目根目录
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
# prompt文件路径
prompt_root = os.path.join(project_root, 'data/Prompt')

# LangChain 配置
os.environ["LANGCHAIN_TRACING"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "AIGC"
os.environ["LANGCHAIN_API_KEY"] = load_info("keys")["LANGCHAIN_API_KEY"]

# 设置页面标题和图标
st.set_page_config(page_title="AIGC 聊天机器人", page_icon="🤖")

st.sidebar.info( 
    "欢迎使用 AIGC 聊天机器人！\n\n"
)

# 读取prompt文件
def read_prompt_file(dept):
    with open(os.path.join(prompt_root,f"{dept}.md"), "r") as file:
        return file.read()

st.sidebar.markdown("### 助手配置")
domain = st.sidebar.selectbox("选择助手领域",("通用领域", "医疗助手", "教育助手", "法律助手"))

if domain == "医疗助手":
    dept = st.sidebar.selectbox("选择科室", ("男科", "内科", "妇产科", "肿瘤科", "儿科", "外科"))
    title = domain + " - " + dept
    # 读取prompt
    system = read_prompt_file(dept)
else:
    title = domain
    system = f"你是一个专业的{domain}助手。请根据用户的问题提供准确、有帮助的回答。"

# 模型列表
models = load_info("models").keys()

st.sidebar.markdown("### 模型配置")
selected_model = st.sidebar.selectbox("选择大模型",models)
temperature = st.sidebar.slider("温度", min_value=0.0, max_value=1.0, value=0.5, step=0.1)
max_tokens = st.sidebar.slider("最大生成Token数", min_value=10, max_value=2048, value=512, step=10)

st.sidebar.markdown("### 配置说明")
st.sidebar.info(
    "温度：控制生成文本的随机性，值越高，生成的文本越随机。\n最大生成Token数：控制生成文本的长度，值越高，生成的文本越长。"
)

# 自定义CSS，美化界面
st.markdown("""
<style>
    .stApp {
        background_color: #f0f2f6;
    }
    .stChatInputContainer > div {
        background-color: white;
    }
    [data-testid="stChatMessageContent"] {
        background-color: #e6e6fa;
        border-radius: 0.5rem;
        padding: 0.75rem;
    }
    [data-testid="stChatMessageContent"][aria-label="assistant message"] {
        background-color: #d1e7dd; /* 浅绿色背景 */
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 0.5rem;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    h1 {
        color: #333;
    }
</style>
""", unsafe_allow_html=True)

st.title(f"💬 AIGC {title}")
st.caption(f"[{selected_model}] Powered by AIE-52 G5")

# 初始化聊天记录 (使用 session_state)
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "您好！我是AIGC 聊天机器人，有什么可以帮助您的吗？"}
    ]

# 显示聊天记录
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# 获取模型配置
model_info = load_info("models")[selected_model]
print(f"模型配置: {model_info}")
model_name = model_info["model_name"]
base_url = model_info["base_url"]
api_key = model_info["api_key"]

if selected_model == "DeepSeek-Chat":
    Model = ChatDeepSeek
else:
    Model = ChatOpenAI

# 定义模型
llm = Model(
    model=model_name,
    base_url=base_url,
    api_key=api_key,
    temperature=temperature,
    max_tokens=max_tokens,
    streaming=True
    )

# 定义提示模板
prompt_template = ChatPromptTemplate.from_messages([
    ("system", system),
    ("human", "{user_input}")
])

# 创建聊天链
chain = prompt_template | llm | StrOutputParser()

# 处理用户输入
if prompt := st.chat_input("请输入您的问题..."):
    # 将用户消息添加到聊天记录
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # 获取机器人回复 (显示加载状态)
    with st.chat_message("assistant"):
        try:
            print("开始处理消息...")
            with st.spinner("思考中..."):
                # 创建空白占位符用于流式输出
                response_placeholder = st.empty()
                response_content = ""
                print("开始处理消息...")
                print(f"处理消息: {prompt}")
                # 使用LangChain处理消息并实现流式输出
                for chunk in chain.stream({"user_input": prompt}):
                    print('开始处理消息的片段...')
                    # print(chunk.content, end='', flush=True)
                    response_content += chunk
                    response_placeholder.markdown(response_content + "▌")  # 添加光标效果
                
                # 完成后显示最终内容
                import re
                think_content_match = re.search(r'<think>(.*?)</think>', response_content, re.DOTALL)
                if think_content_match:
                    think_text = think_content_match.group(1).strip()
                    # 移除原始response_content中的think标签内容
                    response_content_without_think = re.sub(r'<think>.*?</think>', '', response_content, flags=re.DOTALL)
                    st.markdown("\n") # 在</think>标签后进行换行
                    with st.expander("点击查看思考内容"): # 设置点击可以进行收起来
                        st.markdown(think_text)
                    response_placeholder.markdown(response_content_without_think)
                else:
                    response_placeholder.markdown(response_content)

        except Exception as e:
            print(f"Error: {e}")
            response_placeholder.markdown("抱歉，我无法回答您的问题。")
    
    # 将机器人回复添加到聊天记录
    st.session_state.messages.append({"role": "assistant", "content": response_content})

# 清空聊天记录按钮
if len(st.session_state.messages) > 1:
    if st.button("🗑️ 清空对话"):
        st.session_state.messages = [
            {"role": "assistant", "content": "您好！我是AIGC 聊天机器人，有什么可以帮助您的吗？"}
        ]
        st.rerun()