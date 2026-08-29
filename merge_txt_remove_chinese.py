"""合并文件夹中的 txt 文件，并删除包含中文的行。

用法:
    python merge_txt_remove_chinese.py [输入文件夹] [输出文件]

默认:
    输入文件夹 = ./txt_input
    输出文件   = ./merged_output.txt
"""

import os
import re
import sys


# 匹配中日韩统一表意文字（CJK Unified Ideographs）
_CHINESE_RE = re.compile(r'[\u4e00-\u9fff\u3400-\u4dbf\uf900-\ufaff]')


def contains_chinese(line: str) -> bool:
    """判断一行是否包含中文字符。"""
    return bool(_CHINESE_RE.search(line))


def merge_txt_files(input_dir: str, output_file: str) -> None:
    if not os.path.isdir(input_dir):
        print(f"错误：输入文件夹不存在: {input_dir}")
        sys.exit(1)

    txt_files = sorted(
        f for f in os.listdir(input_dir) if f.lower().endswith('.txt')
    )

    if not txt_files:
        print(f"警告：文件夹中没有 txt 文件: {input_dir}")
        return

    total_lines = 0
    removed_lines = 0

    with open(output_file, 'w', encoding='utf-8') as out:
        for filename in txt_files:
            filepath = os.path.join(input_dir, filename)
            with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                for line in f:
                    total_lines += 1
                    if contains_chinese(line):
                        removed_lines += 1
                        continue
                    out.write(line)

    print(f"合并完成: {len(txt_files)} 个文件 -> {output_file}")
    print(f"总行数: {total_lines}，删除中文行: {removed_lines}，"
          f"保留: {total_lines - removed_lines}")


def main() -> None:
    input_dir = sys.argv[1] if len(sys.argv) > 1 else './txt_input'
    output_file = sys.argv[2] if len(sys.argv) > 2 else './merged_output.txt'
    merge_txt_files(input_dir, output_file)


if __name__ == '__main__':
    main()
