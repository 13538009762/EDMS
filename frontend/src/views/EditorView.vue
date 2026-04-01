<template>
  <div class="editor-page" v-loading="loading">
    <div class="header-bar">
      <div class="header-left">
        <el-input v-model="title" style="width: 240px" :disabled="!meta.can_edit" @blur="saveTitle" />
        <el-tag :type="statusTag" class="status-tag">{{ statusLabel }}</el-tag>
        <span class="hint">{{ saveHint }}</span>
      </div>
      
      <div class="header-right">
        <div class="collab-avatars" v-if="collabColors.length">
          <el-tooltip v-for="(c, i) in collabColors" :key="i" :content="c.name" placement="bottom">
            <div class="avatar-dot" :style="{ backgroundColor: c.color }">{{ c.name.charAt(0).toUpperCase() }}</div>
          </el-tooltip>
        </div>
        
        <el-dropdown trigger="click" style="margin-right: 8px;">
          <el-button>{{ t("editor.actions") }} <el-icon class="el-icon--right"><ArrowDown /></el-icon></el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item v-if="meta.can_edit" :loading="saving" @click="saveNow">{{ t("editor.save") }}</el-dropdown-item>
              <el-dropdown-item @click="downloadDocx">{{ t("editor.exportDocx") }}</el-dropdown-item>
              <el-dropdown-item @click="downloadPdf">{{ t("editor.exportPdf") }}</el-dropdown-item>
              <el-dropdown-item v-if="meta.can_edit && meta.status === 'draft'" @click="showApproval = true">{{ t("editor.startApproval") }}</el-dropdown-item>
              <el-dropdown-item v-if="meta.status === 'rejected' && isOwner" @click="newVersion">{{ t("editor.newVersion") }}</el-dropdown-item>
              <el-dropdown-item @click="showFind = true">{{ t("editor.findReplace") }}</el-dropdown-item>
              <el-dropdown-item @click="runPunctuation">{{ t("editor.punctuation") }}</el-dropdown-item>
              <el-dropdown-item @click="showPage = true">{{ t("editor.pageSetup") }}</el-dropdown-item>
              <el-dropdown-item v-if="meta.can_manage_permissions && meta.status === 'draft'" @click="showShare = true">{{ t("library.share") }}</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>

    <div class="editor-toolbar" v-if="editor && meta.can_edit">
      <el-select v-model="currentFontFamily" size="small" style="width: 120px" @change="setFontFamily">
        <el-option label="Default" value="Inter, sans-serif" />
        <el-option label="Arial" value="Arial" />
        <el-option label="Courier New" value="Courier New" />
        <el-option label="Georgia" value="Georgia" />
        <el-option label="Times New Roman" value="Times New Roman" />
      </el-select>
      <el-select v-model="currentFontSize" size="small" style="width: 80px" @change="setFontSize">
        <el-option label="12px" value="12px" />
        <el-option label="14px" value="14px" />
        <el-option label="16px" value="16px" />
        <el-option label="18px" value="18px" />
        <el-option label="24px" value="24px" />
        <el-option label="36px" value="36px" />
      </el-select>
      <div class="toolbar-divider"></div>
      
      <el-button-group class="toolbar-group">
        <el-button size="small" :class="{ 'is-active': editor.isActive('bold') }" @click="editor.chain().focus().toggleBold().run()"><b style="font-family: serif">B</b></el-button>
        <el-button size="small" :class="{ 'is-active': editor.isActive('italic') }" @click="editor.chain().focus().toggleItalic().run()"><i style="font-family: serif">I</i></el-button>
        <el-button size="small" :class="{ 'is-active': editor.isActive('underline') }" @click="editor.chain().focus().toggleUnderline().run()"><u style="font-family: serif">U</u></el-button>
        <el-button size="small" :class="{ 'is-active': editor.isActive('strike') }" @click="editor.chain().focus().toggleStrike().run()"><s style="font-family: serif">S</s></el-button>
      </el-button-group>

      <div class="toolbar-divider"></div>

      <el-button-group class="toolbar-group">
        <el-button size="small" :class="{ 'is-active': editor.isActive('heading', { level: 1 }) }" @click="editor.chain().focus().toggleHeading({ level: 1 }).run()">H1</el-button>
        <el-button size="small" :class="{ 'is-active': editor.isActive('heading', { level: 2 }) }" @click="editor.chain().focus().toggleHeading({ level: 2 }).run()">H2</el-button>
        <el-button size="small" :class="{ 'is-active': editor.isActive('heading', { level: 3 }) }" @click="editor.chain().focus().toggleHeading({ level: 3 }).run()">H3</el-button>
        <el-button size="small" :class="{ 'is-active': editor.isActive('paragraph') }" @click="editor.chain().focus().setParagraph().run()">P</el-button>
      </el-button-group>

      <div class="toolbar-divider"></div>

      <el-button-group class="toolbar-group">
        <el-button size="small" :class="{ 'is-active': editor.isActive({ textAlign: 'left' }) }" @click="editor.chain().focus().setTextAlign('left').run()">L</el-button>
        <el-button size="small" :class="{ 'is-active': editor.isActive({ textAlign: 'center' }) }" @click="editor.chain().focus().setTextAlign('center').run()">C</el-button>
        <el-button size="small" :class="{ 'is-active': editor.isActive({ textAlign: 'right' }) }" @click="editor.chain().focus().setTextAlign('right').run()">R</el-button>
        <el-button size="small" :class="{ 'is-active': editor.isActive({ textAlign: 'justify' }) }" @click="editor.chain().focus().setTextAlign('justify').run()">J</el-button>
      </el-button-group>

      <div class="toolbar-divider"></div>

      <el-button-group class="toolbar-group">
        <el-button size="small" :class="{ 'is-active': editor.isActive('bulletList') }" @click="editor.chain().focus().toggleBulletList().run()">• List</el-button>
        <el-button size="small" :class="{ 'is-active': editor.isActive('orderedList') }" @click="editor.chain().focus().toggleOrderedList().run()">1. List</el-button>
      </el-button-group>
      
      <div class="toolbar-divider"></div>
      
      <el-button-group class="toolbar-group">
        <el-button size="small" @click="doOutdent">- Indent</el-button>
        <el-button size="small" @click="doIndent">+ Indent</el-button>
      </el-button-group>

      <div class="toolbar-divider"></div>
      <el-button size="small" @click="insertImage">Img</el-button>
      <el-button size="small" @click="editor.chain().focus().insertTable({ rows: 3, cols: 3, withHeaderRow: true }).run()">Table</el-button>

      <div class="toolbar-divider"></div>
      <div style="display: flex; align-items: center; gap: 4px; font-size: 12px; margin-right:8px;">
        <label>Col</label>
        <input type="color" v-model="currentColor" @change="setTextColor" style="width: 24px; height: 24px; padding: 0; border: none; cursor: pointer" />
      </div>
      <div style="display: flex; align-items: center; gap: 4px; font-size: 12px">
        <label>Bg</label>
        <input type="color" v-model="currentHighlight" @change="setHighlight" style="width: 24px; height: 24px; padding: 0; border: none; cursor: pointer" />
      </div>

    </div>

    <div class="body">
      <div class="main-wrapper" v-if="editor">
        <div class="main-paper" :class="page.paperFormat">
          <editor-content :editor="editor" class="tiptap" :style="{ paddingTop: page.marginTop + 'px', paddingBottom: page.marginBottom + 'px' }" />
        </div>
      </div>
      <div class="side">
        <div class="comments-header">
          <h4>{{ t("editor.comments") }}</h4>
          <el-button v-if="meta.can_comment" size="small" type="primary" style="width: 100%; margin-top: 8px; margin-bottom: 12px;" @click="addCommentOnSelection">
            {{ t("editor.commentSelection") }}
          </el-button>
        </div>
        
        <div class="comment-filters">
          <el-select v-model="filterAuthor" size="small" placeholder="Author" clearable class="filter-item">
            <el-option v-for="a in authorOptions" :key="a" :label="a" :value="a" />
          </el-select>
          <el-select v-model="filterStatus" size="small" placeholder="Status" class="filter-item">
            <el-option label="All" value="all" />
            <el-option label="Active" value="active" />
            <el-option label="Resolved" value="resolved" />
          </el-select>
          <el-date-picker v-model="filterDate" type="date" placeholder="Date" size="small" class="filter-item" value-format="YYYY-MM-DD" style="width:100%" />
        </div>

        <div class="comments-list">
          <div v-for="m in filteredComments" :key="m.id" class="comment" :class="{ 'resolved': m.status === 'resolved' }" @click="scrollToComment(m.id)">
            <div class="meta">
              <div style="font-weight: 500;">{{ m.author_login }}</div>
              <div class="meta-right">
                <span>{{ m.created_at ? m.created_at.split('T')[0] : '' }} · {{ m.status }}</span>
                <el-button
                  v-if="m.status === 'active'"
                  link
                  type="primary"
                  @click.stop="resolveComment(m.id)"
                  size="small"
                >
                  {{ t("editor.resolve") }}
                </el-button>
              </div>
            </div>
            <div class="comment-body">{{ m.body }}</div>
            <el-input
              v-model="replyMap[m.id]"
              :placeholder="t('editor.replyPlaceholder')"
              size="small"
              @keyup.enter="replyTo(m.id)"
              @click.stop
            />
          </div>
          <el-empty v-if="filteredComments.length === 0" description="No comments" :image-size="60" />
        </div>
        <el-button size="small" @click="loadComments" style="width:100%; margin-top: 12px;">{{ t("editor.refreshComments") }}</el-button>
      </div>
    </div>

    <!-- Modals -->
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
        <el-form-item label="Paper Format">
          <el-select v-model="page.paperFormat">
            <el-option label="A4" value="A4" />
            <el-option label="Letter" value="Letter" />
            <el-option label="Legal" value="Legal" />
          </el-select>
        </el-form-item>
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
import FontFamily from "@tiptap/extension-font-family";
import Image from "@tiptap/extension-image";
import Dropcursor from "@tiptap/extension-dropcursor";
import Table from "@tiptap/extension-table";
import TableRow from "@tiptap/extension-table-row";
import TableCell from "@tiptap/extension-table-cell";
import TableHeader from "@tiptap/extension-table-header";
import { ArrowDown } from "@element-plus/icons-vue";

import { FontSize, LineHeight, Indent, CommentMark } from "@/utils/tiptapExtensions";
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
const hideResolved = ref(true); // Keeping for loadComments API compatibility, though we replaced with frontend block
const comments = ref<
  Array<{
    id: number;
    author_login: string;
    body: string;
    status: string;
    anchor_json?: string;
    created_at?: string;
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
  marginTop: 40,
  marginBottom: 40,
  showPageNumber: true,
  paperFormat: "A4",
});
const saveHint = ref("");
const collabColors = ref<Array<{ name: string; color: string }>>([]);

// Toolbars and Filters
const currentFontFamily = ref("");
const currentFontSize = ref("");
const currentColor = ref("#000000");
const currentHighlight = ref("#ffffff");

const filterAuthor = ref("");
const filterStatus = ref("all");
const filterDate = ref<string | null>(null);

const authorOptions = computed(() => {
  const set = new Set(comments.value.map(c => c.author_login));
  return Array.from(set);
});

const filteredComments = computed(() => {
  return comments.value.filter(c => {
    if (filterAuthor.value && c.author_login !== filterAuthor.value) return false;
    if (filterStatus.value !== "all" && c.status !== filterStatus.value) return false;
    if (filterDate.value && c.created_at && !c.created_at.startsWith(filterDate.value)) return false;
    return true;
  });
});

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
const staticCollabs = ref<Array<{ name: string; color: string }>>([]);

function refreshCollabList() {
  // 如果是已批准状态，使用静态协作者列表
  if (meta.value.status === 'approved') {
    return;
  }
  // 否则使用实时协作者列表
  const states = awareness.getStates();
  const list: Array<{ name: string; color: string }> = [];
  states.forEach((s) => {
    const u = s.user as { name?: string; color?: string } | undefined;
    if (u?.name) list.push({ name: u.name, color: u.color || "#888" });
  });
  collabColors.value = list;
}

async function loadStaticCollaborators() {
  try {
    const { data } = await api.get(`/documents/${docId.value}/collaborators`);
    staticCollabs.value = data.items.map((item: any) => ({
      name: item.name,
      color: "#888",
    }));
    // 如果是已批准状态，使用静态列表
    if (meta.value.status === 'approved') {
      collabColors.value = staticCollabs.value;
    }
  } catch (error) {
    console.error("Failed to load collaborators:", error);
  }
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
    FontFamily,
    Image,
    Dropcursor,
    Table.configure({ resizable: true }),
    TableRow,
    TableHeader,
    TableCell,
    FontSize,
    LineHeight,
    Indent,
    CommentMark,
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

function doIndent() {
  (editor.value?.chain().focus() as any).indent().run();
}

function doOutdent() {
  (editor.value?.chain().focus() as any).outdent().run();
}

function setFontFamily(val: string) {
  if (val) editor.value?.chain().focus().setFontFamily(val).run();
  else editor.value?.chain().focus().unsetFontFamily().run();
}

function setFontSize(val: string) {
  if (val) (editor.value?.chain().focus() as any).setFontSize(val).run();
  else (editor.value?.chain().focus() as any).unsetFontSize().run();
}

function setTextColor(e: Event) {
  const target = e.target as HTMLInputElement;
  editor.value?.chain().focus().setColor(target.value).run();
}

function setHighlight(e: Event) {
  const target = e.target as HTMLInputElement;
  editor.value?.chain().focus().toggleHighlight({ color: target.value }).run();
}

async function insertImage() {
  const { value } = await ElMessageBox.prompt(t("Enter image URL"), "Insert Image", {
    confirmButtonText: t("editor.ok"),
    cancelButtonText: t("inbox.cancel"),
  });
  if (value) {
    editor.value?.chain().focus().setImage({ src: value }).run();
  }
}

function scrollToComment(id: number) {
  const el = document.querySelector(`.tiptap span[data-comment-id="${id}"]`);
  if (el) {
    el.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }
}

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
    
    // 加载静态协作者列表
    await loadStaticCollaborators();
    
    // 如果不是已批准状态，刷新实时协作者列表
    if (meta.value.status !== 'approved') {
      refreshCollabList();
    }
    
    await loadComments();
  } finally {
    loading.value = false;
  }
}

// 监听文档状态变化
watch(() => meta.value.status, async (newStatus) => {
  if (newStatus === 'approved') {
    // 如果是已批准状态，使用静态协作者列表
    if (staticCollabs.value.length > 0) {
      collabColors.value = staticCollabs.value;
    }
  } else {
    // 否则使用实时协作者列表
    refreshCollabList();
  }
});

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
  // We fetch all comments by setting hide_resolved to 0, since we filter locally now.
  const { data } = await api.get(`/documents/${docId.value}/comments`, {
    params: { hide_resolved: 0 },
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
  try {
    const response = await fetch(`/api/documents/${docId.value}/export.docx`, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem("edms_token") || ""}`,
      },
    });
    if (!response.ok) {
      throw new Error("Export failed");
    }
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `doc_${docId.value}.docx`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    ElMessage.success(t("editor.exportDocx"));
  } catch (error) {
    ElMessage.error(t("editor.exportFailed"));
  }
}

async function downloadPdf() {
  try {
    const response = await fetch(`/api/documents/${docId.value}/export.pdf`, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem("edms_token") || ""}`,
      },
    });
    if (!response.ok) {
      throw new Error("Export failed");
    }
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `doc_${docId.value}.pdf`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    ElMessage.success(t("editor.exportPdf"));
  } catch (error) {
    ElMessage.error(t("editor.exportFailed"));
  }
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
  const { data } = await api.post(`/documents/${docId.value}/comments`, {
    body: value.trim(),
    anchor_json: JSON.stringify({ from, to }),
  });
  // Highlight the text using our custom comment extension
  ;(ed.chain().focus() as any).setComment(data.id).run();
  await saveNow();
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
  background-color: var(--el-bg-color-page, #f5f7fa);
}

/* Header */
.header-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background-color: white;
  border-bottom: 1px solid var(--el-border-color-lighter);
}
.header-left, .header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}
.status-tag { margin-left: 8px; }
.hint { font-size: 12px; color: var(--el-text-color-secondary); }

/* Avatars */
.collab-avatars {
  display: flex;
  margin-right: 16px;
}
.avatar-dot {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 500;
  border: 2px solid white;
  margin-left: -8px;
  cursor: pointer;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
.avatar-dot:first-child { margin-left: 0; }

/* Toolbar */
.editor-toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
  padding: 8px 16px;
  background-color: white;
  border-bottom: 1px solid var(--el-border-color-lighter);
  box-shadow: 0 2px 4px rgba(0,0,0,0.02);
  z-index: 10;
}
.toolbar-divider {
  width: 1px;
  height: 24px;
  background-color: var(--el-border-color-lighter);
  margin: 0 4px;
}
.toolbar-group .el-button {
  padding: 5px 8px;
}
.toolbar-group .el-button.is-active {
  background-color: var(--el-color-primary-light-9);
  color: var(--el-color-primary);
  border-color: var(--el-color-primary-light-5);
}

/* Body and Paper */
.body {
  display: flex;
  flex: 1;
  min-height: 0;
  overflow: hidden;
}
.main-wrapper {
  flex: 1;
  overflow: auto;
  padding: 32px;
  display: flex;
  justify-content: center;
}
.main-paper {
  background: white;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  min-height: 1056px;
  box-sizing: border-box;
  padding: 40px;
  transition: width 0.3s ease;
}
/* Paper Formats */
.main-paper.A4 { width: 794px; }
.main-paper.Letter { width: 816px; min-height: 1056px; }
.main-paper.Legal { width: 816px; min-height: 1344px; }

/* Sidebar */
.side {
  width: 320px;
  background-color: white;
  border-left: 1px solid var(--el-border-color);
  display: flex;
  flex-direction: column;
}
.comments-header {
  padding: 16px;
  border-bottom: 1px solid var(--el-border-color-lighter);
}
.comments-header h4 { margin: 0; }
.comment-filters {
  padding: 12px 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  border-bottom: 1px solid var(--el-border-color-lighter);
  background-color: #fafafa;
}
.comments-list {
  flex: 1;
  overflow-y: auto;
  padding: 0 16px 16px;
}
.comment {
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 6px;
  padding: 12px;
  margin-top: 12px;
  background-color: white;
  box-shadow: 0 1px 3px rgba(0,0,0,0.02);
  cursor: pointer;
  transition: all 0.2s;
}
.comment:hover {
  border-color: var(--el-color-primary-light-5);
  box-shadow: 0 2px 6px rgba(0,0,0,0.05);
}
.comment.resolved {
  opacity: 0.6;
  background-color: #f9f9f9;
}
.meta {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 6px;
  font-size: 13px;
}
.meta-right {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--el-text-color-secondary);
  font-size: 12px;
}
.comment-body {
  font-size: 14px;
  margin-bottom: 12px;
  line-height: 1.5;
}

/* Tiptap Editor Core */
.tiptap {
  outline: none;
  min-height: 100%;
}
.tiptap :deep(.ProseMirror) {
  outline: none;
  min-height: 100%;
}
.tiptap :deep(table) {
  border-collapse: collapse;
  table-layout: fixed;
  width: 100%;
  margin: 0;
  overflow: hidden;
}
.tiptap :deep(table td),
.tiptap :deep(table th) {
  min-width: 1em;
  border: 1px solid var(--el-border-color-darker);
  padding: 5px 8px;
  vertical-align: top;
  box-sizing: border-box;
  position: relative;
}
.tiptap :deep(table th) {
  font-weight: bold;
  text-align: left;
  background-color: #f5f5f5;
}
.tiptap :deep(img) {
  max-width: 100%;
  height: auto;
}
</style>
