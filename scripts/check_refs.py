#!/usr/bin/env python3
"""check_refs.py — 引用与产物一致性 lint（两种模式）。

skill 模式（--skill-root，检查 specmark skill 仓库自身）：
  1. 跨文件 section 引用（如 "propose.md §2"）是否指向真实存在的章节
  2. 跨文件 line 引用（如 "converge.md line 79-83"）是否指向有效行范围
  3. 关键术语/清单是否在多文件间出现漂移（重复定义但内容不同）
  4. 反向引用完整性（引用了某文件但该文件不存在）

项目模式（--project，检查用户项目里的活动 change 产物）：
  a. tasks.md 占位符扫描（propose.md §2 禁用短语，硬规则零匹配）
  b. 任务 ID 零填充格式与唯一性、优先级取值域
  c. 任务内文件路径存在性（缺失仅 WARN——可能由更早任务创建）
  d. NEEDS CLARIFICATION 条目计数与 [~] 阻塞任务暴露

退出码：0 = 无问题；1 = 有发现（存在 ERROR）；2 = 脚本错误。

用法：
  python3 scripts/check_refs.py --skill-root <skill-repo> [--json] [--verbose]
  python3 scripts/check_refs.py --project <project-root> [--json] [--verbose]
  # --root 为旧参数名，等价 --skill-root（已弃用，stderr 提示）
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

# ---------- 数据模型 ----------

@dataclass
class Finding:
    severity: str        # ERROR / WARN / INFO
    check: str           # 检测类型
    location: str        # 文件名:行号
    message: str         # 人类可读描述

@dataclass
class Section:
    """Markdown 章节（# / ## / ### 标题）"""
    level: int           # 标题层级 (1/2/3)
    title: str           # 标题文本（不含 # 前缀）
    line: int            # 起始行号 (1-based)
    file: str            # 所属文件

@dataclass
class CrossRef:
    """跨文件引用"""
    source_file: str     # 引用所在文件
    source_line: int     # 引用所在行号
    target_file: str     # 被引用文件（如 "propose.md"）
    ref_type: str        # "section" / "line" / "file"
    ref_target: str      # 引用目标（如 "§2" / "line 79-83" / 整文件）
    raw_text: str        # 原始匹配文本

# ---------- 解析 ----------

SECTION_RE = re.compile(r"^(#{1,3})\s+(.+?)\s*$")
# 匹配 "propose.md §2"、"propose.md §3"、"propose.md 5 元素格式"
SECTION_REF_RE = re.compile(
    r"`?(\w+)\.md`?\s+[§§](\d+)"
)
# 匹配 "converge.md line 79-83"、"SKILL.md line 150"
LINE_REF_RE = re.compile(
    r"`?(\w+(?:-\w+)?\.md)`?\s+line\s+(\d+)(?:\s*[-–]\s*(\d+))?",
    re.IGNORECASE,
)
# 匹配 "[xxx.md](./xxx.md)" 或 "[xxx.md](xxx.md)" 形式的 markdown 链接
MD_LINK_RE = re.compile(
    r"\[([^\]]+)\]\(\.?/?references/([\w-]+\.md)\)"
)
# 匹配 "见 propose.md §2 定义的禁用短语清单" 等自然语言引用
NATURAL_REF_RE = re.compile(
    r"(?:见|参见|参考|对齐|与|同)\s+`?(\w+)\.md`?"
)
# 匹配任务描述中的源码路径（与 specmark_state.py complexity 模块提取同一形状）
CODE_PATH_RE = re.compile(r"(?:src/|lib/|app/)?[A-Za-z0-9_/-]+\.[A-Za-z]+")

# 关键共享概念：在多个文件中出现应保持一致的术语/清单
SHARED_CONCEPTS = {
    "禁用短语": [
        "TBD", "TODO", "FIXME", "???", "<...>",
        "add appropriate error handling",
        "handle edge cases",
        "similar to Task",
        "write tests for the above",
        "as needed", "if relevant", "where appropriate",
    ],
    "8分类": [
        "Functional Scope", "Domain", "UX", "NFR",
        "Integration", "Edge Cases", "Constraints", "Terminology",
    ],
    "长程判定条件": [
        "任务数 ≥ 5", "≥ 3 个独立模块", "多个能力域或子系统",
    ],
    "converge循环上限": [
        "3 次",
    ],
}


def parse_sections(text: str, filename: str) -> list[Section]:
    """提取 Markdown 文件中的所有 ## 级章节"""
    sections = []
    for i, line in enumerate(text.split("\n"), 1):
        m = SECTION_RE.match(line)
        if m:
            sections.append(Section(
                level=len(m.group(1)),
                title=m.group(2).strip(),
                line=i,
                file=filename,
            ))
    return sections


def find_cross_refs(text: str, filename: str) -> list[CrossRef]:
    """提取文件中所有跨文件引用"""
    refs = []
    lines = text.split("\n")

    for i, line in enumerate(lines, 1):
        # §N 形式的 section 引用
        for m in SECTION_REF_RE.finditer(line):
            refs.append(CrossRef(
                source_file=filename,
                source_line=i,
                target_file=m.group(1) + ".md",
                ref_type="section",
                ref_target=f"§{m.group(2)}",
                raw_text=m.group(0),
            ))

        # line N-M 形式的行引用
        for m in LINE_REF_RE.finditer(line):
            end_line = m.group(3) or m.group(2)
            refs.append(CrossRef(
                source_file=filename,
                source_line=i,
                target_file=m.group(1),
                ref_type="line",
                ref_target=f"line {m.group(2)}-{end_line}",
                raw_text=m.group(0),
            ))

        # markdown 链接引用
        for m in MD_LINK_RE.finditer(line):
            refs.append(CrossRef(
                source_file=filename,
                source_line=i,
                target_file=m.group(2),
                ref_type="file",
                ref_target=m.group(2),
                raw_text=m.group(0),
            ))

    return refs


def check_section_number(sections: list[Section], target_num: int) -> tuple[bool, str]:
    """检查 §N 是否指向真实存在的章节。

    §N 可能指：
    1. ## 级章节按顺序编号（第 N 个 ## 章节）
    2. 标题内嵌编号如 '### 2. 禁止占位符'（### 级标题以 N 开头）
    返回 (是否存在, 匹配的标题文本)。
    """
    # 优先匹配标题内嵌编号（如 "2. 禁止占位符"）
    numbered_re = re.compile(rf"^{target_num}\.\s+")
    for s in sections:
        if numbered_re.match(s.title):
            return True, s.title

    # 回退到 ## 级顺序编号
    h2_sections = [s for s in sections if s.level == 2]
    if target_num <= len(h2_sections):
        return True, h2_sections[target_num - 1].title

    return False, ""


def check_line_range(text: str, start: int, end: int) -> bool:
    """检查行范围是否在文件范围内"""
    total_lines = len(text.split("\n"))
    return 1 <= start <= total_lines and 1 <= end <= total_lines


def check_shared_concepts(files: dict[str, str]) -> list[Finding]:
    """检查共享概念在多文件间的一致性"""
    findings = []

    # 检查"禁用短语"清单：propose.md 是真相来源
    # 检查 apply.md 是否复制了清单而非引用
    if "apply.md" in files:
        apply_text = files["apply.md"]
        # 如果 apply.md 直接列出了完整的禁用短语（而非引用 propose.md §2），则是漂移风险
        placeholder_count = 0
        for concept in SHARED_CONCEPTS["禁用短语"][:5]:  # 检查前 5 个关键项
            if concept in apply_text:
                placeholder_count += 1
        # 如果 apply.md 直接包含 3+ 个禁用短语（非引用形式），说明可能在复制清单
        if placeholder_count >= 3:
            # 检查是否有引用标记
            if "propose.md §2" not in apply_text and "propose.md` §2" not in apply_text:
                findings.append(Finding(
                    severity="WARN",
                    check="duplicated-concept",
                    location="apply.md",
                    message="apply.md 直接包含禁用短语清单而非引用 propose.md §2，存在漂移风险",
                ))

    return findings


TASK_ID_RE = re.compile(r"\[T(\d+)\]")
TASK_PRIORITY_RE = re.compile(r"\[P([A-Za-z0-9]+)\]")
NEEDS_CLARIFICATION_RE = re.compile(r"^##\s+NEEDS CLARIFICATION\s*$")
BLOCKED_TASK_RE = re.compile(r"^- \[~\]")


def check_project(root: Path, verbose: bool = False) -> list[Finding]:
    """项目模式：对用户项目 specmark/changes/ 下的活动变更跑产物任务 lint。"""
    findings: list[Finding] = []
    changes_dir = root / "specmark" / "changes"
    if not changes_dir.is_dir():
        findings.append(Finding("ERROR", "no-changes-dir", "-",
                                f"未找到活动变更目录: {changes_dir}"))
        return findings

    active = sorted(d for d in changes_dir.iterdir()
                    if d.is_dir() and not d.name.startswith("."))
    if not active:
        findings.append(Finding("INFO", "no-active-changes", "-",
                                "无活动变更，无产物可检查"))
        return findings

    banned = SHARED_CONCEPTS["禁用短语"]

    for cdir in active:
        name = cdir.name
        tasks_file = cdir / "tasks.md"
        proposal_file = cdir / "proposal.md"
        proposal_text = proposal_file.read_text(encoding="utf-8", errors="replace") \
            if proposal_file.is_file() else ""
        domain = "code"
        m = re.search(r"<!--\s*domain:\s*([a-z]+)", proposal_text)
        if m:
            domain = m.group(1)

        if not tasks_file.is_file():
            findings.append(Finding("ERROR", "missing-tasks", name,
                                    "tasks.md 不存在，先运行 /specmark propose"))
            continue
        tasks_text = tasks_file.read_text(encoding="utf-8", errors="replace")

        # a. 占位符扫描（propose.md §2 硬规则：零匹配）
        seen_banned: set[str] = set()
        for i, line in enumerate(tasks_text.split("\n"), 1):
            for phrase in banned:
                if phrase in line and phrase not in seen_banned:
                    seen_banned.add(phrase)
                    findings.append(Finding(
                        "ERROR", "placeholder", f"{name}/tasks.md:{i}",
                        f"任务含禁用占位符 \"{phrase}\"（propose.md §2）——拆为具体子任务或写入 NEEDS CLARIFICATION",
                    ))

        # b. 任务 ID 格式与唯一性、优先级取值域
        ids: list[str] = []
        for i, line in enumerate(tasks_text.split("\n"), 1):
            if not line.startswith("- ["):
                continue
            for m in TASK_ID_RE.finditer(line):
                digits = m.group(1)
                ids.append(digits)
                if len(digits) != 3:
                    findings.append(Finding(
                        "ERROR", "task-id-format", f"{name}/tasks.md:{i}",
                        f"任务 ID [T{digits}] 非三位零填充（应为 T001 形式）",
                    ))
            for m in TASK_PRIORITY_RE.finditer(line):
                priority = "P" + m.group(1)
                if priority not in ("P0", "P1", "P2"):
                    findings.append(Finding(
                        "ERROR", "task-priority", f"{name}/tasks.md:{i}",
                        f"优先级 [{priority}] 不在 P0/P1/P2 取值域",
                    ))
        dupes = sorted({t for t in ids if ids.count(t) > 1})
        if dupes:
            findings.append(Finding("ERROR", "task-id-duplicate", f"{name}/tasks.md",
                                    f"任务 ID 重复: {', '.join('T' + t for t in dupes)}（永不重排已有 ID）"))

        # c. 交付物路径存在性（缺失仅 WARN：可能由更早任务创建）
        for i, line in enumerate(tasks_text.split("\n"), 1):
            candidates: list[str] = []
            if domain == "code":
                candidates = [m.group(0) for m in CODE_PATH_RE.finditer(line)]
            arrow = re.search(r"→\s*(\S+)", line)
            if arrow and ("/" in arrow.group(1)):
                candidates.append(arrow.group(1))
            for path_text in candidates:
                if not (root / path_text).exists():
                    findings.append(Finding(
                        "WARN", "path-missing", f"{name}/tasks.md:{i}",
                        f"路径不存在: {path_text}（若应由更早任务创建可忽略；否则规格不足）",
                    ))

        # d. NEEDS CLARIFICATION 与 [~] 阻塞暴露
        nc_lines = []
        in_nc = False
        for line in proposal_text.split("\n"):
            if NEEDS_CLARIFICATION_RE.match(line):
                in_nc = True
                continue
            if in_nc and re.match(r"^##\s+", line):
                in_nc = False
            if in_nc and line.strip().startswith("- "):
                nc_lines.append(line.strip()[:80])
        if nc_lines:
            findings.append(Finding(
                "INFO", "needs-clarification", f"{name}/proposal.md",
                f"NEEDS CLARIFICATION 有 {len(nc_lines)} 条——apply 遇到相关任务会暂停；硬上限 3 条",
            ))
        for i, line in enumerate(tasks_text.split("\n"), 1):
            if BLOCKED_TASK_RE.match(line):
                findings.append(Finding(
                    "INFO", "blocked-task", f"{name}/tasks.md:{i}",
                    f"阻塞任务: {line.strip()[:80]}",
                ))

    return findings


def check_all(root: Path, verbose: bool = False) -> list[Finding]:
    findings: list[Finding] = []

    # 收集所有 reference 文件
    ref_dir = root / "references"
    ref_files: dict[str, str] = {}
    if ref_dir.is_dir():
        for f in sorted(ref_dir.glob("*.md")):
            ref_files[f.name] = f.read_text(encoding="utf-8")

    skill_md = root / "SKILL.md"
    if skill_md.is_file():
        ref_files["SKILL.md"] = skill_md.read_text(encoding="utf-8")

    if not ref_files:
        findings.append(Finding("ERROR", "no-files", "-", "未找到任何 reference 文件"))
        return findings

    # 解析所有章节
    all_sections: dict[str, list[Section]] = {}
    for fname, text in ref_files.items():
        all_sections[fname] = parse_sections(text, fname)

    # 检测 1: 跨文件 section 引用完整性
    for fname, text in ref_files.items():
        for ref in find_cross_refs(text, fname):
            # 检查目标文件是否存在
            if ref.target_file not in ref_files:
                # 也检查 references/ 目录下的文件名
                if ref.target_file not in ref_files:
                    findings.append(Finding(
                        severity="ERROR",
                        check="missing-target",
                        location=f"{fname}:{ref.source_line}",
                        message=f"引用了不存在的文件: {ref.raw_text}",
                    ))
                    continue

            target_text = ref_files.get(ref.target_file, "")
            target_sections = all_sections.get(ref.target_file, [])

            if ref.ref_type == "section":
                # 解析 §N
                num_match = re.search(r"§(\d+)", ref.ref_target)
                if num_match:
                    sec_num = int(num_match.group(1))
                    found, matched_title = check_section_number(
                        target_sections, sec_num
                    )
                    if not found:
                        findings.append(Finding(
                            severity="ERROR",
                            check="broken-section-ref",
                            location=f"{fname}:{ref.source_line}",
                            message=f"§{sec_num} 引用无效: {ref.target_file} "
                                    f"无匹配章节（已检查标题编号与 ## 顺序）",
                        ))
                    elif verbose:
                        findings.append(Finding(
                            severity="INFO",
                            check="section-ref-ok",
                            location=f"{fname}:{ref.source_line}",
                            message=f"§{sec_num} → {ref.target_file}: {matched_title}",
                        ))

            elif ref.ref_type == "line":
                line_match = re.search(r"line\s+(\d+)\s*[-–]\s*(\d+)", ref.ref_target)
                if line_match:
                    start = int(line_match.group(1))
                    end = int(line_match.group(2))
                    if not check_line_range(target_text, start, end):
                        total = len(target_text.split("\n"))
                        findings.append(Finding(
                            severity="ERROR",
                            check="broken-line-ref",
                            location=f"{fname}:{ref.source_line}",
                            message=f"行引用越界: {ref.raw_text} "
                                    f"({ref.target_file} 共 {total} 行)",
                        ))

    # 检测 2: SKILL.md 引用的 reference 文件是否存在
    if "SKILL.md" in ref_files:
        skill_refs = find_cross_refs(ref_files["SKILL.md"], "SKILL.md")
        for ref in skill_refs:
            if ref.ref_type == "file" and ref.target_file not in ref_files:
                findings.append(Finding(
                    severity="ERROR",
                    check="missing-reference",
                    location=f"SKILL.md:{ref.source_line}",
                    message=f"SKILL.md 引用了不存在的 reference: {ref.target_file}",
                ))

    # 检测 3: 共享概念一致性
    findings.extend(check_shared_concepts(ref_files))

    # 检测 4: references/ 中每个文件是否在 SKILL.md 中被引用
    if "SKILL.md" in ref_files:
        skill_text = ref_files["SKILL.md"]
        for fname in ref_files:
            if fname == "SKILL.md":
                continue
            if fname not in skill_text:
                findings.append(Finding(
                    severity="WARN",
                    check="orphan-reference",
                    location=fname,
                    message=f"reference 文件 {fname} 未在 SKILL.md 中被引用",
                ))

    # 检测 5: 关键数字一致性（converge 循环上限 3 次）
    converge_mentions = []
    for fname, text in ref_files.items():
        for i, line in enumerate(text.split("\n"), 1):
            if "循环" in line and "3 次" in line:
                converge_mentions.append((fname, i, line.strip()[:80]))
            if "循环" in line and "> 3 次" in line:
                converge_mentions.append((fname, i, line.strip()[:80]))
    if verbose and converge_mentions:
        for fname, lineno, text_snippet in converge_mentions:
            findings.append(Finding(
                severity="INFO",
                check="converge-limit-mention",
                location=f"{fname}:{lineno}",
                message=f"converge 循环上限提及: {text_snippet}",
            ))

    return findings


def format_findings(findings: list[Finding], as_json: bool, mode: str = "skill") -> str:
    if as_json:
        return json.dumps(
            [
                {
                    "severity": f.severity,
                    "check": f.check,
                    "location": f.location,
                    "message": f.message,
                }
                for f in findings
            ],
            ensure_ascii=False,
            indent=2,
        )

    if not findings:
        return f"✅ check_refs ({mode}): 无问题"

    errors = [f for f in findings if f.severity == "ERROR"]
    warns = [f for f in findings if f.severity == "WARN"]
    infos = [f for f in findings if f.severity == "INFO"]

    lines = []
    lines.append(f"check_refs ({mode}) 报告: {len(errors)} error(s), {len(warns)} warning(s), {len(infos)} info(s)")
    lines.append("")

    for f in findings:
        icon = {"ERROR": "❌", "WARN": "⚠️", "INFO": "ℹ️"}.get(f.severity, "?")
        lines.append(f"  {icon} [{f.severity}] {f.location}: {f.message}")

    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="引用与产物一致性 lint（--skill-root 查 skill 仓库；--project 查用户项目活动变更）",
    )
    ap.add_argument("--skill-root", default=None,
                    help="specmark skill 仓库根（含 references/ 与 SKILL.md）")
    ap.add_argument("--project", default=None,
                    help="用户项目根（含 specmark/changes/），运行产物任务 lint")
    ap.add_argument("--root", default=None,
                    help="[Deprecated] 等价 --skill-root；--root 的「项目根」语义已由 --project 承接")
    ap.add_argument("--json", action="store_true", help="JSON 格式输出")
    ap.add_argument("--verbose", action="store_true", help="输出 INFO 级发现")
    args = ap.parse_args(argv)

    if args.root and not args.skill_root:
        print("[WARN] --root 已弃用且语义易混淆：查 skill 仓库用 --skill-root，查用户项目用 --project；本次按 --skill-root 处理",
              file=sys.stderr)

    if args.project:
        mode = "project"
        root = Path(args.project).resolve()
    else:
        mode = "skill"
        root = Path(args.skill_root or args.root or ".").resolve()

    if not root.is_dir():
        print(f"error: 目录不存在: {root}", file=sys.stderr)
        return 2

    findings = check_project(root, verbose=args.verbose) if mode == "project" \
        else check_all(root, verbose=args.verbose)

    # 过滤 INFO（除非 --verbose）；项目模式的 INFO（NEEDS CLARIFICATION / 阻塞任务）
    # 是该模式的主要产出，不过滤
    if not args.verbose and mode == "skill":
        findings = [f for f in findings if f.severity != "INFO"]

    print(format_findings(findings, args.json, mode))

    has_errors = any(f.severity == "ERROR" for f in findings)
    return 1 if has_errors else 0


if __name__ == "__main__":
    sys.exit(main())
