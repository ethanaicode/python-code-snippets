#!/usr/bin/env python3
"""
PDF合同盖章工具
"""
import fitz  # PyMuPDF
from PIL import Image

PDF_IN = "/path/to/input.pdf"
PDF_OUT = "/path/to/output_stamped.pdf"
STAMP_IMG = "/path/to/stamp.png"

FULL_STAMP_PAGE = -1       # -1 表示最后一页
STAMP_WIDTH = 140         # 章的显示宽度（所有页一致）
STAMP_POSITION = "right"  # 完整章位置: "left" 或 "right"
MARGIN_SIDE = 60          # 距左边或右边距
MARGIN_BOTTOM = 120        # 完整章距底部

# 骑缝章设置
ENABLE_CROSS_STAMP = False  # 是否启用骑缝章
CROSS_STAMP_MARGIN = 20    # 骑缝章距边距

doc = fitz.open(PDF_IN)
page_count = doc.page_count

# ---------- 读取公章 ----------
stamp_img = Image.open(STAMP_IMG)
stamp_w, stamp_h = stamp_img.size

# ---------- 骑缝章：按页数切片（左右切分）----------
if ENABLE_CROSS_STAMP:
    slice_width = stamp_w // page_count
    stamp_slices = []

    for i in range(page_count):
        left = i * slice_width
        right = stamp_w if i == page_count - 1 else (i + 1) * slice_width
        slice_img = stamp_img.crop((left, 0, right, stamp_h))
        stamp_slices.append(slice_img)

# ---------- 给每一页盖骑缝章 ----------
if ENABLE_CROSS_STAMP:
    for i, page in enumerate(doc):
        page_width = page.rect.width
        page_height = page.rect.height

        # 保存临时切片
        temp_slice = f"/tmp/stamp_slice_{i}.png"
        stamp_slices[i].save(temp_slice)

        # 按比例计算宽度
        ratio = STAMP_WIDTH / stamp_h  # 注意：这里用stamp_h作为基准高度
        slice_display_width = (stamp_slices[i].size[0]) * ratio

        # 骑缝章放在右侧边缘中间
        rect = fitz.Rect(
            page_width - slice_display_width - CROSS_STAMP_MARGIN,
            (page_height - STAMP_WIDTH) / 2,
            page_width - CROSS_STAMP_MARGIN,
            (page_height + STAMP_WIDTH) / 2
        )

        page.insert_image(rect, filename=temp_slice, overlay=True)

# ---------- 指定页盖完整公章 ----------
full_page = doc[FULL_STAMP_PAGE]

page_width = full_page.rect.width
page_height = full_page.rect.height

# 根据STAMP_POSITION设置位置
if STAMP_POSITION == "left":
    full_rect = fitz.Rect(
        MARGIN_SIDE,
        page_height - STAMP_WIDTH - MARGIN_BOTTOM,
        MARGIN_SIDE + STAMP_WIDTH,
        page_height - MARGIN_BOTTOM
    )
else:  # right
    full_rect = fitz.Rect(
        page_width - STAMP_WIDTH - MARGIN_SIDE,
        page_height - STAMP_WIDTH - MARGIN_BOTTOM,
        page_width - MARGIN_SIDE,
        page_height - MARGIN_BOTTOM
    )

full_page.insert_image(full_rect, filename=STAMP_IMG, overlay=True)

# ---------- 保存 ----------
doc.save(PDF_OUT)
doc.close()