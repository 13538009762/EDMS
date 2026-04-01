<template>
  <el-container class="layout">
    <el-header class="header">
      <span class="brand">EDMS</span>
      <el-menu mode="horizontal" router :default-active="route.path" class="menu">
        <el-menu-item index="/">{{ t("nav.library") }}</el-menu-item>
        <el-menu-item index="/inbox">{{ t("nav.inbox") }}</el-menu-item>
        <el-menu-item index="/import">{{ t("nav.masterData") }}</el-menu-item>
      </el-menu>
      <div class="spacer" />
      <LocaleSwitcher />
      <el-button v-if="auth.user" type="primary" link @click="router.push({ name: 'personal' })">{{ auth.user.display_name }}</el-button>
      <el-button type="primary" link @click="onLogout">{{ t("nav.logout") }}</el-button>
    </el-header>
    <el-main class="main">
      <router-view />
    </el-main>
  </el-container>
</template>

<script setup lang="ts">
import { useRoute, useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import { onMounted } from "vue";
import { useI18n } from "vue-i18n";
import LocaleSwitcher from "@/components/LocaleSwitcher.vue";

const route = useRoute();
const router = useRouter();
const auth = useAuthStore();
const { t } = useI18n();

onMounted(() => {
  auth.fetchMe().catch(() => {});
});

function onLogout() {
  auth.logout();
  router.push({ name: "login" });
}

</script>

<style scoped>
.layout {
  height: 100%;
}
.header {
  display: flex;
  align-items: center;
  gap: 16px;
  border-bottom: 1px solid var(--el-border-color);
}
.brand {
  font-weight: 700;
  margin-right: 24px;
}
.menu {
  flex: 0 1 auto;
  border-bottom: none;
}
.main {
  padding: 16px;
  overflow: auto;
}
.spacer {
  flex: 1;
}
.user {
  margin-right: 12px;
  color: var(--el-text-color-secondary);
}
</style>
