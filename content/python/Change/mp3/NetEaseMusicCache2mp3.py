import os
import re
import requests
import json

def NetEaseCacheToMp3(path):
    # 确保路径存在
    if not os.path.exists(path):
        print(f"路径不存在: {path}")
        return
        
    # 初始化一个字典，用于将歌曲ID映射到文件名
    id2file = {}
    # 获取指定路径下的所有文件列表
    files = os.listdir(path)
    # 遍历路径中的每个文件
    for file in files:
        # 检查文件是否以'.uc'结尾
        if file.endswith('.uc'):
            # 使用正则表达式匹配文件名中的数字部分，使用原始字符串
            match_inst = re.match(r'\d+', file)
            # 如果匹配成功，获取歌曲ID
            if match_inst:
                song_id = match_inst.group()
                try:
                    # 构建歌曲详情的URL
                    url = f'http://music.163.com/api/song/detail/?id={song_id}&ids=%5B{song_id}%5D'
                    # 发送HTTP GET请求获取歌曲详情
                    response = requests.get(url, timeout=10)
                    response.raise_for_status()  # 检查HTTP错误
                    
                    # 解析响应内容为JSON格式
                    jsons = response.json()
                    if not jsons['songs']:
                        print(f"未找到歌曲ID: {song_id} 的信息")
                        continue
                        
                    # 获取歌曲名称
                    song_name = jsons['songs'][0]['name']
                    # 获取歌手名称（处理多歌手情况）
                    artists = jsons['songs'][0]['artists']
                    singer_name = artists[0]['name'] if artists else '未知歌手'
                    
                    # 清理文件名中的非法字符
                    invalid_chars = r'[\\/*?:"<>|]'
                    song_name = re.sub(invalid_chars, '', song_name)
                    singer_name = re.sub(invalid_chars, '', singer_name)
                    
                    # 构建完整的文件路径
                    full_file_path = os.path.join(path, file)
                    
                    # 以二进制读取模式打开UC文件
                    with open(full_file_path, 'rb') as f:
                        # 读取UC文件内容
                        uc_content = f.read()
                        # 将UC文件内容转换为字节数组
                        mp3_content = bytearray(uc_content)
                        # 对字节数组中的每个字节进行异或操作，以转换格式
                        for i in range(len(mp3_content)):
                            mp3_content[i] ^= 0xa3
                    
                    # 构建转换后的MP3文件名
                    mp3_file_name = os.path.join(path, f'{singer_name} - {song_name}.mp3')
                    
                    # 检查文件是否已存在
                    if os.path.exists(mp3_file_name):
                        print(f"文件已存在，跳过: {mp3_file_name}")
                        continue
                    
                    # 以二进制写入模式打开新的MP3文件
                    with open(mp3_file_name, 'wb') as mp3_file:
                        # 将转换后的内容写入MP3文件
                        mp3_file.write(mp3_content)
                        # 打印成功转换的MP3文件名
                        print(f'成功转换: {mp3_file_name}')
                        
                except requests.exceptions.RequestException as e:
                    print(f"获取歌曲信息失败 (ID: {song_id}): {str(e)}")
                except json.JSONDecodeError:
                    print(f"解析歌曲信息失败 (ID: {song_id})")
                except Exception as e:
                    print(f"处理文件 {file} 时出错: {str(e)}")

# 指定歌曲缓存路径
path = r'C:\Users\Admin\Downloads\NetEaseCache\task'
# 调用函数开始处理歌曲文件
NetEaseCacheToMp3(path)