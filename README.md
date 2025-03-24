# Belk.com Google 搜索广告创建工具

本工具用于通过 Google Ads API 创建针对 Belk.com 的响应式搜索广告。

## 文件说明

- **belk_search_ads_creator.py** - 主脚本，用于创建 Google 搜索广告
- **google-ads.yaml** - Google Ads API 配置文件（需要填入您的 API 凭据）
- **auth_helper.py** - 辅助脚本，帮助获取 OAuth 凭据并更新配置文件
- **google_ads_auth_guide.md** - 详细的认证设置指南

## 快速开始

### 1. 准备认证

首先，需要设置 Google Ads API 认证。请按以下步骤操作：

1. 从 Google Cloud Console 获取 OAuth 客户端凭据并下载为 `client_secrets.json`
2. 运行认证助手获取所需令牌：
   ```
   python auth_helper.py --client_secrets=client_secrets.json
   ```
3. 在生成的 `google-ads.yaml` 文件中添加您的开发者令牌

### 2. 运行广告创建脚本

准备好认证后，可以运行主脚本创建广告：

```
python belk_search_ads_creator.py
```

默认情况下，脚本会：
- 使用客户 ID：525-050-7413
- 创建针对 Belk.com 的响应式搜索广告
- 添加适合服装和家居零售的关键词
- 设置美国主要城市的地理定位

## 重要说明

1. **配置文件位置**：脚本现已配置为从**当前目录**读取 `google-ads.yaml`，确保此文件与脚本位于同一目录
2. **日志记录**：所有操作都会记录到 `ad_creation_log.txt` 文件中，便于追踪问题
3. **广告系列状态**：新创建的广告系列默认为**暂停**状态，需要在 Google Ads 界面中手动激活

## 故障排除

如果遇到错误，请检查：

1. 配置文件是否正确填写所有必要的凭据
2. API 凭据是否有足够的权限操作指定的广告账户
3. 查看日志文件了解详细错误信息

## 自定义选项

您可以通过命令行参数自定义广告创建：

```
python belk_search_ads_creator.py --customer_id=YOUR-CUSTOMER-ID --customizer_attribute_name=YOUR-CUSTOM-NAME
```

详细选项请参考脚本说明或使用 `--help` 参数查看。
