<script setup>
import { computed, nextTick, onMounted, onUnmounted, ref } from "vue";
import heroBanner from "./assets/banners/main-banner.png";

const city = ref("Москва");
const search = ref("");
const selectedDateKey = ref("2026-03-11");
const calendarTrack = ref(null);
const stickyMonthLabel = ref("Февраль");
const stickyMonthRef = ref(null);
const stickyMonthLeft = ref(0);
const currentMonthIndex = ref(0);
const calendarScrollLeft = ref(0);
const calendarStep = ref(54);

const events = ref(
  Array.from({ length: 12 }, (_, i) => ({
    id: i + 1,
    title: "Мюзикл «Айболит для детей и взрослых»",
    date: "14 марта, 12:00",
    venue: "Театр музыки и драмы п/р Стаса Намина",
    price: 500,
  }))
);

const filteredEvents = computed(() => {
  const q = search.value.trim().toLowerCase();
  if (!q) return events.value;
  return events.value.filter((e) =>
    `${e.title} ${e.venue}`.toLowerCase().includes(q)
  );
});

const monthNames = [
  "Январь",
  "Февраль",
  "Март",
  "Апрель",
  "Май",
  "Июнь",
  "Июль",
  "Август",
  "Сентябрь",
  "Октябрь",
  "Ноябрь",
  "Декабрь",
];

const dowNames = ["вс", "пн", "вт", "ср", "чт", "пт", "сб"];

function buildCalendarDays(startDate, endDate) {
  const days = [];
  const cursor = new Date(startDate);
  while (cursor <= endDate) {
    const year = cursor.getFullYear();
    const month = cursor.getMonth();
    const day = cursor.getDate();
    const dow = cursor.getDay();
    const key = `${year}-${String(month + 1).padStart(2, "0")}-${String(day).padStart(2, "0")}`;

    days.push({
      key,
      monthKey: `${year}-${month}`,
      monthLabel: monthNames[month],
      day,
      dow: dowNames[dow],
      weekend: dow === 0 || dow === 6,
    });

    cursor.setDate(cursor.getDate() + 1);
  }
  return days;
}

const calendarDays = buildCalendarDays(
  new Date(2026, 1, 20),
  new Date(2026, 11, 31)
);

function findMonthByCellIndex(cellIndex) {
  const safeIndex = Math.max(0, Math.min(cellIndex, calendarDays.length - 1));
  return calendarDays[safeIndex]?.monthLabel || "";
}

const monthStarts = computed(() => {
  const starts = [];
  for (let i = 0; i < calendarDays.length; i += 1) {
    if (i === 0 || calendarDays[i].monthKey !== calendarDays[i - 1].monthKey) {
      starts.push({
        label: calendarDays[i].monthLabel,
        monthKey: calendarDays[i].monthKey,
        startIndex: i,
      });
    }
  }
  return starts;
});

function findMonthStartIndexByCell(cellIndex) {
  let idx = 0;
  for (let i = 0; i < monthStarts.value.length; i += 1) {
    if (monthStarts.value[i].startIndex <= cellIndex) {
      idx = i;
    } else {
      break;
    }
  }
  return idx;
}

function updateStickyMonth() {
  if (!calendarTrack.value) return;
  const calendar = calendarTrack.value.closest(".calendar");
  if (!calendar) return;

  const style = getComputedStyle(calendar);
  const dayCell = parseFloat(style.getPropertyValue("--day-cell")) || 52;
  const dayGap = parseFloat(style.getPropertyValue("--day-gap")) || 2;
  const step = dayCell + dayGap;
  calendarStep.value = step;
  calendarScrollLeft.value = calendarTrack.value.scrollLeft;

  const firstVisibleCell = Math.max(
    0,
    Math.floor((calendarTrack.value.scrollLeft + step * 0.35) / step)
  );
  stickyMonthLabel.value = findMonthByCellIndex(firstVisibleCell);

  const monthIndex = findMonthStartIndexByCell(firstVisibleCell);
  currentMonthIndex.value = monthIndex;
  const current = monthStarts.value[monthIndex];
  const next = monthStarts.value[monthIndex + 1];
  const labelWidth = stickyMonthRef.value?.offsetWidth ?? 120;

  const rawLeft = current.startIndex * step - calendarTrack.value.scrollLeft;
  let nextClamp = Number.POSITIVE_INFINITY;
  if (next) {
    nextClamp = next.startIndex * step - calendarTrack.value.scrollLeft - labelWidth - 8;
  }

  stickyMonthLeft.value = Math.max(0, Math.min(rawLeft, nextClamp));
}

function floatingMonthLeft(startIndex) {
  return startIndex * calendarStep.value - calendarScrollLeft.value;
}

function scrollCalendar(direction) {
  if (!calendarTrack.value) return;
  calendarTrack.value.scrollBy({
    left: direction * 420,
    behavior: "smooth",
  });
}

let onCalendarScroll = null;
let onWindowResize = null;

onMounted(async () => {
  await nextTick();
  if (!calendarTrack.value) return;

  onCalendarScroll = () => updateStickyMonth();
  onWindowResize = () => updateStickyMonth();

  calendarTrack.value.addEventListener("scroll", onCalendarScroll, {
    passive: true,
  });
  window.addEventListener("resize", onWindowResize);
  updateStickyMonth();
});

onUnmounted(() => {
  if (calendarTrack.value && onCalendarScroll) {
    calendarTrack.value.removeEventListener("scroll", onCalendarScroll);
  }
  if (onWindowResize) {
    window.removeEventListener("resize", onWindowResize);
  }
});
</script>

<template>
  <div class="page-bg">
    <main class="screen">
      <header class="header">
        <div class="logo-wrap">
          <span class="logo-star" aria-hidden="true"></span>
          <div class="logo-text">Путь</div>
        </div>

        <div class="search-box">
          <span class="search-icon">⌕</span>
          <input
            v-model="search"
            type="text"
            placeholder="Событие, Персона, Площадка"
          />
        </div>

        <div class="city">{{ city }}</div>

        <div class="menu-icons">
          <button title="Избранное">♡</button>
          <button title="Профиль">◌</button>
          <button title="Корзина">⟠</button>
        </div>
      </header>

      <section class="hero">
        <img :src="heroBanner" alt="Баннер" />
      </section>

      <h1 class="title">Афиша Москвы</h1>

      <section class="calendar">
        <div class="calendar-wrap">
          <button class="cal-arrow" aria-label="Назад" @click="scrollCalendar(-1)">
            &#8249;
          </button>

          <div class="calendar-window">
            <div class="month-overlay">
              <div
                v-for="(m, idx) in monthStarts"
                v-show="idx !== currentMonthIndex"
                :key="`float-${m.monthKey}`"
                class="month-float"
                :style="{ left: `${floatingMonthLeft(m.startIndex)}px` }"
              >
                {{ m.label }}
              </div>
            </div>
            <div
              ref="stickyMonthRef"
              class="sticky-month"
              :style="{ left: `${stickyMonthLeft}px` }"
            >
              {{ stickyMonthLabel }}
            </div>
            <div ref="calendarTrack" class="calendar-track">
              <div class="calendar-days">
              <button
                v-for="d in calendarDays"
                :key="d.key"
                class="day-cell"
                :class="{
                  weekend: d.weekend,
                  selected: selectedDateKey === d.key
                }"
                @click="selectedDateKey = d.key"
              >
                <span class="num">{{ d.day }}</span>
                <span class="dow">{{ d.dow }}</span>
              </button>
              </div>
            </div>
          </div>

          <button class="cal-arrow" aria-label="Вперед" @click="scrollCalendar(1)">
            &#8250;
          </button>
        </div>
      </section>

      <section class="controls">
        <div class="left-controls">
          <button class="soft">Сортировка ∨</button>
          <button class="soft">Фильтры</button>
        </div>
        <button class="route">Составить маршрут</button>
      </section>

      <section class="cards">
        <article v-if="filteredEvents.length" class="card">
          <div class="poster poster-1"></div>
          <div class="price">ОТ {{ filteredEvents[0].price }} ₽</div>
          <h2>{{ filteredEvents[0].title }}</h2>
          <p>{{ filteredEvents[0].date }}<br />{{ filteredEvents[0].venue }}</p>
        </article>
        <article v-else class="card">
          <div class="poster poster-1"></div>
          <h2>События не найдены</h2>
        </article>
      </section>
    </main>
  </div>
</template>

<style scoped>
@font-face {
  font-family: "Airfool";
  src: url("./assets/fonts/Airfool.otf") format("opentype");
  font-weight: 400;
  font-style: normal;
}

@font-face {
  font-family: "Arista Pro";
  src: url("./assets/fonts/AristaPro-Regular.ttf") format("truetype");
  font-weight: 400;
  font-style: normal;
}

@font-face {
  font-family: "Arista Pro";
  src: url("./assets/fonts/AristaPro-Light.ttf") format("truetype");
  font-weight: 300;
  font-style: normal;
}

@font-face {
  font-family: "Arista Pro";
  src: url("./assets/fonts/AristaPro-Bold.ttf") format("truetype");
  font-weight: 700;
  font-style: normal;
}

:root {
  --accent: #ff7264;
  --text: #2c2c31;
}

* {
  box-sizing: border-box;
}

.page-bg {
  min-height: 100vh;
  background:
    radial-gradient(1200px 900px at -10% 60%, #f0ebe2 0%, transparent 55%),
    radial-gradient(1200px 900px at 110% 10%, #f3f0eb 0%, transparent 60%),
    #f8f8f8;
  font-family: "Arista Pro", sans-serif;
  color: var(--text);
}

.screen {
  max-width: 1920px;
  margin: 0 auto;
  padding: 20px 32px 40px;
}

.header {
  display: grid;
  grid-template-columns: auto 1fr auto auto;
  gap: 16px;
  align-items: center;
}

.logo-wrap {
  display: flex;
  align-items: center;
  gap: 8px;
}

.logo-star {
  width: 56px;
  height: 56px;
  background: #ffd039;
  clip-path: polygon(50% 0%, 60% 24%, 84% 12%, 72% 34%, 100% 50%, 72% 66%, 84% 88%, 60% 76%, 50% 100%, 40% 76%, 16% 88%, 28% 66%, 0% 50%, 28% 34%, 16% 12%, 40% 24%);
}

.logo-text {
  font-family: "Airfool", sans-serif;
  font-size: 56px;
  line-height: 0.95;
  color: #1f1f1f;
}

.search-box {
  display: flex;
  align-items: center;
  gap: 12px;
  background: #dcdcdc;
  border-radius: 32px;
  padding: 10px 16px;
}

.search-icon {
  font-size: 30px;
  color: #3c3d46;
}

.search-box input {
  border: 0;
  background: transparent;
  width: 100%;
  outline: none;
  font-size: 30px;
  color: #787983;
  font-family: "Arista Pro", sans-serif;
  font-weight: 300;
}

.city {
  font-size: 16px;
}

.menu-icons {
  display: flex;
  gap: 4px;
}

.menu-icons button {
  border: 0;
  background: transparent;
  width: 28px;
  height: 28px;
  color: #6f7078;
  cursor: pointer;
}

.hero {
  margin-top: 12px;
  width: 100%;
  aspect-ratio: 1856 / 545;
  border-radius: 56px;
  overflow: hidden;
}

.hero img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center;
  display: block;
}

.title {
  margin: 18px 0 8px;
  font-family: "Airfool", sans-serif;
  font-size: clamp(56px, 7vw, 100px);
  line-height: 1;
  color: #ffd039;
  font-weight: 400;
}

.calendar {
  margin-top: 2px;
  --day-cell: 52px;
  --day-gap: 2px;
}

.calendar-wrap {
  display: grid;
  grid-template-columns: 34px 1fr 34px;
  gap: 8px;
  align-items: center;
}

.calendar-window {
  position: relative;
  overflow: hidden;
  padding-top: 32px;
}

.month-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 28px;
  pointer-events: none;
  z-index: 1;
}

.month-float {
  position: absolute;
  top: 0;
  font-size: 24px;
  line-height: 1;
  font-weight: 300;
  white-space: nowrap;
  color: #2f2f35;
  background: #f8f8f8;
  padding-right: 12px;
}

.calendar-track {
  overflow-x: auto;
  scrollbar-width: none;
  scroll-behavior: smooth;
}

.calendar-track::-webkit-scrollbar {
  display: none;
}

.sticky-month {
  position: absolute;
  top: 0;
  z-index: 2;
  font-size: 24px;
  line-height: 1;
  font-weight: 300;
  background: #f8f8f8;
  padding: 0 14px 2px 0;
  pointer-events: none;
  white-space: nowrap;
  will-change: left;
}

.calendar-days {
  display: flex;
  gap: var(--day-gap);
  width: max-content;
}

.cal-arrow {
  width: 34px;
  height: 34px;
  border: 0;
  border-radius: 999px;
  background: #ececec;
  color: #2f2f35;
  font-size: 24px;
  line-height: 1;
  cursor: pointer;
}

.day-cell {
  border: 0;
  background: transparent;
  color: #2f2f35;
  font-family: "Arista Pro", sans-serif;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 56px;
  min-width: var(--day-cell);
  flex: 0 0 var(--day-cell);
  border-radius: 999px;
  padding: 4px 0;
}

.day-cell .num {
  font-size: 28px;
  line-height: 1;
}

.day-cell .dow {
  margin-top: 2px;
  font-size: 13px;
  line-height: 1;
}

.day-cell.weekend {
  color: #ff3b30;
}

.day-cell.selected {
  background: #ececec;
}

.controls {
  margin-top: 14px;
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
}

.left-controls {
  display: flex;
  gap: 8px;
}

.soft,
.route {
  border: 0;
  border-radius: 16px;
  padding: 12px 16px;
  font-family: "Arista Pro", sans-serif;
  font-size: 24px;
}

.soft {
  background: #6b6c766e;
  color: #fff;
}

.route {
  background: var(--accent);
  color: #fff;
}

.cards {
  margin-top: 14px;
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 20px;
}

.poster {
  width: 100%;
  aspect-ratio: 5 / 3;
  border-radius: 24px;
}

.poster-1 {
  background: linear-gradient(135deg, #2f6fa0, #5ba8d9);
}

.poster-2 {
  background: linear-gradient(135deg, #ce7e43, #f0b57b);
}

.poster-3 {
  background: linear-gradient(135deg, #8a4cb5, #df9ad9);
}

.poster-4 {
  background: linear-gradient(135deg, #7f1f1f, #f05c28);
}

.price {
  margin-top: 8px;
  display: inline-block;
  border-radius: 12px;
  background: var(--accent);
  color: #fff;
  padding: 4px 10px;
  font-size: 16px;
}

.card h2 {
  margin: 6px 0 3px;
  font-size: 40px;
  line-height: 0.95;
  font-weight: 300;
}

.card p {
  margin: 0;
  font-size: 14px;
  color: #000000b0;
}

.show-more {
  margin: 18px auto 8px;
  width: fit-content;
  font-size: 28px;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 14px;
  font-size: 56px;
  line-height: 1;
}

.active-page {
  font-weight: 700;
}

.cookie {
  margin-top: 18px;
  max-width: 760px;
  background: #fff;
  border: 1px solid #dbe7f3;
  border-radius: 16px;
  padding: 14px;
}

.cookie p {
  margin: 0 0 10px;
  color: #6f7078;
  font-size: 13px;
}

.cookie button {
  border: 0;
  border-radius: 10px;
  background: var(--accent);
  color: #fff;
  font-size: 12px;
  padding: 8px 12px;
  font-family: "Arista Pro", sans-serif;
}

@media (max-width: 1280px) {
  .screen {
    padding: 14px;
  }

  .search-box input {
    font-size: 22px;
  }

  .cards {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .card h2 {
    font-size: 32px;
  }
}

@media (max-width: 760px) {
  .header {
    grid-template-columns: 1fr;
  }

  .calendar {
    --day-cell: 48px;
    --day-gap: 2px;
  }

  .day-cell .num {
    font-size: 24px;
  }

  .cards {
    grid-template-columns: 1fr;
  }

  .hero {
    aspect-ratio: 16 / 9;
    border-radius: 24px;
  }

  .pagination {
    font-size: 36px;
    gap: 10px;
  }
}
</style>
