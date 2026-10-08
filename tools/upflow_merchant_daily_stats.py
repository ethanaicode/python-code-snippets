"""统计商户月账单中每日收款与退款(退款按原交易订单号对应的实际收款日期归属)。

用法: python merchant_daily_stats.py <trans_YYYY-MM.csv>
"""
import csv
import re
import sys
from collections import defaultdict
from decimal import Decimal

RECORD_START = re.compile(r"(?=\d{4}-\d\d-\d\d \d\d:\d\d:\d\d\s*,)")


def parse(path):
    text = open(path, encoding="utf-8", errors="replace").read()
    text = text.replace("\r", "").replace("\n", "")
    # 明细表之前的汇总部分在首条记录之前,丢弃
    for rec in RECORD_START.split(text)[1:]:
        row = [c.strip().lstrip("`") for c in next(csv.reader([rec]))]
        yield row


def main(path):
    # day -> [收款笔数, 收款金额, 退款笔数, 退款金额]
    stats = defaultdict(lambda: [0, Decimal("0"), 0, Decimal("0")])
    for row in parse(path):
        order_no, amount, orig = row[1], Decimal(row[11]), row[15]
        if order_no.startswith("REFUND") or orig:
            # 单号为 商户号(9位)+日期(8位)+...,与微信支付单号的位置不同
            d = orig[9:17]
            day = f"{d[:4]}-{d[4:6]}-{d[6:]}"
            stats[day][2] += 1
            stats[day][3] += abs(amount)
        else:
            day = row[0][:10]
            stats[day][0] += 1
            stats[day][1] += amount

    print(f"{'日期':<12}{'收款笔数':>8}{'收款金额':>12}{'退款笔数':>8}{'退款金额':>12}{'净额':>12}")
    for day in sorted(stats):
        n1, a1, n2, a2 = stats[day]
        print(f"{day:<12}{n1:>8}{a1:>12.2f}{n2:>8}{a2:>12.2f}{a1 - a2:>12.2f}")
    t = [sum(v[i] for v in stats.values()) for i in range(4)]
    print(f"{'合计':<12}{t[0]:>8}{t[1]:>12.2f}{t[2]:>8}{t[3]:>12.2f}{t[1] - t[3]:>12.2f}")

    out = path.rsplit(".", 1)[0] + "_daily_stats.csv"
    # utf-8-sig 便于 Excel 正确显示中文
    with open(out, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["日期", "收款笔数", "收款金额", "退款笔数", "退款金额", "净额"])
        for day in sorted(stats):
            n1, a1, n2, a2 = stats[day]
            w.writerow([day, n1, f"{a1:.2f}", n2, f"{a2:.2f}", f"{a1 - a2:.2f}"])
        w.writerow(["合计", t[0], f"{t[1]:.2f}", t[2], f"{t[3]:.2f}", f"{t[1] - t[3]:.2f}"])
    print(f"已输出: {out}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "data/trans_2026-09.csv")
