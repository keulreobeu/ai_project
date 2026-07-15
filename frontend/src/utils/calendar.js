const pad = (value) => String(value).padStart(2, '0');

export function toIsoDate(date) {
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}`;
}

export function buildMonthGrid(year, month, today = new Date()) {
  const firstDay = new Date(year, month - 1, 1);
  const firstGridDate = 1 - firstDay.getDay();
  const todayIso = toIsoDate(today);

  return Array.from({ length: 42 }, (_, index) => {
    const date = new Date(year, month - 1, firstGridDate + index);
    const iso = toIsoDate(date);
    return {
      iso,
      day: date.getDate(),
      inCurrentMonth: date.getFullYear() === year && date.getMonth() + 1 === month,
      isToday: iso === todayIso,
    };
  });
}

export function festivalOccursOn(festival, isoDate) {
  return Boolean(
    festival?.event_start_date
    && festival?.event_end_date
    && festival.event_start_date <= isoDate
    && festival.event_end_date >= isoDate
  );
}

export function festivalBoundaryOn(festival, isoDate) {
  const startDate = festival?.event_start_date;
  const endDate = festival?.event_end_date;

  if (!startDate || !endDate) return null;
  if (startDate === isoDate && endDate === isoDate) return 'start-end';
  if (startDate === isoDate) return 'start';
  if (endDate === isoDate) return 'end';
  return null;
}

const DAY_IN_MILLISECONDS = 24 * 60 * 60 * 1000;

const isoDateToDayNumber = (isoDate) => {
  const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(isoDate || '');
  if (!match) return null;
  return Date.UTC(Number(match[1]), Number(match[2]) - 1, Number(match[3])) / DAY_IN_MILLISECONDS;
};

const closestFestivalBoundary = (festival, referenceDay) => {
  const startDay = isoDateToDayNumber(festival?.event_start_date);
  const endDay = isoDateToDayNumber(festival?.event_end_date);
  const startDistance = startDay === null ? Number.POSITIVE_INFINITY : Math.abs(startDay - referenceDay);
  const endDistance = endDay === null ? Number.POSITIVE_INFINITY : Math.abs(endDay - referenceDay);

  if (endDistance <= startDistance) {
    return { distance: endDistance, boundaryPriority: 0, boundaryDay: endDay };
  }
  return { distance: startDistance, boundaryPriority: 1, boundaryDay: startDay };
};

export function sortFestivalsByNearestBoundary(festivals, referenceDate) {
  const referenceDay = isoDateToDayNumber(referenceDate);
  if (referenceDay === null) return [...festivals];

  return [...festivals].sort((first, second) => {
    const firstBoundary = closestFestivalBoundary(first, referenceDay);
    const secondBoundary = closestFestivalBoundary(second, referenceDay);

    if (firstBoundary.distance !== secondBoundary.distance) {
      return firstBoundary.distance - secondBoundary.distance;
    }
    if (firstBoundary.boundaryPriority !== secondBoundary.boundaryPriority) {
      return firstBoundary.boundaryPriority - secondBoundary.boundaryPriority;
    }
    if (firstBoundary.boundaryDay !== secondBoundary.boundaryDay) {
      return firstBoundary.boundaryDay - secondBoundary.boundaryDay;
    }
    return (first?.title || '').localeCompare(second?.title || '', 'ko');
  });
}

export function formatFestivalPeriod(startDate, endDate) {
  if (!startDate || !endDate) return '일정 미등록';
  if (startDate === endDate) return startDate;
  return `${startDate} ~ ${endDate}`;
}
