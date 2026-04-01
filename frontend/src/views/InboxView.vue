<template>
  <div>
    <h2>{{ t("inbox.title") }}</h2>
    <el-button @click="load" :loading="loading">{{ t("inbox.refresh") }}</el-button>
    <el-table :data="items" style="margin-top: 16px">
      <el-table-column prop="document_id" :label="t('inbox.colDocId')" width="100" />
      <el-table-column prop="title" :label="t('inbox.colTitle')" />
      <el-table-column prop="flow_type" :label="t('inbox.colFlow')" width="120" />
      <el-table-column :label="t('inbox.colProgress')">
        <template #default="{ row }">
          {{ row.progress.done }} / {{ row.progress.total }}
        </template>
      </el-table-column>
      <el-table-column :label="t('inbox.colActions')" width="220">
        <template #default="{ row }">
          <el-button type="success" link @click="decide(row.participant_id, 'approve')">
            {{ t("inbox.approve") }}
          </el-button>
          <el-button type="danger" link @click="openReject(row)">{{ t("inbox.reject") }}</el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-dialog v-model="rejectDlg" :title="t('inbox.rejectTitle')" width="400px">
      <el-input v-model="rejectReason" type="textarea" :rows="4" />
      <template #footer>
        <el-button @click="rejectDlg = false">{{ t("inbox.cancel") }}</el-button>
        <el-button type="danger" @click="confirmReject">{{ t("inbox.reject") }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useI18n } from "vue-i18n";
import api from "@/api/client";
import { ElMessage } from "element-plus";

interface InboxRow {
  participant_id: number;
  document_id: number;
  title: string;
  flow_type: string;
  progress: { done: number; total: number };
}

const { t } = useI18n();
const items = ref<InboxRow[]>([]);
const loading = ref(false);
const rejectDlg = ref(false);
const rejectReason = ref("");
const rejectPid = ref<number | null>(null);

async function load() {
  loading.value = true;
  try {
    const { data } = await api.get("/approvals/inbox");
    items.value = data.items;
  } finally {
    loading.value = false;
  }
}

async function decide(participantId: number, decision: "approve" | "reject", reason?: string) {
  await api.post(`/approvals/participants/${participantId}/decision`, {
    decision,
    reason: reason || undefined,
  });
  ElMessage.success(t("inbox.submitted"));
  load();
}

function openReject(row: InboxRow) {
  rejectPid.value = row.participant_id;
  rejectReason.value = "";
  rejectDlg.value = true;
}

function confirmReject() {
  if (!rejectPid.value || !rejectReason.value.trim()) {
    ElMessage.warning(t("inbox.reasonRequired"));
    return;
  }
  decide(rejectPid.value, "reject", rejectReason.value);
  rejectDlg.value = false;
}

onMounted(load);
</script>
