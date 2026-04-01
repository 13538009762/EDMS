import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "@/stores/auth";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/login", name: "login", component: () => import("@/views/LoginView.vue") },
    { path: "/admin", name: "admin", component: () => import("@/views/AdminView.vue") },
    {
      path: "/",
      component: () => import("@/layouts/MainLayout.vue"),
      meta: { requiresAuth: true },
      children: [
        { path: "", name: "library", component: () => import("@/views/LibraryView.vue") },
        { path: "import", name: "import", component: () => import("@/views/ImportView.vue") },
        { path: "inbox", name: "inbox", component: () => import("@/views/InboxView.vue") },
        {
          path: "doc/:id",
          name: "editor",
          component: () => import("@/views/EditorView.vue"),
        },
        {
          path: "doc/:id/diff",
          name: "diff",
          component: () => import("@/views/DiffView.vue"),
        },
      ],
    },
  ],
});

router.beforeEach((to, _from, next) => {
  const auth = useAuthStore();
  if (to.meta.requiresAuth && !auth.token) {
    next({ name: "login", query: { redirect: to.fullPath } });
    return;
  }
  if (to.name === "login" && auth.token) {
    next({ name: "library" });
    return;
  }
  next();
});

export default router;
