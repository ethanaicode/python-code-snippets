import re
from collections import Counter
import sys

# 我在服务器上弄了一个二级域名访问记录收集器，用于查看哪些域名用于获取配置信息，但是被我遗漏了的。
# 这个脚本用于从这些日志中提取 host 和 uri，并统计出现次数

# ==================== 1. 配置项 ====================
# 需要排除的已知无用 URI 匹配规则（支持正则表达式或精确字符串）
EXCLUDE_URIS = {
    "/favicon.ico",
    "/robots.txt",
    "/Client/FeedBack.ashx?appid=56&pcid=8a6605424b8aac9f5ac925989aba62bb&code=320bf8c7d96c4553ece00e382eaa5b20",
    # 可以添加正则模式，例如排除所有静态资源：
    # r"^/static/.*",
}

# 日志文件路径（也可以作为命令行参数传入）
LOG_FILE = "officeoncloud_probe.log"
# LOG_FILE = "yunbiaosoft_probe.log"
# ===================================================

def parse_and_count(log_file):
    # 正则匹配 host="..." 和 uri="..."
    host_pattern = re.compile(r'host="([^"]+)"')
    uri_pattern = re.compile(r'uri="([^"]+)"')

    counter = Counter()

    with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            host_match = host_pattern.search(line)
            uri_match = uri_pattern.search(line)

            if host_match and uri_match:
                host = host_match.group(1)
                uri = uri_match.group(1)

                # 排除判断
                is_excluded = False
                for rule in EXCLUDE_URIS:
                    if uri == rule or re.search(rule, uri):
                        is_excluded = True
                        break

                if not is_excluded:
                    counter[(host, uri)] += 1

    # 打印格式化结果（按数量倒序）
    print(f"{'COUNT':<8} | {'HOST':<35} | {'URI'}")
    print("-" * 80)
    for (host, uri), count in counter.most_common():
        # 如果 uri 以 /Client/FeedBack.ashx?appid= 开头，不打印
        if uri.startswith("/Client/FeedBack.ashx?appid="):
            continue
        if count > 10:
            print(f"{count:<8} | {host:<35} | {uri}")

if __name__ == "__main__":
    file_path = sys.argv[1] if len(sys.argv) > 1 else LOG_FILE
    parse_and_count(file_path)