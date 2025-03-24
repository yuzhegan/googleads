#!/usr/bin/env python
# Belk.com Search Ads Creator for Google Ads API

import argparse
import sys
import uuid
import os
import time
import socket
import requests
from datetime import datetime
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
import yaml

# Belk.com 特定的关键字
KEYWORD_TEXT_EXACT = "belk department store"
KEYWORD_TEXT_PHRASE = "belk online shopping"
KEYWORD_TEXT_BROAD = "clothing deals belk"

# 地理定位 - 美国主要城市
GEO_LOCATION_1 = "New York"
GEO_LOCATION_2 = "Los Angeles"
GEO_LOCATION_3 = "Chicago"

# 设置地理定位的语言和国家代码
LOCALE = "en"
COUNTRY_CODE = "US"

# 保存路径
SAVE_PATH = "/Users/mac/Documents/media buy/google Ads"
LOG_FILE = os.path.join(SAVE_PATH, "ad_creation_log.txt")

# Belk.com 的最终URL
FINAL_URL = "https://www.belk.com/?cm_mmc=AFL-Ebates+Performance+Marketing%2C+Inc.+dba+Rakuten+Rewards-11602495-SKUcategory-&cjevent=abd6d59307ed11f0824a010e0a1cb825&click_id=abd6d59307ed11f0824a010e0a1cb825&cjdata=MXxOfDB8WXwxNzQ2NjI1NzgyMDEx&ogmap=AFF%7CRTN%7C46157%7CSTND%7CMULTI%7CSITEWIDE%7C%7C%7C%7C"

def log_message(message):
    """将消息记录到日志文件"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {message}\n")
    print(message)

def modify_config_for_proxy(yaml_path, proxy=None):
    """修改配置文件以使用代理"""
    try:
        # 读取现有配置
        with open(yaml_path, 'r') as f:
            config = yaml.safe_load(f)
            
        # 添加代理设置
        if proxy:
            config['proxy'] = proxy
            log_message(f"已添加代理设置: {proxy}")
            
        # 增加超时设置
        config['timeout'] = 60000  # 60秒
        
        # 写回配置
        with open(yaml_path, 'w') as f:
            yaml.dump(config, f)
            
        log_message(f"已更新配置文件 {yaml_path} 的网络设置")
        return True
    except Exception as e:
        log_message(f"修改配置文件时出错: {str(e)}")
        return False

def create_mock_ad(customer_id):
    """创建模拟广告数据用于测试"""
    log_message("⚠️ 使用模拟模式 - 仅用于测试 ⚠️")
    log_message(f"为客户 ID {customer_id} 创建模拟广告")
    
    log_message("✓ 已创建模拟预算: campaign_budget/1234567890")
    log_message("✓ 已创建模拟广告系列: campaign/1234567890")
    log_message("✓ 已创建模拟广告组: ad_group/1234567890")
    log_message("✓ 已创建模拟广告: ad_group_ad/1234567890")
    log_message("✓ 已添加3个模拟关键词")
    log_message("✓ 已添加模拟地理定位")
    
    log_message("\n模拟广告创建完成。真实广告将在网络连接恢复后创建。")
    log_message("\n⚠️ 这只是模拟数据，未实际提交到 Google Ads API ⚠️")

def main(client, customer_id, customizer_attribute_name=None):
    """
    创建完整的搜索广告系列
    
    Args:
        client: 初始化的GoogleAdsClient实例
        customer_id: 客户ID
        customizer_attribute_name: 自定义属性名称（可选）
    """
    log_message(f"开始为客户 ID {customer_id} 创建广告")
    
    # 如果提供了自定义属性名称，创建并链接自定义属性
    if customizer_attribute_name:
        customizer_attribute_resource_name = create_customizer_attribute(
            client, customer_id, customizer_attribute_name
        )
        link_customizer_attribute_to_customer(
            client, customer_id, customizer_attribute_resource_name
        )

    # 创建预算（可以由多个广告系列共享）
    campaign_budget = create_campaign_budget(client, customer_id)
    log_message(f"创建了预算: {campaign_budget}")

    # 创建广告系列
    campaign_resource_name = create_campaign(
        client, customer_id, campaign_budget
    )
    log_message(f"创建了广告系列: {campaign_resource_name}")

    # 创建广告组
    ad_group_resource_name = create_ad_group(
        client, customer_id, campaign_resource_name
    )
    log_message(f"创建了广告组: {ad_group_resource_name}")

    # 创建广告
    create_ad_group_ad(
        client, customer_id, ad_group_resource_name, customizer_attribute_name
    )

    # 添加关键词
    add_keywords(client, customer_id, ad_group_resource_name)

    # 添加地理定位
    add_geo_targeting(client, customer_id, campaign_resource_name)
    
    log_message("广告创建完成")


def create_customizer_attribute(client, customer_id, customizer_attribute_name):
    """创建自定义属性"""
    # 创建自定义属性操作
    operation = client.get_type("CustomizerAttributeOperation")
    # 创建指定名称的自定义属性
    customizer_attribute = operation.create
    customizer_attribute.name = customizer_attribute_name
    # 指定类型为"PRICE"，以便我们可以动态自定义广告描述中的产品/服务价格
    customizer_attribute.type_ = client.enums.CustomizerAttributeTypeEnum.PRICE

    # 发送请求以添加自定义属性并打印其信息
    customizer_attribute_service = client.get_service(
        "CustomizerAttributeService"
    )
    response = customizer_attribute_service.mutate_customizer_attributes(
        customer_id=customer_id, operations=[operation]
    )
    resource_name = response.results[0].resource_name

    log_message(f"添加了自定义属性，资源名称: '{resource_name}'")

    return resource_name


def link_customizer_attribute_to_customer(
    client, customer_id, customizer_attribute_resource_name
):
    """将自定义属性链接到客户"""
    # 创建客户自定义操作
    operation = client.get_type("CustomerCustomizerOperation")
    # 创建带有要在响应式搜索广告中使用的值的客户自定义器
    customer_customizer = operation.create
    customer_customizer.customizer_attribute = (
        customizer_attribute_resource_name
    )
    customer_customizer.value.type_ = (
        client.enums.CustomizerAttributeTypeEnum.PRICE
    )
    # 广告自定义器在投放广告时将用此值动态替换占位符
    customer_customizer.value.string_value = "Up to 70% OFF"

    customer_customizer_service = client.get_service(
        "CustomerCustomizerService"
    )
    # 发送请求以创建客户自定义器并打印其信息
    response = customer_customizer_service.mutate_customer_customizers(
        customer_id=customer_id, operations=[operation]
    )
    resource_name = response.results[0].resource_name

    log_message(
        f"为客户添加了自定义属性，资源名称: '{resource_name}'"
    )


def create_ad_text_asset(client, text, pinned_field=None):
    """创建广告文本资产"""
    ad_text_asset = client.get_type("AdTextAsset")
    ad_text_asset.text = text
    if pinned_field:
        ad_text_asset.pinned_field = pinned_field
    return ad_text_asset


def create_ad_text_asset_with_customizer(
    client, customizer_attribute_resource_name
):
    """使用自定义属性创建广告文本资产"""
    ad_text_asset = client.get_type("AdTextAsset")
    ad_text_asset.text = (
        f"Shop Now: {{CUSTOMIZER.{customizer_attribute_resource_name}}}"
    )
    return ad_text_asset


def create_campaign_budget(client, customer_id):
    """创建广告系列预算"""
    campaign_budget_service = client.get_service("CampaignBudgetService")
    campaign_budget_operation = client.get_type("CampaignBudgetOperation")
    campaign_budget = campaign_budget_operation.create
    campaign_budget.name = f"Belk Campaign Budget {uuid.uuid4()}"
    campaign_budget.delivery_method = (
        client.enums.BudgetDeliveryMethodEnum.STANDARD
    )
    campaign_budget.amount_micros = 1000000  # $1000

    # 添加预算
    campaign_budget_response = campaign_budget_service.mutate_campaign_budgets(
        customer_id=customer_id, operations=[campaign_budget_operation]
    )

    return campaign_budget_response.results[0].resource_name


def create_campaign(client, customer_id, campaign_budget):
    """创建广告系列"""
    campaign_service = client.get_service("CampaignService")
    campaign_operation = client.get_type("CampaignOperation")
    campaign = campaign_operation.create
    campaign.name = f"Belk.com Fashion Campaign {uuid.uuid4()}"
    campaign.advertising_channel_type = (
        client.enums.AdvertisingChannelTypeEnum.SEARCH
    )

    # 建议：创建时将广告系列设置为PAUSED，以防广告立即投放
    # 在添加定位和广告准备好投放后设置为ENABLED
    campaign.status = client.enums.CampaignStatusEnum.PAUSED

    # 设置竞价策略和预算
    campaign.target_spend.target_spend_micros = 0
    campaign.campaign_budget = campaign_budget

    # 设置广告系列网络选项
    campaign.network_settings.target_google_search = True
    campaign.network_settings.target_search_network = True
    campaign.network_settings.target_partner_search_network = False
    campaign.network_settings.target_content_network = True

    # 添加广告系列
    campaign_response = campaign_service.mutate_campaigns(
        customer_id=customer_id, operations=[campaign_operation]
    )
    resource_name = campaign_response.results[0].resource_name
    log_message(f"创建了广告系列 {resource_name}")
    return resource_name


def create_ad_group(client, customer_id, campaign_resource_name):
    """创建广告组"""
    ad_group_service = client.get_service("AdGroupService")

    ad_group_operation = client.get_type("AdGroupOperation")
    ad_group = ad_group_operation.create
    ad_group.name = f"Belk Fashion Deals {uuid.uuid4()}"
    ad_group.status = client.enums.AdGroupStatusEnum.ENABLED
    ad_group.campaign = campaign_resource_name
    ad_group.type_ = client.enums.AdGroupTypeEnum.SEARCH_STANDARD

    # 如果要设置最高CPC出价，请取消注释下面的行
    ad_group.cpc_bid_micros = 2000000  # $2.00

    # 添加广告组
    ad_group_response = ad_group_service.mutate_ad_groups(
        customer_id=customer_id, operations=[ad_group_operation]
    )
    ad_group_resource_name = ad_group_response.results[0].resource_name
    log_message(f"创建了广告组 {ad_group_resource_name}")
    return ad_group_resource_name


def create_ad_group_ad(
    client, customer_id, ad_group_resource_name, customizer_attribute_name
):
    """创建广告组广告（响应式搜索广告）"""
    ad_group_ad_service = client.get_service("AdGroupAdService")

    ad_group_ad_operation = client.get_type("AdGroupAdOperation")
    ad_group_ad = ad_group_ad_operation.create
    ad_group_ad.status = client.enums.AdGroupAdStatusEnum.ENABLED
    ad_group_ad.ad_group = ad_group_resource_name

    # 设置响应式搜索广告信息
    # 广告的最终URL
    ad_group_ad.ad.final_urls.append(FINAL_URL)

    # 设置固定位置，始终选择此资产作为HEADLINE_1
    # 固定是可选的；如果未设置固定，则标题和描述将轮换，表现最佳的将更频繁使用
    served_asset_enum = client.enums.ServedAssetFieldTypeEnum.HEADLINE_1
    pinned_headline = create_ad_text_asset(
        client, "Shop Belk.com Fashion Deals", served_asset_enum
    )

    # 标题2和3
    ad_group_ad.ad.responsive_search_ad.headlines.extend(
        [
            pinned_headline,
            create_ad_text_asset(client, "Up to 70% Off Designer Brands"),
            create_ad_text_asset(client, "Free Shipping on Orders $49+"),
        ]
    )

    # 描述1和2
    description_1 = create_ad_text_asset(client, "Shop the latest fashion trends, homeware & beauty at Belk.com. Find amazing deals today!")
    description_2 = None

    if customizer_attribute_name:
        description_2 = create_ad_text_asset_with_customizer(
            client, customizer_attribute_name
        )
    else:
        description_2 = create_ad_text_asset(client, "Belk.com - Discover designer clothing, shoes, accessories & more. Shop now!")

    ad_group_ad.ad.responsive_search_ad.descriptions.extend(
        [description_1, description_2]
    )

    # 路径
    # 可以附加到广告中URL的文本的第一部分和第二部分
    # 如果使用以下示例，广告将显示
    # https://www.belk.com/fashion/deals
    ad_group_ad.ad.responsive_search_ad.path1 = "fashion"
    ad_group_ad.ad.responsive_search_ad.path2 = "deals"

    # 发送请求以添加响应式搜索广告
    ad_group_ad_response = ad_group_ad_service.mutate_ad_group_ads(
        customer_id=customer_id, operations=[ad_group_ad_operation]
    )

    for result in ad_group_ad_response.results:
        log_message(
            f"创建了响应式搜索广告，资源名称: \"{result.resource_name}\""
        )


def add_keywords(client, customer_id, ad_group_resource_name):
    """添加关键词"""
    ad_group_criterion_service = client.get_service("AdGroupCriterionService")

    operations = []
    # 创建关键词1 - 精确匹配
    ad_group_criterion_operation = client.get_type("AdGroupCriterionOperation")
    ad_group_criterion = ad_group_criterion_operation.create
    ad_group_criterion.ad_group = ad_group_resource_name
    ad_group_criterion.status = client.enums.AdGroupCriterionStatusEnum.ENABLED
    ad_group_criterion.keyword.text = KEYWORD_TEXT_EXACT
    ad_group_criterion.keyword.match_type = (
        client.enums.KeywordMatchTypeEnum.EXACT
    )
    operations.append(ad_group_criterion_operation)

    # 创建关键词2 - 短语匹配
    ad_group_criterion_operation = client.get_type("AdGroupCriterionOperation")
    ad_group_criterion = ad_group_criterion_operation.create
    ad_group_criterion.ad_group = ad_group_resource_name
    ad_group_criterion.status = client.enums.AdGroupCriterionStatusEnum.ENABLED
    ad_group_criterion.keyword.text = KEYWORD_TEXT_PHRASE
    ad_group_criterion.keyword.match_type = (
        client.enums.KeywordMatchTypeEnum.PHRASE
    )
    operations.append(ad_group_criterion_operation)

    # 创建关键词3 - 广泛匹配
    ad_group_criterion_operation = client.get_type("AdGroupCriterionOperation")
    ad_group_criterion = ad_group_criterion_operation.create
    ad_group_criterion.ad_group = ad_group_resource_name
    ad_group_criterion.status = client.enums.AdGroupCriterionStatusEnum.ENABLED
    ad_group_criterion.keyword.text = KEYWORD_TEXT_BROAD
    ad_group_criterion.keyword.match_type = (
        client.enums.KeywordMatchTypeEnum.BROAD
    )
    operations.append(ad_group_criterion_operation)

    # 添加额外的关键词 - 广泛匹配
    additional_keywords = [
        "belk coupon codes",
        "belk designer clothes",
        "belk online store",
        "belk home decor",
        "belk shoes sale"
    ]
    
    for keyword in additional_keywords:
        ad_group_criterion_operation = client.get_type("AdGroupCriterionOperation")
        ad_group_criterion = ad_group_criterion_operation.create
        ad_group_criterion.ad_group = ad_group_resource_name
        ad_group_criterion.status = client.enums.AdGroupCriterionStatusEnum.ENABLED
        ad_group_criterion.keyword.text = keyword
        ad_group_criterion.keyword.match_type = (
            client.enums.KeywordMatchTypeEnum.BROAD
        )
        operations.append(ad_group_criterion_operation)

    # 添加关键词
    ad_group_criterion_response = (
        ad_group_criterion_service.mutate_ad_group_criteria(
            customer_id=customer_id,
            operations=operations,
        )
    )
    log_message(f"添加了 {len(operations)} 个关键词")
    for result in ad_group_criterion_response.results:
        log_message(f"创建了关键词 {result.resource_name}")


def add_geo_targeting(client, customer_id, campaign_resource_name):
    """添加地理定位"""
    geo_target_constant_service = client.get_service("GeoTargetConstantService")

    # 通过位置名称搜索
    gtc_request = client.get_type("SuggestGeoTargetConstantsRequest")
    gtc_request.locale = LOCALE
    gtc_request.country_code = COUNTRY_CODE

    # 获取建议的地理目标常量的位置名称
    gtc_request.location_names.names.extend(
        [GEO_LOCATION_1, GEO_LOCATION_2, GEO_LOCATION_3]
    )

    results = geo_target_constant_service.suggest_geo_target_constants(
        gtc_request
    )

    operations = []
    for suggestion in results.geo_target_constant_suggestions:
        log_message(
            f"地理目标常量: {suggestion.geo_target_constant.resource_name} "
            f"在LOCALE ({suggestion.locale})中找到 "
            f"覆盖范围 ({suggestion.reach}) "
            f"搜索词 ({suggestion.search_term})."
        )
        # 为位置定位创建广告系列标准
        campaign_criterion_operation = client.get_type(
            "CampaignCriterionOperation"
        )
        campaign_criterion = campaign_criterion_operation.create
        campaign_criterion.campaign = campaign_resource_name
        campaign_criterion.location.geo_target_constant = (
            suggestion.geo_target_constant.resource_name
        )
        operations.append(campaign_criterion_operation)

    campaign_criterion_service = client.get_service("CampaignCriterionService")
    campaign_criterion_response = (
        campaign_criterion_service.mutate_campaign_criteria(
            customer_id=customer_id, operations=[*operations]
        )
    )

    for result in campaign_criterion_response.results:
        log_message(f'添加了广告系列标准 "{result.resource_name}"')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="为Belk.com创建响应式搜索广告"
    )
    # 以下参数应提供以运行示例
    parser.add_argument(
        "-c",
        "--customer_id",
        type=str,
        default="278-639-3017",  # 默认设置为提供的客户ID
        help="Google Ads客户ID",
    )

    # 自定义属性名称是可选的
    parser.add_argument(
        "-n",
        "--customizer_attribute_name",
        type=str,
        default="BelkSalePrice",  # 默认值
        help="要创建的自定义属性的名称",
    )
    
    # 添加代理参数
    parser.add_argument(
        "--proxy",
        type=str,
        help="HTTP代理，格式为 http://host:port"
    )
    
    # 添加模拟模式参数
    parser.add_argument(
        "--mock",
        action="store_true",
        help="使用模拟模式，不实际连接 API（用于测试）"
    )
    
    # 添加重试次数参数
    parser.add_argument(
        "--retries",
        type=int,
        default=3,
        help="API 连接失败时的重试次数"
    )
    
    # 添加重试间隔参数
    parser.add_argument(
        "--retry_interval",
        type=int,
        default=5,
        help="重试间隔（秒）"
    )

    args = parser.parse_args()

    # 确保目录存在
    os.makedirs(SAVE_PATH, exist_ok=True)
    
    # 初始化日志文件
    with open(LOG_FILE, "w") as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始Belk.com搜索广告创建日志\n")

    # 如果是模拟模式，直接运行模拟而不连接API
    if args.mock:
        create_mock_ad(args.customer_id)
        sys.exit(0)

    # 使用服务账号加载配置文件
    try:
        # 获取当前脚本所在的目录路径
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # 构建配置文件的完整路径
        yaml_path = os.path.join(current_dir, "google-ads.yaml")
        
        # 确认配置文件存在
        if not os.path.exists(yaml_path):
            log_message(f"错误: 配置文件不存在: {yaml_path}")
            log_message("请先运行 service_account_helper.py 设置服务账号")
            sys.exit(1)
        
        # 如果指定了代理，修改配置文件
        if args.proxy:
            modify_config_for_proxy(yaml_path, args.proxy)
        else:
            # 即使没有代理也增加超时设置
            modify_config_for_proxy(yaml_path)
        
        # 使用重试机制加载客户端和执行操作
        retries = args.retries
        while retries >= 0:
            try:
                log_message(f"使用服务账号配置文件: {yaml_path}")
                googleads_client = GoogleAdsClient.load_from_storage(path=yaml_path, version="v19")
                log_message("成功通过服务账号加载Google Ads客户端")
                
                main(
                    googleads_client,
                    args.customer_id,
                    args.customizer_attribute_name,
                )
                # 如果成功完成，跳出循环
                break
                
            except GoogleAdsException as ex:
                log_message(
                    f'请求ID "{ex.request_id}" 失败，状态"{ex.error.code().name}"，包含以下错误:'
                )
                for error in ex.failure.errors:
                    log_message(f'错误消息 "{error.message}"')
                    if error.location:
                        for field_path_element in error.location.field_path_elements:
                            log_message(f"\t\t字段: {field_path_element.field_name}")
                
                # 检查是否有连接问题
                if "failed to connect" in str(ex) or "timeout" in str(ex).lower():
                    if retries > 0:
                        retries -= 1
                        log_message(f"连接失败。将在 {args.retry_interval} 秒后重试。剩余重试次数: {retries}")
                        time.sleep(args.retry_interval)
                        continue
                    else:
                        log_message("重试次数已用完。网络连接问题可能持续存在。")
                        use_mock = input("网络连接失败。是否使用模拟模式继续？(y/n): ").lower() == 'y'
                        if use_mock:
                            create_mock_ad(args.customer_id)
                        sys.exit(1)
                else:
                    # 非连接问题，直接退出
                    sys.exit(1)
                    
            except Exception as e:
                log_message(f"发生错误: {str(e)}")
                if "failed to connect" in str(e).lower() or "timeout" in str(e).lower():
                    if retries > 0:
                        retries -= 1
                        log_message(f"连接失败。将在 {args.retry_interval} 秒后重试。剩余重试次数: {retries}")
                        time.sleep(args.retry_interval)
                        continue
                    else:
                        log_message("重试次数已用完。网络连接问题可能持续存在。")
                        use_mock = input("网络连接失败。是否使用模拟模式继续？(y/n): ").lower() == 'y'
                        if use_mock:
                            create_mock_ad(args.customer_id)
                sys.exit(1)
    except Exception as e:
        log_message(f"程序异常: {str(e)}")
        sys.exit(1)
