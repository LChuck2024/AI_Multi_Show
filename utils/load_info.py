import json
import os

def load_info(info_type,info_name, json_file='config.json'):
    """从JSON文件中加载指定的模型信息。
    Args:
        info_type (str): 信息类型，如 'models' 或 'keys'。
        info_name (str): 要加载的信息名称。
        json_file (str): 包含信息的JSON文件路径。
    Returns:
        str: 加载的信息值。
    """
    # 获取当前文件所在目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(current_dir, json_file)
    # 读取配置文件
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except json.JSONDecodeError:
        config = {}
    
    # 如果key不存在，提示异常
    if info_name not in config[info_type]:
        print(f"未找到{info_name}的信息，请核对配置文件！")
    
    return config[info_type][info_name]


if __name__ == '__main__':
    print(load_info('models','DeepSeek-Chat'))
    # print(load_info('keys','LANGCHAIN_API_KEY'))