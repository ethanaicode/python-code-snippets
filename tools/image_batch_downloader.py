"""
批量图片下载工具
支持两种模式：
  1. 命令行模式：直接在命令行传入图片 URL
  2. 文件模式：读取文本文件，每行一个图片 URL

============================================================
用法示例
============================================================

【模式 1】命令行模式
  python tools/image_batch_downloader.py urls <url1> <url2> ... -o <保存目录>

  示例：
    python tools/image_batch_downloader.py urls \\
        https://example.com/a.png \\
        https://example.com/b.jpg \\
        -o ./downloads

------------------------------------------------------------

【模式 2】文件模式
  python tools/image_batch_downloader.py file <文件路径> -o <保存目录>

  示例：
    python tools/image_batch_downloader.py file ./data/image_urls.txt -o ./downloads

  image_urls.txt 格式（每行一个 URL，空行和 # 开头的注释行会被忽略）：
    # 这是注释
    https://example.com/a.png
    https://example.com/b.jpg

    https://example.com/c.gif

============================================================
"""

import os
import argparse
import requests
from urllib.parse import urlparse


def download_image(url: str, save_dir: str) -> None:
    """下载单张图片，文件名从 URL 中提取。"""
    if not url:
        return

    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()

        parsed = urlparse(url)
        filename = os.path.basename(parsed.path) or "image"
        image_path = os.path.join(save_dir, filename)

        with open(image_path, "wb") as f:
            f.write(response.content)

        print(f"[OK]   {url}")
    except requests.exceptions.RequestException as e:
        print(f"[FAIL] {url}: {e}")


def batch_download(urls: list, save_dir: str) -> None:
    """批量下载图片列表。"""
    os.makedirs(save_dir, exist_ok=True)
    print(f"共 {len(urls)} 张图片，保存到: {save_dir}\n")
    for url in urls:
        download_image(url, save_dir)
    print("\n下载完成！")


def load_urls_from_file(file_path: str) -> list:
    """从文本文件中读取 URL 列表，忽略空行和 # 注释行。"""
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    return [line.strip() for line in lines if line.strip() and not line.strip().startswith("#")]


def main():
    parser = argparse.ArgumentParser(description="批量图片下载工具")
    subparsers = parser.add_subparsers(dest="mode", required=True)

    # --- 命令行模式 ---
    url_parser = subparsers.add_parser("urls", help="从命令行传入 URL 列表下载")
    url_parser.add_argument("urls", nargs="+", help="图片 URL 列表")
    url_parser.add_argument("-o", "--output", default="./downloads", help="保存目录（默认: ./downloads）")

    # --- 文件模式 ---
    file_parser = subparsers.add_parser("file", help="从文本文件读取 URL 列表下载（每行一个 URL）")
    file_parser.add_argument("file_path", help="包含图片 URL 的文本文件路径")
    file_parser.add_argument("-o", "--output", default="./downloads", help="保存目录（默认: ./downloads）")

    args = parser.parse_args()

    if args.mode == "urls":
        batch_download(args.urls, args.output)
    elif args.mode == "file":
        urls = load_urls_from_file(args.file_path)
        print(f"从文件读取到 {len(urls)} 个 URL")
        batch_download(urls, args.output)

if __name__ == "__main__":
    main()
