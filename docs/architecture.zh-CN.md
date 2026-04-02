[简体中文](./architecture.zh-CN.md) | [English](./architecture.en.md)

# 架构概述

- **后端**：Flask REST API (`/api/*`)，Flask-SocketIO 用于 Yjs 中继和感知（`join_document`、`yjs_update`、`awareness_update`）。
- **前端**：Vue 3 SPA，Pinia，Vue Router，TipTap + Yjs 用于协作编辑，Element Plus UI。
- **国际化**：使用 `vue-i18n`，默认语言为 `en`，可选 `zh-CN`；Element Plus 语言与 UI 语言匹配。
- **文档状态**（参见 `app/services/document_state.py`）：`draft` → 可编辑内容；`in_approval` / `approved` / `rejected` 规则与竞赛简报一致；协作者角色 `view` | `edit` | `comment` 在 `DocumentPermission` 上，仅所有者可以在 `draft` 时编辑权限。

请参阅仓库 `README.md` 获取运行说明（包括 **cnpm**）。
