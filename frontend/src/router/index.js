import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../pages/HomeView.vue'
import PostListView from '../pages/PostListView.vue'
import PostDetailView from '../pages/PostDetailView.vue'
import PostEditView from '../pages/PostEditView.vue'
import MapView from '../pages/MapView.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: HomeView
  },
  {
    path: '/posts',
    name: 'PostList',
    component: PostListView
  },
  {
    path: '/posts/new',
    name: 'PostCreate',
    component: PostEditView
  },
  {
    path: '/posts/:id',
    name: 'PostDetail',
    component: PostDetailView
  },
  {
    path: '/posts/:id/edit',
    name: 'PostEdit',
    component: PostEditView
  },
  {
    path: '/map',
    name: 'Map',
    component: MapView
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
