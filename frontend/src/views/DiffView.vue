<template>
  <div v-loading="loading">
    <h2>{{ t("diff.title") }}</h2>
    <el-select v-model="fromId" :placeholder="t('diff.fromVersion')" style="width: 220px">
      <el-option
        v-for="v in versions"
        :key="v.id"
        :label="t('diff.versionLabel', { no: v.version_no, id: v.id })"
        :value="v.id"
      />
    </el-select>
    <el-select
      v-model="toId"
      :placeholder="t('diff.toVersion')"
      style="width: 220px; margin-left: 8px"
    >
      <el-option
        v-for="v in versions"
        :key="v.id"
        :label="t('diff.versionLabel', { no: v.version_no, id: v.id })"
        :value="v.id"
      />
    </el-select>
    <el-button type="primary" style="margin-left: 8px" @click="loadDiff">{{
      t("diff.compare")
    }}</el-button>
    <div v-if="html" class="diff-box" v-html="html" />
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useRoute } from "vue-router";
import { useI18n } from "vue-i18n";
import api from "@/api/client";

const route = useRoute();
const { t } = useI18n();
const id = Number(route.params.id);
const versions = ref<Array<{ id: number; version_no: number }>>([]);
const fromId = ref<number | undefined>();
const toId = ref<number | undefined>();
const html = ref("");
const loading = ref(false);

async function loadVers() {
  const { data } = await api.get(`/documents/${id}/versions`);
  versions.value = data.items;
  if (data.items.length >= 2) {
    fromId.value = data.items[data.items.length - 2]!.id;
    toId.value = data.items[data.items.length - 1]!.id;
  }
}

async function loadDiff() {
  if (!fromId.value || !toId.value) return;
  loading.value = true;
  try {
    const { data } = await api.get(`/documents/${id}/diff`, {
      params: { from: fromId.value, to: toId.value },
    });
    html.value = data.html;
  } finally {
    loading.value = false;
  }
}

onMounted(async () => {
  await loadVers();
});
</script>

<style scoped>
.diff-box {
  margin-top: 16px;
  padding: 16px;
  border: 1px solid var(--el-border-color);
  background: var(--el-fill-color-blank);
}
.diff-box :deep(ins) {
  background: #cfc;
  text-decoration: none;
}
.diff-box :deep(del) {
  background: #fcc;
}
</style>
