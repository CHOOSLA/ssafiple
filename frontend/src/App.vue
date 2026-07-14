<template>
  <div class="app-layout">
    <!-- 글로벌 상단 헤더 네비게이션 -->
    <header class="app-header">
      <div class="header-inner">
        <router-link to="/" class="logo">LocalHub Seoul</router-link>
        <nav class="nav-links">
          <router-link to="/" active-class="active">홈</router-link>
          <router-link to="/map" active-class="active">지도</router-link>
          <router-link to="/posts" active-class="active">게시판</router-link>
        </nav>
      </div>
    </header>

    <!-- 메인 컨텐츠 뷰 렌더링 -->
    <main class="app-content">
      <router-view />
    </main>

    <!-- 전역 AI 챗봇 위젯 (명세 6장 요구사항 준수) -->
    <div class="chatbot-widget" :class="{ open: isChatOpen }">
      <button class="chatbot-toggle-btn" @click="toggleChat">
        <span v-if="!isChatOpen">💬 AI 비서</span>
        <span v-else>❌ 닫기</span>
      </button>
      <div v-if="isChatOpen" class="chatbot-window">
        <header class="chat-header">
          <h4>AI 여행 비서</h4>
        </header>
        <div class="chat-messages">
          <div class="message system">안녕하세요! 서울 관광지나 여행에 대해 물어보세요.</div>
        </div>
        <div class="chat-input-area">
          <input type="text" placeholder="메시지를 입력하세요..." />
          <button>전송</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const isChatOpen = ref(false)
const toggleChat = () => {
  isChatOpen.value = !isChatOpen.value
}
</script>

<style>
/* CSS 초기화 및 전역 폰트/레이아웃 설정 */
body {
  margin: 0;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  background-color: #f7fafc;
  color: #2d3748;
}

.app-layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.app-header {
  background-color: #ffffff;
  border-bottom: 1px solid #e2e8f0;
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  font-size: 1.5rem;
  font-weight: 800;
  color: #3182ce;
  text-decoration: none;
}

.nav-links {
  display: flex;
  gap: 1.5rem;
}

.nav-links a {
  text-decoration: none;
  color: #4a5568;
  font-weight: 600;
  transition: color 0.2s;
}

.nav-links a:hover, .nav-links a.active {
  color: #3182ce;
}

.app-content {
  flex: 1;
}

/* AI 챗봇 위젯 스타일 */
.chatbot-widget {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  z-index: 999;
}

.chatbot-toggle-btn {
  background-color: #3182ce;
  color: white;
  border: none;
  padding: 0.8rem 1.5rem;
  border-radius: 50px;
  font-size: 1rem;
  font-weight: bold;
  cursor: pointer;
  box-shadow: 0 4px 15px rgba(49, 130, 206, 0.4);
  transition: transform 0.2s, background-color 0.2s;
}

.chatbot-toggle-btn:hover {
  background-color: #2b6cb0;
  transform: scale(1.05);
}

.chatbot-window {
  position: absolute;
  bottom: 3.5rem;
  right: 0;
  width: 350px;
  height: 450px;
  background-color: #ffffff;
  border-radius: 12px;
  box-shadow: 0 5px 25px rgba(0,0,0,0.15);
  border: 1px solid #e2e8f0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.chat-header {
  background-color: #3182ce;
  color: white;
  padding: 1rem;
}

.chat-header h4 {
  margin: 0;
}

.chat-messages {
  flex: 1;
  padding: 1rem;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  background-color: #f7fafc;
}

.message {
  padding: 0.8rem;
  border-radius: 8px;
  max-width: 80%;
  font-size: 0.9rem;
}

.message.system {
  background-color: #e2e8f0;
  color: #2d3748;
  align-self: flex-start;
}

.chat-input-area {
  padding: 0.8rem;
  border-top: 1px solid #e2e8f0;
  display: flex;
  gap: 0.5rem;
  background-color: #ffffff;
}

.chat-input-area input {
  flex: 1;
  padding: 0.5rem;
  border: 1px solid #cbd5e0;
  border-radius: 4px;
  outline: none;
}

.chat-input-area button {
  background-color: #3182ce;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
}
</style>
