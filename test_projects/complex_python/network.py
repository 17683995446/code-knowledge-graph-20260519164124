# 子模块2 - 网络请求
import asyncio
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class HTTPResponse:
    """HTTP响应"""
    status_code: int
    body: str
    headers: Dict[str, str]

class HTTPClient:
    """HTTP客户端"""
    def __init__(self, base_url: str):
        self.base_url = base_url
        self._session = None

    async def get(self, path: str, params: Optional[Dict] = None) -> HTTPResponse:
        """GET请求"""
        url = f"{self.base_url}{path}"
        # 模拟请求
        return HTTPResponse(
            status_code=200,
            body=f"Response from {url}",
            headers={'content-type': 'application/json'}
        )

    async def post(self, path: str, data: Dict[str, Any]) -> HTTPResponse:
        """POST请求"""
        url = f"{self.base_url}{path}"
        return HTTPResponse(
            status_code=201,
            body=f"Created at {url}",
            headers={'content-type': 'application/json'}
        )

    async def close(self):
        """关闭连接"""
        pass

class APIClient:
    """API客户端"""
    def __init__(self, client: HTTPClient):
        self.client = client

    async def fetch_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """获取用户"""
        response = await self.client.get(f"/users/{user_id}")
        if response.status_code == 200:
            return {'id': user_id, 'name': 'User'}
        return None

    async def create_user(self, name: str, email: str) -> Dict[str, Any]:
        """创建用户"""
        response = await self.client.post("/users", {'name': name, 'email': email})
        return {'status': 'created', 'response': response.body}
