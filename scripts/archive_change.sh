#!/usr/bin/env bash
# archive_change.sh — 归档/恢复执行器（薄入口）。
#
# 锁（fcntl，跨平台）、只读哨兵、完整性门禁、无部分写入的 delta sync、
# commit SHA 锚定、restore 逆向恢复全部实现在 specmark_state.py。
#
# 用法：
#   archive_change.sh <change-name> [--sync] [--date YYYY-MM-DD] [--dry-run] [--allow-unfinished]
#   archive_change.sh restore <archive-dir-or-change-name>
#
# 退出码：0 成功；1 输入/状态错误（含完整性门禁拒绝）；2 锁竞争失败；3 平台不支持。

set -euo pipefail

SOURCE="$0"
while [ -L "$SOURCE" ]; do
  DIR="$(cd "$(dirname "$SOURCE")" && pwd)"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE"
done
SCRIPT_DIR="$(cd "$(dirname "$SOURCE")" && pwd)"

usage() {
  cat <<'EOF'
Usage:
  archive_change.sh <change-name> [--sync] [--date YYYY-MM-DD] [--dry-run] [--allow-unfinished]
  archive_change.sh restore <archive-dir-or-change-name>

Archive mode moves specmark/changes/<name> to specmark/archive/<date>-<name> under an
exclusive per-change fcntl lock, enforces the archive read-only sentinel, optionally
syncs delta specs (merged in-memory first, atomically replaced only when ALL succeed),
and writes meta.json anchoring the archive to the current git commit SHA.

  --sync              Merge delta specs into specmark/specs/ before archiving.
  --date YYYY-MM-DD   Override archive date stamp (default: today UTC).
  --dry-run           Preview without moving files or writing meta.json.
  --allow-unfinished  Archive despite unfinished tasks / missing artifacts (requires user
                      confirmation); a snapshot is recorded into meta.json.
  --lock-timeout SEC  Lock wait seconds (default 10; contention exits with code 2).

Restore mode moves a mis-archived change back to specmark/changes/<name>/ inside the
same per-change lock, removing meta.json. Accepts the full archive dir name
(<date>-<name>) or the bare change name when unambiguous.

Exit codes: 0 ok; 1 input/state error (incl. completeness gate); 2 lock contention; 3 unsupported platform.
EOF
}

[[ $# -ge 1 ]] || { echo "[ERROR] 需要 change 名或 restore 子命令" >&2; usage; exit 1; }

case "$1" in
  restore)
    shift
    exec python3 "$SCRIPT_DIR/specmark_state.py" restore "$@"
    ;;
  -h|--help)
    usage; exit 0
    ;;
  -*)
    echo "[ERROR] 未知选项: $1" >&2; usage; exit 1
    ;;
esac

MODE_ARGS=(archive "$1")
shift
exec python3 "$SCRIPT_DIR/specmark_state.py" "${MODE_ARGS[@]}" "$@"
