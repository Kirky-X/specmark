# Spec — ci-cd

> Main spec for capability `ci-cd`.

## Requirements

### R-ci-cd-001: 所有 GitHub Actions 引用必须锁定到 commit SHA

`.github/workflows/` 下所有 workflow 文件中的 `uses:` 引用必须从可变标签（`@vN`、`@master`、`@stable`）改为不可变 commit SHA，格式为 `uses: owner/repo@<sha> # <tag>`。

**验收标准：**
- 所有 4 个 workflow 文件（docker.yml, health-check.yml, feature-matrix.yml, release.yml）中无 `@master`、`@stable`、`@vN` 形式的 action 引用
- 每个 SHA 引用后保留 `# <tag>` 注释标识原始版本
- `aquasecurity/trivy-action@master` 必须优先修复（最高风险）

### R-ci-cd-002: CI 集成 checkov 进行 IaC 安全扫描

在 CI workflow 中添加 checkov step 扫描 Dockerfile，覆盖基础设施即代码安全检查。

**验收标准：**
- CI workflow 中存在 checkov 扫描 step
- 扫描目标包含 Dockerfile
- 扫描失败时 CI 标记为失败（非 warning-only）

## Constraints

- SHA 锁定不应改变 workflow 的功能行为
- checkov step 应在 build job 之后运行，不阻塞构建

## Out of Scope

- workflow 逻辑重构
- 其他 CI 工具集成（CodeQL、Semgrep 等）
