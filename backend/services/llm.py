import requests
from typing import List, Dict, Any
from ..config import config

class LLMService:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or config.SILICONFLOW_API_KEY
        self.endpoint = config.SILICONFLOW_ENDPOINT
        self.model = config.LLM_MODEL

    def chat(self, messages: List[Dict[str, str]], project_context: str = "") -> str:
        if project_context:
            system_message = {
                "role": "system",
                "content": f"你是一个代码知识图谱助手。以下是这个项目的代码结构信息：\n{project_context}\n\n请基于这些信息回答用户的问题。"
            }
            messages = [system_message] + messages

        try:
            response = requests.post(
                self.endpoint,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": messages,
                    "stream": False
                },
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                return result.get('choices', [{}])[0].get('message', {}).get('content', '抱歉，无法生成回答。')
            else:
                return f"API调用失败: {response.status_code} - {response.text}"

        except requests.exceptions.Timeout:
            return "请求超时，请稍后重试。"
        except Exception as e:
            return f"发生错误: {str(e)}"

llm_service = LLMService()
