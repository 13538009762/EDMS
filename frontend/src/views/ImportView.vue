<template>
  <div>
    <h2>{{ t("import.title") }}</h2>
    <p class="hint">
      {{ t("import.hint") }}
    </p>
    <el-upload
      :auto-upload="false"
      :on-change="onFile"
      :limit="1"
      accept=".xlsx,.xlsm"
    >
      <el-button type="primary">{{ t("import.selectFile") }}</el-button>
    </el-upload>
    <el-button
      style="margin-left: 12px"
      type="success"
      :loading="loading"
      :disabled="!file"
      @click="upload"
    >
      {{ t("import.upload") }}
    </el-button>
    <pre v-if="result" class="result">{{ JSON.stringify(result, null, 2) }}</pre>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import type { UploadFile } from "element-plus";
import { useI18n } from "vue-i18n";
import api from "@/api/client";
import { ElMessage, ElMessageBox } from "element-plus";

const { t } = useI18n();
const file = ref<File | null>(null);
const loading = ref(false);
const result = ref<unknown>(null);
const adminToken = ref("");

function onFile(f: UploadFile) {
  file.value = f.raw || null;
}

async function upload() {
  if (!file.value) return;
  
  // Show confirmation warning before import
  try {
    await ElMessageBox.confirm(
      t('import.warning'),
      t('import.confirmTitle'),
      {
        confirmButtonText: t('import.confirmImport'),
        cancelButtonText: t('inbox.cancel'),
        type: 'warning',
      }
    );
  } catch {
    // User cancelled
    return;
  }
  
  loading.value = true;
  result.value = null;
  const fd = new FormData();
  fd.append("file", file.value);
  try {
    const { data } = await api.post("/master-data/import", fd, {
      headers: {
        "Content-Type": "multipart/form-data",
        ...(adminToken.value ? { "X-Admin-Token": adminToken.value } : {}),
      },
    });
    result.value = data;
    ElMessage.success(t("import.success"));
  } catch (e: unknown) {
    ElMessage.error(t("import.failed"));
    result.value = e;
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.hint {
  color: var(--el-text-color-secondary);
  max-width: 720px;
}
.result {
  margin-top: 16px;
  background: var(--el-fill-color-light);
  padding: 12px;
}
</style>
