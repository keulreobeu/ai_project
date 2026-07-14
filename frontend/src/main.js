import { createApp } from 'vue';
import { createRouter, createWebHistory } from 'vue-router';
import App from './App.vue';
import FestivalListPage from './pages/FestivalListPage.vue';
import FestivalDetailPage from './pages/FestivalDetailPage.vue';
import './style.css';

const routes = [
  { path: '/', component: FestivalListPage },
  { path: '/festivals/:festivalId', component: FestivalDetailPage, props: true }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

createApp(App).use(router).mount('#app');
