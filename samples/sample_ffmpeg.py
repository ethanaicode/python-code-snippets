import ffmpeg

input_file = './data/春天在哪里.m4a'
output_file = './data/春天在哪里.mp3'

ffmpeg.input(input_file).output(output_file, audio_bitrate='192k').run()