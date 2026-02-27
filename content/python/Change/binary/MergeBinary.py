def merge_binary_files(input_files, output_file):
    try:
        with open(output_file, 'wb') as output:
            for input_file in input_files:
                with open(input_file, 'rb') as input:
                    output.write(input.read())
        print("文件合并完成，已保存为", output_file)
    except Exception as e:
        print("合并文件时出错:", str(e))

if __name__ == "__main__":
    input_files = ["E:\file1.bin", "E:\file2.bin"]  # 输入文件列表
    output_file = "E:\merged_file.bin"  # 合并后的输出文件名
    merge_binary_files(input_files, output_file)