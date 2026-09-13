# Spec — security-scanning

> Main spec for capability `security-scanning`.

## Requirements

### R-security-scanning-001: gitleaks 配置排除已知误报路径

创建 `.gitleaks.toml` 配置文件，排除文档中的示例 JWT token 和构建产物中的二进制数据，减少密钥扫描误报。

**验收标准：**
- 项目根目录存在 `.gitleaks.toml` 文件
- 配置排除 `docs/` 目录
- 配置排除 `target/` 目录
- 运行 `gitleaks detect --source . --config .gitleaks.toml --no-git` 后，文档和构建产物路径不再产生 finding

## Constraints

- 不得排除 `src/` 目录（源码中的真实密钥泄漏仍需检测）
- 配置文件格式必须符合 gitleaks v8 TOML schema（`.gitleaks.toml`）

## Out of Scope

- 自定义 gitleaks 规则
- 其他密钥扫描工具（trufflehog）配置
