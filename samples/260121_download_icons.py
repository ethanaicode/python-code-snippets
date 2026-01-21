import os
import json
import requests
from urllib.parse import urlparse

# 读取 JSON 文件并下载图片到本地，同时更新 JSON 数据

def download_image(url, save_dir, index):
    """下载单张图片，返回本地路径"""
    if not url:
        return ""
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # 从 URL 提取文件扩展名
        parsed_url = urlparse(url)
        path = parsed_url.path
        ext = os.path.splitext(path)[1] or '.png'
        
        # 使用索引作为文件名，避免重名
        image_name = f"icon_{index}{ext}"
        image_path = os.path.join(save_dir, image_name)
        
        with open(image_path, 'wb') as file:
            file.write(response.content)
        
        print(f"[{index}] 下载成功: {url}")
        return image_path
    except requests.exceptions.RequestException as e:
        print(f"[{index}] 下载失败 {url}: {e}")
        return ""

def main():
    # JSON 文件路径
    json_path = "/Users/ethan/Downloads/result.json"
    
    # 图片保存目录
    save_dir = "/Users/ethan/Downloads/icons/"
    
    # 创建保存目录
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    # 读取 JSON 数据
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"共 {len(data)} 条数据，开始下载图片...")
    
    # 遍历并下载图片
    for i, item in enumerate(data):
        icon_url = item.get('icon', '')
        
        # 下载图片并获取本地路径
        local_path = download_image(icon_url, save_dir, i)
        
        # 添加新字段
        item['icon_local'] = local_path
    
    # 保存更新后的 JSON
    output_path = "/Users/ethan/Downloads/result_with_local.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n下载完成！更新后的 JSON 已保存到: {output_path}")

if __name__ == "__main__":
    main()
