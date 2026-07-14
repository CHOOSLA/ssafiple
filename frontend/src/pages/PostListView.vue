<template>
  <div class="board-container">
    <header class="board-header">
      <h1>자유게시판</h1>
      <p>서울 여행에 대한 질문이나 팁을 올려주세요.</p>
      <router-link to="/posts/new" class="btn btn-primary">글쓰기</router-link>
    </header>

    <main class="board-list">
      <!-- Loading state / Table layout placeholder -->
      <table class="post-table">
        <thead>
          <tr>
            <th>번호</th>
            <th>제목</th>
            <th>작성자</th>
            <th>작성일</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td colspan="4" class="empty-row">등록된 게시글이 없습니다.</td>
          </tr>
        </tbody>
      </table>
    </main>
  </div>
</template>

<script setup>
// Post list view logic
</script>

<style scoped>
.board-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 2rem;
}

.board-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  flex-wrap: wrap;
}

h1 {
  font-size: 2.2rem;
  color: #2c3e50;
  margin: 0;
}

.btn {
  display: inline-block;
  padding: 0.8rem 1.5rem;
  border-radius: 6px;
  text-decoration: none;
  font-weight: bold;
  cursor: pointer;
  border: none;
}

.btn-primary {
  background-color: #3498db;
  color: white;
  transition: background-color 0.2s;
}

.btn-primary:hover {
  background-color: #2980b9;
}

.post-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 1rem;
}

.post-table th, .post-table td {
  padding: 1rem;
  text-align: left;
  border-bottom: 1px solid #e2e8f0;
}

.post-table th {
  background-color: #f7fafc;
  color: #4a5568;
  font-weight: 600;
}

.empty-row {
  text-align: center;
  color: #a0aec0;
  padding: 3rem 0;
}
</style>
