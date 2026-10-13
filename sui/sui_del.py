"""删除随手记记录。Cookie 复用同目录 cookies.txt。

用法:
    python sui/sui_del.py 21693789142503 [21693789142504 ...]
    id 来自列表中的 groups[0].list[NUM].sId 或者 groups[0].list[NUM].tranId
"""
import argparse
import sys

from sui_client import BASE_URL, parse_loose_json, post

PATH = "/tally/new.rmi"


def delete_trans(trans_id: str) -> dict:
    resp = post(PATH, {"opt": "del", "transId": trans_id}, referer=f"{BASE_URL}/tally/new.do")
    # 响应形如 {id: [{value: 123}]}
    result = parse_loose_json(resp.text)
    # 返回的 id 列表包含该 transId 才表示删除成功
    items = result.get("id") if isinstance(result, dict) else None
    values = {str(i.get("value")) for i in items if isinstance(i, dict)} if isinstance(items, list) else set()
    if trans_id not in values:
        raise RuntimeError(f"删除未成功: {resp.text[:200]}")
    return result


def main():
    parser = argparse.ArgumentParser(description="删除随手记记录")
    parser.add_argument("trans_ids", nargs="+", help="记录 id（新建时返回的 id）")
    args = parser.parse_args()

    failed = False
    for trans_id in args.trans_ids:
        try:
            delete_trans(trans_id)
            print(f"删除成功: {trans_id}")
        except Exception as e:
            failed = True
            print(f"删除失败 {trans_id}: {e}", file=sys.stderr)
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
