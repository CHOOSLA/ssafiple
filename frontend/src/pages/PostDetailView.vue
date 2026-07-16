<template>
  <div class="detail-shell">
    <header class="detail-header">
      <router-link :to="`/locations/${$route.params.location_id}/posts`" class="back-link">{{ $t('board.backToList') }}</router-link>
      <div class="action-buttons">
        <router-link :to="`/locations/${$route.params.location_id}/posts/${postId}/edit`" class="chip-btn secondary">{{ $t('common.actions.edit') }}</router-link>
        <button type="button" class="chip-btn danger" @click="openDeleteModal">{{ $t('common.actions.delete') }}</button>
      </div>
    </header>

    <div class="detail-body">
      <div v-if="!post" class="status-message">{{ $t('board.loadingPost') }}</div>

      <template v-else>
        <div class="post-content">
          <span class="pill">{{ $t('board.postLabel') }}</span>
          <h1 class="post-title">{{ post.title }}</h1>
          <div class="meta-info">
            <span>{{ $t('board.authorLabel', { author: post.author }) }}</span>
            <span>{{ formatDate(post.created_at) }}</span>
          </div>

          <div v-if="galleryImages.length" class="post-gallery">
            <div class="gallery-track" ref="galleryTrackRef" @scroll="onGalleryScroll">
              <img
                v-for="(img, idx) in galleryImages"
                :key="idx"
                :src="img"
                class="gallery-image"
                :alt="$t('board.attachedImageAlt')"
              />
            </div>
            <div v-if="galleryImages.length > 1" class="gallery-counter">{{ galleryIndex + 1 }} / {{ galleryImages.length }}</div>
          </div>

          <p class="body-text">{{ post.content }}</p>
        </div>

        <div class="section-divider"></div>

        <i18n-t keypath="board.commentsTitle" tag="div" class="comment-section-title">
          <template #count><span>{{ post.comments?.length || 0 }}</span></template>
        </i18n-t>

        <div class="comment-list">
          <div v-for="comment in post.comments || []" :key="comment.id" class="comment-item">
            <div class="comment-meta">
              <strong>{{ comment.author }}</strong>
              <span>{{ formatDate(comment.created_at) }}</span>
              <button type="button" class="comment-delete" @click="deleteComment(comment.id)">{{ $t('common.actions.delete') }}</button>
            </div>
            <p class="comment-content">{{ comment.content }}</p>
          </div>
          <p v-if="!(post.comments || []).length" class="empty-comments">{{ $t('board.noComments') }}</p>
        </div>
      </template>
    </div>

    <form class="comment-form" @submit.prevent="submitComment">
      <div class="comment-form-row">
        <input v-model="commentAuthor" class="comment-input small" :placeholder="$t('board.authorPlaceholder')" required />
        <input v-model="commentPassword" class="comment-input small" type="password" :placeholder="$t('common.passwordPlaceholder')" required />
      </div>
      <div class="comment-form-row">
        <input v-model="commentContent" class="comment-input" :placeholder="$t('board.commentPlaceholder')" required />
        <button type="submit" class="send-btn">{{ $t('common.actions.submit') }}</button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import api from '../api'

const route = useRoute()
const router = useRouter()
const { t, locale } = useI18n()

const postId = computed(() => route.params.id)
const post = ref(null)
const commentAuthor = ref('')
const commentPassword = ref('')
const commentContent = ref('')

const formatDate = (value) => {
  if (!value) return '-'
  return new Date(value).toLocaleDateString(locale.value === 'en' ? 'en-US' : 'ko-KR')
}

// 백엔드가 /uploads/... 상대경로를 반환하므로, 프론트 origin이 아닌 백엔드 origin 기준으로 풀어줘야 함
const resolveUrl = (url) => {
  if (!url) return ''
  if (/^https?:\/\//.test(url)) return url
  return `${import.meta.env.VITE_API_BASE_URL}${url}`
}

// post.images(다중 이미지)가 있으면 그걸 쓰고, 없으면 기존 단일 image_url로 폴백
const galleryImages = computed(() => {
  const imgs = post.value?.images
  if (Array.isArray(imgs) && imgs.length) {
    return imgs.map((img) => resolveUrl(img.image_url))
  }
  return post.value?.image_url ? [resolveUrl(post.value.image_url)] : []
})

const galleryTrackRef = ref(null)
const galleryIndex = ref(0)

const onGalleryScroll = () => {
  const el = galleryTrackRef.value
  if (!el || !el.clientWidth) return
  galleryIndex.value = Math.round(el.scrollLeft / el.clientWidth)
}

const fetchPost = async () => {
  try {
    const { data } = await api.get(`/posts/${postId.value}`)
    post.value = data
  } catch (err) {
    alert(t('board.fetchPostError'))
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
    alert(t('board.commentCreateError'))
  }
}

const deleteComment = async (commentId) => {
  const password = prompt(t('board.commentPasswordPrompt'))
  if (!password) return
  try {
    await api.delete(`/comments/${commentId}?password_in=${encodeURIComponent(password)}`)
    await fetchPost()
  } catch (err) {
    alert(t('board.commentDeleteError'))
  }
}

const openDeleteModal = async () => {
  const password = prompt(t('board.postPasswordPrompt'))
  if (!password) return
  try {
    await api.delete(`/posts/${postId.value}?password_in=${encodeURIComponent(password)}`)
    router.push(`/locations/${route.params.location_id}/posts`)
  } catch (err) {
    alert(t('board.postDeleteError'))
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

.post-gallery {
  position: relative;
  margin-top: 14px;
  border-radius: 12px;
  overflow: hidden;
}

.gallery-track {
  display: flex;
  overflow-x: auto;
  scroll-snap-type: x mandatory;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
}

.gallery-track::-webkit-scrollbar {
  display: none;
}

.gallery-image {
  flex: 0 0 100%;
  scroll-snap-align: start;
  width: 100%;
  height: 220px;
  object-fit: cover;
}

.gallery-counter {
  position: absolute;
  right: 10px;
  bottom: 10px;
  background: rgba(0, 0, 0, 0.55);
  color: #fff;
  font-size: 11px;
  font-weight: 600;
  padding: 3px 9px;
  border-radius: 999px;
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
