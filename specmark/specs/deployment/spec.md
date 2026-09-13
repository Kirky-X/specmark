# Spec — deployment

> Main spec for capability `deployment`.

## Requirements

### R-deployment-001: Dockerfile 基础镜像锁定到 SHA 摘要

Dockerfile 中所有 `FROM` 指令必须使用 `image@sha256:<digest>` 格式，防止标签漂移导致的供应链攻击。

**验收标准：**
- `FROM rust:1.75-slim` 改为 `FROM rust:1.75-slim@sha256:<digest>` 格式
- `FROM debian:bookworm-slim` 改为 `FROM debian:bookworm-slim@sha256:<digest>` 格式
- SHA 摘要来自 Docker Hub 官方镜像的真实 digest
- 保留 `# tag` 注释标识原始镜像版本

## Constraints

- 不得更改构建阶段或运行阶段的功能行为
- 不得更改非 root 用户、端口、健康检查等安全配置

## Out of Scope

- Rust 版本升级（仅锁定当前版本 SHA）
- 多架构镜像支持
