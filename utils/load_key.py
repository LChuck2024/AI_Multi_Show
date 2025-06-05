import json
import os

def load_key(key_name, json_file='config.json'):
    """从JSON文件中加载指定的key值，如果不存在则提示用户输入
    
    Args:
        key_name (str): 要获取的key名称
        json_file (str): JSON配置文件路径，默认为'config.json'
        
    Returns:
        str: 获取到的key值
    """
    # 获取当前文件所在目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(current_dir, json_file)
    
    # 如果配置文件不存在，创建一个空的配置文件
    if not os.path.exists(json_path):
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump({}, f, indent=4)
    
    # 读取配置文件
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except json.JSONDecodeError:
        config = {}
    
    # 如果key不存在，提示用户输入
    if key_name not in config:
        print(f"未找到{key_name}，请输入:")
        key_value = input().strip()
        
        # 将新的key-value保存到配置文件
        config[key_name] = key_value
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
    
    return config[key_name]

def save_key(key_name, key_value, json_file='config.json'):
    """保存key值到JSON文件
    
    Args:
        key_name (str): key名称
        key_value (str): key值
        json_file (str): JSON配置文件路径，默认为'config.json'
    """
    # 获取当前文件所在目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(current_dir, json_file)
    
    # 如果配置文件不存在，创建一个空的配置文件
    if not os.path.exists(json_path):
        config = {}
    else:
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except json.JSONDecodeError:
            config = {}
    
    # 更新配置
    config[key_name] = key_value
    
    # 保存到文件
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4, ensure_ascii=False)

if __name__ == '__main__':
    key_name = 'DEEPSEEK_API_KEY'
    print(load_key(key_name))