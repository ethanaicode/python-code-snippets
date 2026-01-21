import json
from bs4 import BeautifulSoup

# 解析本地 HTML 文件并提取指定信息

# HTML 文件路径
html_path = "/Users/ethan/Downloads/xxx.html"

# 读取 HTML 内容
with open(html_path, "r", encoding="utf-8") as f:
    html = f.read()

# 解析 HTML
soup = BeautifulSoup(html, "html.parser")

result = []

# 找到所有 section.card
sections = soup.find_all("section", class_="card")

for section in sections:
    # 仅仅打印第一个 section，调试用
    # print(section)
    # break

    # 提取 img src
    img = section.find("img", class_="img-icon")
    img_src = img["src"] if img and img.has_attr("src") else ""

    # 提取 title
    title_div = section.find("div", class_="title")
    # 使用 .string 或遍历 children 来获取 TemplateString 类型的文本
    title = "".join(str(child) for child in title_div.children) if title_div else ""
    title = title.strip()

    # 提取 desc
    desc_div = section.find("div", class_="desc")
    desc = "".join(str(child) for child in desc_div.children) if desc_div else ""
    desc = desc.strip()

    result.append({
        "title": title,
        "desc": desc,
        "icon": img_src
    })

# 转成 JSON 字符串（美化输出）
json_data = json.dumps(result, ensure_ascii=False, indent=2)

# 输出到文件（可选）
output_path = "/Users/ethan/Downloads/result.json"
with open(output_path, "w", encoding="utf-8") as f:
    f.write(json_data)

print("提取完成，共提取", len(result), "条数据")
print(json_data)
