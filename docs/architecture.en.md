[简体中文](./architecture.zh-CN.md) | English

# Architecture overview

- **Backend**: Flask REST API (`/api/*`), Flask-SocketIO for Yjs relay and awareness (`join_document`, `yjs_update`, `awareness_update`).
- **Frontend**: Vue 3 SPA, Pinia, Vue Router, TipTap + Yjs for collaborative editing, Element Plus UI.
- **i18n**: `vue-i18n` with default locale `en` and optional `zh-CN`; Element Plus locale matches UI locale.
- **Document state** (see `app/services/document_state.py`): `draft` → editable content; `in_approval` / `approved` / `rejected` rules align with the competition brief; collaborator roles `view` | `edit` | `comment` on `DocumentPermission`, owner-only permission edits while `draft`.

See the repository `README.md` for run instructions (including **cnpm**).
