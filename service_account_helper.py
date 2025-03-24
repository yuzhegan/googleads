#!/usr/bin/env python
"""
Google Ads API 服务账号设置助手

这个脚本帮助您设置 Google Ads API 的服务账号认证。
"""

import os
import sys
import argparse
import json
from datetime import datetime

# 日志文件路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(SCRIPT_DIR, "service_account_setup.log")

def log_message(message):
    """将消息记录到日志文件"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {message}\n")
    print(message)

def setup_service_account(key_file_path, developer_token=None, customer_id="5250507413"):
    """设置服务账号配置"""
    # 确保密钥文件存在
    if not os.path.exists(key_file_path):
        log_message(f"错误: 服务账号密钥文件不存在: {key_file_path}")
        log_message("请从 Google Cloud Console 下载服务账号密钥文件 (JSON 格式)")
        return False
    
    # 尝试读取 JSON 文件以验证其格式
    try:
        with open(key_file_path, 'r') as f:
            key_data = json.load(f)
            
        # 验证是否为有效的服务账号密钥文件
        required_fields = ['type', 'project_id', 'private_key_id', 'private_key', 'client_email']
        for field in required_fields:
            if field not in key_data:
                log_message(f"错误: 密钥文件缺少必要字段: {field}")
                log_message("请确保下载的是有效的服务账号密钥文件")
                return False
                
        if key_data['type'] != 'service_account':
            log_message(f"错误: 不是有效的服务账号密钥文件，类型为: {key_data['type']}")
            log_message("请确保下载的是服务账号密钥文件")
            return False
            
        log_message(f"验证成功: 有效的服务账号密钥文件")
        log_message(f"服务账号邮箱: {key_data['client_email']}")
        log_message(f"项目 ID: {key_data['project_id']}")
        
    except json.JSONDecodeError:
        log_message("错误: 密钥文件不是有效的 JSON 格式")
        return False
    except Exception as e:
        log_message(f"验证密钥文件时出错: {str(e)}")
        return False

    # 创建 google-ads.yaml 配置文件
    yaml_path = os.path.join(SCRIPT_DIR, "google-ads.yaml")
    
    # 确定密钥文件的相对路径
    rel_path = os.path.relpath(key_file_path, SCRIPT_DIR)
    
    # 构建 YAML 内容
    yaml_content = f"""# Google Ads API 服务账号配置
# 由 service_account_helper.py 自动生成于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

# 开发者令牌 - 在 Google Ads API 中心注册应用后获得
developer_token: "{developer_token or 'YOUR-DEVELOPER-TOKEN'}"

# 客户 ID (不带破折号)
login_customer_id: "{customer_id.replace('-', '')}"

# 服务账号密钥文件路径
json_key_file_path: "{rel_path}"

# API 设置
use_proto_plus: True
timeout: 3600
login_timezone: "America/New_York"
"""

    # 写入配置文件
    try:
        with open(yaml_path, 'w') as f:
            f.write(yaml_content)
        log_message(f"成功创建配置文件: {yaml_path}")
        
        if not developer_token or developer_token == 'YOUR-DEVELOPER-TOKEN':
            log_message("\n重要提示: 您需要在配置文件中添加您的开发者令牌!")
            log_message("请编辑 google-ads.yaml 文件，将 YOUR-DEVELOPER-TOKEN 替换为实际的开发者令牌")
            
        log_message("\n以下是使用服务账号方式的步骤:")
        log_message("1. 确保已在 Google Cloud Console 创建了服务账号")
        log_message("2. 确保已授予服务账号访问 Google Ads 账户的权限")
        log_message("3. 在 Google Ads 管理界面的「管理员权限和访问权限」中添加服务账号邮箱")
        log_message("4. 确保已设置了开发者令牌")
        
        return True
    except Exception as e:
        log_message(f"创建配置文件时出错: {str(e)}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Google Ads API 服务账号设置助手")
    parser.add_argument(
        "--key_file",
        type=str,
        required=True,
        help="服务账号密钥文件 (JSON) 的路径"
    )
    parser.add_argument(
        "--developer_token",
        type=str,
        help="Google Ads API 开发者令牌"
    )
    parser.add_argument(
        "--customer_id",
        type=str,
        default="525-050-7413",
        help="Google Ads 客户 ID"
    )
    
    args = parser.parse_args()
    
    # 初始化日志文件
    with open(LOG_FILE, "w") as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始服务账号设置日志\n")
        
    setup_service_account(args.key_file, args.developer_token, args.customer_id)
