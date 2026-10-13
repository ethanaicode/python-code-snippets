"""查询随手记 (sui.com) 报表。Cookie 存放在同目录 cookies.txt，过期后直接替换其内容。

用法:
    python sui/sui_report.py 2026.07.01 2026.07.31 [-m daily] [-o out.json]
"""
import argparse
import json
import sys
from pathlib import Path

from sui_client import post

PATH = "/report.rmi"


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
    resp = post(PATH, data)
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
