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
    <footer class="site-footer">
      <div class="footer-content">
        <div class="footer-brand">
          <strong>Seoul Festival Explorer</strong>
          <p>서울의 축제와 행사를 한눈에 만나보세요.</p>
          <p>SSAFY 교육 과정에서 제작한 비영리 프로젝트입니다.</p>
        </div>

        <div class="footer-contact">
          <strong>SSAFY 서울 캠퍼스</strong>
          <p>서울특별시 강남구 테헤란로 212</p>
          <p>대표전화 02-3429-5100 · 팩스 02-xxxx-xxxx</p>
          <p>ssafy@ssafy.com</p>
        </div>

        <div class="footer-data">
          <strong>데이터 및 저작권 안내</strong>
          <p>
            관광정보 및 이미지는
            <a href="https://www.data.go.kr/data/15101578/openapi.do" target="_blank" rel="noopener noreferrer">한국관광공사 TourAPI 4.0</a>을 활용했습니다.
          </p>
          <p>
            지도 데이터 ©
            <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener noreferrer">OpenStreetMap contributors</a>
            · 데이터 기준일 2026-07-16
          </p>
          <p>AI 답변은 공식 관광정보가 아닌 참고용 정보이며, 정확한 내용은 행사 공식 채널에서 확인해 주세요.</p>
        </div>

        <div class="footer-bottom">
          <span>이용약관 · 개인정보 처리방침 준비 중</span>
          <span>© 2026 Seoul Festival Explorer. All rights reserved.</span>
        </div>
      </div>
    </footer>
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
  color: #ffffff;
}

.footer-content {
  width: min(1200px, 100%);
  height: 100%;
  margin: 0 auto;
  padding: 24px;
  display: grid;
  grid-template-columns: 1fr 1fr 1.8fr;
  gap: 28px;
  align-content: center;
  font-size: 12px;
  line-height: 1.5;
}

.footer-content strong {
  display: block;
  margin-bottom: 6px;
  font-size: 14px;
}

.footer-content p {
  margin: 2px 0;
  color: rgba(255, 255, 255, 0.78);
}

.footer-content a {
  color: #ffffff;
  text-decoration: underline;
  text-underline-offset: 2px;
}

.footer-bottom {
  grid-column: 1 / -1;
  display: flex;
  justify-content: space-between;
  padding-top: 10px;
  border-top: 1px solid rgba(255, 255, 255, 0.22);
  color: rgba(255, 255, 255, 0.72);
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
  background: transparent;
}

.nav-links a.router-link-active {
  color: #00aeef;
  background: transparent;
  font-weight: 800;
}

@media (max-width: 768px) {
  .site-footer {
    height: auto;
    flex-basis: auto;
  }

  .footer-content {
    grid-template-columns: 1fr;
    padding: 28px 24px;
  }

  .footer-bottom {
    grid-column: auto;
    flex-direction: column;
    gap: 4px;
  }

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
