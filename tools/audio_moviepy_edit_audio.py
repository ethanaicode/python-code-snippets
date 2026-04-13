from moviepy.editor import AudioFileClip, concatenate_audioclips
import os
import tempfile
import shutil

# 辅助函数：安全处理输出路径（支持中文和空格）
def safe_write_audiofile(clip, output_path, **kwargs):
    """
    安全地写入音频文件，自动处理包含中文或空格的路径。
    
    :param clip: 音频片段对象
    :param output_path: 目标输出路径（可以包含中文或空格）
    :param kwargs: 传递给 write_audiofile 的其他参数
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
            clip.write_audiofile(temp_path, **kwargs)
            # 移动到目标路径
            shutil.move(temp_path, output_path)
            print(f"✓ 音频已成功保存到: {output_path}")
        except Exception as e:
            # 清理临时文件
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise e
    else:
        # 路径安全，直接写入
        clip.write_audiofile(output_path, **kwargs)
        print(f"✓ 音频已成功保存到: {output_path}")


# 裁截音频
def trim_audio(input_path, output_path, start_time, end_time):
    """
    裁截音频到指定时间段，去掉无用的首尾片段。

    :param input_path: 输入音频路径
    :param output_path: 输出音频路径
    :param start_time: 裁截起始时间（秒）
    :param end_time: 裁截结束时间（秒），如果为 None 则截取到音频末尾
    """
    # 读取原始音频
    audio = AudioFileClip(input_path)
    
    print(f"原音频时长: {audio.duration:.2f} 秒")
    
    # 截取指定时间段
    if end_time is None:
        trimmed_audio = audio.subclip(start_time)
    else:
        trimmed_audio = audio.subclip(start_time, end_time)
    
    print(f"裁截后时长: {trimmed_audio.duration:.2f} 秒")
    
    # 输出音频（支持中文路径）
    safe_write_audiofile(trimmed_audio, output_path, codec='libmp3lame', bitrate='192k')
    
    # 释放资源
    audio.close()
    trimmed_audio.close()


# 重复音频
def repeat_audio(input_path, output_path, repeat_times):
    """
    重复音频指定次数，以满足时长需求。

    :param input_path: 输入音频路径
    :param output_path: 输出音频路径
    :param repeat_times: 重复次数
    """
    # 读取原始音频
    audio = AudioFileClip(input_path)
    
    print(f"原音频时长: {audio.duration:.2f} 秒")
    
    # 创建重复的音频列表
    audio_clips = [audio] * repeat_times
    
    # 拼接所有音频
    final_audio = concatenate_audioclips(audio_clips)
    
    print(f"重复 {repeat_times} 次后时长: {final_audio.duration:.2f} 秒")
    
    # 输出音频（支持中文路径）
    safe_write_audiofile(final_audio, output_path, codec='libmp3lame', bitrate='192k')
    
    # 释放资源
    audio.close()
    final_audio.close()


# 拼接多个音频（支持音频队列）
def concatenate_audio(audio_paths, output_path):
    """
    拼接多个音频文件，可以是不同的音频或重复的音频。

    :param audio_paths: 音频文件路径列表，例如 ['audio1.mp3', 'audio2.mp3', 'audio1.mp3']
    :param output_path: 输出音频路径
    """
    # 读取所有音频
    audio_clips = [AudioFileClip(path) for path in audio_paths]
    
    print(f"音频片段数量: {len(audio_clips)}")
    for i, clip in enumerate(audio_clips):
        print(f"  片段 {i+1}: {audio_paths[i]} (时长: {clip.duration:.2f} 秒)")
    
    # 拼接所有音频
    final_audio = concatenate_audioclips(audio_clips)
    
    print(f"拼接后总时长: {final_audio.duration:.2f} 秒")
    
    # 输出音频（支持中文路径）
    safe_write_audiofile(final_audio, output_path, codec='libmp3lame', bitrate='192k')
    
    # 释放资源
    for clip in audio_clips:
        clip.close()
    final_audio.close()


# 重复拼接以达到目标时长
def repeat_to_duration(input_path, output_path, target_duration, allow_exceed=True):
    """
    重复音频直到达到或超过目标时长。

    :param input_path: 输入音频路径
    :param output_path: 输出音频路径
    :param target_duration: 目标时长（秒）
    :param allow_exceed: 是否允许超过目标时长（默认 True，避免音频被突然裁断）
    """
    # 读取原始音频
    audio = AudioFileClip(input_path)
    
    print(f"原音频时长: {audio.duration:.2f} 秒")
    print(f"目标时长: {target_duration:.2f} 秒")
    
    # 计算需要重复的次数
    repeat_times = int(target_duration / audio.duration) + 1
    
    # 创建重复的音频列表
    audio_clips = [audio] * repeat_times
    
    # 拼接所有音频
    final_audio = concatenate_audioclips(audio_clips)
    
    # 根据参数决定是否裁截到目标时长
    if not allow_exceed and final_audio.duration > target_duration:
        final_audio = final_audio.subclip(0, target_duration)
        print(f"重复 {repeat_times} 次后时长: {final_audio.duration:.2f} 秒（已裁截到目标时长）")
    else:
        print(f"重复 {repeat_times} 次后时长: {final_audio.duration:.2f} 秒")
    
    # 输出音频（支持中文路径）
    safe_write_audiofile(final_audio, output_path, codec='libmp3lame', bitrate='192k')
    
    # 释放资源
    audio.close()
    final_audio.close()


# ==================== 使用示例 ====================
if __name__ == "__main__":
    # 示例 1: 裁截音频（去掉前5秒和后3秒的无用片段）
    # trim_audio(
    #     input_path='./data/input_audio.mp3',
    #     output_path='./data/trimmed_audio.mp3',
    #     start_time=5,      # 从第5秒开始
    #     end_time=-3        # 到倒数第3秒结束（负数表示从末尾倒数）
    # )
    
    # 示例 2: 重复音频10次
    # repeat_audio(
    #     input_path='./data/input_audio.mp3',
    #     output_path='./data/repeated_audio.mp3',
    #     repeat_times=10
    # )
    
    # 示例 3: 拼接多个音频（可以重复同一个或使用不同的音频）
    # concatenate_audio(
    #     audio_paths=[
    #         './data/audio1.mp3',
    #         './data/audio2.mp3',
    #         './data/audio1.mp3',  # 重复 audio1
    #         './data/audio3.mp3'
    #     ],
    #     output_path='./data/concatenated_audio.mp3'
    # )
    
    # 示例 4: 重复音频以达到目标时长（例如10分钟 = 600秒）
    # repeat_to_duration(
    #     input_path='./data/input_audio.mp3',
    #     output_path='./data/temp_trimmed.mp3',
    #     target_duration=600,  # 10分钟
    #     allow_exceed=True     # 允许超过目标时长，避免音频被突然裁断（默认 True）
    # )
    
    # 示例 5: 组合使用 - 先裁截再重复
    # 第一步：裁截音频
    # trim_audio(
    #     input_path='./data/input_audio.mp3',
    #     output_path='./data/temp_trimmed.mp3',
    #     start_time=2,
    #     end_time=-1
    # )
    # 第二步：重复裁截后的音频
    # repeat_to_duration(
    #     input_path='./data/temp_trimmed.mp3',
    #     output_path='./data/final_audio.mp3',
    #     target_duration=600,
    #     allow_exceed=True  # 允许超过600秒
    # )
    
    print("请根据需求取消注释相应的函数调用！")
