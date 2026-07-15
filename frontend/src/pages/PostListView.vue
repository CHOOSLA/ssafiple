<template>
  <div class="page-shell">
    <section class="panel-card app-shell">
      <header class="panel-header">
        <div class="brand-row">
          <span class="brand-badge">L</span>
          <div>
            <div class="brand-title">LocalHub</div>
            <div class="brand-subtitle">서울 여행 정보 커뮤니티</div>
          </div>
        </div>
        <div class="search-bar">
          <svg width="16" height="16" viewBox="0 0 16 16" aria-hidden="true">
            <circle cx="7" cy="7" r="5" fill="none" stroke="#9a968f" stroke-width="2" />
            <line x1="10.8" y1="10.8" x2="15" y2="15" stroke="#9a968f" stroke-width="2" stroke-linecap="round" />
          </svg>
          <input v-model="searchQuery" placeholder="게시글 제목/내용 검색" />
        </div>
      </header>

      <div class="panel-body">
        <div class="section-label">
          게시글 <span>{{ filteredPosts.length }}</span>개 · 최신 순
        </div>

        <div class="action-row">
          <router-link to="/posts/new" class="btn btn-primary">글쓰기</router-link>
        </div>

        <div v-if="loading" class="status-message">불러오는 중...</div>
        <div v-else-if="error" class="status-message error">{{ error }}</div>
        <div v-else class="post-list">
          <article v-for="post in filteredPosts" :key="post.id" class="post-item">
            <div class="thumb-card">
              <span class="thumb-pill">{{ post.image_url ? 'PHOTO' : 'POST' }}</span>
              <span class="thumb-label">{{ post.image_url ? 'IMAGE' : 'TEXT' }}</span>
            </div>
            <div class="post-main">
              <router-link :to="`/posts/${post.id}`" class="post-title">{{ post.title }}</router-link>
              <p class="post-preview">{{ post.content }}</p>
              <div class="post-meta">
                <span>{{ post.author }}</span>
                <span>{{ formatDate(post.created_at) }}</span>
                <span>댓글 {{ post.comments?.length || 0 }}</span>
              </div>
            </div>
          </article>
          <div v-if="filteredPosts.length === 0" class="empty-row">등록된 게시글이 없습니다.</div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import api from '../api'

const posts = ref([])
const loading = ref(false)
const error = ref('')
const searchQuery = ref('')

const filteredPosts = computed(() => {
  const query = searchQuery.value.trim().toLowerCase()
  if (!query) return posts.value

  return posts.value.filter((post) => {
    const target = `${post.title} ${post.content} ${post.author}`.toLowerCase()
    return target.includes(query)
  })
})

const formatDate = (value) => {
  if (!value) return '-'
  return new Date(value).toLocaleDateString('ko-KR')
}

const fetchPosts = async () => {
  loading.value = true
  error.value = ''
  try {
    const { data } = await api.get('/posts/')
    posts.value = data
  } catch (err) {
    error.value = '게시글을 불러오지 못했습니다.'
  } finally {
    loading.value = false
  }
}

onMounted(fetchPosts)
</script>

<style scoped>
.app-shell {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 0;
  padding: 0;
  overflow: hidden;
}

.panel-header {
  padding: 16px 18px 12px;
  border-bottom: 1px solid #eceae6;
  flex: none;
}

.brand-row {
  display: flex;
  align-items: center;
  gap: 9px;
}

.brand-badge {
  width: 28px;
  height: 28px;
  border-radius: 9px;
  background: var(--accent);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 900;
}

.brand-title {
  font-weight: 800;
  font-size: 16px;
}

.brand-subtitle {
  font-size: 11px;
  color: var(--text-secondary);
  margin-top: 3px;
}

.search-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #f4f2ee;
  border-radius: 11px;
  padding: 10px 12px;
  margin-top: 13px;
}

.search-bar input {
  border: none;
  background: transparent;
  outline: none;
  flex: 1;
  min-width: 0;
  font-size: 14px;
  color: var(--text-primary);
}

.panel-body {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding: 14px 16px 10px;
}

.section-label {
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 10px;
}

.section-label span {
  color: var(--text-primary);
  font-weight: 700;
}

.action-row {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 10px;
}

.post-list {
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
}

.post-item {
  display: flex;
  gap: 14px;
  width: 100%;
  padding: 16px;
  border: 1px solid rgba(240, 238, 233, 0.95);
  border-radius: 18px;
  background: linear-gradient(135deg, #fffdfa 0%, #fcf7f0 100%);
  box-shadow: 0 10px 24px rgba(28, 27, 26, 0.04);
}

.thumb-card {
  width: 116px;
  min-width: 116px;
  height: 116px;
  border-radius: 13px;
  background: repeating-linear-gradient(45deg, #e9e7e0, #e9e7e0 9px, #f2f1ec 9px, #f2f1ec 18px);
  border: 1px solid #ece9e2;
  display: flex;
  align-items: flex-end;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.thumb-pill {
  position: absolute;
  top: 9px;
  left: 9px;
  font-size: 11px;
  font-weight: 700;
  color: #fff;
  background: var(--accent);
  padding: 3px 9px;
  border-radius: 16px;
}

.thumb-label {
  margin-bottom: 10px;
  font-family: ui-monospace, SFMono-Regular, monospace;
  font-size: 10px;
  color: #aaa69d;
  letter-spacing: 0.04em;
}

.post-main {
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.post-title {
  display: block;
  font-size: 1.02rem;
  font-weight: 800;
  color: var(--text-primary);
  margin-bottom: 0.35rem;
}

.post-preview {
  margin: 0;
  color: var(--text-secondary);
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.post-meta {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  color: var(--text-secondary);
  font-size: 0.92rem;
  margin-top: auto;
  padding-top: 10px;
}

.status-message,
.empty-row {
  padding: 2rem 1rem;
  text-align: center;
  color: var(--text-secondary);
}

.status-message.error {
  color: #d24b3d;
}

@media (max-width: 720px) {
  .post-item {
    flex-direction: column;
  }

  .thumb-card {
    width: 100%;
    min-width: 0;
  }
}
</style>
