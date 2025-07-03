#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
搜索功能测试脚本
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from frontend.search_service import SearchService


def test_search_functionality():
    """测试搜索功能"""
    print("=== 校园失物招领平台搜索功能测试 ===\n")

    # 创建搜索服务实例
    search_service = SearchService()

    # 测试1: 获取所有物品
    print("1. 测试获取所有物品:")
    all_items = search_service.get_all_items(limit=5)
    print(f"   找到 {len(all_items)} 个物品")
    if all_items:
        for item in all_items[:3]:  # 只显示前3个
            print(f"   - {item.get('item_name', 'N/A')} ({item.get('type', 'N/A')})")
    print()

    # 测试2: 关键字搜索
    print("2. 测试关键字搜索:")
    test_keywords = ["手机", "钱包", "书本", "电脑"]
    for keyword in test_keywords:
        results = search_service.search_by_keyword(keyword)
        print(f"   关键字 '{keyword}': 找到 {len(results)} 个结果")
    print()

    # 测试3: 类型搜索
    print("3. 测试类型搜索:")
    lost_items = search_service.get_lost_items(limit=10)
    found_items = search_service.get_found_items(limit=10)
    print(f"   失物: {len(lost_items)} 个")
    print(f"   招领: {len(found_items)} 个")
    print()

    # 测试4: 分类搜索
    print("4. 测试分类搜索:")
    categories = ["电子产品", "书籍资料", "证件卡片", "衣物饰品", "其他"]
    for category in categories:
        results = search_service.search_by_category(category)
        print(f"   分类 '{category}': 找到 {len(results)} 个结果")
    print()

    # 测试5: 组合搜索
    print("5. 测试组合搜索:")
    combined_results = search_service.search_items(
        keyword="手机",
        item_type="lost",
        category="电子产品"
    )
    print(f"   组合搜索 (手机 + 失物 + 电子产品): 找到 {len(combined_results.get('items', []))} 个结果")
    print()

    # 测试6: 分页搜索
    print("6. 测试分页搜索:")
    page1 = search_service.search_items(limit=3, offset=0)
    page2 = search_service.search_items(limit=3, offset=3)
    print(f"   第1页 (0-3): {len(page1.get('items', []))} 个结果")
    print(f"   第2页 (3-6): {len(page2.get('items', []))} 个结果")
    print(f"   总计: {page1.get('total', 0)} 个物品")
    print()

    # 测试7: 获取物品详情
    print("7. 测试获取物品详情:")
    if all_items:
        first_item = all_items[0]
        item_id = first_item.get('id')
        if item_id:
            detail = search_service.get_item_detail(item_id)
            if detail:
                print(f"   物品ID {item_id} 详情:")
                print(f"   名称: {detail.get('item_name', 'N/A')}")
                print(f"   类型: {detail.get('type', 'N/A')}")
                print(f"   分类: {detail.get('item_category', 'N/A')}")
                print(f"   地点: {detail.get('location', 'N/A')}")
                print(f"   发布者: {detail.get('publisher', 'N/A')}")
            else:
                print(f"   无法获取物品ID {item_id} 的详情")
    print()

    print("=== 测试完成 ===")


def test_api_endpoints():
    """测试API端点"""
    print("=== API端点测试 ===\n")

    import requests
    from frontend.config import get_api_url, get_timeout

    # 测试搜索API
    search_url = get_api_url("get_lost_items")
    print(f"搜索API: {search_url}")

    try:
        response = requests.get(search_url, timeout=get_timeout())
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"响应成功: {data.get('success', False)}")
            if data.get('success'):
                items = data.get('data', {}).get('items', [])
                print(f"返回物品数量: {len(items)}")
        else:
            print(f"响应失败: {response.text}")
    except Exception as e:
        print(f"请求失败: {e}")

    print()


if __name__ == "__main__":
    # 测试API端点
    test_api_endpoints()

    # 测试搜索功能
    test_search_functionality()