import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('../views/Home.vue'),
    },
    {
      path: '/fulltext',
      name: 'fulltext',
      component: () => import('../views/FullTextSearch.vue'),
    },
    {
      path: '/semantic',
      name: 'semantic',
      component: () => import('../views/SemanticSearch.vue'),
    },
    {
      path: '/llm',
      name: 'llm',
      component: () => import('../views/LLMQA.vue'),
    },
  ],
})

export default router
