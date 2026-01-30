#!/usr/bin/env python3
"""
HTTP接口压力测试工具
用于测试接口在高并发情况下的表现，特别适合排查502等间歇性错误
"""

import aiohttp
import asyncio
import time
import statistics
import argparse
import json
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Any
import sys


class HTTPStressTester:
    """HTTP压力测试器"""
    
    def __init__(self, url: str, method: str = "GET", 
                 total_requests: int = 1000, 
                 concurrent: int = 50,
                 timeout: int = 30,
                 headers: Dict = None,
                 body: Any = None,
                 delay: float = 0.0,
                 keepalive: bool = True):
        self.url = url
        self.method = method.upper()
        self.total_requests = total_requests
        self.concurrent = concurrent
        self.timeout = timeout
        self.headers = headers or {}
        self.body = body
        self.delay = delay  # 请求间延迟（秒）
        self.keepalive = keepalive  # 是否启用连接复用
        
        # 统计数据
        self.success_count = 0
        self.failure_count = 0
        self.response_times = []
        self.status_codes = defaultdict(int)
        self.error_details = []
        self.completed = 0
        
        # 记录开始时间
        self.start_time = None
        self.end_time = None
    
    async def send_request(self, session: aiohttp.ClientSession, index: int):
        """发送单个HTTP请求"""
        # 添加请求延迟，模拟真实用户行为
        if self.delay > 0 and index > 0:
            await asyncio.sleep(self.delay)
        
        start_time = time.time()
        
        try:
            # 准备请求参数
            kwargs = {
                "headers": self.headers,
                "ssl": False  # 如果需要忽略SSL证书验证
            }
            
            # 根据HTTP方法添加请求体
            if self.method in ["POST", "PUT", "PATCH"] and self.body:
                if isinstance(self.body, dict):
                    kwargs["json"] = self.body
                else:
                    kwargs["data"] = self.body
            
            # 发送请求
            async with session.request(self.method, self.url, **kwargs) as response:
                await response.text()  # 读取响应体
                duration = time.time() - start_time
                
                # 记录状态码
                self.status_codes[response.status] += 1
                
                # 记录响应时间
                self.response_times.append(duration)
                
                # 判断成功或失败
                if 200 <= response.status < 400:
                    self.success_count += 1
                else:
                    self.failure_count += 1
                    # 记录错误详情（特别关注502等错误）
                    if response.status >= 400:
                        self.error_details.append({
                            "request_index": index,
                            "status_code": response.status,
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
                            "response_time": f"{duration * 1000:.2f}ms"
                        })
                        
        except asyncio.TimeoutError:
            self.failure_count += 1
            self.status_codes["TIMEOUT"] += 1
            self.error_details.append({
                "request_index": index,
                "error": "Timeout",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
            })
            
        except Exception as e:
            self.failure_count += 1
            error_type = type(e).__name__
            self.status_codes[f"ERROR_{error_type}"] += 1
            self.error_details.append({
                "request_index": index,
                "error": error_type,
                "message": str(e),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
            })
        
        finally:
            self.completed += 1
            # 实时显示进度
            if self.completed % max(1, self.total_requests // 20) == 0:
                progress = (self.completed / self.total_requests) * 100
                print(f"进度: {self.completed}/{self.total_requests} ({progress:.1f}%)", end="\r")
    
    async def run_test(self):
        """执行压力测试"""
        print(f"\n{'='*60}")
        print(f"🚀 开始HTTP压力测试")
        print(f"{'='*60}")
        print(f"目标URL: {self.url}")
        print(f"请求方法: {self.method}")
        print(f"总请求数: {self.total_requests}")
        print(f"并发数: {self.concurrent}")
        print(f"超时设置: {self.timeout}秒")
        print(f"连接复用: {'启用' if self.keepalive else '禁用'}")
        if self.delay > 0:
            print(f"请求延迟: {self.delay}秒")
        print(f"{'='*60}\n")
        
        self.start_time = time.time()
        
        # 配置连接器和超时
        connector = aiohttp.TCPConnector(
            limit=self.concurrent,
            limit_per_host=self.concurrent,
            ttl_dns_cache=300,  # DNS缓存5分钟
            force_close=not self.keepalive,  # 根据keepalive设置决定是否复用连接
            enable_cleanup_closed=True  # 自动清理关闭的连接
        )
        timeout = aiohttp.ClientTimeout(
            total=self.timeout,
            connect=10,  # 连接超时10秒
            sock_read=self.timeout  # 读取超时
        )
        
        async with aiohttp.ClientSession(
            connector=connector, 
            timeout=timeout
        ) as session:
            tasks = [
                self.send_request(session, i) 
                for i in range(self.total_requests)
            ]
            await asyncio.gather(*tasks)
        
        self.end_time = time.time()
        print("\n")  # 清除进度显示
    
    def generate_report(self):
        """生成测试报告"""
        total_time = self.end_time - self.start_time
        
        print(f"\n{'='*60}")
        print(f"📊 测试报告")
        print(f"{'='*60}")
        print(f"测试时间: {datetime.fromtimestamp(self.start_time).strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"总耗时: {total_time:.2f}秒")
        print(f"QPS (每秒请求数): {self.total_requests / total_time:.2f}")
        print(f"\n{'='*60}")
        print(f"📈 请求统计")
        print(f"{'='*60}")
        print(f"总请求数: {self.total_requests}")
        print(f"成功请求: {self.success_count} ({self.success_count/self.total_requests*100:.2f}%)")
        print(f"失败请求: {self.failure_count} ({self.failure_count/self.total_requests*100:.2f}%)")
        
        print(f"\n{'='*60}")
        print(f"📋 状态码分布")
        print(f"{'='*60}")
        # 自定义排序：整数状态码在前，字符串错误类型在后
        def sort_key(item):
            status = item[0]
            if isinstance(status, int):
                return (0, status)  # 整数状态码优先，按数值排序
            else:
                return (1, status)  # 字符串错误类型其次，按字母排序
        
        for status, count in sorted(self.status_codes.items(), key=sort_key):
            percentage = (count / self.total_requests) * 100
            print(f"{status}: {count} ({percentage:.2f}%)")
        
        if self.response_times:
            print(f"\n{'='*60}")
            print(f"⏱️  响应时间统计")
            print(f"{'='*60}")
            print(f"平均响应时间: {statistics.mean(self.response_times) * 1000:.2f} ms")
            print(f"最快响应时间: {min(self.response_times) * 1000:.2f} ms")
            print(f"最慢响应时间: {max(self.response_times) * 1000:.2f} ms")
            print(f"中位数响应时间: {statistics.median(self.response_times) * 1000:.2f} ms")
            
            # 计算百分位数
            sorted_times = sorted(self.response_times)
            p95_index = int(len(sorted_times) * 0.95)
            p99_index = int(len(sorted_times) * 0.99)
            print(f"P95响应时间: {sorted_times[p95_index] * 1000:.2f} ms")
            print(f"P99响应时间: {sorted_times[p99_index] * 1000:.2f} ms")
        
        # 显示错误详情
        if self.error_details:
            print(f"\n{'='*60}")
            print(f"❌ 错误详情 (显示前20条)")
            print(f"{'='*60}")
            for i, error in enumerate(self.error_details[:20], 1):
                print(f"\n错误 #{i}:")
                for key, value in error.items():
                    print(f"  {key}: {value}")
        
        print(f"\n{'='*60}")
        
        # 保存详细报告到文件
        self.save_report_to_file()
    
    def save_report_to_file(self):
        """保存详细报告到JSON文件"""
        savepath = "data/stress_test_reports/"
        import os
        if not os.path.exists(savepath):
            os.makedirs(savepath)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{savepath}stress_test_report_{timestamp}.json"
        
        report_data = {
            "test_config": {
                "url": self.url,
                "method": self.method,
                "total_requests": self.total_requests,
                "concurrent": self.concurrent,
                "timeout": self.timeout
            },
            "test_time": {
                "start": datetime.fromtimestamp(self.start_time).isoformat(),
                "end": datetime.fromtimestamp(self.end_time).isoformat(),
                "duration_seconds": self.end_time - self.start_time
            },
            "summary": {
                "total_requests": self.total_requests,
                "success_count": self.success_count,
                "failure_count": self.failure_count,
                "success_rate": f"{self.success_count/self.total_requests*100:.2f}%",
                "qps": self.total_requests / (self.end_time - self.start_time)
            },
            "status_codes": dict(self.status_codes),
            "response_times": {
                "average_ms": statistics.mean(self.response_times) * 1000 if self.response_times else 0,
                "min_ms": min(self.response_times) * 1000 if self.response_times else 0,
                "max_ms": max(self.response_times) * 1000 if self.response_times else 0,
                "median_ms": statistics.median(self.response_times) * 1000 if self.response_times else 0
            },
            "errors": self.error_details
        }
        
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 详细报告已保存到: {filename}")


def main():
    """主函数 - 命令行入口"""
    parser = argparse.ArgumentParser(
        description="HTTP接口压力测试工具 - 用于检测502等间歇性错误",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 基本使用 - 测试GET请求
  python http_stress_test.py -u https://api.example.com/users
  
  # 指定请求数和并发数
  python http_stress_test.py -u https://api.example.com/users -n 5000 -c 200
  
  # 测试POST请求
  python http_stress_test.py -u https://api.example.com/login -m POST -d '{"username":"test","password":"123"}'
  
  # 添加自定义请求头
  python http_stress_test.py -u https://api.example.com/api -H "Authorization: Bearer token123" -H "Content-Type: application/json"
        """
    )
    
    parser.add_argument("-u", "--url", required=True, help="目标URL")
    parser.add_argument("-m", "--method", default="GET", 
                       choices=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"],
                       help="HTTP方法 (默认: GET)")
    parser.add_argument("-n", "--number", type=int, default=1000,
                       help="总请求数 (默认: 1000)")
    parser.add_argument("-c", "--concurrent", type=int, default=50,
                       help="并发数 (默认: 50)")
    parser.add_argument("-t", "--timeout", type=int, default=30,
                       help="请求超时时间(秒) (默认: 30)")
    parser.add_argument("-H", "--header", action="append", dest="headers",
                       help="自定义请求头，可以多次使用。格式: 'Key: Value'")
    parser.add_argument("-d", "--data", help="请求体数据 (用于POST/PUT等)")
    parser.add_argument("--delay", type=float, default=0.0,
                       help="请求间延迟时间(秒)，模拟真实用户行为 (默认: 0)")
    parser.add_argument("--no-keepalive", action="store_true",
                       help="禁用HTTP连接复用，每个请求新建连接")
    
    args = parser.parse_args()
    
    # 解析请求头
    headers = {}
    if args.headers:
        for header in args.headers:
            if ":" in header:
                key, value = header.split(":", 1)
                headers[key.strip()] = value.strip()
    
    # 解析请求体
    body = None
    if args.data:
        try:
            body = json.loads(args.data)
        except json.JSONDecodeError:
            body = args.data
    
    # 创建测试器并运行
    tester = HTTPStressTester(
        url=args.url,
        method=args.method,
        total_requests=args.number,
        concurrent=args.concurrent,
        timeout=args.timeout,
        headers=headers,
        body=body,
        delay=args.delay,
        keepalive=not args.no_keepalive
    )
    
    try:
        asyncio.run(tester.run_test())
        tester.generate_report()
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被用户中断")
        sys.exit(1)


if __name__ == "__main__":
    main()
