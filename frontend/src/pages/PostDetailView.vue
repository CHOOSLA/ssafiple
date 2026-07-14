<template>
  <div class="post-detail-container">
    <header class="detail-header">
      <router-link to="/posts" class="back-link">&larr; 목록으로</router-link>
      <div class="action-buttons">
        <router-link :to="`/posts/${postId}/edit`" class="btn btn-secondary">수정</router-link>
        <button class="btn btn-danger" @click="openDeleteModal">삭제</button>
      </div>
    </header>

    <article class="post-content">
      <h1>게시글 상세 페이지</h1>
      <div class="meta-info">
        <span>작성자: 홍길동</span> | <span>작성일: 2026-07-14</span>
      </div>
      <div class="body-text">
        <p>게시글 내용 로딩 중...</p>
      </div>
    </article>

    <section class="comment-section">
      <h3>댓글</h3>
      <div class="comment-list">
        <p class="empty-comments">댓글이 없습니다.</p>
      </div>
    </section>
  </div>
</template>

<script setup>
import { useRoute } from 'vue-router';
const route = useRoute();
const postId = route.params.id;

const openDeleteModal = () => {
  // logic to show password verification modal before deleting
};
</script>

<style scoped>
.post-detail-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.back-link {
  color: #3498db;
  text-decoration: none;
}

.action-buttons {
  display: flex;
  gap: 0.5rem;
}

.btn {
  padding: 0.5rem 1rem;
  border-radius: 4px;
  border: none;
  font-weight: bold;
  cursor: pointer;
  text-decoration: none;
}

.btn-secondary {
  background-color: #95a5a6;
  color: white;
}

.btn-danger {
  background-color: #e74c3c;
  color: white;
}

.post-content h1 {
  font-size: 2rem;
  color: #2c3e50;
  margin-bottom: 0.5rem;
}

.meta-info {
  color: #7f8c8d;
  font-size: 0.9rem;
  margin-bottom: 2rem;
  border-bottom: 1px solid #ecf0f1;
  padding-bottom: 0.5rem;
}

.body-text {
  line-height: 1.6;
  color: #34495e;
  margin-bottom: 3rem;
}

.comment-section {
  border-top: 1px solid #ecf0f1;
  padding-top: 2rem;
}

.empty-comments {
  color: #95a5a6;
  font-style: italic;
}
</style>
