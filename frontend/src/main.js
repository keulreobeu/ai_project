import { createApp } from 'vue';
import { createRouter, createWebHistory } from 'vue-router';
import App from './App.vue';
import FestivalListPage from './pages/FestivalListPage.vue';
import FestivalDetailPage from './pages/FestivalDetailPage.vue';
import FestivalCalendarPage from './pages/FestivalCalendarPage.vue';
import CommunityPage from './pages/CommunityPage.vue';
import OtherEventsPage from './pages/OtherEventsPage.vue';
/*import CommunityListPage from './pages/CommunityListPage.vue';
import CommunityDetailPage from './pages/CommunityDetailPage.vue';
import CommunityFormPage from './pages/CommunityFormPage.vue';*/
import './style.css';

const routes = [
  { path: '/', component: FestivalListPage },

  { path: '/community', component: CommunityPage },
  { path: '/events', component: OtherEventsPage },
  { path: '/calendar', component: FestivalCalendarPage },
  { path: '/festivals/:festivalId', component: FestivalDetailPage, props: true },
  
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

createApp(App).use(router).mount('#app');
