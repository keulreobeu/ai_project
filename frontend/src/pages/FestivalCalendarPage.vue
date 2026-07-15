<template>
  <section class="calendar-page">
    <div class="calendar-heading">
      <div>
        <p class="calendar-eyebrow">서울 행사 일정</p>
        <h2 class="page-title">축제 캘린더</h2>
        <p class="calendar-description">날짜를 선택해 해당 날짜에 진행되는 축제를 확인해 보세요.</p>
      </div>
      <button class="view-toggle" type="button" @click="toggleView">
        {{ viewMode === 'calendar' ? '달별로 보기' : '캘린더로 보기' }}
      </button>
    </div>

    <div class="month-toolbar" aria-label="캘린더 월 이동">
      <button type="button" aria-label="이전 달" @click="changeMonth(-1)">‹</button>
      <div class="month-title-wrap">
        <strong>{{ monthTitle }}</strong>
        <span>{{ festivals.length }}개의 일정</span>
      </div>
      <button type="button" aria-label="다음 달" @click="changeMonth(1)">›</button>
      <button class="today-button" type="button" @click="goToday">오늘</button>
    </div>

    <div v-if="loading" class="state-card" role="status">행사 일정을 불러오는 중입니다...</div>
    <div v-else-if="error" class="state-card error" role="alert">
      행사 일정을 불러오지 못했습니다.
      <button type="button" @click="loadFestivals">다시 시도</button>
    </div>

    <template v-else-if="viewMode === 'calendar'">
      <div class="calendar-shell">
        <div class="weekday-row" aria-hidden="true">
          <span v-for="weekday in weekdays" :key="weekday">{{ weekday }}</span>
        </div>
        <div class="calendar-grid">
          <article
            v-for="day in calendarDays"
            :key="day.iso"
            class="calendar-cell"
            :class="{
              muted: !day.inCurrentMonth,
              today: day.isToday,
              selected: selectedDate === day.iso,
            }"
          >
            <button
              class="calendar-date-button"
              type="button"
              :disabled="!day.inCurrentMonth"
              :aria-label="`${day.iso} 선택`"
              @click="selectDate(day)"
            >
              {{ day.day }}
            </button>
            <div v-if="day.inCurrentMonth" class="calendar-cell-events">
              <router-link
                v-for="event in boundaryEventsForDay(day).slice(0, 2)"
                :key="`${event.festival.id}-${event.boundary}`"
                class="calendar-event-pill"
                :class="`boundary-${event.boundary}`"
                :to="`/festivals/${event.festival.id}`"
                :title="`${boundaryLabel(event.boundary)}: ${event.festival.title}`"
              >
                <span>{{ boundaryLabel(event.boundary) }}</span>
                {{ event.festival.title }}
              </router-link>
              <button
                v-if="boundaryEventsForDay(day).length > 2"
                class="calendar-more"
                type="button"
                @click="selectDate(day)"
              >
                +{{ boundaryEventsForDay(day).length - 2 }}개
              </button>
            </div>
          </article>
        </div>
      </div>

      <section class="selected-day-panel" aria-live="polite">
        <div class="selected-day-heading">
          <div>
            <span>선택한 날짜</span>
            <h3>{{ selectedDateLabel }}</h3>
          </div>
          <strong>{{ selectedFestivals.length }}개 행사</strong>
        </div>
        <p v-if="selectedFestivals.length === 0" class="empty-message">이 날짜에 진행되는 행사가 없습니다.</p>
        <div v-else class="selected-festival-list">
          <router-link
            v-for="festival in selectedFestivals"
            :key="festival.id"
            class="selected-festival-card"
            :to="`/festivals/${festival.id}`"
          >
            <img
              v-if="festival.thumbnail_url || festival.image_url"
              :src="festival.thumbnail_url || festival.image_url"
              :alt="festival.title"
            />
            <div>
              <strong>{{ festival.title }}</strong>
              <span>{{ formatFestivalPeriod(festival.event_start_date, festival.event_end_date) }}</span>
              <small>{{ festival.address || '장소 정보 없음' }}</small>
            </div>
          </router-link>
        </div>
      </section>
    </template>

    <section v-else class="monthly-list" aria-live="polite">
      <div class="monthly-list-heading">
        <h3>{{ monthTitle }} 행사</h3>
        <span>해당 월과 일정이 겹치는 행사를 보여줍니다.</span>
      </div>
      <p v-if="festivals.length === 0" class="state-card">이 달에 등록된 행사가 없습니다.</p>
      <div v-else class="monthly-event-grid">
        <router-link
          v-for="festival in sortedMonthlyFestivals"
          :key="festival.id"
          class="monthly-event-card"
          :to="`/festivals/${festival.id}`"
        >
          <img
            v-if="festival.thumbnail_url || festival.image_url"
            :src="festival.thumbnail_url || festival.image_url"
            :alt="festival.title"
          />
          <div>
            <span class="monthly-period">{{ formatFestivalPeriod(festival.event_start_date, festival.event_end_date) }}</span>
            <h3>{{ festival.title }}</h3>
            <p>{{ festival.address || '장소 정보 없음' }}</p>
          </div>
        </router-link>
      </div>
    </section>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue';
import { fetchCalendarFestivals } from '../api/festivals';
import {
  buildMonthGrid,
  festivalBoundaryOn,
  festivalOccursOn,
  formatFestivalPeriod,
  sortFestivalsByNearestBoundary,
  toIsoDate,
} from '../utils/calendar';

const today = new Date();
const todayIso = toIsoDate(today);
const currentYear = ref(today.getFullYear());
const currentMonth = ref(today.getMonth() + 1);
const selectedDate = ref(todayIso);
const viewMode = ref('calendar');
const festivals = ref([]);
const loading = ref(false);
const error = ref(false);
const weekdays = ['일', '월', '화', '수', '목', '금', '토'];

const calendarDays = computed(() => buildMonthGrid(currentYear.value, currentMonth.value, today));
const monthTitle = computed(() => `${currentYear.value}년 ${currentMonth.value}월`);
const selectedFestivals = computed(() => sortFestivalsByNearestBoundary(
  festivals.value.filter((festival) => festivalOccursOn(festival, selectedDate.value)),
  todayIso,
));
const sortedMonthlyFestivals = computed(() => sortFestivalsByNearestBoundary(
  festivals.value,
  todayIso,
));
const selectedDateLabel = computed(() => {
  const [year, month, day] = selectedDate.value.split('-').map(Number);
  return new Intl.DateTimeFormat('ko-KR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    weekday: 'short',
  }).format(new Date(year, month - 1, day));
});

const boundaryEventsForDay = (day) => (
  day.inCurrentMonth
    ? festivals.value
      .map((festival) => ({ festival, boundary: festivalBoundaryOn(festival, day.iso) }))
      .filter((event) => event.boundary)
    : []
);

const boundaryLabel = (boundary) => ({
  start: '시작',
  end: '종료',
  'start-end': '시작·종료',
}[boundary] || '');

const selectDate = (day) => {
  if (day.inCurrentMonth) selectedDate.value = day.iso;
};

const setSelectedDateForMonth = () => {
  const isCurrentMonth = currentYear.value === today.getFullYear()
    && currentMonth.value === today.getMonth() + 1;
  selectedDate.value = isCurrentMonth
    ? toIsoDate(today)
    : `${currentYear.value}-${String(currentMonth.value).padStart(2, '0')}-01`;
};

const loadFestivals = async () => {
  loading.value = true;
  error.value = false;
  try {
    const payload = await fetchCalendarFestivals(currentYear.value, currentMonth.value);
    festivals.value = Array.isArray(payload) ? payload : [];
  } catch (err) {
    festivals.value = [];
    error.value = true;
  } finally {
    loading.value = false;
  }
};

const changeMonth = async (offset) => {
  const target = new Date(currentYear.value, currentMonth.value - 1 + offset, 1);
  currentYear.value = target.getFullYear();
  currentMonth.value = target.getMonth() + 1;
  setSelectedDateForMonth();
  await loadFestivals();
};

const goToday = async () => {
  currentYear.value = today.getFullYear();
  currentMonth.value = today.getMonth() + 1;
  selectedDate.value = toIsoDate(today);
  await loadFestivals();
};

const toggleView = () => {
  viewMode.value = viewMode.value === 'calendar' ? 'monthly' : 'calendar';
};

onMounted(loadFestivals);
</script>

<style scoped>
.calendar-page { padding-bottom: 48px; }
.calendar-heading,
.month-toolbar,
.selected-day-heading,
.monthly-list-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}
.calendar-heading { margin-top: 24px; }
.calendar-heading .page-title { margin: 4px 0 8px; }
.calendar-eyebrow { margin: 0; color: var(--color-primary); font-weight: 800; }
.calendar-description { margin: 0; color: var(--color-muted); }
.view-toggle,
.today-button,
.month-toolbar > button {
  border: 1px solid var(--color-border);
  background: white;
  color: var(--color-text);
  border-radius: 999px;
  padding: 10px 16px;
  font-weight: 700;
  cursor: pointer;
}
.view-toggle { background: var(--color-primary); color: white; border-color: var(--color-primary); }
.month-toolbar {
  justify-content: center;
  margin: 28px 0 18px;
  background: white;
  border: 1px solid var(--color-border);
  border-radius: 20px;
  padding: 14px;
}
.month-toolbar > button:not(.today-button) { width: 44px; height: 44px; padding: 0; font-size: 28px; }
.month-title-wrap { min-width: 180px; text-align: center; display: grid; gap: 3px; }
.month-title-wrap strong { font-size: 22px; }
.month-title-wrap span { color: var(--color-muted); font-size: 13px; }
.calendar-shell { background: white; border: 1px solid var(--color-border); border-radius: 24px; overflow: hidden; }
.weekday-row,
.calendar-grid { display: grid; grid-template-columns: repeat(7, minmax(0, 1fr)); }
.weekday-row { background: #f8fafc; border-bottom: 1px solid var(--color-border); }
.weekday-row span { padding: 12px; text-align: center; font-weight: 800; }
.weekday-row span:first-child { color: #ef4444; }
.weekday-row span:last-child { color: #2563eb; }
.calendar-cell {
  min-height: 132px;
  padding: 8px;
  border-right: 1px solid var(--color-border);
  border-bottom: 1px solid var(--color-border);
  background: white;
}
.calendar-cell:nth-child(7n) { border-right: none; }
.calendar-cell.muted { background: #f8fafc; color: #cbd5e1; }
.calendar-cell.today { background: #f0f9ff; }
.calendar-cell.selected { box-shadow: inset 0 0 0 2px var(--color-primary); }
.calendar-date-button {
  width: 30px;
  height: 30px;
  border: none;
  border-radius: 50%;
  background: transparent;
  color: inherit;
  font-weight: 800;
  cursor: pointer;
}
.today .calendar-date-button { background: var(--color-primary); color: white; }
.calendar-date-button:disabled { cursor: default; }
.calendar-cell-events { display: grid; gap: 4px; margin-top: 5px; }
.calendar-event-pill,
.calendar-more {
  display: block;
  width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  border: none;
  border-radius: 6px;
  padding: 5px 7px;
  background: #e0f2fe;
  color: #0369a1;
  font-size: 11px;
  text-align: left;
  cursor: pointer;
}
.calendar-event-pill span { margin-right: 3px; font-weight: 900; }
.calendar-event-pill.boundary-end { background: #fee2e2; color: #b91c1c; }
.calendar-event-pill.boundary-start-end { background: #ede9fe; color: #6d28d9; }
.calendar-more { background: #f1f5f9; color: var(--color-muted); }
.selected-day-panel,
.monthly-list {
  margin-top: 22px;
  padding: 22px;
  background: white;
  border: 1px solid var(--color-border);
  border-radius: 24px;
}
.selected-day-heading span,
.monthly-list-heading span { color: var(--color-muted); font-size: 14px; }
.selected-day-heading h3,
.monthly-list-heading h3 { margin: 4px 0 0; }
.selected-day-heading > strong { color: var(--color-primary); }
.selected-festival-list { display: grid; gap: 10px; margin-top: 18px; }
.selected-festival-card {
  display: grid;
  grid-template-columns: 96px 1fr;
  gap: 14px;
  align-items: center;
  padding: 12px;
  border: 1px solid var(--color-border);
  border-radius: 16px;
  color: var(--color-text);
}
.selected-festival-card img { width: 96px; height: 72px; object-fit: cover; border-radius: 12px; }
.selected-festival-card div { display: grid; gap: 4px; }
.selected-festival-card span,
.selected-festival-card small { color: var(--color-muted); }
.empty-message { color: var(--color-muted); margin: 18px 0 0; }
.monthly-list-heading { margin-bottom: 18px; }
.monthly-event-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 16px; }
.monthly-event-card {
  overflow: hidden;
  border: 1px solid var(--color-border);
  border-radius: 18px;
  background: white;
  color: var(--color-text);
}
.monthly-event-card img { width: 100%; height: 150px; object-fit: cover; }
.monthly-event-card > div { padding: 16px; }
.monthly-event-card h3 { margin: 8px 0; font-size: 18px; }
.monthly-event-card p { margin: 0; color: var(--color-muted); }
.monthly-period { color: var(--color-primary); font-size: 13px; font-weight: 800; }
.state-card button { margin-left: 10px; }

@media (max-width: 768px) {
  .calendar-heading { align-items: flex-start; }
  .view-toggle { flex: 0 0 auto; }
  .month-toolbar { flex-wrap: wrap; }
  .today-button { width: 100%; }
  .calendar-cell { min-height: 76px; padding: 4px; }
  .calendar-event-pill { padding: 4px; font-size: 0; height: 8px; }
  .calendar-more { font-size: 10px; padding: 3px; }
  .selected-day-heading { align-items: flex-start; }
  .selected-festival-card { grid-template-columns: 72px 1fr; }
  .selected-festival-card img { width: 72px; height: 64px; }
  .monthly-event-grid { grid-template-columns: 1fr; }
}
</style>
