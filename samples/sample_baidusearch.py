from baidusearch.baidusearch import search
results = search('为什么小马哥不爱我', num_results=10)
# print(results)
# 格式化下返回结果
for result in results:
    print(f"标题: {result['title']}")
    print(f"链接: {result['url']}")
    print(f"描述: {result['abstract']}")
    print("-" * 80)
    print()