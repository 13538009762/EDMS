<template>
  <div class="editor-page" v-loading="loading">
    <div class="bar">
      <el-input v-model="title" style="width: 240px" :disabled="!meta.can_edit" @blur="saveTitle" />
      <el-tag :type="statusTag">{{ statusLabel }}</el-tag>
      <el-button v-if="meta.can_edit" :loading="saving" @click="saveNow">{{ t("editor.save") }}</el-button>
      <el-button @click="downloadDocx">{{ t("editor.exportDocx") }}</el-button>
      <el-button @click="downloadPdf">{{ t("editor.exportPdf") }}</el-button>
      <el-button v-if="meta.can_edit && meta.status === 'draft'" @click="showApproval = true">
        {{ t("editor.startApproval") }}
      </el-button>
      <el-button v-if="meta.status === 'rejected' && isOwner" @click="newVersion">
        {{ t("editor.newVersion") }}
      </el-button>
      <el-button @click="showFind = true">{{ t("editor.findReplace") }}</el-button>
      <el-button @click="runPunctuation">{{ t("editor.punctuation") }}</el-button>
      <el-button @click="showPage = true">{{ t("editor.pageSetup") }}</el-button>
      <el-upload
        v-if="meta.can_edit"
        :show-file-list="false"
        accept=".docx"
        :before-upload="onImportDocx"
      >
        <el-button>{{ t("editor.importDocx") }}</el-button>
      </el-upload>
      <el-button v-if="meta.can_comment" size="small" @click="addCommentOnSelection">
        {{ t("editor.commentSelection") }}
      </el-button>
      <el-button
        v-if="meta.can_manage_permissions && meta.status === 'draft'"
        size="small"
        @click="showShare = true"
      >
        {{ t("library.share") }}
      </el-button>
      <span class="hint">{{ saveHint }}</span>
    </div>
    <div class="body">
      <div class="main" v-if="editor">
        <editor-content :editor="editor" class="tiptap" />
      </div>
      <div class="side">
        <h4>{{ t("editor.collaborators") }}</h4>
        <ul>
          <li v-for="(c, i) in collabColors" :key="i">
            <span class="dot" :style="{ background: c.color }" /> {{ c.name }}
          </li>
        </ul>
        <h4>{{ t("editor.comments") }}</h4>
        <el-checkbox v-model="hideResolved">{{ t("editor.hideResolved") }}</el-checkbox>
        <div v-for="m in comments" :key="m.id" class="comment">
          <div class="meta">
            {{ m.author_login }} · {{ m.status }}
            <el-button
              v-if="m.status === 'active'"
              link
              type="primary"
              @click="resolveComment(m.id)"
            >
              {{ t("editor.resolve") }}
            </el-button>
          </div>
          <div>{{ m.body }}</div>
          <el-input
            v-model="replyMap[m.id]"
            :placeholder="t('editor.replyPlaceholder')"
            size="small"
            @keyup.enter="replyTo(m.id)"
          />
        </div>
        <el-button size="small" @click="loadComments">{{ t("editor.refreshComments") }}</el-button>
      </div>
    </div>

    <el-dialog v-model="showFind" :title="t('editor.findReplaceTitle')" width="480px">
      <el-input v-model="findText" :placeholder="t('editor.findPlaceholder')" />
      <el-input
        v-model="replaceText"
        :placeholder="t('editor.replacePlaceholder')"
        style="margin-top: 8px"
      />
      <template #footer>
        <el-button @click="doReplace(false)">{{ t("editor.findNext") }}</el-button>
        <el-button type="primary" @click="doReplace(true)">{{ t("editor.replaceAll") }}</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showPage" :title="t('editor.pageSetupTitle')" width="400px">
      <el-form label-width="140px">
        <el-form-item :label="t('editor.orientation')">
          <el-select v-model="page.orientation">
            <el-option :label="t('editor.portrait')" value="portrait" />
            <el-option :label="t('editor.landscape')" value="landscape" />
          </el-select>
        </el-form-item>
        <el-form-item :label="t('editor.marginTop')">
          <el-input-number v-model="page.marginTop" :min="5" />
        </el-form-item>
        <el-form-item :label="t('editor.marginBottom')">
          <el-input-number v-model="page.marginBottom" :min="5" />
        </el-form-item>
        <el-form-item :label="t('editor.showPageNumber')">
          <el-switch v-model="page.showPageNumber" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button type="primary" @click="savePageSettings">{{ t("editor.apply") }}</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showApproval" :title="t('editor.approvalTitle')" width="420px">
      <el-radio-group v-model="approvalType">
        <el-radio label="parallel">{{ t("editor.parallel") }}</el-radio>
        <el-radio label="sequential">{{ t("editor.sequential") }}</el-radio>
      </el-radio-group>
      <el-select
        v-model="approverIds"
        multiple
        filterable
        :placeholder="t('editor.approversPlaceholder')"
        style="width: 100%; margin-top: 12px"
      >
        <el-option v-for="u in userOptions" :key="u.id" :label="`${u.login_name}`" :value="u.id" />
      </el-select>
      <template #footer>
        <el-button type="primary" @click="startApproval">{{ t("editor.start") }}</el-button>
      </template>
    </el-dialog>

    <DocumentShareDialog v-model="showShare" :document-id="docId" @saved="loadDoc" />
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from "vue";
import { useRoute } from "vue-router";
import { useI18n } from "vue-i18n";
import * as Y from "yjs";
import { Awareness } from "y-protocols/awareness";
import { useEditor, EditorContent } from "@tiptap/vue-3";
import StarterKit from "@tiptap/starter-kit";
import Collaboration from "@tiptap/extension-collaboration";
import CollaborationCursor from "@tiptap/extension-collaboration-cursor";
import Underline from "@tiptap/extension-underline";
import TextAlign from "@tiptap/extension-text-align";
import TextStyle from "@tiptap/extension-text-style";
import Color from "@tiptap/extension-color";
import Highlight from "@tiptap/extension-highlight";
import api from "@/api/client";
import { useAuthStore } from "@/stores/auth";
import { attachDocCollab } from "@/composables/useDocSocket";
import { checkPunctuationIssues, fixPunctuation } from "@/utils/punctuation";
import { ElMessage, ElMessageBox } from "element-plus";
import mammoth from "mammoth";
import type { UploadRawFile } from "element-plus";
import DocumentShareDialog from "@/components/DocumentShareDialog.vue";

const route = useRoute();
const { t, locale } = useI18n();
const auth = useAuthStore();
const docId = computed(() => Number(route.params.id));

const loading = ref(true);
const saving = ref(false);
const title = ref("");
const meta = ref({
  status: "draft",
  can_edit: false,
  can_comment: false,
  can_manage_permissions: false,
  owner_id: 0,
});
const showShare = ref(false);
const hideResolved = ref(true);
const comments = ref<
  Array<{
    id: number;
    author_login: string;
    body: string;
    status: string;
    anchor_json?: string;
  }>
>([]);
const replyMap = ref<Record<number, string>>({});
const findText = ref("");
const replaceText = ref("");
const showFind = ref(false);
const showPage = ref(false);
const showApproval = ref(false);
const approvalType = ref("parallel");
const approverIds = ref<number[]>([]);
const userOptions = ref<Array<{ id: number; login_name: string }>>([]);
const page = ref({
  orientation: "portrait",
  marginTop: 20,
  marginBottom: 20,
  showPageNumber: true,
});
const saveHint = ref("");
const collabColors = ref<Array<{ name: string; color: string }>>([]);

const isOwner = computed(() => auth.user?.id === meta.value.owner_id);

const statusLabel = computed(() => {
  const s = meta.value.status;
  const map: Record<string, string> = {
    draft: "editor.statusDraft",
    in_approval: "editor.statusInApproval",
    approved: "editor.statusApproved",
    rejected: "editor.statusRejected",
  };
  const k = map[s];
  return k ? t(k) : s;
});

const statusTag = computed(() => {
  const s = meta.value.status;
  if (s === "approved") return "success";
  if (s === "rejected") return "danger";
  if (s === "in_approval") return "warning";
  return "info";
});

const ydoc = new Y.Doc();
const awareness = new Awareness(ydoc);
const userColor = `#${Math.floor(Math.random() * 0xffffff)
  .toString(16)
  .padStart(6, "0")}`;

let collabDisconnect: (() => void) | null = null;

function refreshCollabList() {
  const states = awareness.getStates();
  const list: Array<{ name: string; color: string }> = [];
  states.forEach((s) => {
    const u = s.user as { name?: string; color?: string } | undefined;
    if (u?.name) list.push({ name: u.name, color: u.color || "#888" });
  });
  collabColors.value = list;
}

const editor = useEditor({
  extensions: [
    StarterKit.configure({ history: false }),
    Underline,
    TextStyle,
    Color,
    Highlight.configure({ multicolor: true }),
    TextAlign.configure({ types: ["heading", "paragraph"] }),
    Collaboration.configure({ document: ydoc }),
    CollaborationCursor.configure({
      provider: { awareness } as never,
    }),
  ],
  editable: true,
  onUpdate: () => scheduleSave(),
});

function scheduleSave() {
  if (!meta.value.can_edit) return;
  if (saveTimer) clearTimeout(saveTimer);
  saveTimer = window.setTimeout(() => saveNow(), 2000);
}
let saveTimer = 0;

async function loadDoc() {
  loading.value = true;
  try {
    const { data } = await api.get(`/documents/${docId.value}`);
    title.value = data.title;
    meta.value = {
      status: data.status,
      can_edit: data.can_edit,
      can_comment: data.can_comment,
      can_manage_permissions: data.can_manage_permissions ?? false,
      owner_id: data.owner_id,
    };
    if (data.page_settings_json) {
      try {
        Object.assign(page.value, JSON.parse(data.page_settings_json));
      } catch {
        /* ignore */
      }
    }
    if (editor.value) {
      editor.value.setEditable(data.can_edit);
    }
    if (data.yjs_state_b64) {
      const u = Uint8Array.from(atob(data.yjs_state_b64), (c) => c.charCodeAt(0));
      Y.applyUpdate(ydoc, u);
    } else if (data.content_json) {
      const j =
        typeof data.content_json === "string" ? JSON.parse(data.content_json) : data.content_json;
      await nextTick();
      editor.value?.commands.setContent(j);
    }
    collabDisconnect?.();
    const name = auth.user?.display_name || auth.user?.login_name || "User";
    collabDisconnect = attachDocCollab(docId.value, ydoc, awareness, {
      name,
      color: userColor,
    });
    awareness.off("update", refreshCollabList);
    awareness.on("update", refreshCollabList);
    refreshCollabList();
    await loadComments();
  } finally {
    loading.value = false;
  }
}

async function saveNow() {
  if (!editor.value || !meta.value.can_edit) return;
  saving.value = true;
  try {
    const content_json = editor.value.getJSON();
    const update = Y.encodeStateAsUpdate(ydoc);
    await api.put(`/documents/${docId.value}/content`, {
      content_json,
      yjs_state_b64: btoa(String.fromCharCode(...update)),
    });
    const time = new Date().toLocaleTimeString(locale.value === "zh-CN" ? "zh-CN" : "en-US");
    saveHint.value = t("editor.savedAt", { time });
  } catch {
    saveHint.value = t("editor.saveFailed");
  } finally {
    saving.value = false;
  }
}

async function saveTitle() {
  await api.patch(`/documents/${docId.value}`, { title: title.value });
}

async function savePageSettings() {
  await api.patch(`/documents/${docId.value}`, {
    page_settings_json: JSON.stringify(page.value),
  });
  showPage.value = false;
  ElMessage.success(t("editor.pageSettingsSaved"));
}

async function loadComments() {
  const { data } = await api.get(`/documents/${docId.value}/comments`, {
    params: { hide_resolved: hideResolved.value ? 1 : 0 },
  });
  comments.value = data.items;
}

watch(hideResolved, loadComments);

async function resolveComment(id: number) {
  await api.patch(`/comments/${id}`, { status: "resolved" });
  loadComments();
}

async function replyTo(parentId: number) {
  const body = (replyMap.value[parentId] || "").trim();
  if (!body) return;
  await api.post(`/documents/${docId.value}/comments`, { body, parent_id: parentId });
  replyMap.value[parentId] = "";
  loadComments();
}

function runPunctuation() {
  const tx = editor.value?.getText() || "";
  const issues = checkPunctuationIssues(tx);
  if (issues.length) ElMessageBox.alert(issues.join("\n"), t("editor.punctuationTitle"));
  else ElMessage.success(t("editor.noIssues"));
}

function doReplace(all: boolean) {
  const ed = editor.value;
  if (!ed || !findText.value) return;
  const { state } = ed.view;
  const { doc } = state;
  let text = "";
  doc.descendants((node) => {
    if (node.isText) text += node.text;
    return true;
  });
  if (!all) {
    const idx = text.indexOf(findText.value);
    if (idx < 0) {
      ElMessage.info(t("editor.notFound"));
      return;
    }
  }
  const fixed = all
    ? text.split(findText.value).join(replaceText.value)
    : text.replace(findText.value, replaceText.value);
  const fixed2 = fixPunctuation(fixed);
  ed.commands.setContent(
    fixed2
      ? [{ type: "paragraph", content: [{ type: "text", text: fixed2 }] }]
      : [{ type: "paragraph" }],
  );
  showFind.value = false;
}

async function downloadDocx() {
  const { data } = await api.get(`/documents/${docId.value}/export.docx`, {
    responseType: "blob",
  });
  const url = URL.createObjectURL(data);
  const a = document.createElement("a");
  a.href = url;
  a.download = `doc_${docId.value}.docx`;
  a.click();
  URL.revokeObjectURL(url);
}

async function downloadPdf() {
  const { data } = await api.get(`/documents/${docId.value}/export.pdf`, {
    responseType: "blob",
  });
  const url = URL.createObjectURL(data);
  const a = document.createElement("a");
  a.href = url;
  a.download = `doc_${docId.value}.pdf`;
  a.click();
  URL.revokeObjectURL(url);
}

async function startApproval() {
  try {
    await api.post(`/documents/${docId.value}/approval`, {
      flow_type: approvalType.value,
      approver_ids: approverIds.value,
    });
    showApproval.value = false;
    ElMessage.success(t("editor.approvalStarted"));
    loadDoc();
  } catch {
    ElMessage.error(t("editor.approvalFailed"));
  }
}

async function newVersion() {
  await api.post(`/documents/${docId.value}/new-version`);
  ElMessage.success(t("editor.newVersionOk"));
  loadDoc();
}

async function onImportDocx(file: UploadRawFile) {
  const ab = await file.arrayBuffer();
  const { value: html } = await mammoth.convertToHtml({ arrayBuffer: ab });
  editor.value?.commands.setContent(html);
  await saveNow();
  ElMessage.success(t("editor.docxImported"));
  return false;
}

async function addCommentOnSelection() {
  const ed = editor.value;
  if (!ed) return;
  const { from, to } = ed.state.selection;
  if (from === to) {
    ElMessage.warning(t("editor.selectTextFirst"));
    return;
  }
  const { value } = await ElMessageBox.prompt(t("editor.commentPrompt"), t("editor.newCommentTitle"), {
    confirmButtonText: t("editor.ok"),
    cancelButtonText: t("inbox.cancel"),
  });
  if (!value?.trim()) return;
  await api.post(`/documents/${docId.value}/comments`, {
    body: value.trim(),
    anchor_json: { from, to },
  });
  loadComments();
}

watch(showApproval, async (v) => {
  if (!v) return;
  const { data } = await api.get("/users");
  userOptions.value = data.items;
});

onMounted(async () => {
  await auth.fetchMe().catch(() => {});
  await loadDoc();
  window.addEventListener("beforeunload", saveNow);
});

onBeforeUnmount(() => {
  window.removeEventListener("beforeunload", saveNow);
  void saveNow();
  awareness.off("update", refreshCollabList);
  collabDisconnect?.();
  editor.value?.destroy();
});

watch(
  () => route.params.id,
  () => loadDoc(),
);
</script>

<style scoped>
.editor-page {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 80px);
}
.bar {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
  margin-bottom: 12px;
}
.hint {
  margin-left: auto;
  font-size: 12px;
  color: var(--el-text-color-secondary);
}
.body {
  display: flex;
  flex: 1;
  min-height: 0;
  gap: 16px;
}
.main {
  flex: 1;
  overflow: auto;
  border: 1px solid var(--el-border-color);
  padding: 16px;
  background: white;
}
.side {
  width: 280px;
  overflow: auto;
  border: 1px solid var(--el-border-color);
  padding: 12px;
}
.tiptap {
  min-height: 400px;
  outline: none;
}
.tiptap :deep(.ProseMirror) {
  min-height: 400px;
  outline: none;
}
.comment {
  border-bottom: 1px solid var(--el-border-color-lighter);
  padding: 8px 0;
}
.meta {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}
.dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-right: 6px;
}
</style>
