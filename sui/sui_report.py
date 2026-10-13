"""查询随手记 (sui.com) 报表。Cookie 存放在同目录 cookies.txt，过期后直接替换其内容。

用法:
    python sui/sui_report.py 2026.07.01 2026.07.31 [-m daily] [-o out.json]
"""
import argparse
import json
import sys
from pathlib import Path

import requests

BASE_DIR = Path(__file__).resolve().parent
COOKIE_FILE = BASE_DIR / "cookies.txt"
URL = "https://www.sui.com/report.rmi"

HEADERS = {
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "no-cache",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "dnt": "1",
    "origin": "https://www.sui.com",
    "pragma": "no-cache",
    "referer": "https://www.sui.com/report.shtml?r=daily",
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


def query_report(begin_date: str, end_date: str, mode: str = "daily") -> dict:
    data = {
        "m": mode,
        "beginDate": begin_date,
        "endDate": end_date,
        "cids": 0,
        "aids": 0,
        "sids": 0,
        "pids": 0,
        "note": "",
    }
    headers = {**HEADERS, "cookie": load_cookie()}
    resp = requests.post(URL, data=data, headers=headers, timeout=30)
    resp.raise_for_status()
    try:
        return resp.json()
    except ValueError:
        raise RuntimeError(f"响应不是 JSON，Cookie 可能已过期: {resp.text[:200]}")


def main():
    parser = argparse.ArgumentParser(description="查询随手记报表")
    parser.add_argument("begin_date", help="开始日期，如 2026.07.01")
    parser.add_argument("end_date", help="结束日期，如 2026.07.31")
    parser.add_argument("-m", "--mode", default="daily")
    parser.add_argument("-o", "--output", help="保存结果到 JSON 文件")
    args = parser.parse_args()

    try:
        result = query_report(args.begin_date, args.end_date, args.mode)
    except Exception as e:
        print(f"查询失败: {e}", file=sys.stderr)
        sys.exit(1)

    text = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
        print(f"已保存到 {args.output}")
    else:
        print(text)


if __name__ == "__main__":
    main()
