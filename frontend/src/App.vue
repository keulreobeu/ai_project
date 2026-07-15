<template>
  <div class="app-shell">
    <header class="hero">
      <div class="container">
        <h1>서울 축제와 관광을 한눈에</h1>
        <p>축제 목록부터 지도 기반 추천 정보까지, 서울 여행을 더 쉽게 계획해보세요.</p>
        <nav class="main-nav" aria-label="주요 메뉴">
          <router-link to="/">축제</router-link>
          <router-link to="/events">행사</router-link>
          <router-link to="/community">커뮤니티</router-link>
        </nav>
      </div>
    </header>
    <main class="container">
      <router-view />
    </main>
    <ChatWidget />
  </div>
</template>

<script setup>
import ChatWidget from './components/ChatWidget.vue';
</script>
