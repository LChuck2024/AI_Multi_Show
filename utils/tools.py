import datetime
from langchain.tools import tool

@tool
def get_current_date():
    """ 获取当前日期 """
    return datetime.datetime.now().strftime("%Y-%m-%d")