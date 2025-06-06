import streamlit as st
import os
from utils.load_key import load_key
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
os.environ["LANGCHAIN_API_KEY"] = load_key("LANGCHAIN_API_KEY")

# DeepSeek API 配置
DEEPSEEK_MODEL = "deepseek-chat"
DEEPSEEK_API_KEY = load_key("DEEPSEEK_API_KEY")
DEEPSEEK_URL = "https://api.deepseek.com/v1/"

# 设置页面标题和图标
st.set_page_config(page_title="AIGC 聊天机器人", page_icon="🤖")

# st.sidebar.title("AIGC 领域")
st.sidebar.info( 
    "欢迎使用 AIGC 聊天机器人！\n\n"
)

# 读取prompt文件
def read_prompt_file(dept):
    with open(os.path.join(prompt_root,f"{dept}.md"), "r") as file:
        return file.read()

st.sidebar.header("助手领域")
domain = st.sidebar.selectbox("选择助手领域",("通用领域", "医疗助手", "教育助手", "法律助手"))

if domain == "医疗助手":
    dept = st.sidebar.selectbox("选择科室", ("男科", "内科", "妇产科", "肿瘤科", "儿科", "外科"))
    title = domain + " - " + dept
    # 读取prompt
    system = read_prompt_file(dept)
else:
    title = domain
    system = f"你是一个专业的{domain}助手。请根据用户的问题提供准确、有帮助的回答。"

# 侧边栏信息
st.sidebar.header("模型配置")
if st.sidebar.checkbox("启用流式输出", value=True):
    stream_output = True
else:
    stream_output = False

temperature = st.sidebar.slider("温度", min_value=0.0, max_value=1.0, value=0.5, step=0.1)
max_tokens = st.sidebar.slider("最大生成Token数", min_value=10, max_value=2048, value=512, step=10)


st.sidebar.header("使用说明")
st.sidebar.info(
    "选择一个领域后，并选择一个模型参数。在输入框中输入您的问题，然后点击发送按钮即可开始对话。"
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
st.caption("Powered by AIE-52 G5")

# 初始化聊天记录 (使用 session_state)
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "您好！我是AIGC 聊天机器人，有什么可以帮助您的吗？"}
    ]

# 显示聊天记录
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# 初始化LangChain ChatDeepSeek
llm = ChatDeepSeek(
    model=DEEPSEEK_MODEL,
    base_url=DEEPSEEK_URL,
    api_key=DEEPSEEK_API_KEY,
    temperature=temperature,
    max_tokens=max_tokens,
    streaming=stream_output
    )

# 定义提示模板
prompt_template = ChatPromptTemplate.from_messages([
    ("system", system),
    ("human", "{user_input}")
])

# 创建聊天链
chain = prompt_template | llm | StrOutputParser()

# 获取DeepSeek响应的函数
def get_deepseek_response(user_message, chat_history):
    if not DEEPSEEK_API_KEY:
        return "错误：DEEPSEEK_API_KEY 未设置。请在环境变量中设置您的API密钥。"
    
    try:
        # 构建包含聊天历史的上下文
        context = {
            "user_input": user_message,
            "chat_history": "\n".join([f"{msg['role']}: {msg['content']}" for msg in chat_history])
        }
        
        # 使用LangChain链处理消息
        response = chain.invoke(context)
        return response
    except Exception as e:
        st.error(f"请求失败: {e}")
        return "抱歉，处理请求时发生错误。"

# 处理用户输入
if prompt := st.chat_input("请输入您的问题..."):
    # 将用户消息添加到聊天记录
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # 获取机器人回复 (显示加载状态)
    with st.chat_message("assistant"):
        with st.spinner("思考中..."):
            # 创建空白占位符用于流式输出
            response_placeholder = st.empty()
            response_content = ""
            
            # 使用LangChain处理消息并实现流式输出
            for chunk in chain.stream({"domain": domain, "user_input": prompt}):
                response_content += chunk
                response_placeholder.markdown(response_content + "▌")  # 添加光标效果
            
            # 完成后显示最终内容
            response_placeholder.markdown(response_content)
    
    # 将机器人回复添加到聊天记录
    st.session_state.messages.append({"role": "assistant", "content": response_content})

# 清空聊天记录按钮
if len(st.session_state.messages) > 1:
    if st.button("🗑️ 清空对话"):
        st.session_state.messages = [
            {"role": "assistant", "content": "您好！我是AIGC 聊天机器人，有什么可以帮助您的吗？"}
        ]
        st.rerun()


# 提示API Key设置
if not DEEPSEEK_API_KEY:
    st.error("警告：DEEPSEEK_API_KEY 环境变量未设置。请设置API密钥后刷新页面。")
    st.info("如何设置API Key:\n1. 获取您的DeepSeek API Key。\n2. 在您的运行环境中设置名为 `DEEPSEEK_API_KEY` 的环境变量，值为您的API Key。例如，在终端中使用 `export DEEPSEEK_API_KEY='your_actual_api_key'` (Linux/macOS) 或在 `.env` 文件中添加 `DEEPSEEK_API_KEY='your_actual_api_key'`。")