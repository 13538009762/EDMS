<template>
  <div>
    <div class="toolbar">
      <el-button type="primary" @click="createDoc">{{ t("library.newDoc") }}</el-button>
      <el-upload
        :show-file-list="false"
        accept=".docx"
        :before-upload="onImportDocx"
        style="display: inline-block; margin-left: 12px"
      >
        <el-button>{{ t("library.importDocx") }}</el-button>
      </el-upload>
      <el-select
        v-model="scope"
        clearable
        style="width: 200px; margin-left: 12px"
        :placeholder="t('library.scopePlaceholder')"
        @change="load"
      >
        <el-option :label="t('library.scopeAll')" value="" />
        <el-option :label="t('library.scopeMine')" value="mine" />
        <el-option :label="t('library.scopeCollab')" value="collab" />
        <el-option :label="t('library.scopeDepartment')" value="department" />
      </el-select>
      <el-select
        v-model="statusFilter"
        clearable
        style="width: 180px; margin-left: 12px"
        :placeholder="t('library.statusFilter')"
        @change="load"
      >
        <el-option :label="t('library.statusAll')" value="" />
        <el-option :label="t('library.statusDraft')" value="draft" />
        <el-option :label="t('library.statusInApproval')" value="in_approval" />
        <el-option :label="t('library.statusApproved')" value="approved" />
        <el-option :label="t('library.statusRejected')" value="rejected" />
      </el-select>
      <el-button @click="load">{{ t("library.refresh") }}</el-button>
    </div>
    <el-table :data="items" v-loading="loading" style="margin-top: 16px">
      <el-table-column prop="id" :label="t('library.colId')" width="70" />
      <el-table-column prop="title" :label="t('library.colTitle')" min-width="140" />
      <el-table-column prop="status" :label="t('library.colStatus')" width="120" />
      <el-table-column prop="owner_name" :label="t('library.colOwner')" min-width="120" />
      <el-table-column prop="owner_department" :label="t('library.colDepartment')" min-width="120" />
      <el-table-column prop="my_role" :label="t('library.colRole')" width="100" />
      <el-table-column :label="t('library.colActions')" width="260" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" link @click="open(row.id)">{{ t("library.open") }}</el-button>
          <el-button
            v-if="row.can_manage_permissions && row.status === 'draft'"
            type="warning"
            link
            @click="openShare(row.id)"
          >
            {{ t("library.share") }}
          </el-button>
          <el-button
            v-if="row.status === 'approved'"
            type="info"
            link
            @click="router.push({ name: 'diff', params: { id: row.id } })"
          >
            {{ t("library.diff") }}
          </el-button>
        </template>
      </el-table-column>
    </el-table>
    <DocumentShareDialog
      v-model="shareOpen"
      :document-id="shareDocId"
      @saved="load"
    />
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { useI18n } from "vue-i18n";
import api from "@/api/client";
import { ElMessage } from "element-plus";
import mammoth from "mammoth";
import type { UploadRawFile } from "element-plus";
import DocumentShareDialog from "@/components/DocumentShareDialog.vue";

interface DocRow {
  id: number;
  title: string;
  status: string;
  my_role?: string;
  can_manage_permissions?: boolean;
  owner_name?: string;
  owner_department?: string;
}

const router = useRouter();
const { t } = useI18n();
const items = ref<DocRow[]>([]);
const loading = ref(false);
const scope = ref("");
const statusFilter = ref("");
const shareOpen = ref(false);
const shareDocId = ref<number | null>(null);

async function load() {
  loading.value = true;
  try {
    const params: Record<string, string> = { scope: scope.value || "all" };
    if (statusFilter.value) params.status = statusFilter.value;
    const { data } = await api.get("/documents", { params });
    items.value = data.items as DocRow[];
  } finally {
    loading.value = false;
  }
}

async function createDoc() {
  try {
    const { data } = await api.post("/documents", { title: t("common.untitled") });
    router.push({ name: "editor", params: { id: data.id } });
  } catch {
    ElMessage.error(t("library.createFailed"));
  }
}

function open(id: number) {
  router.push({ name: "editor", params: { id } });
}

function openShare(id: number) {
  shareDocId.value = id;
  shareOpen.value = true;
}

async function onImportDocx(file: UploadRawFile) {
  try {
    // Create a new document
    const { data: docData } = await api.post("/documents", { title: file.name.replace(/\.docx$/, "") });
    const docId = docData.id;
    
    // Convert DOCX to raw text (without HTML tags)
    const ab = await file.arrayBuffer();
    const { value: rawText } = await mammoth.extractRawText({ arrayBuffer: ab });
    
    // Convert raw text to TipTap JSON structure
    // Split by newlines to create paragraphs
    const lines = rawText.split('\n').filter(line => line.trim().length > 0);
    const content = {
      type: "doc",
      content: lines.length > 0 ? lines.map(line => ({
        type: "paragraph",
        attrs: { textAlign: "left" },
        content: line.trim() ? [{ type: "text", text: line.trim() }] : [],
      })) : [{
        type: "paragraph",
        attrs: { textAlign: "left" },
        content: [],
      }],
    };
    
    // Save the content to the new document using the correct API endpoint
    await api.put(`/documents/${docId}/content`, {
      content_json: JSON.stringify(content),
    });
    
    ElMessage.success(t("library.importDocxSuccess"));
    // Reload the document list
    await load();
  } catch (error) {
    console.error("Import DOCX error:", error);
    ElMessage.error(t("library.importDocxFailed"));
  }
  return false;
}

onMounted(load);
</script>

<style scoped>
.toolbar {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}
</style>
