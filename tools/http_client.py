#!/usr/bin/env python3
"""
HTTP客户端工具 - Postman的命令行替代品
支持发送HTTP请求、美化显示响应、保存请求配置等
"""

import requests
import json
import argparse
import sys
import time
from pathlib import Path
from typing import Dict, Any, Optional
from urllib.parse import urlencode


class Colors:
    """终端颜色常量
    
    ANSI转义序列格式: \033[{code}m
    - \033 是ESC转义字符（八进制）
    - [code] 是颜色/样式代码
    - m 是结束标记
    
    常用代码:
    - 0m: 重置
    - 1m: 粗体
    - 30-37: 标准前景色
    - 90-97: 高亮前景色
    - 38;2;R;G;B: 24位真彩色（RGB模式）
    """
    RESET = '\033[0m'
    BOLD = '\033[1m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    GRAY = '\033[38;2;88;110;117m'  # #586E75 - Solarized base01


class HTTPClient:
    """HTTP客户端"""
    
    def __init__(self, timeout: int = 30, verify_ssl: bool = True, follow_redirects: bool = True):
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.follow_redirects = follow_redirects
        self.session = requests.Session()
    
    def send_request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, str]] = None,
        body: Any = None,
        body_file: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        发送HTTP请求
        
        Args:
            method: HTTP方法
            url: 请求URL
            headers: 请求头
            params: 查询参数
            body: 请求体（字符串或字典）
            body_file: 请求体文件路径
        
        Returns:
            包含响应信息的字典
        """
        # 读取body文件
        if body_file:
            body_path = Path(body_file)
            if not body_path.exists():
                raise FileNotFoundError(f"Body文件不存在: {body_file}")
            
            with open(body_path, 'r', encoding='utf-8') as f:
                if body_file.endswith('.json'):
                    body = json.load(f)
                else:
                    body = f.read()
        
        # 记录开始时间
        start_time = time.time()
        
        try:
            # 准备请求参数
            kwargs = {
                'timeout': self.timeout,
                'verify': self.verify_ssl,
                'allow_redirects': self.follow_redirects
            }
            
            if headers:
                kwargs['headers'] = headers
            
            if params:
                kwargs['params'] = params
            
            # 处理请求体
            if body is not None:
                if isinstance(body, dict):
                    kwargs['json'] = body
                elif isinstance(body, str):
                    # 尝试解析为JSON
                    try:
                        kwargs['json'] = json.loads(body)
                    except json.JSONDecodeError:
                        kwargs['data'] = body
                else:
                    kwargs['data'] = body
            
            # 发送请求
            response = self.session.request(method, url, **kwargs)
            
            # 计算耗时
            elapsed_ms = (time.time() - start_time) * 1000
            
            # 解析响应体
            try:
                response_body = response.json()
                content_type = 'json'
            except json.JSONDecodeError:
                response_body = response.text
                content_type = 'text'
            
            return {
                'status_code': response.status_code,
                'status_text': response.reason,
                'elapsed_ms': elapsed_ms,
                'headers': dict(response.headers),
                'body': response_body,
                'content_type': content_type,
                'url': response.url,
                'encoding': response.encoding
            }
            
        except requests.exceptions.Timeout:
            return {
                'error': 'Timeout',
                'message': f'请求超时（{self.timeout}秒）',
                'elapsed_ms': (time.time() - start_time) * 1000
            }
        except requests.exceptions.ConnectionError as e:
            return {
                'error': 'ConnectionError',
                'message': f'连接错误: {str(e)}',
                'elapsed_ms': (time.time() - start_time) * 1000
            }
        except requests.exceptions.RequestException as e:
            return {
                'error': type(e).__name__,
                'message': str(e),
                'elapsed_ms': (time.time() - start_time) * 1000
            }


class ResponsePrinter:
    """响应结果打印器"""
    
    @staticmethod
    def print_response(response: Dict[str, Any], verbose: bool = False):
        """打印响应结果"""
        
        # 如果有错误
        if 'error' in response:
            print(f"\n{Colors.RED}{Colors.BOLD}✗ 请求失败{Colors.RESET}")
            print(f"{Colors.RED}错误类型: {response['error']}{Colors.RESET}")
            print(f"{Colors.RED}错误信息: {response['message']}{Colors.RESET}")
            print(f"{Colors.GRAY}耗时: {response['elapsed_ms']:.2f} ms{Colors.RESET}")
            return
        
        # 状态码颜色
        status_code = response['status_code']
        if 200 <= status_code < 300:
            status_color = Colors.GREEN
            status_icon = "✓"
        elif 300 <= status_code < 400:
            status_color = Colors.YELLOW
            status_icon = "↻"
        else:
            status_color = Colors.RED
            status_icon = "✗"
        
        # 打印状态行
        print(f"\n{status_color}{Colors.BOLD}{status_icon} {status_code} {response['status_text']}{Colors.RESET}")
        print(f"{Colors.GRAY}耗时: {response['elapsed_ms']:.2f} ms{Colors.RESET}")
        print(f"{Colors.GRAY}URL: {response['url']}{Colors.RESET}")
        
        # 打印响应头（仅verbose模式）
        if verbose:
            print(f"\n{Colors.CYAN}{Colors.BOLD}响应头:{Colors.RESET}")
            for key, value in response['headers'].items():
                print(f"{Colors.CYAN}{key}:{Colors.RESET} {value}")
        
        # 打印响应体
        print(f"\n{Colors.CYAN}{Colors.BOLD}响应体:{Colors.RESET}")
        
        if response['content_type'] == 'json':
            # JSON格式化输出
            json_str = json.dumps(response['body'], indent=2, ensure_ascii=False)
            ResponsePrinter._print_colored_json(json_str)
        else:
            # 文本输出
            body_text = response['body']
            if len(body_text) > 5000:
                print(f"{Colors.YELLOW}(响应体过长，仅显示前5000字符){Colors.RESET}")
                body_text = body_text[:5000] + "..."
            print(body_text)
        
        print()  # 空行
    
    @staticmethod
    def _print_colored_json(json_str: str):
        """彩色打印JSON"""
        import re
        
        # 简单的语法高亮
        # 字符串值 - 绿色
        json_str = re.sub(r'(: )(".*?")', r'\1' + Colors.GREEN + r'\2' + Colors.RESET, json_str)
        # 键名 - 蓝色
        json_str = re.sub(r'(".*?")(: )', Colors.BLUE + r'\1' + Colors.RESET + r'\2', json_str)
        # 数字 - 黄色
        json_str = re.sub(r'(: )(\d+\.?\d*)', r'\1' + Colors.YELLOW + r'\2' + Colors.RESET, json_str)
        # 布尔值和null - 品红色
        json_str = re.sub(r'(: )(true|false|null)', r'\1' + Colors.MAGENTA + r'\2' + Colors.RESET, json_str)
        
        print(json_str)


class RequestConfig:
    """请求配置管理"""
    
    @staticmethod
    def save_config(config: Dict[str, Any], filepath: str):
        """保存请求配置到文件"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        print(f"{Colors.GREEN}✓ 配置已保存到: {filepath}{Colors.RESET}")
    
    @staticmethod
    def load_config(filepath: str) -> Dict[str, Any]:
        """从文件加载请求配置"""
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)


def parse_key_value_pairs(pairs: list) -> Dict[str, str]:
    """解析键值对列表 ['key:value', 'key2:value2'] -> {'key': 'value', 'key2': 'value2'}"""
    result = {}
    if pairs:
        for pair in pairs:
            if ':' in pair:
                key, value = pair.split(':', 1)
                result[key.strip()] = value.strip()
    return result


def main():
    """主函数 - 命令行入口"""
    parser = argparse.ArgumentParser(
        description="HTTP客户端工具 - Postman的命令行替代品",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 简单GET请求
  python http_client.py GET https://api.github.com/users/octocat
  
  # POST请求（JSON body）
  python http_client.py POST https://api.example.com/login -d '{"username":"admin","password":"123456"}'
  
  # 从文件读取body
  python http_client.py POST https://api.example.com/users -f data/user.json
  
  # 添加请求头
  python http_client.py GET https://api.example.com/protected -H "Authorization:Bearer token123" -H "Accept:application/json"
  
  # 添加查询参数
  python http_client.py GET https://api.example.com/search -q "keyword:python" -q "page:1"
  
  # 保存请求配置
  python http_client.py GET https://api.example.com/users -H "Auth:token" --save my_request.json
  
  # 从配置文件加载请求
  python http_client.py --load my_request.json
  
  # 显示详细信息（包括响应头）
  python http_client.py GET https://httpbin.org/get -v
        """
    )
    
    # 位置参数
    parser.add_argument("method", nargs='?', 
                       choices=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"],
                       help="HTTP方法")
    parser.add_argument("url", nargs='?', help="请求URL")
    
    # 请求配置
    parser.add_argument("-H", "--header", action="append", dest="headers",
                       help="请求头，格式: 'Key:Value'，可多次使用")
    parser.add_argument("-q", "--query", action="append", dest="params",
                       help="查询参数，格式: 'key:value'，可多次使用")
    parser.add_argument("-d", "--data", help="请求体数据（字符串或JSON）")
    parser.add_argument("-f", "--file", dest="body_file", help="从文件读取请求体")
    
    # 选项
    parser.add_argument("-t", "--timeout", type=int, default=30, help="超时时间（秒），默认30")
    parser.add_argument("-v", "--verbose", action="store_true", help="显示详细信息（包括响应头）")
    parser.add_argument("--no-ssl-verify", action="store_true", help="忽略SSL证书验证")
    parser.add_argument("--no-redirect", action="store_true", help="不跟随重定向")
    
    # 配置管理
    parser.add_argument("--save", metavar="FILE", help="保存请求配置到文件")
    parser.add_argument("--load", metavar="FILE", help="从文件加载请求配置")
    
    args = parser.parse_args()
    
    # 从文件加载配置
    if args.load:
        try:
            config = RequestConfig.load_config(args.load)
            args.method = config.get('method', 'GET')
            args.url = config.get('url')
            args.headers = config.get('headers', [])
            args.params = config.get('params', [])
            args.data = config.get('data')
            args.body_file = config.get('body_file')
            args.timeout = config.get('timeout', 30)
            print(f"{Colors.GREEN}✓ 已从配置文件加载: {args.load}{Colors.RESET}\n")
        except Exception as e:
            print(f"{Colors.RED}✗ 加载配置文件失败: {e}{Colors.RESET}")
            sys.exit(1)
    
    # 验证必需参数
    if not args.method or not args.url:
        parser.print_help()
        sys.exit(1)
    
    # 解析请求头和查询参数
    headers = parse_key_value_pairs(args.headers)
    params = parse_key_value_pairs(args.params)
    
    # 打印请求信息
    print(f"\n{Colors.BOLD}{Colors.CYAN}➜ {args.method} {args.url}{Colors.RESET}")
    if headers:
        print(f"{Colors.GRAY}请求头: {headers}{Colors.RESET}")
    if params:
        print(f"{Colors.GRAY}查询参数: {params}{Colors.RESET}")
    if args.data:
        print(f"{Colors.GRAY}请求体: {args.data[:100]}{'...' if len(args.data) > 100 else ''}{Colors.RESET}")
    elif args.body_file:
        print(f"{Colors.GRAY}请求体文件: {args.body_file}{Colors.RESET}")
    
    # 保存配置
    if args.save:
        config = {
            'method': args.method,
            'url': args.url,
            'headers': args.headers or [],
            'params': args.params or [],
            'data': args.data,
            'body_file': args.body_file,
            'timeout': args.timeout
        }
        RequestConfig.save_config(config, args.save)
    
    # 创建HTTP客户端
    client = HTTPClient(
        timeout=args.timeout,
        verify_ssl=not args.no_ssl_verify,
        follow_redirects=not args.no_redirect
    )
    
    # 发送请求
    try:
        response = client.send_request(
            method=args.method,
            url=args.url,
            headers=headers or None,
            params=params or None,
            body=args.data,
            body_file=args.body_file
        )
        
        # 打印响应
        ResponsePrinter.print_response(response, verbose=args.verbose)
        
        # 根据状态码返回退出码
        if 'error' in response or response.get('status_code', 0) >= 400:
            sys.exit(1)
            
    except Exception as e:
        print(f"\n{Colors.RED}{Colors.BOLD}✗ 发生异常{Colors.RESET}")
        print(f"{Colors.RED}{type(e).__name__}: {e}{Colors.RESET}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
