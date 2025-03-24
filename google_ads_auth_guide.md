# Google Ads API 认证指南

本指南将帮助您完成 Google Ads API 认证设置过程，以便您能够成功运行广告创建脚本。

## 第一步：获取开发者令牌

1. 访问 [Google Ads API 中心](https://developers.google.com/google-ads/api/docs/first-call/overview)
2. 登录您的 Google Ads 账户
3. 创建或选择现有项目
4. 申请开发者令牌
   - 注意：如果您是第一次使用 Google Ads API，可能需要提交申请表并等待审批
   - 对于测试目的，您可以使用测试账户而无需批准

## 第二步：创建 OAuth 凭据

1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 选择您的项目
3. 导航至 "API 和服务" > "凭据"
4. 点击 "创建凭据" > "OAuth 客户端 ID"
5. 应用类型选择 "桌面应用"
6. 输入名称（如 "Google Ads API Client"）并创建
7. 记下生成的客户端 ID 和客户端密钥

## 第三步：获取刷新令牌

1. 使用 Google 提供的 [OAuth2 工具](https://developers.google.com/google-ads/api/docs/oauth/playground)
2. 或者安装 Google 的认证库并运行以下 Python 脚本：

```python
from google_auth_oauthlib.flow import InstalledAppFlow

# 定义 OAuth2 范围
SCOPES = ["https://www.googleapis.com/auth/adwords"]

# 创建 OAuth2 流程
flow = InstalledAppFlow.from_client_secrets_file(
    "client_secrets.json",  # 从 Google Cloud Console 下载的 OAuth 凭据文件
    scopes=SCOPES
)

# 运行本地服务器以获取认证码
credentials = flow.run_local_server(port=8080)

# 打印刷新令牌
print("Refresh token:", credentials.refresh_token)
```

注意：为了使用上述脚本，您需要从 Google Cloud Console 下载 OAuth 凭据为 JSON 文件（通常命名为 "client_secrets.json"）。

## 第四步：更新配置文件

打开 `google-ads.yaml` 文件，填入您获取的凭据：

```yaml
developer_token: "YOUR-DEVELOPER-TOKEN"  # 替换为您的开发者令牌
login_customer_id: "5250507413"  # 您的客户 ID，不带破折号
client_id: "YOUR-CLIENT-ID"  # 替换为您的客户端 ID
client_secret: "YOUR-CLIENT-SECRET"  # 替换为您的客户端密钥
refresh_token: "YOUR-REFRESH-TOKEN"  # 替换为您的刷新令牌
```

## 第五步：移动配置文件至主目录（可选）

如果您希望脚本直接从主目录读取配置文件，可以将 `google-ads.yaml` 文件复制到您的主目录：

```bash
cp "/Users/mac/Documents/media buy/google Ads/google-ads.yaml" /Users/mac/google-ads.yaml
```

## 故障排除

1. **凭据错误**：确保所有 ID、令牌和密钥都正确无误，不包含额外的空格
2. **权限问题**：确保您的 Google 账户有权访问指定的客户 ID
3. **API 配额**：检查您是否超出了 Google Ads API 配额限制
4. **依赖包**：确保安装了所有必要的 Python 包：
   ```
   pip install google-ads google-auth google-auth-oauthlib google-auth-httplib2
   ```

如需更详细的信息，请参考 [Google Ads API 官方文档](https://developers.google.com/google-ads/api/docs/start)。
