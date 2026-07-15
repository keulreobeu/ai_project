import { createApp } from 'vue';
import { createRouter, createWebHistory } from 'vue-router';
import App from './App.vue';
import FestivalListPage from './pages/FestivalListPage.vue';
import FestivalDetailPage from './pages/FestivalDetailPage.vue';
import OtherEventsPage from './pages/OtherEventsPage.vue';
import CommunityListPage from './pages/CommunityListPage.vue';
import CommunityDetailPage from './pages/CommunityDetailPage.vue';
import CommunityFormPage from './pages/CommunityFormPage.vue';
import './style.css';

const routes = [
  { path: '/', component: FestivalListPage },
  { path: '/events', component: OtherEventsPage },
  { path: '/festivals/:festivalId', component: FestivalDetailPage, props: true },
  { path: '/community', component: CommunityListPage },
  { path: '/community/new', component: CommunityFormPage },
  { path: '/community/:postId', component: CommunityDetailPage },
  { path: '/community/:postId/edit', component: CommunityFormPage }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

createApp(App).use(router).mount('#app');
