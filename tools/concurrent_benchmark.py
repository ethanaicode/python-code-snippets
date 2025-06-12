import aiohttp
import asyncio
import time
import statistics
import traceback

# 配置项
# HOST 和 URI 可以根据实际情况修改
HOST = "http://example.com"
URI = "/api/endpoint"
# 总请求数
TOTAL_REQUESTS = 2000
# 同时并发数量
CONCURRENT = 100

# 统计数据
success_count = 0
failure_count = 0
response_times = []
error_details = []


async def send_request(session, i):
    global success_count, failure_count
    start_time = time.time()
    try:
        async with session.get(f"{HOST}{URI}") as response:
            text = await response.text()
            duration = time.time() - start_time
            if response.status == 200:
                success_count += 1
                response_times.append(duration)
            else:
                failure_count += 1
                error_details.append({
                    "index": i,
                    "status": response.status,
                    "body": text[:100]  # 截取前100字符
                })
    except Exception as e:
        failure_count += 1
        error_details.append({
            "index": i,
            "error_type": type(e).__name__,
            "error_repr": repr(e),
            "error_trace": traceback.format_exc().splitlines()[-1]  # 仅记录最后一行
        })


async def main():
    connector = aiohttp.TCPConnector(limit=CONCURRENT)
    # 设置连接超时
    timeout = aiohttp.ClientTimeout(total=50)
    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        tasks = [send_request(session, i) for i in range(TOTAL_REQUESTS)]
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    start = time.time()
    asyncio.run(main())
    end = time.time()

    print(f"\n📊 测试结果统计:")
    print(f"总请求数: {TOTAL_REQUESTS}")
    print(f"成功请求: {success_count}")
    print(f"失败请求: {failure_count}")
    print(f"总耗时: {end - start:.2f} 秒")

    if response_times:
        print(f"平均响应时间: {statistics.mean(response_times) * 1000:.2f} ms")
        print(f"最大响应时间: {max(response_times) * 1000:.2f} ms")
        print(f"最小响应时间: {min(response_times) * 1000:.2f} ms")

    if error_details:
        print(f"\n❗️失败详情（最多显示前10条）：")
        for err in error_details[:10]:
            print(err)

