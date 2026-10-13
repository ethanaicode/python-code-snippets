"""随手记 (sui.com) 公共组件：请求头、Cookie 读取、POST 封装、非标准 JSON 解析。

Cookie 存放在同目录 cookies.txt，过期后直接替换其内容。
"""
import json
import re
from pathlib import Path

import requests

BASE_URL = "https://www.sui.com"
COOKIE_FILE = Path(__file__).resolve().parent / "cookies.txt"

HEADERS = {
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "no-cache",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "dnt": "1",
    "origin": BASE_URL,
    "pragma": "no-cache",
    "referer": f"{BASE_URL}/report.shtml?r=daily",
    "user-agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36"
    ),
    "x-requested-with": "XMLHttpRequest",
}


def load_cookie(path: Path = COOKIE_FILE) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Cookie 文件不存在: {path}")
    cookie = " ".join(path.read_text(encoding="utf-8").split())
    if not cookie:
        raise ValueError(f"Cookie 文件为空: {path}")
    return cookie


def post(path: str, data: dict, referer: str = "") -> requests.Response:
    """向 BASE_URL + path 发送表单 POST，自动附带通用请求头和 Cookie。"""
    headers = {**HEADERS, "cookie": load_cookie()}
    if referer:
        headers["referer"] = referer
    resp = requests.post(BASE_URL + path, data=data, headers=headers, timeout=30)
    resp.raise_for_status()
    return resp


def parse_loose_json(text: str):
    """解析键未加引号的响应，如 {id:{id:123},budget:0}；仅适用于值不含字符串的响应。"""
    try:
        return json.loads(re.sub(r'([{,])\s*([A-Za-z_]\w*)\s*:', r'\1"\2":', text))
    except ValueError:
        raise RuntimeError(f"响应无法解析，Cookie 可能已过期: {text[:200]}")
