from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip
import numpy as np
import os
import tempfile
import shutil

# 辅助函数：安全处理输出路径（支持中文和空格）
def safe_write_videofile(clip, output_path, **kwargs):
    """
    安全地写入视频文件，自动处理包含中文或空格的路径。
    
    :param clip: 视频片段对象
    :param output_path: 目标输出路径（可以包含中文或空格）
    :param kwargs: 传递给 write_videofile 的其他参数
    """
    # 检查输出路径是否包含非ASCII字符或可能导致问题的字符
    try:
        output_path.encode('ascii')
        has_special_chars = False
    except UnicodeEncodeError:
        has_special_chars = True
    
    # 如果包含特殊字符，使用临时文件
    if has_special_chars or ' ' in output_path:
        # 获取目标目录和文件扩展名
        output_dir = os.path.dirname(output_path)
        file_ext = os.path.splitext(output_path)[1]
        
        # 创建临时文件（使用英文名称）
        with tempfile.NamedTemporaryFile(suffix=file_ext, delete=False, dir=output_dir) as tmp_file:
            temp_path = tmp_file.name
        
        try:
            # 写入临时文件
            clip.write_videofile(temp_path, **kwargs)
            # 移动到目标路径
            shutil.move(temp_path, output_path)
            print(f"✓ 视频已成功保存到: {output_path}")
        except Exception as e:
            # 清理临时文件
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise e
    else:
        # 路径安全，直接写入
        clip.write_videofile(output_path, **kwargs)
        print(f"✓ 视频已成功保存到: {output_path}")


# 添加视频水印
def add_watermark(input_path, output_path, watermark_path, position=('center', 'center')):
    """
    为视频添加水印。

    :param input_path: 输入视频路径
    :param output_path: 输出视频路径
    :param watermark_path: 水印图片路径
    :param position: 水印位置，可以是 'center', 'left', 'right', 'top', 'bottom' 或它们的组合，或者是 (x, y) 坐标
    """

    # 读取原始视频
    video = VideoFileClip(input_path)

    # 读取水印图片并设置其位置和透明度
    watermark = (
        ImageClip(watermark_path)
        .set_duration(video.duration)  # 使水印持续整个视频
        .set_position(position)        # 设置水印位置
    )

    # 合成视频
    final_video = CompositeVideoClip([video, watermark])

    # 输出视频（支持中文路径）
    safe_write_videofile(final_video, output_path, codec="libx264", audio_codec="aac", fps=video.fps)

# 裁剪视频
def crop_video(input_path, output_path, x1, y1, x2, y2):
    """
    裁剪视频到指定区域。

    :param input_path: 输入视频路径
    :param output_path: 输出视频路径
    :param x1: 裁剪区域左上角的 x 坐标
    :param y1: 裁剪区域左上角的 y 坐标
    :param x2: 裁剪区域右下角的 x 坐标
    :param y2: 裁剪区域右下角的 y 坐标
    """
    # 读取原始视频
    video = VideoFileClip(input_path)

    # 裁剪视频
    cropped_video = video.crop(x1=x1, y1=y1, x2=x2, y2=y2)

    # 输出视频（支持中文路径）
    safe_write_videofile(cropped_video, output_path, codec="libx264", audio_codec="aac", fps=video.fps)

# 截断视频
def trim_video(input_path, output_path, start_time, end_time):
    """
    截断视频到指定时间段。

    :param input_path: 输入视频路径
    :param output_path: 输出视频路径
    :param start_time: 截断起始时间（秒）
    :param end_time: 截断结束时间（秒）
    """
    # 读取原始视频
    video = VideoFileClip(input_path)

    # 截取指定时间段
    trimmed_video = video.subclip(start_time, end_time)

    # 输出视频（支持中文路径）
    safe_write_videofile(trimmed_video, output_path, codec="libx264", audio_codec="aac", fps=video.fps)

# 镜像翻转视频
def flip_video(input_path, output_path):
    """
    镜像翻转视频。

    :param input_path: 输入视频路径
    :param output_path: 输出视频路径
    """

    # 加载视频文件
    video = VideoFileClip(input_path)
    
    # 定义一个函数用于镜像翻转帧
    def flip_image(image):
        return np.fliplr(image)

    # 应用镜像翻转到每一帧
    flipped_video = video.fl_image(flip_image)
    
    # 保存处理后的视频（支持中文路径）
    safe_write_videofile(flipped_video, output_path, codec='libx264', audio_codec='aac')

# 调用函数(按照自己的需求修改参数，并调用相应的函数)
# 现在支持包含中文和空格的路径了！
input_video = './data/input_video.mp4'
output_video = './data/output_video.mp4'
watermark = './data/video_watermark.png'
position = ('left', 'top')

# 按照自己的需求调用相应的函数
flip_video(input_video, output_video)