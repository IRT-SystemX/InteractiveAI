import { createRouter, createWebHistory } from 'vue-router'

import { useAuthStore } from '@/stores/auth'
import { EntitiesArray, type Entity } from '@/types/entities'
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
      path: `/cab/:entity(${EntitiesArray.join('|')})`,
      name: 'cab',
      component: CAB,
      meta: {
        auth: true
      }
    }
  ]
})

router.beforeEach((to) => {
  const authStore = useAuthStore()

  if (to.meta.auth && !authStore.user) return { name: 'login' }
  if (!to.meta.auth && authStore.user) return { name: 'home' }
  if (to.name === 'home' && authStore.entities.length === 1)
    return { name: 'cab', params: { entity: authStore.entities[0] } }
  if (!to.name || (to.name === 'cab' && !authStore.entities.includes(to.params.entity as Entity)))
    return { name: 'home' }
})

export default router
