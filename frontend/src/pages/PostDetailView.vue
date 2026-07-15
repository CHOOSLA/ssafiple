<template>
  <div class="page-shell">
    <header class="detail-header panel-card">
      <router-link to="/posts" class="back-link">← 목록으로</router-link>
      <div class="action-buttons">
        <router-link :to="`/posts/${postId}/edit`" class="btn btn-secondary">수정</router-link>
        <button class="btn btn-danger" @click="openDeleteModal">삭제</button>
      </div>
    </header>

    <article v-if="post" class="panel-card post-card">
      <div class="hero-media" :class="{ 'has-image': post.image_url }">
        <img v-if="post.image_url" :src="post.image_url" alt="첨부 이미지" />
        <div v-else class="hero-placeholder">PHOTO · {{ post.author }}</div>
      </div>
      <div class="post-body">
        <div class="post-head">
          <span class="pill">게시글</span>
          <h1>{{ post.title }}</h1>
          <div class="meta-info">
            <span>작성자 {{ post.author }}</span>
            <span>{{ formatDate(post.created_at) }}</span>
          </div>
        </div>
        <div class="body-text">
          <p>{{ post.content }}</p>
        </div>
      </div>
    </article>

    <div v-else class="panel-card status-card">게시글을 불러오는 중...</div>

    <section class="panel-card comment-card">
      <h3>댓글</h3>
      <form class="comment-form" @submit.prevent="submitComment">
        <input v-model="commentAuthor" class="form-control" placeholder="작성자" required />
        <input v-model="commentPassword" class="form-control" type="password" placeholder="비밀번호" required />
        <textarea v-model="commentContent" class="form-control" rows="3" placeholder="댓글을 입력하세요" required></textarea>
        <button type="submit" class="btn btn-primary">댓글 작성</button>
      </form>

      <div class="comment-list">
        <div v-for="comment in post?.comments || []" :key="comment.id" class="comment-item">
          <div class="comment-meta">
            <strong>{{ comment.author }}</strong>
            <span>{{ formatDate(comment.created_at) }}</span>
          </div>
          <p>{{ comment.content }}</p>
          <button class="btn btn-secondary" @click="deleteComment(comment.id)">삭제</button>
        </div>
        <p v-if="!(post?.comments || []).length" class="empty-comments">댓글이 없습니다.</p>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../api'
import { useModalStore } from '../stores/modal'

const route = useRoute()
const router = useRouter()
const modalStore = useModalStore()

const postId = computed(() => route.params.id)
const post = ref(null)
const commentAuthor = ref('')
const commentPassword = ref('')
const commentContent = ref('')

const formatDate = (value) => {
  if (!value) return '-'
  return new Date(value).toLocaleDateString('ko-KR')
}

const fetchPost = async () => {
  try {
    const { data } = await api.get(`/posts/${postId.value}`)
    post.value = data
  } catch (err) {
    alert('게시글을 불러오지 못했습니다.')
  }
}

const submitComment = async () => {
  try {
    await api.post(`/comments/?post_id=${postId.value}`, {
      content: commentContent.value,
      author: commentAuthor.value,
      password: commentPassword.value
    })
    commentAuthor.value = ''
    commentPassword.value = ''
    commentContent.value = ''
    await fetchPost()
  } catch (err) {
    alert('댓글 작성에 실패했습니다.')
  }
}

const deleteComment = async (commentId) => {
  const password = prompt('댓글 비밀번호를 입력하세요')
  if (!password) return
  try {
    await api.delete(`/comments/${commentId}?password_in=${encodeURIComponent(password)}`)
    await fetchPost()
  } catch (err) {
    alert('댓글 삭제에 실패했습니다.')
  }
}

const openDeleteModal = async () => {
  const password = prompt('게시글 비밀번호를 입력하세요')
  if (!password) return
  try {
    await api.delete(`/posts/${postId.value}?password_in=${encodeURIComponent(password)}`)
    router.push('/posts')
  } catch (err) {
    alert('게시글 삭제에 실패했습니다.')
  }
}

onMounted(fetchPost)
</script>

<style scoped>
.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.2rem;
  margin-bottom: 1rem;
  border-left: 5px solid var(--accent);
}

.back-link {
  color: var(--accent);
  font-weight: 700;
}

.action-buttons {
  display: flex;
  gap: 0.5rem;
}

.post-card,
.comment-card,
.status-card {
  padding: 1.25rem;
  margin-bottom: 1rem;
}

.post-card {
  border-left: 4px solid var(--accent);
  padding: 0;
  overflow: hidden;
}

.hero-media {
  position: relative;
  height: 158px;
  background: repeating-linear-gradient(45deg, #e6e4dd, #e6e4dd 11px, #f0efea 11px, #f0efea 22px);
}

.hero-media img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.hero-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: ui-monospace, SFMono-Regular, monospace;
  font-size: 11px;
  color: #aaa69d;
  letter-spacing: 0.04em;
}

.post-body {
  padding: 16px 18px 18px;
}

.post-head h1 {
  margin: 0.45rem 0 0.55rem;
  font-size: 1.7rem;
}

.pill {
  display: inline-flex;
  align-items: center;
  padding: 3px 9px;
  border-radius: 999px;
  background: #f6f5f2;
  color: var(--accent);
  font-size: 12px;
  font-weight: 700;
}

.meta-info {
  display: flex;
  gap: 1rem;
  color: var(--text-secondary);
  font-size: 0.92rem;
  padding-bottom: 0.8rem;
  border-bottom: 1px solid var(--border-color);
}

.body-text {
  line-height: 1.7;
  color: var(--text-primary);
  margin: 1rem 0 0;
  white-space: pre-wrap;
}

.comment-form {
  display: flex;
  flex-direction: column;
  gap: 0.7rem;
  margin-bottom: 1rem;
}

.comment-item {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: flex-start;
  padding: 0.9rem 0;
  border-top: 1px solid var(--border-color);
}

.comment-meta {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  color: var(--text-secondary);
}

.empty-comments {
  color: var(--text-secondary);
  padding: 0.8rem 0 0;
}

@media (max-width: 720px) {
  .detail-header,
  .comment-item {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
