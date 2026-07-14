<template>
  <div class="post-edit-container">
    <h1>{{ isEdit ? '게시글 수정' : '새 게시글 작성' }}</h1>
    <form @submit.prevent="handleSubmit" class="edit-form">
      <div class="form-group">
        <label for="title">제목</label>
        <input type="text" id="title" required placeholder="제목을 입력하세요" />
      </div>

      <div class="form-group">
        <label for="author">작성자</label>
        <input type="text" id="author" required :disabled="isEdit" placeholder="닉네임을 입력하세요" />
      </div>

      <div class="form-group">
        <label for="password">비밀번호</label>
        <input type="password" id="password" required placeholder="비밀번호를 입력하세요" />
      </div>

      <div class="form-group">
        <label for="content">내용</label>
        <textarea id="content" required rows="10" placeholder="내용을 입력하세요"></textarea>
      </div>

      <div class="form-actions">
        <button type="button" class="btn btn-cancel" @click="handleCancel">취소</button>
        <button type="submit" class="btn btn-submit">저장</button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';

const route = useRoute();
const router = useRouter();

const isEdit = computed(() => !!route.params.id);

const handleSubmit = () => {
  // Logic to save or update post
};

const handleCancel = () => {
  if (isEdit.value) {
    router.push(`/posts/${route.params.id}`);
  } else {
    router.push('/posts');
  }
};
</script>

<style scoped>
.post-edit-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
}

h1 {
  font-size: 2rem;
  color: #2c3e50;
  margin-bottom: 2rem;
}

.edit-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

label {
  font-weight: bold;
  color: #34495e;
}

input[type="text"], input[type="password"], textarea {
  padding: 0.8rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 1rem;
}

.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 1rem;
}

.btn {
  padding: 0.8rem 1.5rem;
  border-radius: 4px;
  border: none;
  font-weight: bold;
  cursor: pointer;
}

.btn-cancel {
  background-color: #ecf0f1;
  color: #7f8c8d;
}

.btn-submit {
  background-color: #2ecc71;
  color: white;
}
</style>
