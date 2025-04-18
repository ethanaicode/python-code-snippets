from baidusearch.baidusearch import search
results = search('今天天气如何', num_results=20)
print(results)
# 格式化下返回结果
for result in results:
    print(f"标题: {result['title']}")
    print(f"链接: {result['url']}")
    print(f"描述: {result['abstract']}")
    print("-" * 80)
    print()