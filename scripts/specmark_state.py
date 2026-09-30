#!/usr/bin/env python3
"""specmark_state.py — specmark 状态判定与归档操作的单一实现。

check_phase.sh / status.sh / archive_change.sh 是薄入口，判定与写操作全部在本模块：
  - 任务解析（四态：- [ ] / - [x] / - [~]，含 Convergence 节与轮数计数）
  - 产物存在性、阶段推断、三档复杂度（simple/medium/complex）
  - 状态查询（活动/归档 + next_command 确定性路由）
  - 归档执行器：fcntl 进程锁（跨平台，替代 util-linux flock）、无部分写入的
    delta sync（先全部合并到临时文件再原子替换）、--allow-unfinished 豁免快照、
    commit SHA 锚定、restore 逆向恢复

被其他 Python 脚本 import 时提供纯函数；独立运行时提供 CLI。
退出码：0 = 条件满足/成功；1 = 条件不满足/拒绝执行/输入状态错误；2 = 输入错误（check/status 路径）与锁竞争（archive 路径专属）；3 = 平台不支持。
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent

KEBAB_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
TASK_RE = re.compile(r"^- \[([xX~ ])\]")
CONVERGENCE_SECTION_RE = re.compile(r"^## Phase \d+: Convergence")
DOMAIN_RE = re.compile(r"<!--\s*domain:\s*([a-z]+)")
CODE_PATH_RE = re.compile(r"(?:src/|lib/|app/)?[A-Za-z0-9_/-]+\.[A-Za-z]+")
DELIVERABLE_RE = re.compile(r"→\s*(\S+)")
ARCHIVE_PREFIX_RE = re.compile(r"^\d{4}-\d{2}-\d{2}-")

CHANGE_MISSING_REMEDY = "Run /specmark propose {name} to create the change and its artifacts"


class StateError(Exception):
    """带结构化错误码的状态错误（对应 CLI 退出码 1 或 2）。"""

    def __init__(self, code: str, message: str, remedy: str = "", exit_code: int = 1):
        super().__init__(message)
        self.code = code
        self.message = message
        self.remedy = remedy
        self.exit_code = exit_code


class LockTimeout(StateError):
    def __init__(self, lock_path: Path):
        super().__init__(
            "lock_contention",
            f"无法获取锁（其他进程持有，已等满超时）: {lock_path}",
            remedy="等待其他 specmark 进程完成后重试；确认无进程后再清理 specmark/.locks/ 残留锁文件",
            exit_code=2,
        )


# ---------- 路径解析 ----------

def resolve_root(root_arg: str | None) -> Path:
    """--root > 环境变量 SPECMARK_ROOT > 调用方 cwd 所在 git 仓库顶层 > cwd。"""
    if root_arg:
        return Path(root_arg).expanduser().resolve()
    env = os.environ.get("SPECMARK_ROOT")
    if env:
        return Path(env).expanduser().resolve()
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, check=True,
        )
        top = out.stdout.strip()
        if top:
            return Path(top).resolve()
    except (OSError, subprocess.SubprocessError):
        pass
    return Path.cwd().resolve()


def skill_version() -> str:
    try:
        meta = json.loads((SCRIPT_DIR.parent / "skill.json").read_text(encoding="utf-8"))
        return str(meta.get("version", "unknown"))
    except (OSError, ValueError):
        return "unknown"


def validate_change_name(name: str, exit_code: int = 2) -> None:
    if not KEBAB_RE.match(name):
        raise StateError(
            "invalid_change_name",
            f"非法 change 名（须 kebab-case）: {name}",
            exit_code=exit_code,
        )


def changes_dir(root: Path) -> Path:
    return root / "specmark" / "changes"


def archive_dir(root: Path) -> Path:
    return root / "specmark" / "archive"


def locks_dir(root: Path) -> Path:
    return root / "specmark" / ".locks"


def change_dir(root: Path, name: str) -> Path:
    return changes_dir(root) / name


# ---------- 任务解析（单一谓词源） ----------

@dataclass
class TaskStats:
    total: int = 0
    completed: int = 0
    open: int = 0
    blocked: int = 0
    original_total: int = 0
    original_completed: int = 0
    convergence_total: int = 0
    convergence_completed: int = 0
    convergence_rounds: int = 0
    blocked_items: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "total": self.total,
            "completed": self.completed,
            "remaining": self.open + self.blocked,
            "open": self.open,
            "blocked": self.blocked,
            "blocked_items": self.blocked_items,
            "original_total": self.original_total,
            "original_completed": self.original_completed,
            "convergence_total": self.convergence_total,
            "convergence_completed": self.convergence_completed,
            "convergence_rounds": self.convergence_rounds,
            "all_original_done": int(self.original_total > 0 and self.original_completed == self.original_total),
            "all_done": int(self.total > 0 and self.completed == self.total),
        }


def parse_tasks_text(text: str) -> TaskStats:
    stats = TaskStats()
    in_convergence = False
    for lineno, line in enumerate(text.split("\n"), 1):
        if CONVERGENCE_SECTION_RE.match(line):
            in_convergence = True
            stats.convergence_rounds += 1
            continue
        m = TASK_RE.match(line)
        if not m:
            continue
        mark = m.group(1)
        stats.total += 1
        if mark in ("x", "X"):
            stats.completed += 1
        elif mark == "~":
            stats.blocked += 1
            stats.blocked_items.append({"line": lineno, "text": line.strip()})
        else:
            stats.open += 1
        if in_convergence:
            stats.convergence_total += 1
            if mark in ("x", "X"):
                stats.convergence_completed += 1
        else:
            stats.original_total += 1
            if mark in ("x", "X"):
                stats.original_completed += 1
    return stats


def load_tasks_stats(tasks_file: Path) -> TaskStats:
    """tasks.md 不存在时抛结构化错误（不静默计 0）。"""
    if not tasks_file.is_file():
        raise StateError("tasks_md_not_found", f"tasks.md 不存在: {tasks_file}", exit_code=2)
    return parse_tasks_text(tasks_file.read_text(encoding="utf-8", errors="replace"))


# ---------- 产物与阶段 ----------

def artifact_presence(cdir: Path) -> dict:
    specs = cdir / "specs"
    spec_count = 0
    if specs.is_dir():
        spec_count = sum(1 for _ in specs.glob("*/spec.md"))
    presence = {
        "proposal": int((cdir / "proposal.md").is_file()),
        "design": int((cdir / "design.md").is_file()),
        "tasks": int((cdir / "tasks.md").is_file()),
        "specs": int(spec_count > 0),
        "spec_count": spec_count,
    }
    presence["all_present"] = int(
        presence["proposal"] == 1 and presence["design"] == 1 and presence["tasks"] == 1
    )
    return presence


def infer_phase(cdir: Path, stats: TaskStats | None = None) -> str:
    """阶段推断（status.md 规则表的唯一实现）。

    无 tasks.md：有 proposal → propose；仅 design → explore；全无 → new。
    有 tasks.md：0 任务 → propose；原始任务全勾（>0）→ converge；否则 → apply。
    stats 可传入已解析的任务计数，避免重复读文件。
    """
    presence = artifact_presence(cdir)
    if presence["tasks"] == 0:
        if presence["proposal"] == 1:
            return "propose"
        if presence["design"] == 1:
            return "explore"
        return "new"
    if stats is None:
        stats = parse_tasks_text((cdir / "tasks.md").read_text(encoding="utf-8", errors="replace"))
    if stats.total == 0:
        return "propose"
    if stats.original_total > 0 and stats.original_completed == stats.original_total:
        return "converge"
    return "apply"


def _strip_filename(path_text: str) -> str:
    return re.sub(r"/[^/]*$", "", path_text)


def complexity_of(cdir: Path) -> dict:
    """三档复杂度（对齐 SKILL.md 自动链短路表）：simple / medium / complex。

    complex：任务数 ≥5 或模块数 ≥3 或 proposal Scope 跨多个能力域；
    simple：任务数 ≤2 且模块数 ≤1 且非多域；
    其余 → medium。delta spec 生成与「propose 之后跳过 analyze/converge」均以本判定为准。
    """
    presence = artifact_presence(cdir)
    if presence["tasks"] == 0:
        raise StateError(
            "tasks_md_not_found",
            f"tasks.md 不存在，无法评估复杂度: {cdir / 'tasks.md'}",
            remedy=CHANGE_MISSING_REMEDY.format(name=cdir.name),
            exit_code=2,
        )

    tasks_file = cdir / "tasks.md"
    tasks_text = tasks_file.read_text(encoding="utf-8", errors="replace")
    stats = parse_tasks_text(tasks_text)

    # proposal.md 只读一次：domain 提取与 Scope 宽度统计共用同一文本
    proposal_text = ""
    proposal_file = cdir / "proposal.md"
    if proposal_file.is_file():
        proposal_text = proposal_file.read_text(encoding="utf-8", errors="replace")
    domain_m = DOMAIN_RE.search(proposal_text)
    domain = domain_m.group(1) if domain_m else "code"

    if domain == "code":
        modules = {
            _strip_filename(m.group(0))
            for m in CODE_PATH_RE.finditer(tasks_text)
        }
    else:
        modules = {
            _strip_filename(m.group(1))
            for m in DELIVERABLE_RE.finditer(tasks_text)
        }
    module_count = len(modules)

    multi_domain = 0
    if proposal_text and _section_line_count(proposal_text, "Scope") > 10:
        multi_domain = 1

    task_count = stats.total
    is_complex = task_count >= 5 or module_count >= 3 or multi_domain == 1
    is_simple = task_count <= 2 and module_count <= 1 and multi_domain == 0
    if is_complex:
        complexity = "complex"
    elif is_simple:
        complexity = "simple"
    else:
        complexity = "medium"

    return {
        "change": cdir.name,
        "complexity": complexity,
        "long": int(complexity == "complex"),  # 旧契约别名：v0.2.3 的 short/long 二值语义
        "delta_spec": int(complexity == "complex"),
        "domain": domain,
        "task_count": task_count,
        "module_count": module_count,
        "multi_domain": multi_domain,
        "criteria": {
            "tasks_ge_5": task_count >= 5,
            "modules_ge_3": module_count >= 3,
            "multi_domain": multi_domain == 1,
            "tasks_le_2": task_count <= 2,
            "modules_le_1": module_count <= 1,
        },
    }


def _section_line_count(text: str, section: str) -> int:
    """统计 `## <section>` 到下一个 `## ` 标题之间的行数（含标题行，与原 sed 语义一致）。"""
    in_section = False
    count = 0
    for line in text.split("\n"):
        if re.match(r"^##\s+", line):
            if in_section:
                break
            if line.strip().lstrip("#").strip() == section:
                in_section = True
                count = 1
            continue
        if in_section:
            count += 1
    return count


# ---------- 归档 meta（缺字段容错，前向兼容） ----------

def read_meta(entry: Path) -> dict:
    meta_file = entry / "meta.json"
    meta = {"archived_at": "unknown", "synced": False, "commit_sha": None}
    if meta_file.is_file():
        try:
            raw = json.loads(meta_file.read_text(encoding="utf-8"))
            if isinstance(raw, dict):
                meta["archived_at"] = raw.get("archived_at", "unknown")
                meta["synced"] = bool(raw.get("synced", False))
                meta["commit_sha"] = raw.get("commit_sha")
                meta["unfinished"] = raw.get("unfinished")
        except ValueError:
            meta["archived_at"] = "invalid-meta"
    return meta


# ---------- next_command（确定性路由） ----------

def _change_next(name: str, phase: str) -> str:
    if phase in ("new", "explore"):
        return f"/specmark propose {name}"
    if phase == "propose":
        return f"/specmark propose {name}（补全产物）"
    if phase == "apply":
        return f"/specmark apply {name}"
    return f"/specmark converge {name}"


def next_command(active: list[dict]) -> str:
    """按 converge > apply > propose > explore > new 优先级推导全局下一步。"""
    if not active:
        return "/specmark explore 或 /specmark propose <name>"
    for phase in ("converge", "apply", "propose", "explore", "new"):
        for entry in active:
            if entry["phase"] == phase:
                return _change_next(entry["name"], phase)
    return "/specmark status"


# ---------- 状态收集 ----------

def list_entries(base: Path) -> list[str]:
    if not base.is_dir():
        return []
    return sorted(
        d.name for d in base.iterdir()
        if d.is_dir() and not d.name.startswith(".")
    )


def collect_status(root: Path) -> dict:
    active = []
    for name in list_entries(changes_dir(root)):
        cdir = changes_dir(root) / name
        tasks_file = cdir / "tasks.md"
        stats = None
        entry = {"name": name, "phase": "", "tasks": "0/0", "blocked": 0, "specs": 0, "next": ""}
        if tasks_file.is_file():
            stats = parse_tasks_text(tasks_file.read_text(encoding="utf-8", errors="replace"))
            entry["tasks"] = f"{stats.completed}/{stats.total}"
            entry["blocked"] = stats.blocked
        entry["phase"] = infer_phase(cdir, stats)
        entry["specs"] = artifact_presence(cdir)["spec_count"]
        entry["next"] = _change_next(name, entry["phase"])
        active.append(entry)

    archived = []
    for dirname in list_entries(archive_dir(root)):
        meta = read_meta(archive_dir(root) / dirname)
        sha = meta.get("commit_sha")
        archived.append({
            "dir": dirname,
            "archived_at": meta["archived_at"],
            "synced": meta["synced"],
            "commit_sha": sha if sha else "null",
        })

    return {
        "active_changes": active,
        "archived_changes": archived,
        "next_command": next_command(active),
    }


def status_table(status: dict) -> str:
    lines = ["## Specmark 状态", ""]
    active = status["active_changes"]
    if not active:
        lines += ["**活动变更：** 无", ""]
    else:
        lines += [f"**活动变更：** {len(active)} 个", ""]
        lines += ["| 变更名 | 阶段 | 进度 | 阻塞 | delta spec |", "|--------|------|------|------|------------|"]
        for e in active:
            spec_info = f"{e['specs']} 个" if e["specs"] > 0 else "无"
            lines.append(f"| {e['name']} | {e['phase']} | {e['tasks']} | {e['blocked']} | {spec_info} |")
        lines.append("")

    archived = status["archived_changes"]
    if not archived:
        lines.append("**已归档变更：** 无")
    else:
        lines += [f"**已归档变更：** {len(archived)} 个（最近 5 个）", ""]
        lines += ["| 归档目录 | 日期 | synced | commit |", "|----------|------|--------|--------|"]
        for e in reversed(archived[-5:]):
            synced = "✓" if e["synced"] else "✗"
            sha = e["commit_sha"]
            sha_short = sha[:7] if isinstance(sha, str) and len(sha) >= 7 else "null"
            lines.append(f"| {e['dir']} | {e['archived_at']} | {synced} | {sha_short} |")

    lines += ["", f"**建议下一步：** {status['next_command']}"]
    return "\n".join(lines)


# ---------- check 子命令 ----------

def _emit(payload: dict, human: list[str], quiet: bool) -> None:
    print(json.dumps(payload, ensure_ascii=False))
    for line in human:
        if not quiet:
            print(line, file=sys.stderr)


def cmd_check(sub: str, name: str, root: Path, quiet: bool) -> int:
    validate_change_name(name)
    cdir = change_dir(root, name)
    if not cdir.is_dir():
        raise StateError(
            "change_dir_not_found",
            f"change 目录不存在: {cdir}",
            remedy=CHANGE_MISSING_REMEDY.format(name=name),
            exit_code=2,
        )

    if sub == "artifacts":
        p = artifact_presence(cdir)
        payload = {"change": name, **p}
        human = []
        if p["all_present"] == 1:
            extra = f" + {p['spec_count']} specs" if p["specs"] == 1 else ""
            human.append(f"[INFO] ✓ 产物完整 (proposal + design + tasks{extra})")
        else:
            missing = [f for f in ("proposal", "design", "tasks") if p[f] == 0]
            human.append(f"[INFO] ✗ 缺失产物: {', '.join(m + '.md' for m in missing)}")
            payload["remedy"] = f"Run /specmark propose {name} to create missing artifacts"
        _emit(payload, human, quiet)
        return 0 if p["all_present"] == 1 else 1

    if sub == "tasks":
        try:
            stats = load_tasks_stats(cdir / "tasks.md")
        except StateError as e:
            payload = {
                "change": name,
                "tasks_file": None,
                "total": None, "completed": None, "remaining": None,
                "original_total": None, "original_completed": None,
                "convergence_total": None, "convergence_completed": None,
                "convergence_rounds": None,
                "all_original_done": None, "all_done": None,
                "error_code": e.code,
                "remedy": CHANGE_MISSING_REMEDY.format(name=name),
            }
            _emit(payload, [f"[ERROR] {e.message}"], quiet)
            return e.exit_code
        payload = {"change": name, **stats.to_dict()}
        human = [
            f"[INFO] 任务进度: {stats.completed}/{stats.total} 完成"
            f" (原始: {stats.original_completed}/{stats.original_total},"
            f" 收敛: {stats.convergence_completed}/{stats.convergence_total},"
            f" 轮数: {stats.convergence_rounds})"
        ]
        d = payload
        if d["all_done"] == 1:
            human.append("[INFO] ✓ 所有任务完成")
        elif d["all_original_done"] == 1:
            human.append(f"[INFO] ✓ 原始任务全部完成，收敛任务仍有 {d['convergence_total'] - d['convergence_completed']} 个")
        else:
            human.append(f"[INFO] ✗ 仍有 {d['remaining']} 个任务未完成（含阻塞 {stats.blocked} 个）")
        _emit(payload, human, quiet)
        return 0 if d["all_done"] == 1 else 1

    if sub == "converge-readiness":
        try:
            stats = load_tasks_stats(cdir / "tasks.md")
        except StateError as e:
            payload = {"change": name, "ready": False, "reason": e.code, "remedy": CHANGE_MISSING_REMEDY.format(name=name)}
            _emit(payload, [f"[ERROR] {e.message}"], quiet)
            return e.exit_code
        if stats.original_total == 0:
            payload = {"change": name, "ready": False, "reason": "no tasks found",
                       "remedy": f"Run /specmark propose {name} to create tasks"}
            _emit(payload, ["[INFO] ✗ 未找到任何任务"], quiet)
            return 1
        if stats.original_completed < stats.original_total:
            open_count = stats.original_total - stats.original_completed
            payload = {"change": name, "ready": False, "original_total": stats.original_total,
                       "original_open": open_count,
                       "remedy": f"Run /specmark apply {name} to complete {open_count} original tasks"}
            _emit(payload, [f"[INFO] ✗ 仍有 {open_count} 个原始任务未完成，不能进入 converge"], quiet)
            return 1
        payload = {"change": name, "ready": True, "original_total": stats.original_total}
        _emit(payload, ["[INFO] ✓ 所有原始任务完成，可进入 converge"], quiet)
        return 0

    if sub == "archive-readiness":
        try:
            stats = load_tasks_stats(cdir / "tasks.md")
        except StateError as e:
            payload = {"change": name, "ready": False, "reason": e.code,
                       "remedy": CHANGE_MISSING_REMEDY.format(name=name)}
            _emit(payload, [f"[ERROR] {e.message}"], quiet)
            return 1
        remaining = stats.total - stats.completed
        if remaining > 0:
            payload = {"change": name, "ready": False, "remaining": remaining, "total": stats.total,
                       "blocked": stats.blocked,
                       "remedy": f"Run /specmark apply {name} to finish {remaining} tasks,"
                                 f" or archive with --allow-unfinished after user confirmation"}
            _emit(payload, [f"[INFO] ✗ 仍有 {remaining}/{stats.total} 个任务未完成，不能归档"], quiet)
            return 1
        p = artifact_presence(cdir)
        if p["proposal"] == 0 or p["design"] == 0:
            payload = {"change": name, "ready": False, "reason": "missing artifacts",
                       "remedy": f"Run /specmark propose {name} to create missing artifacts,"
                                 f" or archive with --allow-unfinished after user confirmation"}
            _emit(payload, ["[INFO] ✗ 缺失产物文件"], quiet)
            return 1
        payload = {"change": name, "ready": True, "total": stats.total}
        _emit(payload, ["[INFO] ✓ 所有任务完成且产物完整，可归档"], quiet)
        return 0

    if sub == "complexity":
        result = complexity_of(cdir)
        human = (f"[INFO] 复杂度: {result['complexity']} (domain: {result['domain']},"
                 f" 任务: {result['task_count']}, 模块: {result['module_count']},"
                 f" 多域: {result['multi_domain']}, delta spec: {'是' if result['delta_spec'] else '否'})",)
        _emit(result, list(human), quiet)
        return 0

    raise StateError("unknown_subcommand", f"未知子命令: {sub}", exit_code=2)


# ---------- fcntl 进程锁 ----------

def acquire_lock(lock_path: Path, timeout: float = 10.0):
    """独占锁（fcntl，POSIX 可用；Windows 原生 Python 无 fcntl → 结构化报错）。"""
    try:
        import fcntl
    except ImportError:
        raise StateError(
            "platform_not_supported",
            "当前平台无 fcntl（Windows 原生 Python 不支持），归档/恢复操作需要 POSIX 锁",
            remedy="在 Linux/WSL/macOS 上运行归档与恢复操作",
            exit_code=3,
        )
    try:
        lock_path.parent.mkdir(parents=True, exist_ok=True)
        # O_NOFOLLOW：锁文件被预埋为 symlink 时拒绝跟随
        nofollow = getattr(os, "O_NOFOLLOW", 0)
        fd = os.open(lock_path, os.O_RDWR | os.O_CREAT | nofollow, 0o644)
    except OSError as e:
        raise StateError(
            "lock_open_failed",
            f"无法打开锁文件: {lock_path} ({e})",
            remedy="检查 specmark/.locks/ 权限；若锁文件是指向外部目标且不被 kill 的 symlink，删除后重试",
            exit_code=1,
        )
    deadline = time.monotonic() + timeout
    while True:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return fd
        except OSError:
            if time.monotonic() >= deadline:
                os.close(fd)
                raise LockTimeout(lock_path)
            time.sleep(0.1)


def release_lock(fd: int) -> None:
    try:
        import fcntl
        fcntl.flock(fd, fcntl.LOCK_UN)
    except ImportError:
        pass
    finally:
        os.close(fd)


# ---------- 归档 / 恢复 ----------

def _git_head(root: Path) -> str | None:
    try:
        out = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            capture_output=True, text=True, check=True,
        )
        return out.stdout.strip() or None
    except (OSError, subprocess.SubprocessError):
        return None


def _stamp_version(root: Path) -> None:
    marker = root / "specmark" / ".specmark-version"
    if not marker.exists():
        marker.parent.mkdir(parents=True, exist_ok=True)
        marker.write_text(skill_version() + "\n", encoding="utf-8")


def _merge_delta_to(main_spec: Path, delta_spec: Path) -> str:
    """内存中完成 delta 合并，返回合并文本（不落盘——由调用方决定原子写入）。"""
    merge_dir = str(SCRIPT_DIR)
    if merge_dir not in sys.path:
        sys.path.insert(0, merge_dir)
    import merge_delta_spec as mds
    main_existed = main_spec.is_file()
    main_spec_obj = mds.parse_spec(main_spec) if main_existed else mds.Spec()
    delta_obj = mds.parse_spec(delta_spec)
    return mds.emit(mds.merge(main_spec_obj, delta_obj, main_existed))


def _plan_sync(change_path: Path, specs_root: Path) -> list[tuple[Path, Path, str]]:
    """返回 [(main_spec, delta_spec, capability)]，并校验 capability 名。"""
    deltas = sorted(change_path.glob("specs/*/spec.md"))
    plan = []
    for delta in deltas:
        cap = delta.parent.name
        if not KEBAB_RE.match(cap):
            raise StateError("invalid_capability", f"非法 capability 目录名: {cap}", exit_code=1)
        plan.append((specs_root / cap / "spec.md", delta, cap))
    return plan


def cmd_archive(name: str, root: Path, sync: bool, date_override: str,
                dry_run: bool, allow_unfinished: bool, lock_timeout: float = 10.0) -> int:
    # 归档路径的输入错误按 1 报（2 专属锁竞争，避免语义冲突）
    validate_change_name(name, exit_code=1)
    cdir = change_dir(root, name)
    arch_root = archive_dir(root)
    specs_root = root / "specmark" / "specs"

    if not cdir.is_dir():
        raise StateError("change_dir_not_found", f"change 目录不存在: {cdir}",
                         remedy=CHANGE_MISSING_REMEDY.format(name=name), exit_code=1)

    date = date_override or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", date):
        raise StateError("invalid_date", f"非法日期: {date}", exit_code=1)

    target = arch_root / f"{date}-{name}"

    # 锁前检查只做快速失败；锁内二次检查才是 race-safe 判定
    lock_fd = acquire_lock(locks_dir(root) / f"{name}.lock", timeout=lock_timeout)
    try:
        if target.exists():
            raise StateError(
                "archive_target_exists",
                f"归档目标已存在: {target}",
                remedy="只读强制：拒绝覆盖。请换 --date 或清理冲突后重试",
                exit_code=1,
            )
        if not cdir.is_dir():
            raise StateError("change_vanished", f"change 目录在锁内消失: {cdir}", exit_code=1)

        # 归档完整性门禁（默认拒绝未完成；--allow-unfinished 显式豁免并写快照）
        unfinished_snapshot = None
        tasks_file = cdir / "tasks.md"
        if tasks_file.is_file():
            stats = load_tasks_stats(tasks_file)
            remaining = stats.total - stats.completed
            if remaining > 0 and not allow_unfinished:
                raise StateError(
                    "unfinished_tasks",
                    f"仍有 {remaining}/{stats.total} 个任务未完成，拒绝归档",
                    remedy=f"完成剩余任务（含阻塞 {stats.blocked} 个）后归档，"
                           f"或在用户确认后传 --allow-unfinished 豁免",
                    exit_code=1,
                )
            if remaining > 0:
                unfinished_snapshot = {"remaining": remaining, "total": stats.total,
                                       "blocked": stats.blocked}
        presence = artifact_presence(cdir)
        if (presence["proposal"] == 0 or presence["design"] == 0) and not allow_unfinished:
            raise StateError(
                "missing_artifacts",
                "proposal.md 或 design.md 缺失，拒绝归档",
                remedy="补全产物，或在用户确认后传 --allow-unfinished 豁免",
                exit_code=1,
            )

        commit_sha = _git_head(root)

        # sync 计划与合并：先全部合并到临时文件，全部成功后一次性原子替换（无部分写入）；
        # dry-run 只在内存计算合并计划，不产生任何磁盘副作用
        sync_plan = _plan_sync(cdir, specs_root) if sync else []
        pending: list[tuple[Path, Path]] = []
        try:
            if sync_plan and not dry_run:
                for main_spec, delta, _cap in sync_plan:
                    merged = _merge_delta_to(main_spec, delta)
                    main_spec.parent.mkdir(parents=True, exist_ok=True)
                    fd, tmpname = tempfile.mkstemp(dir=str(main_spec.parent),
                                                   prefix=main_spec.name + ".", suffix=".tmp")
                    with os.fdopen(fd, "w", encoding="utf-8") as f:
                        f.write(merged)
                    pending.append((main_spec, Path(tmpname)))
            if dry_run:
                print("## 归档预览 (dry-run)\n")
                print(f"**变更：** {name}")
                print(f"**将归档到：** specmark/archive/{date}-{name}/")
                print(f"**Commit SHA：** {commit_sha or 'null'}")
                if sync_plan:
                    print(f"**Sync：** 将合并 {len(sync_plan)} 个 delta spec")
                elif sync:
                    print("**Sync：** --sync 但无 delta spec")
                else:
                    print("**Sync：** 未启用 --sync")
                if unfinished_snapshot:
                    print(f"**豁免快照：** {unfinished_snapshot['remaining']}/{unfinished_snapshot['total']} 未完成将记入 meta.json")
                print("\n[dry-run] 未执行实际操作。去掉 --dry-run 以执行归档。")
                return 0
            # 原子替换；任一失败用内存快照回滚已替换项，不留部分合并状态
            originals = {main: (main.read_bytes() if main.exists() else None)
                         for main, _tmp in pending}
            replaced: list[Path] = []
            try:
                for main_spec, tmp in pending:
                    os.replace(tmp, main_spec)
                    replaced.append(main_spec)
                pending = []
            except OSError as e:
                for main in replaced:
                    snap = originals[main]
                    if snap is None:
                        main.unlink(missing_ok=True)
                    else:
                        main.write_bytes(snap)
                raise StateError(
                    "sync_replace_failed",
                    f"合并结果写入失败，已回滚已替换项: {e}",
                    remedy="检查 specmark/specs/ 写权限后重试归档",
                    exit_code=1,
                )
        finally:
            for _main, tmp in pending:
                tmp.unlink(missing_ok=True)

        # 原子移动；锁文件保留（本进程仍持有，删除会造成假互斥竞态）
        arch_root.mkdir(parents=True, exist_ok=True)
        sentinel = arch_root / ".readonly"
        if not sentinel.exists():
            sentinel.write_text(
                "specmark archive — read-only history. 仅追加新归档条目，禁止修改/删除既有条目。\n",
                encoding="utf-8",
            )
        shutil.move(str(cdir), str(target))

        meta = {
            "change": name,
            "archived_at": date,
            "commit_sha": commit_sha,
            "synced": bool(sync and sync_plan),
        }
        if unfinished_snapshot:
            meta["unfinished"] = unfinished_snapshot
        (target / "meta.json").write_text(
            json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        _stamp_version(root)

        # 清理空目录（changes/ 可能变空；.locks/ 按设计保留锁文件——持有期间删除会造成假互斥竞态）
        try:
            changes_dir(root).rmdir()
        except OSError:
            pass

        print("## 归档完成\n")
        print(f"**变更：** {name}")
        print(f"**归档到：** specmark/archive/{date}-{name}/")
        print(f"**Commit SHA：** {commit_sha or 'null'}")
        if sync_plan:
            print(f"**Sync：** 已同步 {len(sync_plan)} 个 spec")
        elif sync:
            print("**Sync：** --sync 但无 delta spec")
        else:
            print("**Sync：** 未启用 --sync")
        if unfinished_snapshot:
            print(f"**豁免：** {unfinished_snapshot['remaining']}/{unfinished_snapshot['total']} 未完成任务已记入 meta.json 快照")
        return 0
    finally:
        release_lock(lock_fd)


def cmd_restore(ref: str, root: Path, lock_timeout: float = 10.0) -> int:
    """把误归档的变更移回活动区（同一把 change 级锁内完成，替代手动 mv）。"""
    # ref 仅允许「完整归档目录名（日期前缀 + kebab）」或「无歧义 kebab 短名」，
    # 拒绝路径穿越与任意目录（restore 会 shutil.move 条目并删除其 meta.json）
    full_re = re.compile(r"^\d{4}-\d{2}-\d{2}-[a-z0-9][a-z0-9-]*$")
    if not full_re.match(ref) and not KEBAB_RE.match(ref):
        raise StateError(
            "invalid_restore_ref",
            f"非法归档引用（须为归档目录名或 kebab change 名）: {ref}",
            remedy="使用 specmark/archive/ 下的完整目录名，如 2026-09-30-<change-name>",
            exit_code=1,
        )

    arch = archive_dir(root)
    if not arch.is_dir():
        raise StateError("archive_not_found", f"归档目录不存在: {arch}", exit_code=1)

    entry = arch / ref
    if not entry.is_dir():
        candidates = [d.name for d in arch.iterdir()
                      if d.is_dir() and d.name.endswith(f"-{ref}") and not d.name.startswith(".")]
        if len(candidates) == 1:
            entry = arch / candidates[0]
        elif len(candidates) > 1:
            raise StateError(
                "ambiguous_restore_ref",
                f"归档引用有歧义: {ref}，匹配到 {len(candidates)} 个条目",
                remedy=f"使用完整归档目录名，候选: {', '.join(sorted(candidates))}",
                exit_code=1,
            )
        else:
            raise StateError("archive_entry_not_found", f"归档条目不存在: {arch / ref}", exit_code=1)

    # 只接受归档树内的真实目录：拒绝 symlink、拒绝逃出归档树（resolve 包含性检查）
    if entry.is_symlink() or entry.resolve().parent != arch.resolve():
        raise StateError(
            "invalid_archive_entry",
            f"归档条目非法（symlink 或位于归档树之外）: {entry}",
            exit_code=1,
        )

    name = ARCHIVE_PREFIX_RE.sub("", entry.name)
    if not KEBAB_RE.match(name):
        raise StateError("invalid_change_name", f"从归档目录名解析出非法 change 名: {name}", exit_code=1)

    lock_fd = acquire_lock(locks_dir(root) / f"{name}.lock", timeout=lock_timeout)
    try:
        dest = changes_dir(root) / name
        if dest.exists():
            raise StateError(
                "active_name_conflict",
                f"活动区已存在同名变更: {dest}",
                remedy="先处理活动区同名变更（归档或重命名）后再 restore",
                exit_code=1,
            )
        meta = read_meta(entry)
        changes_dir(root).mkdir(parents=True, exist_ok=True)
        shutil.move(str(entry), str(dest))
        (dest / "meta.json").unlink(missing_ok=True)
        _stamp_version(root)

        print("## 恢复完成\n")
        print(f"**变更：** {name}")
        print(f"**移回：** specmark/changes/{name}/")
        print("**meta.json：** 已删除（归档标记随之失效）")
        if meta["synced"]:
            print("**注意：** 该归档曾 --sync 合并 delta 到主 specs；恢复后主 specs 仍含其内容，"
                  "如需回滚主规格请手工编辑 specmark/specs/（归档树只读约束不自动反向合并）")
        print(f"**下一步：** /specmark apply {name}")
        return 0
    finally:
        release_lock(lock_fd)


# ---------- status 子命令 ----------

def cmd_status(root: Path, as_json: bool) -> int:
    status = collect_status(root)
    if as_json:
        print(json.dumps(status, ensure_ascii=False))
    else:
        print(status_table(status))
    return 0


# ---------- CLI ----------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="specmark_state.py", description="specmark 状态判定与归档操作")
    sub = parser.add_subparsers(dest="command", required=True)

    p_check = sub.add_parser("check", help="阶段完成确定性判定（check_phase.sh 入口）")
    p_check.add_argument("subcommand", choices=["artifacts", "tasks", "converge-readiness",
                                                "archive-readiness", "complexity"])
    p_check.add_argument("change")
    p_check.add_argument("--root", default=None)
    p_check.add_argument("--json", action="store_true", help="静默 stderr 人类摘要，stdout 恒为 JSON")

    p_status = sub.add_parser("status", help="全局状态查询（status.sh 入口）")
    p_status.add_argument("--root", default=None)
    p_status.add_argument("--json", action="store_true")

    p_arch = sub.add_parser("archive", help="归档执行器（archive_change.sh 入口）")
    p_arch.add_argument("change")
    p_arch.add_argument("--root", default=None)
    p_arch.add_argument("--sync", action="store_true")
    p_arch.add_argument("--date", default=None)
    p_arch.add_argument("--dry-run", action="store_true")
    p_arch.add_argument("--allow-unfinished", action="store_true")
    p_arch.add_argument("--lock-timeout", type=float, default=10.0,
                        help="锁等待秒数（默认 10；超时退出码 2）")

    p_rest = sub.add_parser("restore", help="误归档恢复（archive_change.sh restore 入口）")
    p_rest.add_argument("archive_ref")
    p_rest.add_argument("--root", default=None)
    p_rest.add_argument("--lock-timeout", type=float, default=10.0,
                        help="锁等待秒数（默认 10；超时退出码 2）")

    args = parser.parse_args(argv)
    root = resolve_root(args.root)

    try:
        if args.command == "check":
            return cmd_check(args.subcommand, args.change, root, quiet=args.json)
        if args.command == "status":
            return cmd_status(root, args.json)
        if args.command == "archive":
            return cmd_archive(args.change, root, args.sync, args.date,
                               args.dry_run, args.allow_unfinished, args.lock_timeout)
        if args.command == "restore":
            return cmd_restore(args.archive_ref, root, args.lock_timeout)
        parser.error(f"未知命令: {args.command}")
    except StateError as e:
        print(f"[ERROR] {e.message}", file=sys.stderr)
        payload = {"error_code": e.code, "message": e.message}
        if e.remedy:
            payload["remedy"] = e.remedy
            print(f"[ERROR] remedy: {e.remedy}", file=sys.stderr)
        print(json.dumps(payload, ensure_ascii=False))
        return e.exit_code
    return 0


if __name__ == "__main__":
    sys.exit(main())
