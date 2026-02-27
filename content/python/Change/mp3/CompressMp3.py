#压缩mp3
from pydub import AudioSegment
import os

def compress_mp3(input_path, output_path, bitrate='64k'):
    audio = AudioSegment.from_mp3(input_path)
    compressed_audio = audio.export(output_path, format="mp3", bitrate=bitrate)
    return compressed_audio

folder = r'C:\Users\i12cu84\Desktop\test'
files = [f for f in os.listdir(folder) if f.endswith((".mp3"))]
print(files)
for file in files:
    input_path = os.path.join(folder, file)
    output_path = os.path.join(folder, f"compressed_{file}")
    
    # 默认使用 64kbps 的比特率进行压缩，你可以根据需要调整
    compress_mp3(input_path, output_path, bitrate='64k')

print("Compression completed.")
