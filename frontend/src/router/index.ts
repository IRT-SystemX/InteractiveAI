import { createRouter, createWebHistory } from 'vue-router'

import { useAuthStore } from '@/stores/auth'
import { EntitiesArray, type Entity } from '@/types/entities'
import HomeView from '@/views/HomeView.vue'
import LoginView from '@/views/LoginView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
      meta: {
        auth: true
      }
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView,
      meta: {
        auth: false
      }
    },
    {
      path: `/cab/:entity(${EntitiesArray.join('|')})`,
      name: 'cab',
      // route level code-splitting
      // this generates a separate chunk (About.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () => import('../views/CABView.vue'),
      meta: {
        auth: true
      }
    }
  ]
})

router.beforeEach((to) => {
  const authStore = useAuthStore()

  if (to.meta.auth && !authStore.user) return { name: 'login' }
  if (to.name === 'home' && authStore.entities.length === 1)
    return { name: 'cab', params: { entity: authStore.entities[0] } }
  if (!to.name || (to.name === 'cab' && !authStore.entities.includes(to.params.entity as Entity)))
    return { name: 'home' }
})

export default router
