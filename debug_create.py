#!/usr/bin/env python3
"""调试创建项目的问题"""
import sys
import os
import time
import subprocess
import requests

BASE_URL = "http://127.0.0.1:8000"
api_process = None

try:
    # 启动服务器
    print("启动服务器...")
    api_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.main:app", "--host", "127.0.0.1", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    time.sleep(3)
    
    # 测试健康检查
    print("健康检查:", requests.get(f"{BASE_URL}/health").json())
    
    # 测试空路径是否有效
    print("\n--- 测试 1: 创建项目 ---")
    test_path = "/workspace/test_projects/mega_chaos"
    print(f"测试路径: {test_path}")
    print(f"路径存在? {os.path.exists(test_path)}")
    
    create_data = {
        "name": "DebugTest",
        "path": test_path
    }
    resp = requests.post(f"{BASE_URL}/api/projects", json=create_data)
    print(f"响应状态: {resp.status_code}")
    print(f"响应内容: {resp.text}")
    
finally:
    if api_process:
        api_process.terminate()
        try:
            api_process.wait(timeout=3)
        except:
            api_process.kill()
