<template>
  <div class="detail-shell">
    <header class="detail-header">
      <router-link :to="`/locations/${$route.params.location_id}/posts`" class="back-link">← 목록으로</router-link>
      <div class="action-buttons">
        <router-link :to="`/locations/${$route.params.location_id}/posts/${postId}/edit`" class="chip-btn secondary">수정</router-link>
        <button type="button" class="chip-btn danger" @click="openDeleteModal">삭제</button>
      </div>
    </header>

    <div class="detail-body">
      <div v-if="!post" class="status-message">게시글을 불러오는 중...</div>

      <template v-else>
        <img v-if="post.image_url" :src="resolvedImageUrl" class="post-image" alt="첨부 이미지" />

        <div class="post-content">
          <span class="pill">게시글</span>
          <h1 class="post-title">{{ post.title }}</h1>
          <div class="meta-info">
            <span>작성자 {{ post.author }}</span>
            <span>{{ formatDate(post.created_at) }}</span>
          </div>
          <p class="body-text">{{ post.content }}</p>
        </div>

        <div class="section-divider"></div>

        <div class="comment-section-title">댓글 <span>{{ post.comments?.length || 0 }}</span></div>

        <div class="comment-list">
          <div v-for="comment in post.comments || []" :key="comment.id" class="comment-item">
            <div class="comment-meta">
              <strong>{{ comment.author }}</strong>
              <span>{{ formatDate(comment.created_at) }}</span>
              <button type="button" class="comment-delete" @click="deleteComment(comment.id)">삭제</button>
            </div>
            <p class="comment-content">{{ comment.content }}</p>
          </div>
          <p v-if="!(post.comments || []).length" class="empty-comments">첫 댓글을 남겨보세요.</p>
        </div>
      </template>
    </div>

    <form class="comment-form" @submit.prevent="submitComment">
      <div class="comment-form-row">
        <input v-model="commentAuthor" class="comment-input small" placeholder="작성자" required />
        <input v-model="commentPassword" class="comment-input small" type="password" placeholder="비밀번호" required />
      </div>
      <div class="comment-form-row">
        <input v-model="commentContent" class="comment-input" placeholder="익명으로 댓글 남기기" required />
        <button type="submit" class="send-btn">등록</button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../api'

const route = useRoute()
const router = useRouter()

const postId = computed(() => route.params.id)
const post = ref(null)
const commentAuthor = ref('')
const commentPassword = ref('')
const commentContent = ref('')

const formatDate = (value) => {
  if (!value) return '-'
  return new Date(value).toLocaleDateString('ko-KR')
}

// 백엔드가 /uploads/... 상대경로를 반환하므로, 프론트 origin이 아닌 백엔드 origin 기준으로 풀어줘야 함
const resolvedImageUrl = computed(() => {
  const url = post.value?.image_url
  if (!url) return ''
  if (/^https?:\/\//.test(url)) return url
  return `${import.meta.env.VITE_API_BASE_URL}${url}`
})

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
    router.push(`/locations/${route.params.location_id}/posts`)
  } catch (err) {
    alert('게시글 삭제에 실패했습니다.')
  }
}

onMounted(fetchPost)
</script>

<style scoped>
.detail-shell {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 0;
  flex: 1;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.98), rgba(248, 245, 239, 0.96));
}

.detail-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-bottom: 1px solid var(--border-color);
  flex: none;
}

.back-link {
  color: var(--accent);
  font-weight: 700;
  font-size: 13.5px;
}

.action-buttons {
  display: flex;
  gap: 0.5rem;
}

.chip-btn {
  border: none;
  border-radius: 8px;
  padding: 7px 13px;
  font-weight: 700;
  font-size: 13px;
  cursor: pointer;
}

.chip-btn.secondary {
  background: #f2f1ed;
  color: var(--text-secondary);
}

.chip-btn.danger {
  background: #ef6a5f;
  color: #fff;
}

.detail-body {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
}

.status-message {
  padding: 2rem 1rem;
  text-align: center;
  color: var(--text-secondary);
}

.post-image {
  display: block;
  width: 100%;
  max-height: 260px;
  object-fit: cover;
}

.post-content {
  padding: 18px 18px 6px;
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

.post-title {
  margin: 10px 0 0;
  font-size: 1.4rem;
  line-height: 1.4;
  color: var(--text-primary);
}

.meta-info {
  display: flex;
  gap: 10px;
  color: var(--text-muted);
  font-size: 12px;
  margin-top: 10px;
}

.body-text {
  font-size: 14.5px;
  line-height: 1.75;
  color: #333;
  margin: 16px 0 0;
  white-space: pre-wrap;
}

.section-divider {
  height: 8px;
  background: #f6f5f2;
  margin-top: 14px;
}

.comment-section-title {
  padding: 15px 18px 6px;
  font-weight: 700;
  font-size: 14px;
  color: var(--text-primary);
}

.comment-section-title span {
  color: var(--accent);
}

.comment-item {
  padding: 12px 18px;
  border-bottom: 1px solid #f4f2ee;
}

.comment-meta {
  display: flex;
  align-items: baseline;
  gap: 8px;
  font-size: 12.5px;
  color: var(--text-secondary);
}

.comment-meta strong {
  font-weight: 700;
}

.comment-meta span {
  color: #c2bfb7;
  font-size: 11.5px;
}

.comment-delete {
  margin-left: auto;
  background: none;
  border: none;
  color: var(--text-muted);
  font-size: 11.5px;
  cursor: pointer;
  padding: 0;
}

.comment-content {
  font-size: 13.5px;
  line-height: 1.6;
  margin: 5px 0 0;
  color: #2a2825;
}

.empty-comments {
  padding: 26px 18px;
  color: var(--text-muted);
  font-size: 13px;
  text-align: center;
}

.comment-form {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 12px;
  border-top: 1px solid var(--border-color);
  background: #fff;
  flex: none;
}

.comment-form-row {
  display: flex;
  gap: 8px;
}

.comment-input {
  flex: 1;
  min-width: 0;
  border: 1px solid #e3e0d9;
  border-radius: 11px;
  padding: 11px 13px;
  font-size: 13.5px;
  outline: none;
}

.comment-input.small {
  flex: none;
  width: 130px;
}

.send-btn {
  background: var(--accent);
  color: #fff;
  border: none;
  border-radius: 11px;
  padding: 0 17px;
  font-weight: 700;
  font-size: 13.5px;
  cursor: pointer;
  flex: none;
}

@media (max-width: 480px) {
  .comment-input.small {
    width: auto;
  }
}
</style>
