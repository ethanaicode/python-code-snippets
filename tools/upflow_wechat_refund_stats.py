"""按订单日期(取自微信支付单号第11-18位)统计微信退款笔数与金额。

用法: python wechat_refund_stats.py <退款账单.csv>
"""
import csv
import re
import sys
from collections import defaultdict
from decimal import Decimal

# 记录以"退款申请时间"开头;字段内含换行,需先拼接再切分
RECORD_START = re.compile(r"(?=\d{4}-\d\d-\d\d \d\d:\d\d:\d\d,`)")


def parse(path):
    text = open(path, encoding="gbk", errors="replace").read()
    text = text.replace("\r", "").replace("\n", "")
    # 去掉表头(首条记录之前的内容)
    records = RECORD_START.split(text)[1:]
    for rec in records:
        row = next(csv.reader([rec]))
        yield row[7].lstrip("`"), Decimal(row[5]), row[3]


def main(path):
    stats = defaultdict(lambda: [0, Decimal("0")])
    for pay_id, amount, status in parse(path):
        d = pay_id[10:18]
        day = f"{d[:4]}-{d[4:6]}-{d[6:]}"
        stats[day][0] += 1
        stats[day][1] += amount

    print(f"{'订单日期':<12}{'退款笔数':>8}{'退款金额(元)':>14}")
    for day in sorted(stats):
        n, amt = stats[day]
        print(f"{day:<12}{n:>8}{amt:>14.2f}")
    print(f"{'合计':<12}{sum(v[0] for v in stats.values()):>8}"
          f"{sum(v[1] for v in stats.values()):>14.2f}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "data/915052822REFUND2026-10-08.csv")
