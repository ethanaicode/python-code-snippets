from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip
import numpy as np

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

    # 输出视频
    final_video.write_videofile(output_path, codec="libx264", fps=video.fps)

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

    # 输出视频
    cropped_video.write_videofile(output_path, codec="libx264", fps=video.fps)

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

    # 输出视频
    trimmed_video.write_videofile(output_path, codec="libx264", fps=video.fps)

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
    
    # 保存处理后的视频，包括音频和视频编解码器设置
    flipped_video.write_videofile(output_path, codec='libx264', audio_codec='aac')

# 调用函数(按照自己的需求修改参数，并调用相应的函数)
input_video = './data/input_video.mp4'
output_video = './data/output_video.mp4'
watermark = './data/video_watermark.png'
position = ('left', 'top')
add_watermark(input_video, output_video, watermark, position)