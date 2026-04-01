<template>
  <div class="wrap">
    <div class="top-bar">
      <LocaleSwitcher />
    </div>
    <el-card class="card">
      <template #header>{{ t("login.title") }}</template>
      <el-form @submit.prevent="submit">
        <el-form-item :label="t('login.loginName')">
          <el-input v-model="loginName" autocomplete="username" />
        </el-form-item>
        <el-button type="primary" native-type="submit" :loading="loading" style="width: 100%">{{
          t("login.submit")
        }}</el-button>
        <div class="admin-link">
          <el-button type="primary" link @click="router.push({ name: 'admin' })">{{
            t("login.goAdmin")
          }}</el-button>
        </div>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useRouter, useRoute } from "vue-router";
import { ElMessage } from "element-plus";
import { useI18n } from "vue-i18n";
import { useAuthStore } from "@/stores/auth";
import LocaleSwitcher from "@/components/LocaleSwitcher.vue";

const loginName = ref("");
const loading = ref(false);
const router = useRouter();
const route = useRoute();
const auth = useAuthStore();
const { t } = useI18n();

async function submit() {
  loading.value = true;
  try {
    await auth.login(loginName.value.trim());
    const r = (route.query.redirect as string) || "/";
    router.replace(r);
  } catch {
    ElMessage.error(t("login.invalid"));
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.wrap {
  min-height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: var(--el-fill-color-light);
  position: relative;
}
.top-bar {
  position: absolute;
  top: 16px;
  right: 16px;
}
.card {
  width: 400px;
}
.admin-link {
  margin-top: 12px;
  text-align: center;
}
</style>
