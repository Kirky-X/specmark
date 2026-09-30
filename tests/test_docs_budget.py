"""文档字节预算 ratchet（借鉴 GSD workflow-size-budget）。

references/ 按 @-import 加载进 agent 上下文，超预算的文档直接稀释任务注意力。
预算为硬上限；确需上调必须显式改本文件的常量并在 commit 说明里给出理由。
"""

from __future__ import annotations

import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

SKILL_MD_BUDGET = 20 * 1024          # SKILL.md 恒加载，预算最紧
REFERENCE_BUDGET = 40 * 1024         # 单个 reference 按需加载（GSD 40 KiB 档）


class DocsBudgetTest(unittest.TestCase):
    def test_skill_md_within_budget(self):
        size = (REPO / "SKILL.md").stat().st_size
        self.assertLessEqual(
            size, SKILL_MD_BUDGET,
            f"SKILL.md {size} 字节超预算 {SKILL_MD_BUDGET}；"
            "优先精简或下沉到 references/，上调预算需给出理由",
        )

    def test_references_within_budget(self):
        refs = sorted((REPO / "references").glob("*.md"))
        self.assertTrue(refs, "references/ 目录为空？")
        for f in refs:
            size = f.stat().st_size
            self.assertLessEqual(
                size, REFERENCE_BUDGET,
                f"{f.name} {size} 字节超预算 {REFERENCE_BUDGET}",
            )


if __name__ == "__main__":
    unittest.main()
