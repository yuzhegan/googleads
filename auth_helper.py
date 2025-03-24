#!/usr/bin/env python
"""
Google Ads API 认证助手

这个脚本帮助您获取 Google Ads API 所需的刷新令牌。
请先从 Google Cloud Console 下载 OAuth 凭据 JSON 文件。
"""

import argparse
import os
import json
from google_auth_oauthlib.flow import InstalledAppFlow

# Google Ads API 所需的 OAuth 范围
SCOPES = ["https://www.googleapis.com/auth/adwords"]

def get_refresh_token(client_secrets_path):
    """获取 Google Ads API 的刷新令牌。"""
    
    # 检查文件是否存在
    if not os.path.exists(client_secrets_path):
        print(f"错误: OAuth 凭据文件 '{client_secrets_path}' 不存在。")
        print("请从 Google Cloud Console 下载 OAuth 凭据 JSON 文件。")
        return None
    
    # 从客户端秘钥文件创建 OAuth 流程
    try:
        flow = InstalledAppFlow.from_client_secrets_file(
            client_secrets_path,
            scopes=SCOPES
        )
        
        # 提示用户进行授权
        print("\n" + "="*80)
        print("即将在浏览器中打开 Google 授权页面。")
        print("请登录您的 Google 账户并授权应用访问 Google Ads 数据。")
        print("="*80 + "\n")
        
        # 运行本地服务器获取授权
        credentials = flow.run_local_server(port=8080)
        
        # 提取客户端信息
        with open(client_secrets_path, 'r') as f:
            client_info = json.load(f)['installed']
            client_id = client_info['client_id']
            client_secret = client_info['client_secret']
        
        # 显示结果
        print("\n" + "="*80)
        print("授权成功！以下是您的 OAuth 凭据:")
        print("="*80)
        print(f"客户端 ID: {client_id}")
        print(f"客户端密钥: {client_secret}")
        print(f"刷新令牌: {credentials.refresh_token}")
        print("="*80)
        
        # 更新配置文件
        yaml_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'google-ads.yaml')
        update_yaml_file(yaml_path, client_id, client_secret, credentials.refresh_token)
        
        return credentials.refresh_token
    except Exception as e:
        print(f"获取刷新令牌时出错: {str(e)}")
        return None

def update_yaml_file(yaml_path, client_id, client_secret, refresh_token):
    """更新 YAML 配置文件中的认证信息。"""
    try:
        # 读取现有文件
        with open(yaml_path, 'r') as f:
            yaml_content = f.read()
        
        # 替换占位符
        yaml_content = yaml_content.replace("YOUR-CLIENT-ID", client_id)
        yaml_content = yaml_content.replace("YOUR-CLIENT-SECRET", client_secret)
        yaml_content = yaml_content.replace("YOUR-REFRESH-TOKEN", refresh_token)
        
        # 写回文件
        with open(yaml_path, 'w') as f:
            f.write(yaml_content)
        
        print(f"\n已自动更新配置文件: {yaml_path}")
        print("请记得还需要手动添加您的开发者令牌到此文件中。")
        
        # 重点提示使用当前目录的文件
        print("\n\u91cd要提示: 脚本已配置为使用当前目录下的 yaml 文件。")
        print(f"请确保保留此配置文件在脚本所在目录: {yaml_path}\n")
    
    except Exception as e:
        print(f"更新配置文件时出错: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Google Ads API 认证助手")
    parser.add_argument(
        "--client_secrets",
        type=str,
        default="client_secrets.json",
        help="从 Google Cloud Console 下载的 OAuth 客户端凭据 JSON 文件的路径"
    )
    
    args = parser.parse_args()
    get_refresh_token(args.client_secrets)
