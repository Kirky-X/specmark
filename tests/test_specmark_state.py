"""specmark_state.py 纯函数单元测试：任务解析、阶段推断、三档复杂度、路由。"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import specmark_state as ss


def make_change(tmp: Path, name: str, *, proposal: str | None = "# x\n",
                design: str | None = None, tasks: str | None = None,
                specs: int = 0) -> Path:
    cdir = tmp / "specmark" / "changes" / name
    cdir.mkdir(parents=True)
    if proposal is not None:
        (cdir / "proposal.md").write_text(proposal, encoding="utf-8")
    if design is not None:
        (cdir / "design.md").write_text(design, encoding="utf-8")
    if tasks is not None:
        (cdir / "tasks.md").write_text(tasks, encoding="utf-8")
    for i in range(specs):
        (cdir / "specs" / f"cap-{i}").mkdir(parents=True, exist_ok=True)
        (cdir / "specs" / f"cap-{i}" / "spec.md").write_text("# Spec\n", encoding="utf-8")
    return cdir


class ParseTasksTest(unittest.TestCase):
    def test_four_state_counts(self):
        text = "\n".join([
            "- [x] [T001] [P0] done src/a.ts",
            "- [ ] [T002] [P1] open src/b.ts",
            "- [~] [T003] [P2] blocked src/c.ts — blocked: 等依赖",
            "- [X] [T004] [P0] uppercase src/d.ts",
        ])
        s = ss.parse_tasks_text(text)
        self.assertEqual(s.total, 4)
        self.assertEqual(s.completed, 2)
        self.assertEqual(s.open, 1)
        self.assertEqual(s.blocked, 1)
        self.assertEqual(s.blocked_items[0]["line"], 3)

    def test_convergence_split_and_rounds(self):
        text = "\n".join([
            "- [x] [T001] [P0] original done src/a.ts",
            "- [ ] [T002] [P0] original open src/b.ts",
            "## Phase 1: Convergence",
            "- [x] [T003] [P1] conv done src/c.ts",
            "## Phase 2: Convergence",
            "- [ ] [T004] [P1] conv open src/d.ts",
        ])
        s = ss.parse_tasks_text(text)
        self.assertEqual((s.original_total, s.original_completed), (2, 1))
        self.assertEqual((s.convergence_total, s.convergence_completed), (2, 1))
        self.assertEqual(s.convergence_rounds, 2)
        # remaining = open + blocked，不含已完成
        self.assertEqual(s.to_dict()["remaining"], 2)

    def test_indented_and_non_task_lines_ignored(self):
        text = "\n".join([
            "# Tasks",
            "  - [x] 缩进的不算任务",
            "- [x] real src/a.ts",
            "正文里的 - [ ] 不是任务行",
        ])
        s = ss.parse_tasks_text(text)
        self.assertEqual(s.total, 1)


class InferPhaseTest(unittest.TestCase):
    def setUp(self):
        import tempfile
        self.tmp = Path(tempfile.mkdtemp())

    def test_empty_is_new(self):
        cdir = make_change(self.tmp, "a", proposal=None)
        self.assertEqual(ss.infer_phase(cdir), "new")

    def test_design_only_is_explore(self):
        cdir = make_change(self.tmp, "b", proposal=None, design="# d")
        self.assertEqual(ss.infer_phase(cdir), "explore")

    def test_proposal_no_tasks_is_propose(self):
        cdir = make_change(self.tmp, "c", proposal="# p", design="# d")
        self.assertEqual(ss.infer_phase(cdir), "propose")

    def test_tasks_file_zero_tasks_is_propose(self):
        cdir = make_change(self.tmp, "d", tasks="# Tasks\n")
        self.assertEqual(ss.infer_phase(cdir), "propose")

    def test_originals_done_is_converge_even_with_open_convergence(self):
        """按 status.md 规则表：原始任务全勾即 converge（不要求收敛任务完成）。"""
        cdir = make_change(self.tmp, "e", tasks="\n".join([
            "- [x] [T001] [P0] a src/a.ts",
            "## Phase 1: Convergence",
            "- [ ] [T002] [P1] b src/b.ts",
        ]))
        self.assertEqual(ss.infer_phase(cdir), "converge")

    def test_open_original_is_apply(self):
        cdir = make_change(self.tmp, "f", tasks="- [ ] [T001] [P0] a src/a.ts")
        self.assertEqual(ss.infer_phase(cdir), "apply")


class ComplexityTest(unittest.TestCase):
    def setUp(self):
        import tempfile
        self.tmp = Path(tempfile.mkdtemp())

    def _change(self, name: str, tasks: str, proposal: str = "# x\n## Scope\ns\n") -> Path:
        return make_change(self.tmp, name, proposal=proposal, design="# d", tasks=tasks)

    def test_simple_tier(self):
        cdir = self._change("s", "- [x] [T001] [P0] fix typo src/one.ts")
        r = ss.complexity_of(cdir)
        self.assertEqual(r["complexity"], "simple")
        self.assertEqual(r["delta_spec"], 0)

    def test_medium_tier(self):
        cdir = self._change("m", "\n".join([
            "- [ ] [T001] [P0] a src/a/one.ts",
            "- [ ] [T002] [P0] b src/a/two.ts",
            "- [ ] [T003] [P1] c src/a/three.ts",
        ]))
        r = ss.complexity_of(cdir)
        self.assertEqual(r["complexity"], "medium")

    def test_complex_by_task_count(self):
        tasks = "\n".join(f"- [ ] [T00{i}] [P0] t src/m{i}.ts" for i in range(1, 6))
        r = ss.complexity_of(self._change("c1", tasks))
        self.assertEqual(r["complexity"], "complex")
        self.assertEqual(r["delta_spec"], 1)

    def test_complex_by_module_count(self):
        tasks = "\n".join(f"- [ ] [T00{i}] [P0] t src/mod{i}/f.ts" for i in range(1, 4))
        r = ss.complexity_of(self._change("c2", tasks))
        self.assertEqual(r["complexity"], "complex")

    def test_complex_by_multi_domain_scope(self):
        proposal = "# x\n## Scope\n" + "\n".join(f"- line {i}" for i in range(12)) + "\n"
        r = ss.complexity_of(self._change("c3", "- [ ] [T001] [P0] t src/a.ts", proposal))
        self.assertEqual(r["multi_domain"], 1)
        self.assertEqual(r["complexity"], "complex")

    def test_non_code_domain_uses_deliverable_arrow(self):
        tasks = "\n".join(f"- [ ] [T00{i}] [P1] 写第 {i} 章 → docs/ch{i}/main.md" for i in range(1, 4))
        proposal = "<!-- domain: doc -->\n# x\n## Scope\ns\n"
        r = ss.complexity_of(self._change("d1", tasks, proposal))
        self.assertEqual(r["domain"], "doc")
        self.assertEqual(r["module_count"], 3)
        self.assertEqual(r["complexity"], "complex")

    def test_missing_tasks_raises_structured(self):
        cdir = make_change(self.tmp, "no-tasks", tasks=None, design="# d")
        with self.assertRaises(ss.StateError) as ctx:
            ss.complexity_of(cdir)
        self.assertEqual(ctx.exception.code, "tasks_md_not_found")
        self.assertEqual(ctx.exception.exit_code, 2)


class NextCommandTest(unittest.TestCase):
    def test_priority_converge_over_apply(self):
        active = [{"name": "a", "phase": "apply"}, {"name": "b", "phase": "converge"}]
        self.assertIn("converge b", ss.next_command(active))

    def test_empty_suggests_propose_or_explore(self):
        self.assertIn("propose", ss.next_command([]))


class RootResolutionTest(unittest.TestCase):
    def test_explicit_root_wins(self):
        self.assertEqual(ss.resolve_root("/tmp"), ss.Path("/tmp").resolve())

    def test_env_root(self):
        old = ss.os.environ.get("SPECMARK_ROOT")
        ss.os.environ["SPECMARK_ROOT"] = "/tmp"
        try:
            self.assertEqual(ss.resolve_root(None), ss.Path("/tmp").resolve())
        finally:
            if old is None:
                del ss.os.environ["SPECMARK_ROOT"]
            else:
                ss.os.environ["SPECMARK_ROOT"] = old

    def test_kebab_validation(self):
        with self.assertRaises(ss.StateError):
            ss.validate_change_name("Bad_Name")
        ss.validate_change_name("add-auth-2")


if __name__ == "__main__":
    unittest.main()
