#!/usr/bin/env bash
# check_phase.sh — 阶段完成确定性判定器（薄入口）。
#
# 判定实现全部在 specmark_state.py（单一谓词源，跨平台：无 flock/grep -P 依赖）。
# 本脚本只做参数转发，保持既有调用约定不变。
#
# 子命令：
#   artifacts <change>           检查产物完整性
#   tasks <change>               检查任务完成状态（含 [~] 阻塞态与收敛轮数）
#   converge-readiness <change>  检查是否可进入 converge（原始任务全勾）
#   archive-readiness <change>   检查是否可归档
#   complexity <change>          三档复杂度判定（simple/medium/complex）
#
# 退出码：0 = 条件满足；1 = 条件不满足；2 = 输入错误。
# JSON 恒输出到 stdout；人类可读摘要到 stderr（--json 时静默）。

set -euo pipefail

# 便携符号链接解析（不依赖 readlink -f，macOS 旧版可用）
SOURCE="$0"
while [ -L "$SOURCE" ]; do
  DIR="$(cd "$(dirname "$SOURCE")" && pwd)"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE"
done
SCRIPT_DIR="$(cd "$(dirname "$SOURCE")" && pwd)"

usage() {
  cat <<'EOF'
Usage: check_phase.sh <subcommand> <change-name> [--root <project-root>] [--json]

Subcommands:
  artifacts <name>          检查产物完整性
  tasks <name>              检查任务完成状态（含 [~] 阻塞态与收敛轮数）
  converge-readiness <name> 检查是否可进入 converge
  archive-readiness <name>  检查是否可归档
  complexity <name>         三档复杂度判定（simple/medium/complex）

Options:
  --root <dir>  项目根目录（任意参数位；默认：cwd 所在 git 仓库顶层，可用 SPECMARK_ROOT 覆盖）
  --json        静默 stderr 人类摘要（stdout 恒为 JSON）

Exit codes: 0 = condition met; 1 = condition not met; 2 = input error.
EOF
}

err() { printf '[ERROR] %s\n' "$*" >&2; }

[[ $# -ge 1 ]] || { usage; exit 2; }
SUBCMD="$1"
case "$SUBCMD" in
  artifacts|tasks|converge-readiness|archive-readiness|complexity) ;;
  -h|--help) usage; exit 0 ;;
  *) err "未知子命令: $SUBCMD"; usage; exit 2 ;;
esac

shift
[[ $# -ge 1 ]] || { usage; exit 2; }
CHANGE_NAME="$1"
shift

exec python3 "$SCRIPT_DIR/specmark_state.py" check "$SUBCMD" "$CHANGE_NAME" "$@"
