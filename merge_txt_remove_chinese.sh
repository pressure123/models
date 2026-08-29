#!/bin/sh
# 合并文件夹中的 txt 文件，删除包含中文(CJK)的行
# 用法: ./merge_txt_remove_chinese.sh [输入文件夹] [输出文件]
# 可通过 system("./merge_txt_remove_chinese.sh ...") 调用

INPUT_DIR="${1:-./txt_input}"
OUTPUT_FILE="${2:-./merged_output.txt}"

if [ ! -d "$INPUT_DIR" ]; then
    echo "错误：输入文件夹不存在: $INPUT_DIR" >&2
    exit 1
fi

# 选择过滤器：优先 perl，其次 grep -P
if command -v perl >/dev/null 2>&1; then
    FILTER='perl -CSD -ne '"'"'print unless /[\x{4e00}-\x{9fff}\x{3400}-\x{4dbf}\x{f900}-\x{faff}]/'"'"
elif printf '' | grep -Pq '' >/dev/null 2>&1; then
    FILTER='grep -avP "[\x{4e00}-\x{9fff}\x{3400}-\x{4dbf}\x{f900}-\x{faff}]"'
else
    echo "错误：需要 perl 或支持 -P 的 grep" >&2
    exit 1
fi

# 合并所有 txt，管道末端过滤含中文的行
{
    has_file=0
    for f in "$INPUT_DIR"/*.txt; do
        [ -e "$f" ] || continue
        has_file=1
        cat "$f"
    done
    if [ "$has_file" -eq 0 ]; then
        echo "警告：文件夹中没有 txt 文件: $INPUT_DIR" >&2
    fi
} | eval "$FILTER" > "$OUTPUT_FILE"

echo "合并完成 -> $OUTPUT_FILE"
