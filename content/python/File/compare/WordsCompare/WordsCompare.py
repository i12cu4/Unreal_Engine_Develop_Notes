import os
import shutil
from datetime import datetime

def remove_duplicates_in_file(file_path, backup=True):
    """
    对单个文件进行查重，移除重复行并保留原始顺序
    
    参数:
    file_path: 文件路径
    backup: 是否创建备份文件
    """
    try:
        # 如果需要备份，创建备份文件
        if backup and os.path.exists(file_path):
            backup_path = f"{file_path}.backup.txt"
            shutil.copy2(file_path, backup_path)
            print(f"已创建备份文件: {backup_path}")
        
        # 读取文件内容并去重（保留顺序）
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        
        # 使用字典来去重并保留顺序
        seen = set()
        unique_lines = []
        duplicates_count = 0
        
        for line in lines:
            stripped_line = line.strip()
            if stripped_line:  # 只处理非空行
                if stripped_line not in seen:
                    seen.add(stripped_line)
                    unique_lines.append(stripped_line)
                else:
                    duplicates_count += 1
            else:  # 保留空行
                unique_lines.append("")
        
        # 写回文件
        with open(file_path, 'w', encoding='utf-8') as file:
            for line in unique_lines:
                file.write(line + '\n')
        
        print(f"文件 {os.path.basename(file_path)} 查重完成:")
        print(f"  原始行数: {len(lines)}")
        print(f"  去重后行数: {len(unique_lines)}")
        print(f"  移除重复行数: {duplicates_count}")
        
        return duplicates_count
        
    except Exception as e:
        print(f"处理文件 {file_path} 时发生错误: {e}")
        return -1

def compare_txt_files(file_a_path, file_b_path, output_c_path, output_d_path, output_e_path, output_f_path):
    """
    比较两个txt文件，将A中有B中没有的行输出到C文件，将B中有A中没有的行输出到D文件，
    将A和B中都有的行输出到E文件（交集），将A和B中所有的行输出到F文件（并集）
    
    参数:
    file_a_path: 文件A的路径
    file_b_path: 文件B的路径  
    output_c_path: 输出文件C的路径（A有B无）
    output_d_path: 输出文件D的路径（B有A无）
    output_e_path: 输出文件E的路径（A和B的交集）
    output_f_path: 输出文件F的路径（A和B的并集）
    """
    
    try:
        # 读取文件A的内容
        with open(file_a_path, 'r', encoding='utf-8') as file_a:
            lines_a = set(line.strip() for line in file_a if line.strip())
        
        # 读取文件B的内容
        with open(file_b_path, 'r', encoding='utf-8') as file_b:
            lines_b = set(line.strip() for line in file_b if line.strip())
        
        # 找出A中有但B中没有的行
        a_minus_b = lines_a - lines_b
        
        # 找出B中有但A中没有的行
        b_minus_a = lines_b - lines_a
        
        # 找出A和B中都有的行（交集）
        intersection = lines_a & lines_b
        
        # 找出A和B中所有的行（并集）
        union = lines_a | lines_b
        
        # 将结果写入文件C（A有B无）
        with open(output_c_path, 'w', encoding='utf-8') as file_c:
            for line in sorted(a_minus_b):
                file_c.write(line + '\n')
        
        # 将结果写入文件D（B有A无）
        with open(output_d_path, 'w', encoding='utf-8') as file_d:
            for line in sorted(b_minus_a):
                file_d.write(line + '\n')
        
        # 将结果写入文件E（交集）
        with open(output_e_path, 'w', encoding='utf-8') as file_e:
            for line in sorted(intersection):
                file_e.write(line + '\n')
        
        # 将结果写入文件F（并集）
        with open(output_f_path, 'w', encoding='utf-8') as file_f:
            for line in sorted(union):
                file_f.write(line + '\n')
        
        # 打印统计信息
        print(f"比较完成！")
        print(f"文件A总行数: {len(lines_a)}")
        print(f"文件B总行数: {len(lines_b)}")
        print(f"输出到文件C的行数(A有B无): {len(a_minus_b)}")
        print(f"输出到文件D的行数(B有A无): {len(b_minus_a)}")
        print(f"输出到文件E的行数(交集): {len(intersection)}")
        print(f"输出到文件F的行数(并集): {len(union)}")
        
        # 验证数据一致性
        print(f"数据验证:")
        print(f"  A + B - 交集 = 并集: {len(lines_a) + len(lines_b) - len(intersection) == len(union)}")
        print(f"  C + D + E = 并集: {len(a_minus_b) + len(b_minus_a) + len(intersection) == len(union)}")
        
    except FileNotFoundError as e:
        print(f"文件未找到: {e}")
    except Exception as e:
        print(f"发生错误: {e}")

def get_script_directory():
    """获取当前Python脚本所在的目录路径"""
    return os.path.dirname(os.path.abspath(__file__))

def compare_txt_files_in_same_directory():
    """
    自动将ABCDEF六个文件放在Python代码的同路径下，并提供查重选项
    """
    # 获取当前脚本所在目录
    script_dir = get_script_directory()
    
    # 构建文件路径（放在同一目录下）
    file_a = os.path.join(script_dir, "A.txt")
    file_b = os.path.join(script_dir, "B.txt")
    output_c = os.path.join(script_dir, "C.txt")
    output_d = os.path.join(script_dir, "D.txt")
    output_e = os.path.join(script_dir, "E.txt")  # 交集文件
    output_f = os.path.join(script_dir, "F.txt")  # 并集文件
    
    print(f"脚本所在目录: {script_dir}")
    print(f"文件A路径: {file_a}")
    print(f"文件B路径: {file_b}")
    print(f"输出文件C路径(A有B无): {output_c}")
    print(f"输出文件D路径(B有A无): {output_d}")
    print(f"输出文件E路径(交集): {output_e}")
    print(f"输出文件F路径(并集): {output_f}")
    print("-" * 50)
    
    # 检查输入文件是否存在
    if not os.path.exists(file_a):
        print(f"错误: 文件A不存在 - {file_a}")
        return
    if not os.path.exists(file_b):
        print(f"错误: 文件B不存在 - {file_b}")
        return
    
    # 询问用户是否要对A和B文件进行查重
    print("是否要对A.txt和B.txt进行查重操作？")
    print("查重将移除文件中的重复行，并保留原始顺序。")
    print("系统会自动创建备份文件以防数据丢失。")
    choice = input("请输入 Y/y 确认查重，或其他键跳过: ").strip().lower()
    
    if choice == 'y':
        print("\n开始查重处理...")
        print("-" * 30)
        
        # 对文件A进行查重
        if os.path.exists(file_a):
            print(f"处理文件A: {file_a}")
            result_a = remove_duplicates_in_file(file_a)
            if result_a >= 0:
                print(f"文件A查重完成，移除了 {result_a} 个重复行")
            print("-" * 30)
        
        # 对文件B进行查重
        if os.path.exists(file_b):
            print(f"处理文件B: {file_b}")
            result_b = remove_duplicates_in_file(file_b)
            if result_b >= 0:
                print(f"文件B查重完成，移除了 {result_b} 个重复行")
            print("-" * 30)
        
        print("查重操作已完成，开始文件比较...\n")
    
    # 调用比较函数
    compare_txt_files(file_a, file_b, output_c, output_d, output_e, output_f)

# 使用示例
if __name__ == "__main__":
    compare_txt_files_in_same_directory()