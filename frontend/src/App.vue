<template>
  <div class="app-shell">
    <nav class="navbar">
      <div class="container">
        <div class="nav-content">
          <router-link to="/" class="nav-brand">
            🎉 서울 축제
          </router-link>
          <ul class="nav-links">
            <li><router-link to="/">축제</router-link></li>
            <li><router-link to="/community">커뮤니티</router-link></li>
            <li><router-link to="/calendar">캘린더</router-link></li>
          </ul>
        </div>
      </div>
    </nav>

    <header class="hero">
      <div class="container">
        <h1>서울 축제와 관광을 한눈에</h1>
        <p>축제 목록부터 지도 기반 추천 정보까지, 서울 여행을 더 쉽게 계획해보세요.</p>
      </div>
    </header>
    <main class="container">
      <router-view />
    </main>
    <footer class="site-footer" />
    <ChatWidget />
  </div>
</template>

<script setup>
import ChatWidget from './components/ChatWidget.vue';
</script>

<style scoped>
.navbar {
  background-color: #ffffff;
  border-bottom: 1px solid #e5e7eb;
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.site-footer {
  height: 200px;
  flex: 0 0 200px;
  margin-top: 80px;
  background: #0b2b96;
}

.nav-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 64px;
}

.nav-brand {
  font-size: 18px;
  font-weight: 700;
  color: #222222;
  text-decoration: none;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: color 0.3s ease;
}

.nav-brand:hover {
  color: #00aeef;
}

.nav-links {
  display: flex;
  list-style: none;
  gap: 24px;
  margin: 0;
  padding: 0;
}

.nav-links a {
  color: #222222;
  text-decoration: none;
  font-size: 15px;
  font-weight: 600;
  padding: 8px 12px;
  border-radius: 6px;
  transition: all 0.3s ease;
}

.nav-links a:hover {
  color: #00aeef;
  background-color: #f0f9ff;
}

.nav-links a.router-link-active {
  color: #00aeef;
  background-color: #f0f9ff;
}

@media (max-width: 768px) {
  .nav-links {
    gap: 12px;
  }

  .nav-links a {
    font-size: 14px;
    padding: 6px 10px;
  }

  .nav-brand {
    font-size: 16px;
  }
}
</style>
