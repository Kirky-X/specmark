"""merge_delta_spec.py 语义与幂等测试（调研附录 B-6 的固化）。"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))

import merge_delta_spec as mds


def write_spec(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


MAIN = """# Spec — auth

> Main spec for capability `auth`.

## Requirements

### R-auth-001: 登录
<旧正文>

**验收标准：**
- 成功返回 200

### R-auth-002: 保留项
<keep>

## Constraints
- 现有约束 A
"""

DELTA = """# Spec — auth

> Delta spec for change `demo`.

## Requirements

### R-auth-001: 登录改版
<新正文>

**验收标准：**
- 失败返回 401

### R-auth-003: 新增项
<new>

### R-auth-002: ~~DELETE~~
~~DELETE~~

## Constraints
- 新增约束 B
"""


class MergeSemanticsTest(unittest.TestCase):
    def setUp(self):
        import tempfile
        self.dir = Path(tempfile.mkdtemp())

    def _merge_once(self, tmp: Path) -> str:
        main = write_spec(self.dir / "main.md", MAIN) if not tmp else tmp
        delta = write_spec(self.dir / "delta.md", DELTA)
        result = mds.merge(mds.parse_spec(main), mds.parse_spec(delta), True)
        return mds.emit(result)

    def test_modify_add_delete_keep_and_ordering(self):
        out = self._merge_once(None)
        self.assertIn("登录改版", out)          # MODIFY：delta 覆盖 main
        self.assertNotIn("<旧正文>", out)
        self.assertIn("R-auth-003", out)        # ADD
        self.assertNotIn("R-auth-002", out)     # DELETE
        self.assertIn("现有约束 A", out)         # Constraints 并集
        self.assertIn("新增约束 B", out)
        # 稳定排序：R-auth-001 在 R-auth-003 前
        self.assertLess(out.index("R-auth-001"), out.index("R-auth-003"))

    def test_idempotent_byte_identical(self):
        first = self._merge_once(None)
        merged = write_spec(self.dir / "merged.md", first)
        second = self._merge_once(merged)
        self.assertEqual(first, second)

    def test_merge_into_nonexistent_creates_main_header(self):
        delta = write_spec(self.dir / "delta.md", DELTA)
        result = mds.merge(mds.Spec(), mds.parse_spec(delta), False)
        out = mds.emit(result)
        self.assertIn("Main spec for capability", out)
        self.assertIn("R-auth-001", out)


if __name__ == "__main__":
    unittest.main()
