<template>
  <div class="map-view-container">
    <h1>관광지 지도</h1>
    <p>서울의 매력적인 명소들을 카카오 지도로 탐색해 보세요.</p>
    
    <div class="map-wrapper">
      <div id="kakaomap" class="map-canvas"></div>
      <aside class="sidebar">
        <h3>관광지 리스트</h3>
        <ul class="location-list">
          <li class="empty-list">등록된 관광지가 없습니다.</li>
        </ul>
      </aside>
    </div>
  </div>
</template>

<script setup>
// Map logic with Kakao Map SDK
</script>

<style scoped>
.map-view-container {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

h1 {
  font-size: 2rem;
  color: #2c3e50;
  margin-bottom: 0.5rem;
}

p {
  color: #7f8c8d;
  margin-bottom: 2rem;
}

.map-wrapper {
  display: flex;
  gap: 1.5rem;
  height: 600px;
  background-color: #fff;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}

.map-canvas {
  flex: 3;
  background-color: #e5e5e5; /* Loading placeholder background */
}

.sidebar {
  flex: 1;
  background-color: #f8f9fa;
  padding: 1.5rem;
  border-left: 1px solid #e9ecef;
  display: flex;
  flex-direction: column;
}

.sidebar h3 {
  margin-top: 0;
  margin-bottom: 1rem;
  color: #343a40;
}

.location-list {
  list-style: none;
  padding: 0;
  margin: 0;
  overflow-y: auto;
  flex: 1;
}

.empty-list {
  color: #adb5bd;
  text-align: center;
  padding: 2rem 0;
}
</style>
