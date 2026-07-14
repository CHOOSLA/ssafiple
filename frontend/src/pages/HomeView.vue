<template>
  <div class="home-container">
    <header class="hero-section">
      <h1>LocalHub Seoul</h1>
      <p>서울의 매력적인 관광지 정보를 찾고, 다른 여행자들과 이야기를 나누어보세요.</p>
    </header>
    <main class="menu-grid">
      <router-link to="/map" class="menu-card map-card">
        <div class="card-content">
          <h2>관광지 지도</h2>
          <p>카카오 지도로 서울의 명소를 찾아보세요.</p>
        </div>
      </router-link>
      <router-link to="/posts" class="menu-card board-card">
        <div class="card-content">
          <h2>자유게시판</h2>
          <p>여행 후기와 팁을 공유하고 소통해 보세요.</p>
        </div>
      </router-link>
    </main>
  </div>
</template>

<script setup>
// Home view base logic
</script>

<style scoped>
.home-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  text-align: center;
}

.hero-section {
  margin-bottom: 4rem;
}

h1 {
  font-size: 3rem;
  color: #2c3e50;
  margin-bottom: 1rem;
}

p {
  font-size: 1.2rem;
  color: #7f8c8d;
}

.menu-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
  justify-content: center;
}

.menu-card {
  display: block;
  text-decoration: none;
  color: inherit;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  height: 250px;
  position: relative;
  background-color: #ffffff;
}

.menu-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.card-content {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 2rem;
  background: linear-gradient(transparent, rgba(0, 0, 0, 0.8));
  color: #ffffff;
  text-align: left;
}

.map-card {
  background-image: linear-gradient(135deg, #70a1ff, #1e90ff);
}

.board-card {
  background-image: linear-gradient(135deg, #ff6b81, #ff4757);
}

.card-content h2 {
  margin: 0 0 0.5rem 0;
  font-size: 1.8rem;
}

.card-content p {
  margin: 0;
  font-size: 1rem;
  color: rgba(255, 255, 255, 0.8);
}
</style>
