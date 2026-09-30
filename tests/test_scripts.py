"""脚本层端到端测试：薄入口子进程调用 + 归档/恢复全链路 + check_refs 两模式。

ROOT 一律用 SPECMARK_ROOT 环境变量注入临时目录，避免依赖外部 git 仓库。
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCRIPTS = REPO / "scripts"

GOOD_TASKS = """# Tasks — demo

- [x] [T001] [P0] 登录 src/auth/login.ts
- [x] [T002] [P0] 会话 src/auth/session.ts
"""

DELTA_SPEC = """# Spec — auth-core

> Delta spec for change `demo`.

## Requirements

### R-auth-core-001: 登录失败返回 401
<spec body>

**验收标准：**
- 失败时 401

## Constraints
- 不缓存密码
"""


class WorkspaceCase(unittest.TestCase):
    """每个用例一个干净临时项目。"""

    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        self.env = dict(os.environ, SPECMARK_ROOT=str(self.root))

    def make_change(self, name: str, *, proposal: str = "# p\n", design: str = "# d\n",
                    tasks: str | None = GOOD_TASKS, specs: dict[str, str] | None = None) -> Path:
        cdir = self.root / "specmark" / "changes" / name
        cdir.mkdir(parents=True)
        if proposal is not None:
            (cdir / "proposal.md").write_text(proposal, encoding="utf-8")
        if design is not None:
            (cdir / "design.md").write_text(design, encoding="utf-8")
        if tasks is not None:
            (cdir / "tasks.md").write_text(tasks, encoding="utf-8")
        for cap, body in (specs or {}).items():
            d = cdir / "specs" / cap
            d.mkdir(parents=True)
            (d / "spec.md").write_text(body, encoding="utf-8")
        return cdir

    def run_sh(self, script: str, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["bash", str(SCRIPTS / script), *args],
            capture_output=True, text=True, env=self.env, timeout=60,
        )

    def run_py(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(SCRIPTS / "specmark_state.py"), *args],
            capture_output=True, text=True, env=self.env, timeout=60,
        )


class CheckPhaseTest(WorkspaceCase):
    """对齐调研报告附录 B-4 的五子命令期望，另加新字段断言。"""

    def setUp(self):
        super().setUp()
        self.make_change("demo", proposal="<!-- domain: code -->\n# demo\n## Scope\n- auth\n")

    def test_artifacts_incomplete_reports_remedy(self):
        self.make_change("demo2", design=None, tasks=None)
        r = self.run_sh("check_phase.sh", "artifacts", "demo2")
        self.assertEqual(r.returncode, 1)
        payload = json.loads(r.stdout)
        self.assertEqual(payload["design"], 0)
        self.assertIn("propose", payload["remedy"])

    def test_tasks_counts_and_blocked(self):
        (self.root / "specmark/changes/demo/tasks.md").write_text(
            "- [x] [T001] [P0] a src/a.ts\n- [ ] [T002] [P1] b src/b.ts\n"
            "- [~] [T003] [P2] c src/c.ts — blocked: x\n", encoding="utf-8")
        r = self.run_sh("check_phase.sh", "tasks", "demo")
        self.assertEqual(r.returncode, 1)
        payload = json.loads(r.stdout)
        self.assertEqual((payload["total"], payload["completed"]), (3, 1))
        self.assertEqual(payload["blocked"], 1)
        self.assertEqual(payload["convergence_rounds"], 0)

    def test_complexity_three_tiers_and_delta_flag(self):
        (self.root / "specmark/changes/demo/tasks.md").write_text(GOOD_TASKS, encoding="utf-8")
        r = self.run_sh("check_phase.sh", "complexity", "demo")
        self.assertEqual(r.returncode, 0)
        payload = json.loads(r.stdout)
        self.assertEqual(payload["complexity"], "simple")
        self.assertEqual(payload["delta_spec"], 0)
        # 旧契约别名：simple/medium → long=0；complex → long=1
        self.assertEqual(payload["long"], 0)
        self.assertIn("tasks_le_2", payload["criteria"])

    def test_converge_readiness_not_ready_has_remedy(self):
        (self.root / "specmark/changes/demo/tasks.md").write_text(
            "- [x] [T001] [P0] a src/a.ts\n- [ ] [T002] [P0] b src/b.ts\n", encoding="utf-8")
        r = self.run_sh("check_phase.sh", "converge-readiness", "demo")
        self.assertEqual(r.returncode, 1)
        payload = json.loads(r.stdout)
        self.assertFalse(payload["ready"])
        self.assertIn("apply", payload["remedy"])

    def test_archive_readiness_ready(self):
        r = self.run_sh("check_phase.sh", "archive-readiness", "demo")
        self.assertEqual(r.returncode, 0)
        self.assertTrue(json.loads(r.stdout)["ready"])

    def test_root_flag_accepted_anywhere(self):
        env = dict(os.environ)
        env.pop("SPECMARK_ROOT", None)
        r = subprocess.run(
            ["bash", str(SCRIPTS / "check_phase.sh"), "complexity", "demo",
             "--root", str(self.root), "--json"],
            capture_output=True, text=True, env=env, timeout=60,
        )
        self.assertEqual(r.returncode, 0, r.stderr)
        # --json：stdout 合法 JSON 且 stderr 无人类摘要
        self.assertEqual(json.loads(r.stdout)["complexity"], "simple")
        self.assertEqual(r.stderr, "")

    def test_missing_change_exit_2_with_error_code(self):
        r = self.run_sh("check_phase.sh", "artifacts", "ghost")
        self.assertEqual(r.returncode, 2)
        self.assertEqual(json.loads(r.stdout)["error_code"], "change_dir_not_found")

    def test_invalid_name_exit_2(self):
        r = self.run_sh("check_phase.sh", "artifacts", "Bad_Name")
        self.assertEqual(r.returncode, 2)

    def test_unknown_subcommand_exit_2(self):
        r = self.run_sh("check_phase.sh", "nope", "demo")
        self.assertEqual(r.returncode, 2)


class StatusTest(WorkspaceCase):
    def test_json_shape_and_next_command(self):
        # 夹具任务全 [x] → 阶段推断为 converge
        self.make_change("demo")
        r = self.run_sh("status.sh", "--json")
        self.assertEqual(r.returncode, 0)
        payload = json.loads(r.stdout)
        self.assertEqual(payload["active_changes"][0]["phase"], "converge")
        self.assertIn("/specmark converge demo", payload["active_changes"][0]["next"])
        self.assertIn("next_command", payload)
        self.assertEqual(payload["archived_changes"], [])

    def test_table_contains_next_hint(self):
        self.make_change("demo")
        r = self.run_sh("status.sh")
        self.assertIn("建议下一步", r.stdout)
        self.assertIn("| 变更名 |", r.stdout)

    def test_unknown_flag_exit_2(self):
        r = self.run_sh("status.sh", "--wat")
        self.assertEqual(r.returncode, 2)


class ArchiveRestoreTest(WorkspaceCase):
    def _full_change(self, name="demo"):
        self.make_change(name, specs={"auth-core": DELTA_SPEC})

    def test_archive_happy_path_with_sync_and_version_stamp(self):
        self._full_change()
        r = self.run_sh("archive_change.sh", "demo", "--sync")
        self.assertEqual(r.returncode, 0, r.stderr)
        target = self.root / "specmark" / "archive"
        entries = [d for d in target.iterdir() if d.name.endswith("-demo")]
        self.assertEqual(len(entries), 1)
        meta = json.loads((entries[0] / "meta.json").read_text(encoding="utf-8"))
        self.assertTrue(meta["synced"])
        main_spec = self.root / "specmark" / "specs" / "auth-core" / "spec.md"
        self.assertIn("Main spec for capability", main_spec.read_text(encoding="utf-8"))
        self.assertEqual(
            (self.root / "specmark" / ".specmark-version").read_text().strip(),
            json.loads((REPO / "skill.json").read_text(encoding="utf-8"))["version"],
        )
        self.assertFalse((self.root / "specmark/changes/demo").exists())

    def test_archive_refuses_unfinished_without_flag(self):
        self.make_change("demo", tasks="- [x] [T001] [P0] a src/a.ts\n- [ ] [T002] [P0] b src/b.ts\n")
        r = self.run_sh("archive_change.sh", "demo")
        self.assertEqual(r.returncode, 1)
        payload = json.loads(r.stdout)
        self.assertEqual(payload["error_code"], "unfinished_tasks")
        self.assertTrue((self.root / "specmark/changes/demo").exists(), "拒绝归档不得移动目录")

    def test_allow_unfinished_writes_snapshot(self):
        self.make_change("demo", tasks="- [x] [T001] [P0] a src/a.ts\n- [ ] [T002] [P0] b src/b.ts\n")
        r = self.run_sh("archive_change.sh", "demo", "--allow-unfinished")
        self.assertEqual(r.returncode, 0, r.stderr)
        meta_file = next((self.root / "specmark/archive").glob("*-demo/meta.json"))
        meta = json.loads(meta_file.read_text(encoding="utf-8"))
        self.assertEqual(meta["unfinished"]["remaining"], 1)

    def test_dry_run_moves_nothing(self):
        self._full_change()
        r = self.run_sh("archive_change.sh", "demo", "--dry-run")
        self.assertEqual(r.returncode, 0)
        self.assertIn("dry-run", r.stdout)
        self.assertTrue((self.root / "specmark/changes/demo").exists())
        self.assertFalse((self.root / "specmark/archive").exists())

    def test_refuse_overwrite_existing_archive(self):
        self._full_change()
        self.run_sh("archive_change.sh", "demo", "--date", "2026-01-01")
        self.make_change("demo")
        r = self.run_sh("archive_change.sh", "demo", "--date", "2026-01-01")
        self.assertEqual(r.returncode, 1)
        self.assertEqual(json.loads(r.stdout)["error_code"], "archive_target_exists")

    def test_restore_roundtrip_and_synced_hint(self):
        self._full_change()
        self.run_sh("archive_change.sh", "demo", "--sync")
        r = self.run_sh("archive_change.sh", "restore", "demo")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue((self.root / "specmark/changes/demo/proposal.md").exists())
        self.assertFalse((self.root / "specmark/changes/demo/meta.json").exists())
        self.assertIn("主 specs", r.stdout)

    def test_restore_conflict_with_active_change(self):
        self._full_change("a")
        self.run_sh("archive_change.sh", "a")
        self.make_change("a")
        r = self.run_sh("archive_change.sh", "restore", "a")
        self.assertEqual(r.returncode, 1)
        self.assertEqual(json.loads(r.stdout)["error_code"], "active_name_conflict")

    def test_restore_rejects_traversal_and_symlink(self):
        # 路径穿越引用被格式校验拒绝
        outside = self.root / "outside-dir"
        outside.mkdir()
        r = self.run_sh("archive_change.sh", "restore", str(outside))
        self.assertEqual(r.returncode, 1)
        self.assertEqual(json.loads(r.stdout)["error_code"], "invalid_restore_ref")
        r = self.run_sh("archive_change.sh", "restore", "..")
        self.assertEqual(r.returncode, 1)
        self.assertEqual(json.loads(r.stdout)["error_code"], "invalid_restore_ref")
        # 归档树内的 symlink 条目被拒绝，不移动、不删外部文件
        self._full_change("s")
        self.run_sh("archive_change.sh", "s")
        entry = next((self.root / "specmark/archive").glob("*-s"))
        victim = self.root / "victim" / "meta.json"
        victim.parent.mkdir(parents=True)
        victim.write_text("{}", encoding="utf-8")
        entry.rename(self.root / "specmark/archive/real-s")
        (self.root / "specmark/archive/2026-01-01-s").symlink_to(victim.parent)
        r = self.run_sh("archive_change.sh", "restore", "2026-01-01-s")
        self.assertEqual(r.returncode, 1)
        self.assertEqual(json.loads(r.stdout)["error_code"], "invalid_archive_entry")
        self.assertTrue(victim.exists(), "symlink 指向的外部文件不得被删")

    def test_restore_ambiguous_short_name(self):
        self._full_change("a")
        self.run_sh("archive_change.sh", "a", "--date", "2026-01-01")
        self.make_change("a")
        self.run_sh("archive_change.sh", "a", "--allow-unfinished", "--date", "2026-02-01")
        r = self.run_sh("archive_change.sh", "restore", "a")
        self.assertEqual(r.returncode, 1)
        self.assertEqual(json.loads(r.stdout)["error_code"], "ambiguous_restore_ref")

    def test_lock_contention_exits_2(self):
        sys.path.insert(0, str(SCRIPTS))
        import specmark_state as ss
        self.make_change("demo")
        fd = ss.acquire_lock(ss.locks_dir(self.root) / "demo.lock")
        try:
            # 亚秒超时验证同一争用路径（默认 10s 会拖慢整个套件）
            r = self.run_py("archive", "demo", "--root", str(self.root), "--lock-timeout", "0.3")
            self.assertEqual(r.returncode, 2)
            self.assertEqual(json.loads(r.stdout)["error_code"], "lock_contention")
        finally:
            ss.release_lock(fd)
        sys.path.pop(0)


class CheckRefsTest(WorkspaceCase):
    def test_project_mode_clean(self):
        self.make_change("ok", tasks="- [ ] [T001] [P0] 登录 src/auth/login.ts\n")
        r = subprocess.run(
            [sys.executable, str(SCRIPTS / "check_refs.py"), "--project", str(self.root)],
            capture_output=True, text=True, timeout=60,
        )
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("(project)", r.stdout)

    def test_project_mode_flags_violations(self):
        self.make_change("bad", tasks="\n".join([
            "- [ ] [T1] [P9] handle edge cases src/nope/a.ts",
            "- [x] [T001] [P0] dup src/x.ts",
            "- [x] [T001] [P0] dup2 src/y.ts",
        ]))
        r = subprocess.run(
            [sys.executable, str(SCRIPTS / "check_refs.py"), "--project", str(self.root), "--json"],
            capture_output=True, text=True, timeout=60,
        )
        self.assertEqual(r.returncode, 1)
        findings = json.loads(r.stdout)
        checks = {f["check"] for f in findings}
        self.assertIn("placeholder", checks)
        self.assertIn("task-id-format", checks)
        self.assertIn("task-id-duplicate", checks)
        self.assertIn("task-priority", checks)
        self.assertIn("path-missing", checks)

    def test_project_mode_missing_dir_is_error(self):
        r = subprocess.run(
            [sys.executable, str(SCRIPTS / "check_refs.py"), "--project", str(self.root), "--json"],
            capture_output=True, text=True, timeout=60,
        )
        self.assertEqual(r.returncode, 1)
        findings = json.loads(r.stdout)
        self.assertEqual(findings[0]["check"], "no-changes-dir")

    def test_skill_mode_on_this_repo(self):
        r = subprocess.run(
            [sys.executable, str(SCRIPTS / "check_refs.py"), "--skill-root", str(REPO)],
            capture_output=True, text=True, timeout=60,
        )
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_deprecated_root_alias(self):
        r = subprocess.run(
            [sys.executable, str(SCRIPTS / "check_refs.py"), "--root", str(REPO)],
            capture_output=True, text=True, timeout=60,
        )
        self.assertEqual(r.returncode, 0)
        self.assertIn("已弃用", r.stderr)


if __name__ == "__main__":
    unittest.main()
