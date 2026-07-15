import test from 'node:test';
import assert from 'node:assert/strict';
import {
  buildMonthGrid,
  festivalBoundaryOn,
  festivalOccursOn,
  formatFestivalPeriod,
  sortFestivalsByNearestBoundary,
} from '../src/utils/calendar.js';


test('builds a six-week grid for the selected month', () => {
  const days = buildMonthGrid(2024, 2, new Date(2024, 1, 15));

  assert.equal(days.length, 42);
  assert.equal(days[0].iso, '2024-01-28');
  assert.equal(days.at(-1).iso, '2024-03-09');
  assert.equal(days.find((day) => day.iso === '2024-02-29').inCurrentMonth, true);
  assert.equal(days.find((day) => day.iso === '2024-02-15').isToday, true);
});


test('matches every date inside a multi-day festival period', () => {
  const festival = {
    event_start_date: '2026-06-20',
    event_end_date: '2026-07-03',
  };

  assert.equal(festivalOccursOn(festival, '2026-06-19'), false);
  assert.equal(festivalOccursOn(festival, '2026-07-01'), true);
  assert.equal(festivalOccursOn(festival, '2026-07-04'), false);
});


test('marks only the start and end dates of a festival on the calendar', () => {
  const festival = {
    event_start_date: '2026-07-10',
    event_end_date: '2026-07-15',
  };

  assert.equal(festivalBoundaryOn(festival, '2026-07-10'), 'start');
  assert.equal(festivalBoundaryOn(festival, '2026-07-12'), null);
  assert.equal(festivalBoundaryOn(festival, '2026-07-15'), 'end');
  assert.equal(festivalBoundaryOn({
    event_start_date: '2026-07-20',
    event_end_date: '2026-07-20',
  }, '2026-07-20'), 'start-end');
});


test('sorts festivals by the boundary nearest to today and prioritizes endings on a tie', () => {
  const festivals = [
    { title: '내일 시작', event_start_date: '2026-07-16', event_end_date: '2026-07-30' },
    { title: '사흘 뒤 종료', event_start_date: '2026-07-01', event_end_date: '2026-07-18' },
    { title: '내일 종료', event_start_date: '2026-07-01', event_end_date: '2026-07-16' },
    { title: '오늘 시작', event_start_date: '2026-07-15', event_end_date: '2026-07-25' },
  ];

  const sorted = sortFestivalsByNearestBoundary(festivals, '2026-07-15');

  assert.deepEqual(sorted.map((festival) => festival.title), [
    '오늘 시작',
    '내일 종료',
    '내일 시작',
    '사흘 뒤 종료',
  ]);
  assert.equal(festivals[0].title, '내일 시작');
});


test('formats single-day and ranged festival periods', () => {
  assert.equal(formatFestivalPeriod('2026-07-15', '2026-07-15'), '2026-07-15');
  assert.equal(formatFestivalPeriod('2026-07-15', '2026-07-20'), '2026-07-15 ~ 2026-07-20');
});
