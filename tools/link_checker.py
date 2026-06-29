#!/usr/bin/env python3
"""
链接有效性检查工具

支持批量检查 URL 是否可访问，支持命令行传参、文件读取、并发检查、
结果汇总和 JSON 报告导出。
"""

import argparse
import concurrent.futures
import json
import re
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set

import requests


class Colors:
    """终端颜色常量。"""

    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    GRAY = "\033[38;2;88;110;117m"


URL_PATTERN = re.compile(r"https?://[^\s<>'\"]+", re.IGNORECASE)


@dataclass
class LinkResult:
    """单个链接的检查结果。"""

    index: int
    input_url: str
    checked_url: str
    final_url: Optional[str]
    status_code: Optional[int]
    status_text: str
    ok: bool
    redirected: bool
    redirect_chain: List[str]
    method_used: str
    elapsed_ms: float
    error: Optional[str] = None
    message: Optional[str] = None


def parse_key_value_pairs(pairs: Optional[Sequence[str]]) -> Dict[str, str]:
    """解析形如 key:value 的参数列表。"""

    result: Dict[str, str] = {}
    if not pairs:
        return result

    for pair in pairs:
        if ":" not in pair:
            continue
        key, value = pair.split(":", 1)
        result[key.strip()] = value.strip()
    return result


def normalize_url(url: str) -> Optional[str]:
    """清理并规范化单个 URL。"""

    cleaned = url.strip().strip('"\'<>[](){}，。；：,.;!')
    if not cleaned:
        return None

    if not cleaned.lower().startswith(("http://", "https://")):
        return None

    return cleaned


def extract_urls_from_text(text: str) -> List[str]:
    """从文本中提取所有 http/https 链接。"""

    urls: List[str] = []
    seen: Set[str] = set()

    for match in URL_PATTERN.findall(text):
        normalized = normalize_url(match)
        if normalized and normalized not in seen:
            seen.add(normalized)
            urls.append(normalized)

    return urls


def load_urls_from_file(file_path: str) -> List[str]:
    """从文件中提取链接，支持纯文本、Markdown、HTML、JSON 等内容。"""

    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"文件不存在: {file_path}")

    text = path.read_text(encoding="utf-8", errors="ignore")
    return extract_urls_from_text(text)


def collect_urls(urls: Iterable[Optional[str]], files: Iterable[str], read_stdin: bool) -> List[str]:
    """合并命令行、文件和标准输入中的链接，并去重保序。"""

    collected: List[str] = []
    seen: Set[str] = set()

    def add_url(value: Optional[str]) -> None:
        normalized = normalize_url(value or "")
        if normalized and normalized not in seen:
            seen.add(normalized)
            collected.append(normalized)

    for url in urls:
        add_url(url)

    for file_path in files:
        for url in load_urls_from_file(file_path):
            add_url(url)

    if read_stdin:
        stdin_text = sys.stdin.read()
        for url in extract_urls_from_text(stdin_text):
            add_url(url)

    return collected


def parse_status_spec(spec: str) -> Set[int]:
    """把 200,2xx,301-399 之类的描述解析成状态码集合。"""

    allowed: Set[int] = set()
    tokens = [token.strip().lower() for token in re.split(r"[\s,]+", spec) if token.strip()]

    for token in tokens:
        if token == "all":
            return set(range(100, 600))

        if re.fullmatch(r"[1-5]xx", token):
            start = int(token[0]) * 100
            allowed.update(range(start, start + 100))
            continue

        range_match = re.fullmatch(r"(\d{3})-(\d{3})", token)
        if range_match:
            start = int(range_match.group(1))
            end = int(range_match.group(2))
            if start > end:
                start, end = end, start
            allowed.update(range(start, end + 1))
            continue

        if re.fullmatch(r"\d{3}", token):
            allowed.add(int(token))
            continue

        raise ValueError(f"无法识别的状态码规则: {token}")

    if not allowed:
        raise ValueError("状态码规则不能为空")

    return allowed


class LinkChecker:
    """批量链接检查器。"""

    def __init__(
        self,
        timeout: float = 10.0,
        verify_ssl: bool = True,
        follow_redirects: bool = True,
        trace_redirects: bool = True,
        method: str = "HEAD",
        headers: Optional[Dict[str, str]] = None,
        valid_status_codes: Optional[Set[int]] = None,
    ):
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.follow_redirects = follow_redirects
        self.trace_redirects = trace_redirects
        self.method = method.upper()
        self.headers = headers or {}
        self.valid_status_codes = valid_status_codes or set(range(200, 400))
        self.session = requests.Session()

    def check_one(self, index: int, url: str) -> LinkResult:
        """检查单个链接。"""

        start_time = time.time()
        checked_url = url
        method_used = self.method
        redirect_chain: List[str] = []

        try:
            response = self._send(method_used, checked_url)

            if self.method == "HEAD" and response.status_code in {405, 501}:
                method_used = "GET"
                response = self._send(method_used, checked_url)

            elapsed_ms = (time.time() - start_time) * 1000
            final_url = response.url if self.trace_redirects else checked_url
            status_code = response.status_code
            status_text = response.reason or ""
            redirected = response.is_redirect or bool(response.history)
            if self.trace_redirects and response.history:
                redirect_chain = [item.url for item in response.history] + [response.url]
            ok = status_code in self.valid_status_codes

            return LinkResult(
                index=index,
                input_url=url,
                checked_url=checked_url,
                final_url=final_url,
                status_code=status_code,
                status_text=status_text,
                ok=ok,
                redirected=redirected,
                redirect_chain=redirect_chain,
                method_used=method_used,
                elapsed_ms=elapsed_ms,
            )

        except requests.exceptions.Timeout:
            elapsed_ms = (time.time() - start_time) * 1000
            return LinkResult(
                index=index,
                input_url=url,
                checked_url=checked_url,
                final_url=None,
                status_code=None,
                status_text="",
                ok=False,
                redirected=False,
                redirect_chain=[],
                method_used=method_used,
                elapsed_ms=elapsed_ms,
                error="Timeout",
                message=f"请求超时（{self.timeout}秒）",
            )
        except requests.exceptions.ConnectionError as exc:
            elapsed_ms = (time.time() - start_time) * 1000
            return LinkResult(
                index=index,
                input_url=url,
                checked_url=checked_url,
                final_url=None,
                status_code=None,
                status_text="",
                ok=False,
                redirected=False,
                redirect_chain=[],
                method_used=method_used,
                elapsed_ms=elapsed_ms,
                error="ConnectionError",
                message=str(exc),
            )
        except requests.exceptions.RequestException as exc:
            elapsed_ms = (time.time() - start_time) * 1000
            return LinkResult(
                index=index,
                input_url=url,
                checked_url=checked_url,
                final_url=None,
                status_code=None,
                status_text="",
                ok=False,
                redirected=False,
                redirect_chain=[],
                method_used=method_used,
                elapsed_ms=elapsed_ms,
                error=type(exc).__name__,
                message=str(exc),
            )

    def _send(self, method: str, url: str) -> requests.Response:
        """发送请求并返回响应。"""

        return self.session.request(
            method=method,
            url=url,
            headers=self.headers or None,
            timeout=self.timeout,
            verify=self.verify_ssl,
            allow_redirects=self.follow_redirects,
        )

    def check_urls(self, urls: Sequence[str], concurrency: int) -> List[LinkResult]:
        """并发检查多个链接。"""

        if not urls:
            return []

        worker_count = max(1, concurrency)
        results: List[Optional[LinkResult]] = [None] * len(urls)

        with concurrent.futures.ThreadPoolExecutor(max_workers=worker_count) as executor:
            future_map = {
                executor.submit(self.check_one, index + 1, url): index
                for index, url in enumerate(urls)
            }

            for future in concurrent.futures.as_completed(future_map):
                index = future_map[future]
                results[index] = future.result()

        return [result for result in results if result is not None]


class ResultPrinter:
    """结果打印器。"""

    @staticmethod
    def print_summary(results: Sequence[LinkResult], total_elapsed_ms: float) -> None:
        """打印汇总信息。"""

        total = len(results)
        valid = sum(1 for result in results if result.ok)
        invalid = sum(1 for result in results if not result.ok and not result.error)
        failed = sum(1 for result in results if result.error)
        redirected = sum(1 for result in results if result.redirected)

        print()
        print(f"{Colors.BOLD}{Colors.CYAN}检查完成{Colors.RESET}")
        print(f"{Colors.GRAY}总数: {total}{Colors.RESET}")
        print(f"{Colors.GREEN}有效: {valid}{Colors.RESET}")
        print(f"{Colors.YELLOW}重定向: {redirected}{Colors.RESET}")
        print(f"{Colors.RED}无效: {invalid}{Colors.RESET}")
        print(f"{Colors.RED}错误: {failed}{Colors.RESET}")
        print(f"{Colors.GRAY}总耗时: {total_elapsed_ms:.2f} ms{Colors.RESET}")

    @staticmethod
    def print_result(result: LinkResult, verbose: bool = False) -> None:
        """打印单条结果。"""

        if result.error:
            print(
                f"[{result.index:03d}] {Colors.RED}FAIL{Colors.RESET} "
                f"{Colors.GRAY}{result.elapsed_ms:8.2f} ms{Colors.RESET}  {result.input_url}"
            )
            print(f"      {Colors.RED}{result.error}: {result.message}{Colors.RESET}")
            return

        if result.redirected and result.ok:
            status_color = Colors.YELLOW
            label = "REDIRECT_OK"
        elif result.redirected and not result.ok:
            status_color = Colors.RED
            label = "REDIRECT_BAD"
        elif result.ok:
            status_color = Colors.GREEN
            label = "OK"
        else:
            status_color = Colors.RED
            label = "BAD"

        final_part = ""
        if result.redirected and result.final_url:
            final_part = f" -> {result.final_url}"

        status_text = f"{result.status_code} {result.status_text}".strip()
        print(
            f"[{result.index:03d}] {status_color}{label}{Colors.RESET} "
            f"{Colors.GRAY}{result.elapsed_ms:8.2f} ms{Colors.RESET}  "
            f"{status_text}{final_part}"
        )

        if not result.ok:
            print(f"      {Colors.RED}原始链接: {result.input_url}{Colors.RESET}")

        if verbose:
            print(f"      {Colors.GRAY}输入: {result.input_url}{Colors.RESET}")
            print(f"      {Colors.GRAY}方法: {result.method_used}{Colors.RESET}")
            if result.redirect_chain:
                print(f"      {Colors.GRAY}跳转链: {' -> '.join(result.redirect_chain)}{Colors.RESET}")


def build_report(results: Sequence[LinkResult], args: argparse.Namespace, urls: Sequence[str], elapsed_ms: float) -> Dict[str, Any]:
    """构造导出报告。"""

    valid = sum(1 for result in results if result.ok)
    invalid = sum(1 for result in results if not result.ok and not result.error)
    failed = sum(1 for result in results if result.error)

    return {
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "options": {
            "method": args.method,
            "timeout": args.timeout,
            "concurrency": args.concurrency,
            "follow_redirects": args.trace_redirects,
            "trace_redirects": args.trace_redirects,
            "verify_ssl": not args.no_ssl_verify,
            "valid_status": args.valid_status,
            "headers": args.header or [],
        },
        "summary": {
            "total": len(results),
            "valid": valid,
            "invalid": invalid,
            "failed": failed,
            "elapsed_ms": elapsed_ms,
        },
        "input_urls": list(urls),
        "results": [asdict(result) for result in results],
    }


def main() -> None:
    """命令行入口。"""

    parser = argparse.ArgumentParser(
        description="链接有效性检查工具 - 批量验证 URL 是否可访问",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 直接传 URL 检查
  python tools/link_checker.py https://example.com https://github.com

  # 使用 -u/--url 参数重复传入
  python tools/link_checker.py -u https://example.com -u https://github.com

  # 从文件读取（支持 txt/md/html/json 等文本文件）
  python tools/link_checker.py -f data/urls.txt

  # 从标准输入读取
  cat data/urls.txt | python tools/link_checker.py --stdin

  # 自定义并发、超时和请求头
  python tools/link_checker.py -f data/urls.txt -c 20 -t 5 -H "User-Agent:Mozilla/5.0"

  # 导出 JSON 报告
  python tools/link_checker.py -f data/urls.txt --output link_checker_report.json
        """,
    )

    parser.add_argument("urls", nargs="*", help="待检查的 URL，可直接跟在命令后面")
    parser.add_argument("-u", "--url", action="append", dest="input_urls", help="待检查的 URL，可多次使用")
    parser.add_argument("-f", "--file", action="append", dest="files", help="从文件读取 URL，可多次使用")
    parser.add_argument("--stdin", action="store_true", help="从标准输入读取 URL 文本")

    parser.add_argument("-m", "--method", choices=["HEAD", "GET", "OPTIONS"], default="HEAD", help="检查时使用的 HTTP 方法，默认 HEAD")
    parser.add_argument("-c", "--concurrency", type=int, default=20, help="并发数，默认 20")
    parser.add_argument("-t", "--timeout", type=float, default=10.0, help="单个链接超时时间（秒），默认 10")
    parser.add_argument("-H", "--header", action="append", dest="header", help="请求头，格式: Key:Value，可多次使用")
    parser.add_argument("--valid-status", default="200-399", help="认为有效的状态码规则，支持 200,2xx,301-399,all，默认 200-399")
    parser.add_argument("--no-ssl-verify", action="store_true", help="忽略 SSL 证书验证")
    parser.add_argument("--trace-redirects", action=argparse.BooleanOptionalAction, default=True, help="重定向后继续追踪最终结果，默认开启")
    parser.add_argument("--no-redirect", action="store_false", dest="trace_redirects", help=argparse.SUPPRESS)
    parser.add_argument("--output", metavar="FILE", help="将检查报告导出为 JSON 文件")
    parser.add_argument("-v", "--verbose", action="store_true", help="显示更多信息")

    args = parser.parse_args()

    try:
        valid_status_codes = parse_status_spec(args.valid_status)
    except ValueError as exc:
        print(f"{Colors.RED}✗ {exc}{Colors.RESET}")
        sys.exit(1)

    input_urls = collect_urls(args.urls + (args.input_urls or []), args.files or [], args.stdin)

    if not input_urls:
        parser.print_help()
        sys.exit(1)

    headers = parse_key_value_pairs(args.header)

    print(f"\n{Colors.BOLD}{Colors.CYAN}➜ 开始检查 {len(input_urls)} 个链接{Colors.RESET}")
    if headers:
        print(f"{Colors.GRAY}请求头: {headers}{Colors.RESET}")
    print(f"{Colors.GRAY}方法: {args.method}  并发: {args.concurrency}  超时: {args.timeout}s{Colors.RESET}")

    checker = LinkChecker(
        timeout=args.timeout,
        verify_ssl=not args.no_ssl_verify,
        follow_redirects=args.trace_redirects,
        trace_redirects=args.trace_redirects,
        method=args.method,
        headers=headers,
        valid_status_codes=valid_status_codes,
    )

    start_time = time.time()
    results = checker.check_urls(input_urls, args.concurrency)
    elapsed_ms = (time.time() - start_time) * 1000

    for result in results:
        ResultPrinter.print_result(result, verbose=args.verbose)

    ResultPrinter.print_summary(results, elapsed_ms)

    if args.output:
        report = build_report(results, args, input_urls, elapsed_ms)
        output_path = Path(args.output)
        output_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"{Colors.GREEN}✓ 报告已保存到: {output_path}{Colors.RESET}")

    has_failures = any((not result.ok) for result in results)
    sys.exit(1 if has_failures else 0)


if __name__ == "__main__":
    main()