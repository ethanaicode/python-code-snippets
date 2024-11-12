from moviepy.editor import VideoFileClip
import numpy as np

# 定义一个函数用于镜像翻转视频
def flip_video(input_path, output_path):
    # 加载视频文件
    video = VideoFileClip(input_path)
    
    # 定义一个函数用于镜像翻转帧
    def flip_image(image):
        return np.fliplr(image)

    # 应用镜像翻转到每一帧
    flipped_video = video.fl_image(flip_image)
    
    # 保存处理后的视频，包括音频和视频编解码器设置
    flipped_video.write_videofile(output_path, codec='libx264', audio_codec='aac')


# 调用函数
input_video = './data/input_video.mp4'
output_video = './data/flipped_video.mp4'
flip_video(input_video, output_video)
