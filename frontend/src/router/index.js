import { createRouter, createWebHistory } from 'vue-router'
import PostListView from '../pages/PostListView.vue'
import PostDetailView from '../pages/PostDetailView.vue'
import PostEditView from '../pages/PostEditView.vue'
import MapView from '../pages/MapView.vue'
import ExampleView from '../pages/ExampleView.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: MapView
  },
  {
    path: '/locations/:location_id/posts',
    name: 'PostList',
    component: PostListView
  },
  {
    path: '/locations/:location_id/posts/new',
    name: 'PostCreate',
    component: PostEditView
  },
  {
    path: '/locations/:location_id/posts/:id',
    name: 'PostDetail',
    component: PostDetailView
  },
  {
    path: '/locations/:location_id/posts/:id/edit',
    name: 'PostEdit',
    component: PostEditView
  },
  {
    path: '/map',
    name: 'Map',
    component: MapView
  },
  {
    path: '/example',
    name: 'Example',
    component: ExampleView
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
