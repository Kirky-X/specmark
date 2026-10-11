# Revision Protocol — spec 已存在时,重开即修订

> 本文件回答一个具体问题:**change 目录已在、proposal 已成型,而需求又变了时,怎么走。** 答案不是重新 `explore` / `clarify` / `propose`,而是修订。与 [`troubleshooting.md`](troubleshooting.md) 分工:那篇管 apply 中途发现 design 有误等**故障恢复**(局部回退重做);本篇管**需求侧变更**(spec 本身要改)。来源:mouse-lin/finesse-brief 仓的 handoff 文档 §7(keep excluded and deferred intact),2026-10 吸收。

## 触发条件

满足任一即进入本协议,而不是重新发起 propose:

- `specmark/changes/<name>/` 已存在,用户对**已写进 proposal 的需求**提出修改(范围增删、约束变化、排除项翻转);
- 上一轮 propose 被 `analyze` 打回后需要改 proposal 本体;
- 用户拿着已确认的产物说「其实是……不用……」式更正。

## 修订六步

1. **读全量产物**。先读完 `proposal.md` / `design.md` / `tasks.md`(长程变更含 `specs/`)再动手——修订的依据是当前 spec 的完整状态,不是用户口述的那一句。
2. **只改受影响部分**。把新需求映射到具体产物与具体条目,做外科手术式修改;未受影响的条目、段落、任务 ID 一律不动。
3. **决策记忆原样保留**。`## Scope`(覆盖范围)、`## Non-Goals`(排除项及理由)、`## Deferred`(推迟项 + 原因 + 重开条件)、`## Clarifications`(已答澄清)四类内容默认原样保留。已排除的范围不得因新一轮对话被静默重新纳入;已承诺的重开条件不得因「现在看着不急」被悄悄删掉——重开既有决策必须显式进行,并写进 Deferred 或一条新的 Clarification。
4. **每轮重发全量产物,附一行「动了什么」**。修订后把完整产物重新呈现给用户(不是只贴改动的行),并在末尾附一行变更摘要:「本轮动了什么:<条目级清单>」。用户看的是同一份越来越好的文档,不是在脑里合并五条消息。
5. **任务侧联动**。需求变化波及 `tasks.md` 时,追加/重排任务按 apply 的 append 纪律走,不静默改写已完成任务;被新需求失效的已完成任务,标记失效并说明,不删除历史记录。
6. **已交付部分列失效清单**。若变更影响已交付的产物(已产出的代码 / 文档 / 页面),必须列出「哪些已交付部分因此失效、要重做什么」——spec 与已交付物悄悄脱钩会留下两个真相来源,而页面/代码永远默认获胜。

## 与相邻流程的分工

| 场景 | 走哪 |
| --- | --- |
| 需求变了、spec 已在(本协议) | revision-protocol |
| apply 中途发现 design/tasks 有误 | [troubleshooting.md](troubleshooting.md) 的故障恢复 |
| 全新需求、无 change 目录 | [propose.md](propose.md) |
| 需求有歧义、spec 未成型 | [clarify.md](clarify.md) |
