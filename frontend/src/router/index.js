import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import ChatView from '../views/ChatView.vue'
import LoginView from '../views/LoginView.vue'
import SettingsView from '../views/SettingsView.vue'

const routes = [
  {
    path: '/login',
    name: 'login',
    component: LoginView,
    meta: { guest: true }
  },
  {
    path: '/',
    redirect: '/chat'
  },
  {
    path: '/chat',
    name: 'chat',
    component: ChatView
  },
  {
    path: '/chat/:id',
    name: 'chat-detail',
    component: ChatView
  },
  {
    path: '/settings',
    name: 'settings',
    component: SettingsView
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  if (authStore.skipAuth) {
    return next()
  }

  if (to.meta.guest && authStore.isLoggedIn) {
    return next('/')
  }

  if (!to.meta.guest && !authStore.isLoggedIn) {
    return next('/login')
  }

  next()
})

export default router
