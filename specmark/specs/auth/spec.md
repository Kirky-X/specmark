# Spec — auth

> Main spec for capability `auth`.

## Requirements

### R-auth-001: auth_rate_limit_middleware 必须通过 XFF 信任边界提取客户端 IP

`auth_rate_limit_middleware` 在提取客户端 IP 用于限流判断时，必须复用 `extract_client_ip()` 函数，该函数在 `trusted_proxies` 非空时校验 X-Forwarded-For 来源是否在信任 CIDR 范围内，为空时回退到 ConnectInfo peer IP。

**验收标准：**
- `auth_rate_limit_middleware` 签名包含 `State(auth_config): State<AuthConfig>` 参数
- IP 提取调用 `extract_client_ip(request.headers(), connect_info, &auth_config.trusted_proxies)`
- 当 `trusted_proxies` 配置为 `["10.0.0.0/8"]` 且请求来自 `10.0.0.1` 带 `X-Forwarded-For: 203.0.113.50` 时，限流使用 IP `203.0.113.50`
- 当 `trusted_proxies` 为空且请求带 `X-Forwarded-For` 时，限流使用 ConnectInfo peer IP

### R-auth-002: auth_rate_limit_middleware XFF 行为与 auth_middleware 一致

`auth_rate_limit_middleware` 的 IP 提取行为必须与 `auth_middleware` 中的 IP 提取逻辑完全一致，确保认证审计和限流使用相同的客户端 IP 来源。

**验收标准：**
- 两个中间件调用相同的 `extract_client_ip()` 函数
- 单元测试覆盖 `trusted_proxies` 非空/空两种路径

## Constraints

- 不得修改 `extract_client_ip()` 函数签名或逻辑
- 必须保持 `auth_rate_limit_middleware` 的现有限流逻辑（Governor + 白名单 + 指标记录）不变

## Out of Scope

- `auth_middleware` 自身的逻辑修改
- 非 auth 端点的限流中间件
