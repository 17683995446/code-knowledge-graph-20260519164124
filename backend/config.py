import os

class Config:
    DATABASE_PATH = os.getenv("DATABASE_PATH", "codegraph.db")
    SILICONFLOW_API_KEY = os.getenv("SILICONFLOW_API_KEY", "REDACTED_API_KEY")
    SILICONFLOW_ENDPOINT = "https://api.siliconflow.cn/v1/chat/completions"
    LLM_MODEL = "deepseek-ai/DeepSeek-V2.5"
    DEBOUNCE_DELAY_MS = 1000
    SUPPORTED_LANGUAGES = {
        ".py": "python",
        ".js": "javascript",
        ".jsx": "javascript",
        ".ts": "typescript",
        ".tsx": "typescript",
        ".java": "java",
        ".go": "go",
        ".rs": "rust",
        ".c": "c",
        ".cpp": "cpp",
        ".cc": "cpp",
        ".cxx": "cpp",
        ".h": "c",
        ".hpp": "cpp",
    }

config = Config()
