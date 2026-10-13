"""新建随手记支出记录。Cookie 复用同目录 cookies.txt。

用法:
    python sui/sui_add.py 12.50 -c 核对金额 -m "午餐" [-t "2026-10-13 18:37"] [--dry-run]

CATEGORY / STORE / PROJECT / MEMBER / ACCOUNT 为 名称 -> id 映射，请按需补充；
传入的名称不在映射中时，按原始 id 直接使用。
"""
import argparse
import sys
from datetime import datetime

from sui_client import BASE_URL, parse_loose_json, post

PATH = "/tally/payout.rmi"

CATEGORY = {
    "核对金额": "5577791174415",
}
STORE = {
    "552649155660": "552649155660",
}
PROJECT = {
    "5577791174360": "5577791174360",
}
MEMBER = {
    "0": "0",
}
ACCOUNT = {
    "532319189831": "532319189831",
}

DEFAULTS = {
    "category": "5577791174415",
    "store": "0",
    "project": "0",
    "member": "0",
    "account": "532319189831",
}


def resolve(mapping: dict, key: str, field: str) -> str:
    if key in mapping:
        return mapping[key]
    if key.isdigit():
        return key
    raise ValueError(f"{field} 未在映射中定义: {key}（已定义: {', '.join(mapping)}）")


def add_payout(price: str, category: str, store: str, project: str, member: str,
               account: str, memo: str = "", time: str = "", dry_run: bool = False) -> dict:
    data = {
        "id": 0,
        "category": resolve(CATEGORY, category, "category"),
        "store": resolve(STORE, store, "store"),
        "time": time or datetime.now().strftime("%Y-%m-%d %H:%M"),
        "project": resolve(PROJECT, project, "project"),
        "member": resolve(MEMBER, member, "member"),
        "memo": memo,
        "url": "",
        "out_account": 0,
        "in_account": 0,
        "debt_account": "",
        "account": resolve(ACCOUNT, account, "account"),
        "price": f"{float(price):.2f}",
        "price2": "",
    }
    if dry_run:
        return {"dry_run": True, "data": data}

    resp = post(PATH, data, referer=f"{BASE_URL}/tally/new.do")
    # 响应形如 {id:{id:123},budget:0,price:12.50}
    result = parse_loose_json(resp.text)
    # 内层 id 有值才表示新建成功
    inner = result.get("id") if isinstance(result, dict) else None
    if not (isinstance(inner, dict) and inner.get("id")):
        raise RuntimeError(f"新建未成功: {resp.text[:200]}")
    return result


def main():
    parser = argparse.ArgumentParser(description="新建随手记支出")
    parser.add_argument("price", help="金额，如 12.50")
    parser.add_argument("-c", "--category", default=DEFAULTS["category"], help="分类")
    parser.add_argument("-s", "--store", default=DEFAULTS["store"], help="商家")
    parser.add_argument("-p", "--project", default=DEFAULTS["project"], help="项目")
    parser.add_argument("--member", default=DEFAULTS["member"], help="成员，默认 0")
    parser.add_argument("-a", "--account", default=DEFAULTS["account"], help="账户")
    parser.add_argument("-m", "--memo", default="", help="备注")
    parser.add_argument("-t", "--time", default="", help="时间，如 2026-10-13 18:37，默认当前时间")
    parser.add_argument("--dry-run", action="store_true", help="只打印表单，不发送请求")
    args = parser.parse_args()

    try:
        result = add_payout(args.price, args.category, args.store, args.project,
                            args.member, args.account, args.memo, args.time, args.dry_run)
    except Exception as e:
        print(f"新建失败: {e}", file=sys.stderr)
        sys.exit(1)
    if args.dry_run:
        print(result)
    else:
        print(f"新建成功: 记录 id={result['id']['id']}, 金额={result['price']}")


if __name__ == "__main__":
    main()
