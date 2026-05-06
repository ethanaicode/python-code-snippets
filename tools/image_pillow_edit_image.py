from PIL import Image


def add_watermark(
    input_path,
    output_path,
    watermark_path,
    position=("right", "bottom"),
    opacity=128,
    margin=(20, 20),
):
    """
    为图片添加水印。

    :param input_path: 输入图片路径
    :param output_path: 输出图片路径
    :param watermark_path: 水印图片路径
    :param position: 水印位置，支持 ("left"|"center"|"right", "top"|"center"|"bottom")
    :param opacity: 水印透明度，范围 0-255
    :param margin: 水印边距 (x_margin, y_margin)
    """
    with Image.open(input_path) as base_img, Image.open(watermark_path) as wm_img:
        base = base_img.convert("RGBA")
        watermark = wm_img.convert("RGBA")

        if opacity < 0:
            opacity = 0
        if opacity > 255:
            opacity = 255

        # 调整水印整体透明度
        alpha = watermark.split()[-1].point(lambda p: int(p * (opacity / 255)))
        watermark.putalpha(alpha)

        bw, bh = base.size
        ww, wh = watermark.size

        px = {
            "left": margin[0],
            "center": (bw - ww) // 2,
            "right": bw - ww - margin[0],
        }.get(position[0], bw - ww - margin[0])
        py = {
            "top": margin[1],
            "center": (bh - wh) // 2,
            "bottom": bh - wh - margin[1],
        }.get(position[1], bh - wh - margin[1])

        px = max(0, min(px, bw - ww))
        py = max(0, min(py, bh - wh))

        result = base.copy()
        result.paste(watermark, (px, py), watermark)
        result.convert(base_img.mode).save(output_path)
        print(f"✓ 图片已成功保存到: {output_path}")


def crop_image(input_path, output_path, x1, y1, x2, y2):
    """
    裁剪图片到指定区域。

    :param input_path: 输入图片路径
    :param output_path: 输出图片路径
    :param x1: 左上角 x
    :param y1: 左上角 y
    :param x2: 右下角 x
    :param y2: 右下角 y
    """
    with Image.open(input_path) as img:
        w, h = img.size

        x1 = max(0, min(x1, w - 1))
        y1 = max(0, min(y1, h - 1))
        x2 = max(x1 + 1, min(x2, w))
        y2 = max(y1 + 1, min(y2, h))

        cropped = img.crop((x1, y1, x2, y2))
        cropped.save(output_path)
        print(f"✓ 图片已成功保存到: {output_path}")


def crop_left_right_black_borders(input_path, output_path, border_width=140):
    """
    裁掉图片左右两边黑边。

    :param input_path: 输入图片路径
    :param output_path: 输出图片路径
    :param border_width: 每一侧要裁掉的像素宽度，默认 140
    """
    with Image.open(input_path) as img:
        w, h = img.size
        bw = max(0, int(border_width))

        if bw * 2 >= w:
            raise ValueError(
                f"border_width={bw} 过大，图片宽度为 {w}，无法同时裁剪左右两边"
            )

        cropped = img.crop((bw, 0, w - bw, h))
        cropped.save(output_path)
        print(f"✓ 已裁掉左右黑边（每边 {bw}px），输出到: {output_path}")


# 调用函数（按照自己的需求修改参数，并调用相应函数）
input_image = "./data/input_image.jpg"
output_image = "./data/output_image_cropped.jpg"
watermark_image = "./data/image_watermark.png"

# 当前需求：裁掉左右黑边，每边约 40px
crop_left_right_black_borders(input_image, output_image, border_width=140)
