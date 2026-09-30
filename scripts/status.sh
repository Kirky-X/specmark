#!/usr/bin/env bash
# status.sh — specmark 全局状态查询（薄入口）。
#
# 状态收集与阶段推断实现在 specmark_state.py（单一谓词源）。
# 本脚本只做参数转发，保持既有调用约定不变。
#
# 用法：
#   status.sh [--json] [--root <project-root>]
#
# 退出码：0 正常；2 参数错误。

set -euo pipefail

SOURCE="$0"
while [ -L "$SOURCE" ]; do
  DIR="$(cd "$(dirname "$SOURCE")" && pwd)"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE"
done
SCRIPT_DIR="$(cd "$(dirname "$SOURCE")" && pwd)"

usage() {
  echo "Usage: status.sh [--json] [--root <dir>]"
}

JSON_ARGS=()
ROOT_ARGS=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --json) JSON_ARGS+=(--json) ;;
    --root)
      shift
      [[ $# -gt 0 ]] || { echo '[ERROR] --root 需要参数' >&2; exit 2; }
      ROOT_ARGS+=(--root "$1")
      ;;
    -h|--help) usage; exit 0 ;;
    *) echo "[ERROR] 未知选项: $1" >&2; usage; exit 2 ;;
  esac
  shift
done

exec python3 "$SCRIPT_DIR/specmark_state.py" status "${JSON_ARGS[@]+"${JSON_ARGS[@]}"}" "${ROOT_ARGS[@]+"${ROOT_ARGS[@]}"}"
