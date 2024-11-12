from moviepy.editor import VideoFileClip

# 定义一个函数提取音频
def extract_audio(input_path, output_path):
    # 加载视频文件
    video = VideoFileClip(input_path)
    
    # 提取音频并保存为音频文件
    video.audio.write_audiofile(output_path)

# 调用函数
input_video = './data/input_video.mp4'
output_audio = './data/extracted_audio.mp3'
extract_audio(input_video, output_audio)
