import requests
from typing import List, Dict, Optional
from .config import get_api_url, get_timeout


class SearchService:
    """失物招领搜索服务类"""

    def __init__(self):
        self.base_url = get_api_url("get_lost_items")

    def search_items(self,
                     keyword: str = "",
                     item_type: str = "",
                     category: str = "",
                     limit: int = 50,
                     offset: int = 0) -> Dict:
        """
        搜索失物招领信息

        Args:
            keyword: 搜索关键字（物品名称、描述、地点）
            item_type: 物品类型（'lost' 或 'found'）
            category: 物品分类
            limit: 返回数量限制
            offset: 分页偏移

        Returns:
            Dict: 包含搜索结果和统计信息
        """
        try:
            params = {
                'keyword': keyword.strip(),
                'type': item_type,
                'category': category,
                'limit': limit,
                'offset': offset
            }

            # 移除空参数
            params = {k: v for k, v in params.items() if v}

            response = requests.get(
                self.base_url,
                params=params,
                timeout=get_timeout()
            )

            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    return result["data"]
                else:
                    return {
                        "items": [],
                        "total": 0,
                        "limit": limit,
                        "offset": offset,
                        "error": result.get("message", "搜索失败")
                    }
            else:
                return {
                    "items": [],
                    "total": 0,
                    "limit": limit,
                    "offset": offset,
                    "error": f"HTTP错误: {response.status_code}"
                }

        except Exception as e:
            return {
                "items": [],
                "total": 0,
                "limit": limit,
                "offset": offset,
                "error": f"网络错误: {str(e)}"
            }

    def get_item_detail(self, item_id: int) -> Optional[Dict]:
        """
        获取单个物品的详细信息

        Args:
            item_id: 物品ID

        Returns:
            Dict: 物品详细信息，失败时返回None
        """
        try:
            response = requests.get(
                get_api_url("get_item_detail").replace("<int:item_id>", str(item_id)),
                timeout=get_timeout()
            )

            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    return result["data"]
                else:
                    print(f"获取物品详情失败: {result.get('message')}")
                    return None
            else:
                print(f"HTTP错误: {response.status_code}")
                return None

        except Exception as e:
            print(f"网络错误: {str(e)}")
            return None

    def search_by_keyword(self, keyword: str) -> List[Dict]:
        """
        根据关键字搜索物品

        Args:
            keyword: 搜索关键字

        Returns:
            List[Dict]: 搜索结果列表
        """
        result = self.search_items(keyword=keyword)
        return result.get("items", [])

    def search_by_type(self, item_type: str) -> List[Dict]:
        """
        根据类型搜索物品

        Args:
            item_type: 物品类型（'lost' 或 'found'）

        Returns:
            List[Dict]: 搜索结果列表
        """
        result = self.search_items(item_type=item_type)
        return result.get("items", [])

    def search_by_category(self, category: str) -> List[Dict]:
        """
        根据分类搜索物品

        Args:
            category: 物品分类

        Returns:
            List[Dict]: 搜索结果列表
        """
        result = self.search_items(category=category)
        return result.get("items", [])

    def get_all_items(self, limit: int = 100) -> List[Dict]:
        """
        获取所有物品信息

        Args:
            limit: 返回数量限制

        Returns:
            List[Dict]: 所有物品列表
        """
        result = self.search_items(limit=limit)
        return result.get("items", [])

    def get_lost_items(self, limit: int = 50) -> List[Dict]:
        """
        获取所有失物信息

        Args:
            limit: 返回数量限制

        Returns:
            List[Dict]: 失物列表
        """
        return self.search_by_type("lost")

    def get_found_items(self, limit: int = 50) -> List[Dict]:
        """
        获取所有招领信息

        Args:
            limit: 返回数量限制

        Returns:
            List[Dict]: 招领列表
        """
        return self.search_by_type("found")


# 使用示例
if __name__ == "__main__":
    # 创建搜索服务实例
    search_service = SearchService()

    # 搜索示例
    print("=== 搜索测试 ===")

    # 1. 搜索所有物品
    all_items = search_service.get_all_items(limit=10)
    print(f"找到 {len(all_items)} 个物品")

    # 2. 关键字搜索
    keyword_results = search_service.search_by_keyword("手机")
    print(f"关键字'手机'搜索结果: {len(keyword_results)} 个")

    # 3. 类型搜索
    lost_items = search_service.get_lost_items()
    found_items = search_service.get_found_items()
    print(f"失物: {len(lost_items)} 个, 招领: {len(found_items)} 个")

    # 4. 分类搜索
    electronic_items = search_service.search_by_category("电子产品")
    print(f"电子产品: {len(electronic_items)} 个")

    # 5. 组合搜索
    combined_results = search_service.search_items(
        keyword="手机",
        item_type="lost",
        category="电子产品"
    )
    print(f"组合搜索结果: {len(combined_results.get('items', []))} 个")