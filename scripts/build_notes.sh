#!/usr/bin/env bash
# 一键重建文档：自动挑 Python 3，避开 PATH 上的 Python 2.7
# 用法：bash scripts/build_notes.sh
set -e
cd "$(dirname "$0")/.."

PYCMD=()
if command -v py >/dev/null 2>&1 && py -3 -V >/dev/null 2>&1; then
    PYCMD=(py -3)
elif command -v python3 >/dev/null 2>&1 && python3 -V >/dev/null 2>&1; then
    PYCMD=(python3)
elif python -V 2>&1 | grep -q '^Python 3'; then
    PYCMD=(python)
else
    echo "未找到 Python 3。当前 python 是：$(python -V 2>&1)" >&2
    echo "请安装 Python 3.9+ 后重试，或直接用：py -3 scripts/build_notes.py" >&2
    exit 1
fi

echo "使用解释器: $("${PYCMD[@]}" -V 2>&1)"

if ! "${PYCMD[@]}" -c "import markdown" >/dev/null 2>&1; then
    echo "缺少 markdown 依赖，请执行：" >&2
    echo "  ${PYCMD[*]} -m pip install markdown" >&2
    exit 1
fi

"${PYCMD[@]}" scripts/build_notes.py "$@"
