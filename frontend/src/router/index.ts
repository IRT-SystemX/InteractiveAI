import { createRouter, createWebHistory } from 'vue-router'

import { useAuthStore } from '@/stores/auth'
import { ENTITIES, type Entity } from '@/types/entities'
import { handleSessionExpired } from '@/utils/session'
import CAB from '@/views/CAB.vue'
import Home from '@/views/Home.vue'
import Login from '@/views/Login.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: Home,
      meta: {
        auth: true
      }
    },
    {
      path: '/login',
      name: 'login',
      component: Login,
      meta: {
        auth: false
      }
    },
    {
      path: `/cab/:entity(${ENTITIES.join('|')})`,
      name: 'cab',
      component: CAB,
      meta: {
        auth: true
      }
    }
  ]
})

router.beforeEach(async (to) => {
  const authStore = useAuthStore()

  // The auth store is persisted, so reopening the app restores a token that
  // may already have aged out. Renew it here rather than letting every request
  // 401; only a dead refresh token actually ends the session.
  if (to.meta.auth && authStore.user && authStore.isTokenExpired) {
    if (!(await authStore.refresh())) {
      handleSessionExpired({ redirect: false })
      return { name: 'login' }
    }
  }

  if (to.meta.auth && !authStore.user) return { name: 'login' }
  if (!to.meta.auth && authStore.user) return { name: 'home' }
  if (to.name === 'home' && authStore.entities.length === 1)
    return { name: 'cab', params: { entity: authStore.entities[0] } }
  if (!to.name || (to.name === 'cab' && !authStore.entities.includes(to.params.entity as Entity)))
    return { name: 'home' }
})

export default router
