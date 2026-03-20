<script setup>
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from "vue";
import heroBanner from "./assets/banners/main-banner.png";

const apiBase = import.meta.env.VITE_API_BASE || "http://localhost:8000";
const currentPath = ref(window.location.pathname || "/");

function loadAuth() {
  try {
    const raw = localStorage.getItem("it_cons_auth");
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

const auth = ref(loadAuth());
const loginForm = ref({ login: "", password: "" });
const registerForm = ref({ full_name: "", login: "", password: "" });
const loginError = ref("");
const loginLoading = ref(false);
const registerError = ref("");
const registerLoading = ref(false);

const profile = ref(null);
const profileLoading = ref(false);
const profileError = ref("");
const adminTab = ref("dashboard");
const createUserForm = ref({
  full_name: "",
  login: "",
  password: "",
  user_type: "user",
});
const createUserLoading = ref(false);
const createUserError = ref("");
const createUserSuccess = ref("");
const adminRefundsLoading = ref(false);
const adminRefundsError = ref("");
const adminRefundsSuccess = ref("");
const adminRefunds = ref([]);
const adminRefundRejectComment = ref({});
const adminModerationEventsLoading = ref(false);
const adminModerationEventsError = ref("");
const adminModerationEventsSuccess = ref("");
const adminModerationEvents = ref([]);
const adminModerationRejectComment = ref({});
const adminNearbyPlacesLoading = ref(false);
const adminNearbyPlacesError = ref("");
const adminNearbyPlacesSuccess = ref("");
const adminNearbyPlaces = ref([]);
const adminNearbyVenues = ref([]);
const adminNearbyPlaceEditId = ref(null);
const adminNearbyImagePreview = ref("");
const adminNearbyPlaceForm = ref({
  venue_id: "",
  title: "",
  description: "",
  working_hours: "",
  average_check: "",
  travel_time_minutes: "",
  image: null,
  clear_image: false,
});
const organizerCompany = ref({
  display_name: "",
  phone: "",
  telegram: "",
  whatsapp: "",
  website_url: "",
  address_text: "",
  contact_person: "",
  about_text: "",
});
const organizerDetails = ref({
  short_legal_name: "",
  full_legal_name: "",
  legal_address: "",
  inn: "",
  ogrn: "",
  kpp: "",
  org_type: "legal_entity",
  registration_date: "",
  head_full_name: "",
  head_position: "",
  okved: "",
  okopf: "",
  opf_name: "",
});
const organizerLoading = ref(false);
const organizerError = ref("");
const organizerSuccess = ref("");
const editCompany = ref(false);
const editAbout = ref(false);
const editDetails = ref(false);
const organizerTab = ref("company");
const organizerEvents = ref([]);
const organizerEventsLoading = ref(false);
const organizerEventsError = ref("");
const showCreateEventForm = ref(false);
const newEvent = ref({
  title: "",
  description: "",
  category_name: "",
  venue_city: "",
  venue_address: "",
  status: "draft",
});
const ageOptions = [
  { label: "0 - 3", min: 0, max: 3 },
  { label: "4 - 6", min: 4, max: 6 },
  { label: "7 - 10", min: 7, max: 10 },
  { label: "11 - 14", min: 11, max: 14 },
  { label: "0+", min: 0, max: null },
  { label: "4+", min: 4, max: null },
  { label: "7+", min: 7, max: null },
  { label: "11+", min: 11, max: null },
];
const categoryOptions = [
  "Спектакль",
  "Концерт",
  "Мюзикл",
  "Экскурсия",
  "Мастер-класс",
];
const cityOptions = ["Москва", "Санкт-Петербург", "Казань"];
const addressOptionsByCity = {
  "Москва": ["Театр музыки и драмы", "КЦ ЗИЛ", "Дом музыки"],
  "Санкт-Петербург": ["БКЗ Октябрьский", "Александринский театр", "Лендок"],
  "Казань": ["Театр им. Камала", "Культурный центр Сайдаш", "УНИКС"],
};
const selectedAgeOption = ref(null);
const sessionDraft = ref({
  date: "",
  start_time: "",
  end_time: "",
});
const sessions = ref([]);
const ticketDraft = ref({
  name: "",
  price: "",
  qty_total: "",
  currency: "RUB",
});
const ticketTypes = ref([]);
const eventCoverFile = ref(null);
const eventCoverPreview = ref("");
const eventGalleryItems = ref([]);
const removedGalleryImageIds = ref([]);
const clearCoverOnSave = ref(false);
const coverInputRef = ref(null);
const galleryInputRef = ref(null);
const editingEventId = ref(null);
const selectedOrganizerEvent = ref(null);
const organizerEventDetailLoading = ref(false);
const userCabinetTab = ref("profile");
const userProfileForm = ref({
  first_name: "",
  last_name: "",
  phone: "",
  email: "",
});
const userProfileLoading = ref(false);
const userProfileSaving = ref(false);
const userProfileError = ref("");
const userProfileSuccess = ref("");
const userProfileEdit = ref(false);
const userBookingsLoading = ref(false);
const userBookingsError = ref("");
const userCurrentBookings = ref([]);
const userHistoryBookings = ref([]);
const userFavoritesLoading = ref(false);
const userFavoritesError = ref("");
const userFavorites = ref([]);
const favoriteEventIds = ref([]);
const ticketReceiptBooking = ref(null);
const userRefundLoading = ref(false);
const userRefundError = ref("");
const userRefundSuccess = ref("");
const refundConfirmBooking = ref(null);
const userPaymentsLoading = ref(false);
const userPaymentsError = ref("");
const userPaymentsSuccess = ref("");
const userPaymentMethods = ref([]);
const userPaymentEditId = ref(null);
const userPaymentEditorOpen = ref(false);
const userPaymentShowCvv = ref(false);
const userPaymentForm = ref({
  card_brand: "",
  card_number: "",
  expires_at: "",
  holder_name: "",
  cvv_code: "",
});
const userPrivacyLoading = ref(false);
const userPrivacySaving = ref(false);
const userPrivacyError = ref("");
const userPrivacySuccess = ref("");
const userPrivacyForm = ref({
  show_profile_in_reviews: false,
  allow_email_notifications: true,
  allow_sms_notifications: false,
});

function persistAuth(value) {
  auth.value = value;
  if (value) {
    localStorage.setItem("it_cons_auth", JSON.stringify(value));
  } else {
    localStorage.removeItem("it_cons_auth");
  }
}

function setPendingAuthRedirect(path) {
  if (!path) return;
  localStorage.setItem("it_cons_next_path", path);
}

function popPendingAuthRedirect() {
  const path = localStorage.getItem("it_cons_next_path");
  if (path) localStorage.removeItem("it_cons_next_path");
  return path;
}

function setPendingUserCabinetTab(tab) {
  if (!tab) return;
  localStorage.setItem("it_cons_user_tab", tab);
}

function popPendingUserCabinetTab() {
  const tab = localStorage.getItem("it_cons_user_tab");
  if (tab) localStorage.removeItem("it_cons_user_tab");
  return tab;
}

function navigate(path) {
  if (currentPath.value === path) return;
  history.pushState({}, "", path);
  currentPath.value = path;
  handleRoute();
}

function logout() {
  persistAuth(null);
  profile.value = null;
  userFavorites.value = [];
  favoriteEventIds.value = [];
  navigate("/");
}

function openCabinetFromHeader() {
  if (auth.value) {
    navigate("/cabinet");
  } else {
    navigate("/login");
  }
}

function openFavoritesFromHeader() {
  if (!auth.value) {
    setPendingAuthRedirect("/cabinet");
    setPendingUserCabinetTab("favorites");
    navigate("/login");
    return;
  }
  if (auth.value.role !== "user") {
    navigate("/cabinet");
    return;
  }
  userCabinetTab.value = "favorites";
  setPendingUserCabinetTab("favorites");
  navigate("/cabinet");
}

async function submitLogin() {
  loginLoading.value = true;
  loginError.value = "";
  try {
    const response = await fetch(`${apiBase}/api/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        login: loginForm.value.login,
        password: loginForm.value.password,
      }),
    });
    const payload = await response.json();
    if (!response.ok) {
      loginError.value = payload.error || "Ошибка авторизации";
      return;
    }
    persistAuth({
      token: payload.token,
      role: payload.user.role,
      login: payload.user.login,
    });
    const nextPath = popPendingAuthRedirect();
    navigate(nextPath || "/cabinet");
  } catch (error) {
    loginError.value = error instanceof Error ? error.message : String(error);
  } finally {
    loginLoading.value = false;
  }
}

async function loadProfile() {
  if (!auth.value?.token) {
    navigate("/login");
    return;
  }
  profileLoading.value = true;
  profileError.value = "";
  try {
    const response = await fetch(`${apiBase}/api/auth/me`, {
      headers: { Authorization: `Bearer ${auth.value.token}` },
    });
    const payload = await response.json();
    if (!response.ok) {
      profileError.value = payload.error || "Нет доступа";
      if (response.status === 401 || response.status === 403) {
        persistAuth(null);
        navigate("/login");
      }
      return;
    }
    profile.value = payload;
    if (payload.role === "organizer") {
      organizerTab.value = "company";
      await loadOrganizerCompany();
      await loadOrganizerEvents();
    } else if (payload.role === "user") {
      userCabinetTab.value = popPendingUserCabinetTab() || "profile";
      userProfileEdit.value = false;
      await loadUserCabinetData();
    }
  } catch (error) {
    profileError.value = error instanceof Error ? error.message : String(error);
  } finally {
    profileLoading.value = false;
  }
}

async function loadOrganizerCompany() {
  if (!auth.value?.token) return;
  organizerLoading.value = true;
  organizerError.value = "";
  try {
    const response = await fetch(`${apiBase}/api/organizer/company`, {
      headers: { Authorization: `Bearer ${auth.value.token}` },
    });
    const payload = await response.json();
    if (!response.ok) {
      organizerError.value = payload.error || "Не удалось загрузить данные организатора";
      return;
    }
    organizerCompany.value = { ...organizerCompany.value, ...(payload.company || {}) };
    organizerDetails.value = { ...organizerDetails.value, ...(payload.details || {}) };
  } catch (error) {
    organizerError.value = error instanceof Error ? error.message : String(error);
  } finally {
    organizerLoading.value = false;
  }
}

async function saveOrganizerSection(section) {
  if (!auth.value?.token) return;
  organizerError.value = "";
  organizerSuccess.value = "";
  try {
    const body = { company: {}, details: {} };
    if (section === "company") {
      body.company = {
        display_name: organizerCompany.value.display_name,
        phone: organizerCompany.value.phone,
        telegram: organizerCompany.value.telegram,
        whatsapp: organizerCompany.value.whatsapp,
        website_url: organizerCompany.value.website_url,
        address_text: organizerCompany.value.address_text,
        contact_person: organizerCompany.value.contact_person,
      };
    } else if (section === "about") {
      body.company = { about_text: organizerCompany.value.about_text };
    } else if (section === "details") {
      body.details = { ...organizerDetails.value };
    }

    const response = await fetch(`${apiBase}/api/organizer/company`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${auth.value.token}`,
      },
      body: JSON.stringify(body),
    });
    const payload = await response.json();
    if (!response.ok) {
      organizerError.value = payload.error || "Не удалось сохранить изменения";
      return;
    }
    organizerCompany.value = { ...organizerCompany.value, ...(payload.company || {}) };
    organizerDetails.value = { ...organizerDetails.value, ...(payload.details || {}) };
    organizerSuccess.value = "Данные сохранены";
    if (section === "company") editCompany.value = false;
    if (section === "about") editAbout.value = false;
    if (section === "details") editDetails.value = false;
  } catch (error) {
    organizerError.value = error instanceof Error ? error.message : String(error);
  }
}

async function loadOrganizerEvents() {
  if (!auth.value?.token) return;
  organizerEventsLoading.value = true;
  organizerEventsError.value = "";
  try {
    const response = await fetch(`${apiBase}/api/organizer/events`, {
      headers: { Authorization: `Bearer ${auth.value.token}` },
    });
    const payload = await response.json();
    if (!response.ok) {
      organizerEventsError.value = payload.error || "Не удалось загрузить мероприятия";
      return;
    }
    organizerEvents.value = payload.events || [];
  } catch (error) {
    organizerEventsError.value = error instanceof Error ? error.message : String(error);
  } finally {
    organizerEventsLoading.value = false;
  }
}

function addSession() {
  if (!sessionDraft.value.date || !sessionDraft.value.start_time) return;
  sessions.value.push({
    date: sessionDraft.value.date,
    start_time: sessionDraft.value.start_time,
    end_time: sessionDraft.value.end_time,
  });
  sessionDraft.value = { date: "", start_time: "", end_time: "" };
}

function removeSession(index) {
  sessions.value.splice(index, 1);
}

function addTicketType() {
  if (!ticketDraft.value.name || ticketDraft.value.price === "") return;
  ticketTypes.value.push({
    name: ticketDraft.value.name,
    price: ticketDraft.value.price,
    qty_total: ticketDraft.value.qty_total,
    currency: ticketDraft.value.currency || "RUB",
  });
  ticketDraft.value = { name: "", price: "", qty_total: "", currency: "RUB" };
}

function removeTicketType(index) {
  ticketTypes.value.splice(index, 1);
}

function collectSessionsForSubmit() {
  const prepared = [...sessions.value];
  const draft = {
    date: (sessionDraft.value.date || "").trim(),
    start_time: (sessionDraft.value.start_time || "").trim(),
    end_time: (sessionDraft.value.end_time || "").trim(),
  };
  const hasDraftValues = Boolean(draft.date || draft.start_time || draft.end_time);
  if (!hasDraftValues) return prepared;

  if (!draft.date || !draft.start_time) {
    throw new Error("Чтобы добавить сеанс, заполните дату и время начала или очистите поля сеанса.");
  }

  const duplicate = prepared.some(
    (session) =>
      session.date === draft.date &&
      session.start_time === draft.start_time &&
      (session.end_time || "") === (draft.end_time || "")
  );
  if (!duplicate) {
    prepared.push(draft);
    sessions.value = prepared;
  }
  sessionDraft.value = { date: "", start_time: "", end_time: "" };
  return prepared;
}

function resetEventForm() {
  newEvent.value = {
    title: "",
    description: "",
    category_name: "",
    venue_city: "",
    venue_address: "",
    status: "draft",
  };
  selectedAgeOption.value = null;
  sessions.value = [];
  ticketTypes.value = [];
  sessionDraft.value = { date: "", start_time: "", end_time: "" };
  ticketDraft.value = { name: "", price: "", qty_total: "", currency: "RUB" };
  eventCoverFile.value = null;
  eventCoverPreview.value = "";
  eventGalleryItems.value = [];
  removedGalleryImageIds.value = [];
  clearCoverOnSave.value = false;
  editingEventId.value = null;
  if (coverInputRef.value) coverInputRef.value.value = "";
  if (galleryInputRef.value) galleryInputRef.value.value = "";
}

function toggleCreateEventForm() {
  if (showCreateEventForm.value) {
    showCreateEventForm.value = false;
    return;
  }
  resetEventForm();
  showCreateEventForm.value = true;
}

function formatSessionDate(dateStr) {
  if (!dateStr) return "";
  const [y, m, d] = dateStr.split("-");
  if (!y || !m || !d) return dateStr;
  const monthName = [
    "января",
    "февраля",
    "марта",
    "апреля",
    "мая",
    "июня",
    "июля",
    "августа",
    "сентября",
    "октября",
    "ноября",
    "декабря",
  ][Number(m) - 1];
  return `${Number(d)} ${monthName || ""}`.trim();
}

function formatSessionRange(startTime, endTime) {
  if (!startTime && !endTime) return "--:--";
  if (!endTime) return `${startTime} - --:--`;
  return `${startTime} - ${endTime}`;
}

function onPickCoverFile(event) {
  const file = event.target.files?.[0];
  if (!file) {
    eventCoverFile.value = null;
    eventCoverPreview.value = "";
    return;
  }
  clearCoverOnSave.value = false;
  eventCoverFile.value = file;
  eventCoverPreview.value = URL.createObjectURL(file);
  event.target.value = "";
}

function onPickGalleryFiles(event) {
  const files = Array.from(event.target.files || []);
  if (eventGalleryItems.value.length + files.length > 5) {
    organizerEventsError.value = "Можно загрузить не более 5 фото в галерею";
    return;
  }
  organizerEventsError.value = "";
  files.forEach((file) => {
    eventGalleryItems.value.push({
      image_id: null,
      url: URL.createObjectURL(file),
      file,
      existing: false,
    });
  });
  event.target.value = "";
}

function removeCoverImage() {
  eventCoverFile.value = null;
  eventCoverPreview.value = "";
  clearCoverOnSave.value = true;
  if (coverInputRef.value) coverInputRef.value.value = "";
}

function removeGalleryImage(index) {
  const item = eventGalleryItems.value[index];
  if (!item) return;
  if (item.existing && item.image_id) {
    removedGalleryImageIds.value.push(item.image_id);
  }
  eventGalleryItems.value.splice(index, 1);
}

async function uploadEventImages(eventId) {
  if (!auth.value?.token) return;
  const newGalleryFiles = eventGalleryItems.value.filter((x) => x.file).map((x) => x.file);
  if (
    !eventCoverFile.value &&
    !newGalleryFiles.length &&
    !removedGalleryImageIds.value.length &&
    !clearCoverOnSave.value
  ) {
    return;
  }
  const formData = new FormData();
  if (eventCoverFile.value) formData.append("cover_image", eventCoverFile.value);
  if (clearCoverOnSave.value) formData.append("clear_cover", "1");
  newGalleryFiles.forEach((file) => formData.append("gallery_images", file));
  if (removedGalleryImageIds.value.length) {
    formData.append("deleted_gallery_ids", JSON.stringify(removedGalleryImageIds.value));
  }

  const response = await fetch(`${apiBase}/api/organizer/events/${eventId}/images`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${auth.value.token}`,
    },
    body: formData,
  });
  const payload = await response.json();
  if (!response.ok) {
    throw new Error(payload.error || "Не удалось загрузить изображения");
  }
}

function ageLabelFromRange(min, max) {
  const found = ageOptions.find((x) => x.min === min && x.max === max);
  return found?.label || null;
}

function hydrateEventFormFromDetail(detail) {
  editingEventId.value = detail.event_id;
  showCreateEventForm.value = true;
  newEvent.value = {
    title: detail.title || "",
    description: detail.description || "",
    category_name: detail.category_name || "",
    venue_city: detail.venue_city || "",
    venue_address: detail.venue_address || "",
    status: detail.status || "draft",
  };
  selectedAgeOption.value = ageLabelFromRange(detail.age_min, detail.age_max);
  sessions.value = (detail.sessions || []).map((s) => {
    const dt = new Date(s.starts_at);
    const end = s.ends_at ? new Date(s.ends_at) : null;
    const to2 = (n) => String(n).padStart(2, "0");
    return {
      date: `${dt.getFullYear()}-${to2(dt.getMonth() + 1)}-${to2(dt.getDate())}`,
      start_time: `${to2(dt.getHours())}:${to2(dt.getMinutes())}`,
      end_time: end ? `${to2(end.getHours())}:${to2(end.getMinutes())}` : "",
    };
  });
  ticketTypes.value = detail.sessions?.[0]?.ticket_types?.map((t) => ({
    name: t.name,
    price: t.price,
    qty_total: t.qty_total,
    currency: t.currency || "RUB",
  })) || [];
  eventCoverFile.value = null;
  clearCoverOnSave.value = false;
  removedGalleryImageIds.value = [];
  eventCoverPreview.value = detail.cover_image_url || "";
  eventGalleryItems.value = (detail.images || []).map((img) => ({
    image_id: img.image_id,
    url: img.url,
    file: null,
    existing: true,
  }));
  if (coverInputRef.value) coverInputRef.value.value = "";
  if (galleryInputRef.value) galleryInputRef.value.value = "";
}

async function openOrganizerEvent(eventId) {
  if (!auth.value?.token) return;
  organizerEventDetailLoading.value = true;
  organizerEventsError.value = "";
  try {
    const response = await fetch(`${apiBase}/api/organizer/events/${eventId}`, {
      headers: {
        Authorization: `Bearer ${auth.value.token}`,
      },
    });
    const payload = await response.json();
    if (!response.ok) {
      organizerEventsError.value = payload.error || "Не удалось загрузить мероприятие";
      return;
    }
    selectedOrganizerEvent.value = payload;
  } catch (error) {
    organizerEventsError.value = error instanceof Error ? error.message : String(error);
  } finally {
    organizerEventDetailLoading.value = false;
  }
}

async function openOrganizerEventForEdit(eventId) {
  await openOrganizerEvent(eventId);
  if (selectedOrganizerEvent.value) {
    hydrateEventFormFromDetail(selectedOrganizerEvent.value);
  }
}

async function createOrganizerEvent(status = "draft") {
  if (!auth.value?.token) return;
  organizerEventsError.value = "";
  organizerSuccess.value = "";
  try {
    const sessionsForSubmit = collectSessionsForSubmit();
    if (status === "published" && sessionsForSubmit.length === 0) {
      organizerEventsError.value = "Для отправки на модерацию добавьте хотя бы один сеанс.";
      return;
    }

    const selected = ageOptions.find((a) => a.label === selectedAgeOption.value) || null;
    const isEdit = !!editingEventId.value;
    const url = isEdit
      ? `${apiBase}/api/organizer/events/${editingEventId.value}`
      : `${apiBase}/api/organizer/events`;
    const response = await fetch(url, {
      method: isEdit ? "PUT" : "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${auth.value.token}`,
      },
      body: JSON.stringify({
        ...newEvent.value,
        status,
        age_min: selected?.min ?? null,
        age_max: selected?.max ?? null,
        sessions: sessionsForSubmit,
        ticket_types: ticketTypes.value,
      }),
    });
    const payload = await response.json();
    if (!response.ok) {
      organizerEventsError.value = payload.error || "Не удалось создать мероприятие";
      return;
    }
    const eventId = payload.event_id;
    await uploadEventImages(eventId);
    resetEventForm();
    showCreateEventForm.value = false;
    organizerSuccess.value =
      status === "published"
        ? "Мероприятие отправлено на модерацию."
        : "Черновик сохранен.";
    await loadOrganizerEvents();
    await openOrganizerEvent(eventId);
  } catch (error) {
    organizerEventsError.value = error instanceof Error ? error.message : String(error);
  }
}

function hydrateUserProfileForm(payload) {
  userProfileForm.value = {
    first_name: payload?.first_name || "",
    last_name: payload?.last_name || "",
    phone: payload?.phone || "",
    email: payload?.email || "",
  };
}

async function loadUserProfile() {
  if (!auth.value?.token) return;
  userProfileLoading.value = true;
  userProfileError.value = "";
  try {
    const response = await fetch(`${apiBase}/api/user/profile`, {
      headers: { Authorization: `Bearer ${auth.value.token}` },
    });
    const payload = await response.json();
    if (!response.ok) {
      userProfileError.value = payload.error || "Не удалось загрузить профиль";
      return;
    }
    hydrateUserProfileForm(payload);
  } catch (error) {
    userProfileError.value = error instanceof Error ? error.message : String(error);
  } finally {
    userProfileLoading.value = false;
  }
}

async function saveUserProfile() {
  if (!auth.value?.token) return;
  userProfileSaving.value = true;
  userProfileError.value = "";
  userProfileSuccess.value = "";
  try {
    const response = await fetch(`${apiBase}/api/user/profile`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${auth.value.token}`,
      },
      body: JSON.stringify(userProfileForm.value),
    });
    const payload = await response.json();
    if (!response.ok) {
      userProfileError.value = payload.error || "Не удалось сохранить профиль";
      return;
    }
    hydrateUserProfileForm(payload);
    profile.value = { ...profile.value, ...payload };
    userProfileEdit.value = false;
    userProfileSuccess.value = "Профиль сохранен";
  } catch (error) {
    userProfileError.value = error instanceof Error ? error.message : String(error);
  } finally {
    userProfileSaving.value = false;
  }
}

async function loadUserBookings() {
  if (!auth.value?.token) return;
  userBookingsLoading.value = true;
  userBookingsError.value = "";
  try {
    const response = await fetch(`${apiBase}/api/user/bookings`, {
      headers: { Authorization: `Bearer ${auth.value.token}` },
    });
    const payload = await response.json();
    if (!response.ok) {
      userBookingsError.value = payload.error || "Не удалось загрузить бронирования";
      return;
    }
    userCurrentBookings.value = payload.current || [];
    userHistoryBookings.value = payload.history || [];
  } catch (error) {
    userBookingsError.value = error instanceof Error ? error.message : String(error);
  } finally {
    userBookingsLoading.value = false;
  }
}

function resetUserPaymentForm() {
  userPaymentEditId.value = null;
  userPaymentShowCvv.value = false;
  userPaymentForm.value = {
    card_brand: "",
    card_number: "",
    expires_at: "",
    holder_name: "",
    cvv_code: "",
  };
}

function openAddPaymentEditor() {
  resetUserPaymentForm();
  userPaymentEditorOpen.value = true;
}

function startEditUserPayment(method) {
  userPaymentEditId.value = method.payment_method_id;
  userPaymentShowCvv.value = false;
  userPaymentForm.value = {
    card_brand: method.card_brand || "",
    card_number: method.card_number || "",
    expires_at: method.expires_at || "",
    holder_name: method.holder_name || "",
    cvv_code: method.cvv_code || "",
  };
  userPaymentEditorOpen.value = true;
  userPaymentsSuccess.value = "";
}

async function loadUserPaymentMethods() {
  if (!auth.value?.token) return;
  userPaymentsLoading.value = true;
  userPaymentsError.value = "";
  try {
    const response = await fetch(`${apiBase}/api/user/payment-methods`, {
      headers: { Authorization: `Bearer ${auth.value.token}` },
    });
    const payload = await response.json();
    if (!response.ok) {
      userPaymentsError.value = payload.error || "Не удалось загрузить платежные данные";
      return;
    }
    userPaymentMethods.value = payload.items || [];
  } catch (error) {
    userPaymentsError.value = error instanceof Error ? error.message : String(error);
  } finally {
    userPaymentsLoading.value = false;
  }
}

async function saveUserPaymentMethod() {
  if (!auth.value?.token) return;
  userPaymentsError.value = "";
  userPaymentsSuccess.value = "";
  const form = {
    card_brand: (userPaymentForm.value.card_brand || "").trim(),
    card_number: (userPaymentForm.value.card_number || "").trim(),
    expires_at: (userPaymentForm.value.expires_at || "").trim(),
    holder_name: (userPaymentForm.value.holder_name || "").trim(),
    cvv_code: (userPaymentForm.value.cvv_code || "").trim(),
  };
  if (!form.card_brand) {
    userPaymentsError.value = "Укажите название банка/карты";
    return;
  }
  if (!/^\d{12}$/.test(form.card_number)) {
    userPaymentsError.value = "Номер карты должен содержать 12 цифр";
    return;
  }
  if (!/^\d{2}\/\d{2}$/.test(form.expires_at)) {
    userPaymentsError.value = "Срок действия укажите в формате MM/YY";
    return;
  }
  if (!form.holder_name) {
    userPaymentsError.value = "Укажите ФИО владельца карты";
    return;
  }
  if (!/^\d{3,4}$/.test(form.cvv_code)) {
    userPaymentsError.value = "CVV должен содержать 3 или 4 цифры";
    return;
  }

  userPaymentsLoading.value = true;
  try {
    const isEdit = !!userPaymentEditId.value;
    const url = isEdit
      ? `${apiBase}/api/user/payment-methods/${userPaymentEditId.value}`
      : `${apiBase}/api/user/payment-methods`;
    const response = await fetch(url, {
      method: isEdit ? "PUT" : "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${auth.value.token}`,
      },
      body: JSON.stringify(form),
    });
    const payload = await response.json();
    if (!response.ok) {
      userPaymentsError.value = payload.error || "Не удалось сохранить способ оплаты";
      return;
    }
    await loadUserPaymentMethods();
    userPaymentsSuccess.value = isEdit ? "Способ оплаты обновлен" : "Способ оплаты добавлен";
    userPaymentEditorOpen.value = false;
    resetUserPaymentForm();
  } catch (error) {
    userPaymentsError.value = error instanceof Error ? error.message : String(error);
  } finally {
    userPaymentsLoading.value = false;
  }
}

async function deleteUserPaymentMethod(paymentMethodId) {
  if (!auth.value?.token) return;
  userPaymentsError.value = "";
  userPaymentsSuccess.value = "";
  userPaymentsLoading.value = true;
  try {
    const response = await fetch(`${apiBase}/api/user/payment-methods/${paymentMethodId}`, {
      method: "DELETE",
      headers: {
        Authorization: `Bearer ${auth.value.token}`,
      },
    });
    const payload = await response.json();
    if (!response.ok) {
      userPaymentsError.value = payload.error || "Не удалось удалить способ оплаты";
      return;
    }
    if (userPaymentEditId.value === paymentMethodId) {
      resetUserPaymentForm();
    }
    await loadUserPaymentMethods();
    userPaymentsSuccess.value = "Способ оплаты удален";
  } catch (error) {
    userPaymentsError.value = error instanceof Error ? error.message : String(error);
  } finally {
    userPaymentsLoading.value = false;
  }
}

async function loadUserPrivacy() {
  if (!auth.value?.token) return;
  userPrivacyLoading.value = true;
  userPrivacyError.value = "";
  try {
    const response = await fetch(`${apiBase}/api/user/privacy`, {
      headers: { Authorization: `Bearer ${auth.value.token}` },
    });
    const payload = await response.json();
    if (!response.ok) {
      userPrivacyError.value = payload.error || "Не удалось загрузить настройки конфиденциальности";
      return;
    }
    userPrivacyForm.value = {
      show_profile_in_reviews: !!payload.show_profile_in_reviews,
      allow_email_notifications: !!payload.allow_email_notifications,
      allow_sms_notifications: !!payload.allow_sms_notifications,
    };
  } catch (error) {
    userPrivacyError.value = error instanceof Error ? error.message : String(error);
  } finally {
    userPrivacyLoading.value = false;
  }
}

async function saveUserPrivacy() {
  if (!auth.value?.token) return;
  userPrivacySaving.value = true;
  userPrivacyError.value = "";
  userPrivacySuccess.value = "";
  try {
    const response = await fetch(`${apiBase}/api/user/privacy`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${auth.value.token}`,
      },
      body: JSON.stringify(userPrivacyForm.value),
    });
    const payload = await response.json();
    if (!response.ok) {
      userPrivacyError.value = payload.error || "Не удалось сохранить настройки конфиденциальности";
      return;
    }
    userPrivacyForm.value = {
      show_profile_in_reviews: !!payload.show_profile_in_reviews,
      allow_email_notifications: !!payload.allow_email_notifications,
      allow_sms_notifications: !!payload.allow_sms_notifications,
    };
    userPrivacySuccess.value = "Настройки конфиденциальности сохранены";
  } catch (error) {
    userPrivacyError.value = error instanceof Error ? error.message : String(error);
  } finally {
    userPrivacySaving.value = false;
  }
}

async function loadUserCabinetData() {
  userProfileSuccess.value = "";
  userPaymentsSuccess.value = "";
  userPrivacySuccess.value = "";
  userPaymentEditorOpen.value = false;
  resetUserPaymentForm();
  await loadUserProfile();
  await loadUserBookings();
  await loadUserFavorites();
  await loadUserPaymentMethods();
  await loadUserPrivacy();
}

function formatCabinetDate(isoDate) {
  if (!isoDate) return "Дата уточняется";
  const dt = new Date(isoDate);
  if (Number.isNaN(dt.getTime())) return "Дата уточняется";
  return dt.toLocaleString("ru-RU", {
    day: "numeric",
    month: "long",
    hour: "2-digit",
    minute: "2-digit",
  });
}

async function submitCreateUser() {
  if (!auth.value?.token) return;
  createUserLoading.value = true;
  createUserError.value = "";
  createUserSuccess.value = "";
  try {
    const response = await fetch(`${apiBase}/api/admin/users`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${auth.value.token}`,
      },
      body: JSON.stringify(createUserForm.value),
    });
    const payload = await response.json();
    if (!response.ok) {
      createUserError.value = payload.error || "Не удалось создать пользователя";
      return;
    }
    createUserSuccess.value = `Создан ${payload.role}: ${payload.login}`;
    createUserForm.value = {
      full_name: "",
      login: "",
      password: "",
      user_type: "user",
    };
  } catch (error) {
    createUserError.value = error instanceof Error ? error.message : String(error);
  } finally {
    createUserLoading.value = false;
  }
}

function handleRoute() {
  if (currentPath.value === "/") {
    loadPublicEvents();
    if (auth.value?.role === "user") {
      loadUserFavorites();
    } else {
      userFavorites.value = [];
      favoriteEventIds.value = [];
    }
    return;
  }

  const ticketEventId = getEventTicketsIdFromPath(currentPath.value);
  if (ticketEventId) {
    if (!auth.value) {
      setPendingAuthRedirect(currentPath.value);
      navigate("/login");
      return;
    }
    if (auth.value.role !== "user") {
      navigate("/cabinet");
      return;
    }
    loadTicketSelection(ticketEventId);
    return;
  }

  const paymentReservationId = getReservationPaymentIdFromPath(currentPath.value);
  if (paymentReservationId) {
    if (!auth.value) {
      setPendingAuthRedirect(currentPath.value);
      navigate("/login");
      return;
    }
    if (auth.value.role !== "user") {
      navigate("/cabinet");
      return;
    }
    loadReservationPayment(paymentReservationId);
    return;
  }

  const publicEventId = getEventIdFromPath(currentPath.value);
  if (publicEventId) {
    loadPublicEventDetail(publicEventId);
    return;
  }

  if (currentPath.value === "/cabinet") {
    if (!auth.value) {
      navigate("/login");
      return;
    }
    if (auth.value.role === "admin") {
      adminTab.value = "create-user";
    }
    loadProfile();
  }

  if (currentPath.value === "/admin") {
    navigate("/cabinet");
  }
}

const city = ref("Москва");
const search = ref("");
const selectedDateKey = ref(null);
const showFiltersPanel = ref(false);
const filters = ref({
  priceFrom: "",
  priceTo: "",
  priceSort: "",
  ageLabel: "",
  venueName: "",
});
const calendarTrack = ref(null);
const stickyMonthRef = ref(null);
const stickyMonthLabel = ref("");
const stickyMonthLeft = ref(0);
const currentMonthIndex = ref(0);
const calendarScrollLeft = ref(0);
const calendarStep = ref(54);

const events = ref([]);
const publicEventsLoading = ref(false);
const publicEventsError = ref("");
const publicEventLoading = ref(false);
const publicEventError = ref("");
const publicEvent = ref(null);
const ticketSelectionLoading = ref(false);
const ticketSelectionError = ref("");
const ticketSelectionData = ref(null);
const selectedTicketSessionId = ref(null);
const selectedTicketTypeId = ref(null);
const selectedSeatIds = ref([]);
const reservationLoading = ref(false);
const reservationError = ref("");
const reservationSuccess = ref("");
const latestReservation = ref(null);
const paymentPageLoading = ref(false);
const paymentPageError = ref("");
const paymentPageSuccess = ref("");
const reservationPayment = ref(null);
const selectedPaymentMethodId = ref(null);
const paymentSubmitting = ref(false);
const paymentCountdownSec = ref(0);
let paymentTimerHandle = null;

const filteredEvents = computed(() => {
  const q = search.value.trim().toLowerCase();
  const priceFrom = Number(filters.value.priceFrom);
  const priceTo = Number(filters.value.priceTo);
  const filtered = events.value.filter((e) => {
    const haystack = `${e.title} ${e.venue} ${e.venueCity || ""}`.toLowerCase();
    const matchesSearch = !q || haystack.includes(q);
    const matchesDate = !selectedDateKey.value || e.date_key === selectedDateKey.value;
    const matchesVenue = !filters.value.venueName || e.venueName === filters.value.venueName;
    const eventPrice = Number(e.price);
    const matchesPriceFrom =
      !filters.value.priceFrom || !Number.isFinite(priceFrom) || (Number.isFinite(eventPrice) && eventPrice >= priceFrom);
    const matchesPriceTo =
      !filters.value.priceTo || !Number.isFinite(priceTo) || (Number.isFinite(eventPrice) && eventPrice <= priceTo);
    const matchesAge = !filters.value.ageLabel || ageLabelFromRange(e.ageMin, e.ageMax) === filters.value.ageLabel;
    return matchesSearch && matchesDate && matchesVenue && matchesPriceFrom && matchesPriceTo && matchesAge;
  });

  if (!filters.value.priceSort) {
    return filtered;
  }

  return [...filtered].sort((a, b) => {
    const priceA = Number(a.price);
    const priceB = Number(b.price);
    const safeA = Number.isFinite(priceA) ? priceA : Number.POSITIVE_INFINITY;
    const safeB = Number.isFinite(priceB) ? priceB : Number.POSITIVE_INFINITY;
    return filters.value.priceSort === "asc" ? safeA - safeB : safeB - safeA;
  });
});

const availableEventVenues = computed(() =>
  [...new Set(events.value.map((event) => event.venueName).filter(Boolean))].sort((a, b) =>
    a.localeCompare(b, "ru")
  )
);

function resetEventFilters() {
  filters.value = {
    priceFrom: "",
    priceTo: "",
    priceSort: "",
    ageLabel: "",
    venueName: "",
  };
}

function dateKeyFromIso(isoDate) {
  if (!isoDate) return null;
  const dt = new Date(isoDate);
  if (Number.isNaN(dt.getTime())) return null;
  const y = dt.getFullYear();
  const m = String(dt.getMonth() + 1).padStart(2, "0");
  const d = String(dt.getDate()).padStart(2, "0");
  return `${y}-${m}-${d}`;
}

function toggleCalendarDate(key) {
  selectedDateKey.value = selectedDateKey.value === key ? null : key;
}

function formatEventDateTime(isoDate) {
  if (!isoDate) return "Дата уточняется";
  const dt = new Date(isoDate);
  return dt.toLocaleString("ru-RU", {
    day: "numeric",
    month: "long",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function formatEventDetailDate(isoDate) {
  if (!isoDate) return "Дата уточняется";
  return new Date(isoDate).toLocaleString("ru-RU", {
    day: "numeric",
    month: "long",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function bookingStatusLabel(status) {
  if (status === "paid") return "Оплачен";
  if (status === "awaiting_payment") return "Ожидает оплату";
  return status || "Неизвестно";
}

function organizerEventStatusLabel(status) {
  if (status === "draft") return "Черновик";
  if (status === "on_moderation") return "На модерации";
  if (status === "published") return "Опубликовано";
  if (status === "rejected") return "Отклонено";
  if (status === "archived") return "Архив";
  return status || "Неизвестно";
}

function resetAdminNearbyPlaceForm() {
  adminNearbyPlaceEditId.value = null;
  adminNearbyImagePreview.value = "";
  adminNearbyPlaceForm.value = {
    venue_id: "",
    title: "",
    description: "",
    working_hours: "",
    average_check: "",
    travel_time_minutes: "",
    image: null,
    clear_image: false,
  };
}

function refundStatusLabel(status) {
  if (status === "requested") return "Запрошен";
  if (status === "approved") return "Одобрен";
  if (status === "processing") return "В обработке";
  if (status === "succeeded") return "Выполнен";
  if (status === "rejected") return "Отклонен";
  return status || "—";
}

function formatDaysLeft(days) {
  const n = Number(days);
  if (!Number.isFinite(n)) return "дата уточняется";
  if (n <= 0) return "сегодня";
  if (n === 1) return "1 день";
  if (n >= 2 && n <= 4) return `${n} дня`;
  return `${n} дней`;
}

function openTicketReceipt(booking, event) {
  if (event) event.stopPropagation();
  userRefundError.value = "";
  userRefundSuccess.value = "";
  ticketReceiptBooking.value = booking || null;
}

function closeTicketReceipt() {
  ticketReceiptBooking.value = null;
  refundConfirmBooking.value = null;
}

function openRefundConfirm(booking) {
  userRefundError.value = "";
  userRefundSuccess.value = "";
  refundConfirmBooking.value = booking || null;
}

function closeRefundConfirm() {
  refundConfirmBooking.value = null;
}

async function requestRefundForBooking() {
  const booking = refundConfirmBooking.value || ticketReceiptBooking.value;
  const orderId = booking?.order_id;
  if (!orderId || !auth.value?.token) return;
  userRefundLoading.value = true;
  userRefundError.value = "";
  userRefundSuccess.value = "";
  try {
    const response = await fetch(`${apiBase}/api/user/orders/${orderId}/refund-request`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${auth.value.token}`,
      },
    });
    const payload = await response.json();
    if (!response.ok) {
      userRefundError.value = payload.error || "Не удалось отправить заявку на возврат";
      return;
    }
    userRefundSuccess.value = "Заявка на возврат отправлена администратору";
    closeRefundConfirm();
    await loadUserBookings();
    if (ticketReceiptBooking.value?.order_id === orderId) {
      const updated = userCurrentBookings.value.find((item) => item.order_id === orderId);
      if (updated) ticketReceiptBooking.value = updated;
    }
  } catch (error) {
    userRefundError.value = error instanceof Error ? error.message : String(error);
  } finally {
    userRefundLoading.value = false;
  }
}

async function submitRegister() {
  registerLoading.value = true;
  registerError.value = "";
  try {
    const response = await fetch(`${apiBase}/api/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        full_name: registerForm.value.full_name,
        login: registerForm.value.login,
        password: registerForm.value.password,
      }),
    });
    const payload = await response.json();
    if (!response.ok) {
      registerError.value = payload.error || "Не удалось зарегистрироваться";
      return;
    }
    persistAuth({
      token: payload.token,
      role: payload.user.role,
      login: payload.user.login,
    });
    registerForm.value = { full_name: "", login: "", password: "" };
    const nextPath = popPendingAuthRedirect();
    navigate(nextPath || "/cabinet");
  } catch (error) {
    registerError.value = error instanceof Error ? error.message : String(error);
  } finally {
    registerLoading.value = false;
  }
}

async function loadUserFavorites() {
  if (!auth.value?.token || auth.value.role !== "user") {
    userFavorites.value = [];
    favoriteEventIds.value = [];
    return;
  }
  userFavoritesLoading.value = true;
  userFavoritesError.value = "";
  try {
    const response = await fetch(`${apiBase}/api/user/favorites`, {
      headers: { Authorization: `Bearer ${auth.value.token}` },
    });
    const payload = await response.json();
    if (!response.ok) {
      userFavoritesError.value = payload.error || "Не удалось загрузить избранное";
      return;
    }
    userFavorites.value = payload.events || [];
    favoriteEventIds.value = payload.event_ids || [];
  } catch (error) {
    userFavoritesError.value = error instanceof Error ? error.message : String(error);
  } finally {
    userFavoritesLoading.value = false;
  }
}

function isFavoriteEvent(eventId) {
  if (!auth.value || auth.value.role !== "user") return false;
  return favoriteEventIds.value.includes(eventId);
}

async function toggleFavorite(eventId, event) {
  if (event) event.stopPropagation();
  if (!eventId) return;
  if (!auth.value) {
    setPendingAuthRedirect(currentPath.value || "/");
    navigate("/login");
    return;
  }
  if (auth.value.role !== "user") {
    return;
  }

  const isFavorite = isFavoriteEvent(eventId);
  try {
    if (isFavorite) {
      const response = await fetch(`${apiBase}/api/user/favorites/${eventId}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${auth.value.token}` },
      });
      if (!response.ok) {
        const payload = await response.json();
        throw new Error(payload.error || "Не удалось удалить из избранного");
      }
      favoriteEventIds.value = favoriteEventIds.value.filter((id) => id !== eventId);
      userFavorites.value = userFavorites.value.filter((item) => item.event_id !== eventId);
      return;
    }

    const response = await fetch(`${apiBase}/api/user/favorites`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${auth.value.token}`,
      },
      body: JSON.stringify({ event_id: eventId }),
    });
    const payload = await response.json();
    if (!response.ok) {
      throw new Error(payload.error || "Не удалось добавить в избранное");
    }
    if (!favoriteEventIds.value.includes(eventId)) {
      favoriteEventIds.value = [...favoriteEventIds.value, eventId];
    }
    await loadUserFavorites();
  } catch (error) {
    publicEventsError.value = error instanceof Error ? error.message : String(error);
  }
}

function eventPrimarySession(eventPayload) {
  const sessionsList = Array.isArray(eventPayload?.sessions) ? eventPayload.sessions : [];
  const parsed = sessionsList
    .map((session) => ({
      ...session,
      ts: Date.parse(session?.starts_at || ""),
    }))
    .filter((session) => Number.isFinite(session.ts))
    .sort((a, b) => a.ts - b.ts);
  if (!parsed.length) return null;
  const now = Date.now();
  const upcoming = parsed.find((session) => session.ts >= now);
  return upcoming || parsed[0];
}

function eventMinPrice(eventPayload) {
  const sessionsList = Array.isArray(eventPayload?.sessions) ? eventPayload.sessions : [];
  let minPrice = null;
  sessionsList.forEach((session) => {
    (session?.ticket_types || []).forEach((ticket) => {
      const value = Number(ticket?.price);
      if (!Number.isFinite(value)) return;
      if (minPrice === null || value < minPrice) {
        minPrice = value;
      }
    });
  });
  return minPrice;
}

function formatPriceRu(value) {
  if (value == null) return "Цена уточняется";
  return `от ${new Intl.NumberFormat("ru-RU", { maximumFractionDigits: 0 }).format(value)} ₽`;
}

function eventAgeLabel(eventPayload) {
  if (!eventPayload) return "Для всей семьи";
  if (eventPayload.age_min == null && eventPayload.age_max == null) return "Для всей семьи";
  if (eventPayload.age_max == null) return `${eventPayload.age_min}+`;
  return `${eventPayload.age_min}-${eventPayload.age_max}`;
}

const activePublicSession = computed(() => eventPrimarySession(publicEvent.value));
const activePublicMinPrice = computed(() => eventMinPrice(publicEvent.value));
const eventInfoTab = ref("description");

const currentEventReviews = computed(() =>
  Array.isArray(publicEvent.value?.reviews) ? publicEvent.value.reviews : []
);

const reviewsAverage = computed(() => {
  if (!currentEventReviews.value.length) return null;
  const sum = currentEventReviews.value.reduce((acc, review) => acc + (Number(review.rating) || 0), 0);
  return sum / currentEventReviews.value.length;
});

const reviewsDistribution = computed(() => {
  const base = [5, 4, 3, 2, 1].map((stars) => ({ stars, count: 0 }));
  currentEventReviews.value.forEach((review) => {
    const rating = Math.max(1, Math.min(5, Math.round(Number(review.rating) || 0)));
    const row = base.find((item) => item.stars === rating);
    if (row) row.count += 1;
  });
  return base;
});

const reviewsMaxCount = computed(() =>
  reviewsDistribution.value.reduce((max, row) => Math.max(max, row.count), 0)
);

function formatReviewDate(isoDate) {
  if (!isoDate) return "";
  const dt = new Date(isoDate);
  if (Number.isNaN(dt.getTime())) return "";
  return dt.toLocaleDateString("ru-RU", {
    day: "numeric",
    month: "long",
    year: "numeric",
  });
}

watch(
  () => publicEvent.value?.event_id,
  () => {
    eventInfoTab.value = "description";
  }
);

async function fetchJsonWithRetry(url, options = {}, retries = 3, delayMs = 700) {
  let lastError = null;
  for (let i = 0; i < retries; i += 1) {
    try {
      const response = await fetch(url, options);
      const payload = await response.json();
      return { response, payload };
    } catch (error) {
      lastError = error;
      if (i < retries - 1) {
        await new Promise((resolve) => setTimeout(resolve, delayMs));
      }
    }
  }
  throw lastError instanceof Error ? lastError : new Error(String(lastError));
}

async function loadPublicEvents() {
  publicEventsLoading.value = true;
  publicEventsError.value = "";
  try {
    const { response, payload } = await fetchJsonWithRetry(`${apiBase}/api/events`);
    if (!response.ok) {
      publicEventsError.value = payload.error || "Не удалось загрузить мероприятия";
      return;
    }
    events.value = (payload.events || []).map((event) => ({
      id: event.event_id,
      title: event.title,
      date: formatEventDateTime(event.starts_at),
      date_key: dateKeyFromIso(event.starts_at),
      venue: event.venue_name || event.venue_address || "-",
      venueName: event.venue_name || "",
      venueCity: event.venue_city || "",
      price: event.min_price,
      ageMin: event.age_min,
      ageMax: event.age_max,
      cover_image_url: event.cover_image_url,
    }));
  } catch (error) {
    publicEventsError.value = error instanceof Error ? error.message : String(error);
  } finally {
    publicEventsLoading.value = false;
  }
}

function getEventIdFromPath(path) {
  const match = path.match(/^\/event\/(\d+)$/);
  return match ? Number(match[1]) : null;
}

function getEventTicketsIdFromPath(path) {
  const match = path.match(/^\/event\/(\d+)\/tickets$/);
  return match ? Number(match[1]) : null;
}

function getReservationPaymentIdFromPath(path) {
  const match = path.match(/^\/reservations\/(\d+)\/pay$/);
  return match ? Number(match[1]) : null;
}

const isTicketSelectionPath = computed(() => getEventTicketsIdFromPath(currentPath.value) !== null);
const isReservationPaymentPath = computed(() => getReservationPaymentIdFromPath(currentPath.value) !== null);

const ticketSessions = computed(() => ticketSelectionData.value?.sessions || []);

const activeTicketSession = computed(() => {
  if (!ticketSessions.value.length) return null;
  return (
    ticketSessions.value.find((s) => s.session_id === selectedTicketSessionId.value) ||
    ticketSessions.value[0]
  );
});

const activeTicketTypes = computed(() => activeTicketSession.value?.ticket_types || []);

const selectedTicketType = computed(() => {
  if (!activeTicketTypes.value.length) return null;
  return (
    activeTicketTypes.value.find((t) => t.ticket_type_id === selectedTicketTypeId.value) ||
    activeTicketTypes.value[0]
  );
});

const groupedSeats = computed(() => {
  const source = ticketSelectionData.value?.seats || [];
  const map = new Map();
  source.forEach((seat) => {
    const key = seat.row_number || "-";
    if (!map.has(key)) map.set(key, []);
    map.get(key).push(seat);
  });
  return Array.from(map.entries())
    .map(([row, seats]) => ({
      row,
      seats: seats.sort((a, b) => Number(a.seat_number) - Number(b.seat_number)),
    }))
    .sort((a, b) => Number(a.row) - Number(b.row));
});

const reservationTotal = computed(() => {
  const unitPrice = Number(selectedTicketType.value?.price);
  if (!Number.isFinite(unitPrice)) return null;
  return unitPrice * selectedSeatIds.value.length;
});

const serviceFeePerSeat = 80;

const seatsById = computed(() => {
  const map = new Map();
  (ticketSelectionData.value?.seats || []).forEach((seat) => {
    map.set(seat.seat_id, seat);
  });
  return map;
});

const selectedSeatItems = computed(() =>
  selectedSeatIds.value
    .map((seatId) => {
      const seat = seatsById.value.get(seatId);
      if (!seat) return null;
      return {
        seat_id: seatId,
        row_number: seat.row_number,
        seat_number: seat.seat_number,
      };
    })
    .filter(Boolean)
    .sort((a, b) => {
      if (a.row_number !== b.row_number) return Number(a.row_number) - Number(b.row_number);
      return Number(a.seat_number) - Number(b.seat_number);
    })
);

const reservationServiceFee = computed(() =>
  selectedSeatIds.value.length ? selectedSeatIds.value.length * serviceFeePerSeat : 0
);

const reservationGrandTotal = computed(() => {
  if (reservationTotal.value == null) return null;
  return reservationTotal.value + reservationServiceFee.value;
});

const activeUserPaymentMethods = computed(() =>
  (userPaymentMethods.value || []).filter((method) => method.status === "active")
);

const paymentTotalAmount = computed(() => {
  const base = Number(reservationPayment.value?.total_amount);
  if (!Number.isFinite(base)) return null;
  return base + serviceFeePerSeat * Number(reservationPayment.value?.qty || 0);
});

const selectedPaymentMethod = computed(() =>
  activeUserPaymentMethods.value.find((item) => item.payment_method_id === selectedPaymentMethodId.value) || null
);

function isSeatSelected(seatId) {
  return selectedSeatIds.value.includes(seatId);
}

function toggleSeatSelection(seat) {
  if (!seat?.is_available) return;
  const idx = selectedSeatIds.value.indexOf(seat.seat_id);
  if (idx >= 0) {
    selectedSeatIds.value.splice(idx, 1);
    return;
  }
  selectedSeatIds.value.push(seat.seat_id);
}

function clearSeatSelection() {
  selectedSeatIds.value = [];
}

function stopPaymentTimer() {
  if (paymentTimerHandle) {
    clearInterval(paymentTimerHandle);
    paymentTimerHandle = null;
  }
}

async function loadAdminRefunds() {
  if (!auth.value?.token) return;
  adminRefundsLoading.value = true;
  adminRefundsError.value = "";
  try {
    const response = await fetch(`${apiBase}/api/admin/refunds?status=requested`, {
      headers: {
        Authorization: `Bearer ${auth.value.token}`,
      },
    });
    const payload = await response.json();
    if (!response.ok) {
      adminRefundsError.value = payload.error || "Не удалось загрузить заявки на возврат";
      return;
    }
    adminRefunds.value = payload.items || [];
  } catch (error) {
    adminRefundsError.value = error instanceof Error ? error.message : String(error);
  } finally {
    adminRefundsLoading.value = false;
  }
}

async function adminReviewRefund(refundId, action) {
  if (!auth.value?.token) return;
  adminRefundsSuccess.value = "";
  adminRefundsError.value = "";
  const comment = (adminRefundRejectComment.value[refundId] || "").trim();
  if (action === "reject" && !comment) {
    adminRefundsError.value = "Укажите причину отклонения";
    return;
  }
  try {
    const response = await fetch(`${apiBase}/api/admin/refunds/${refundId}/review`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${auth.value.token}`,
      },
      body: JSON.stringify({
        action,
        admin_comment: comment,
      }),
    });
    const payload = await response.json();
    if (!response.ok) {
      adminRefundsError.value = payload.error || "Не удалось обработать заявку";
      return;
    }
    adminRefundsSuccess.value = action === "approve" ? "Возврат одобрен" : "Возврат отклонен";
    delete adminRefundRejectComment.value[refundId];
    await loadAdminRefunds();
  } catch (error) {
    adminRefundsError.value = error instanceof Error ? error.message : String(error);
  }
}

async function loadAdminModerationEvents() {
  if (!auth.value?.token) return;
  adminModerationEventsLoading.value = true;
  adminModerationEventsError.value = "";
  try {
    const response = await fetch(`${apiBase}/api/admin/events/moderation`, {
      headers: {
        Authorization: `Bearer ${auth.value.token}`,
      },
    });
    const payload = await response.json();
    if (!response.ok) {
      adminModerationEventsError.value =
        payload.error || "Не удалось загрузить мероприятия на модерации";
      return;
    }
    adminModerationEvents.value = payload.items || [];
  } catch (error) {
    adminModerationEventsError.value = error instanceof Error ? error.message : String(error);
  } finally {
    adminModerationEventsLoading.value = false;
  }
}

async function adminReviewEventModeration(eventId, action) {
  if (!auth.value?.token) return;
  adminModerationEventsSuccess.value = "";
  adminModerationEventsError.value = "";
  const comment = (adminModerationRejectComment.value[eventId] || "").trim();
  if (action === "reject" && !comment) {
    adminModerationEventsError.value = "Укажите причину отклонения";
    return;
  }
  try {
    const response = await fetch(`${apiBase}/api/admin/events/${eventId}/review`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${auth.value.token}`,
      },
      body: JSON.stringify({
        action,
        moderation_comment: comment,
      }),
    });
    const payload = await response.json();
    if (!response.ok) {
      adminModerationEventsError.value =
        payload.error || "Не удалось обработать мероприятие";
      return;
    }
    adminModerationEventsSuccess.value =
      action === "publish"
        ? "Мероприятие опубликовано"
        : "Мероприятие отклонено";
    delete adminModerationRejectComment.value[eventId];
    await loadAdminModerationEvents();
  } catch (error) {
    adminModerationEventsError.value = error instanceof Error ? error.message : String(error);
  }
}

async function loadAdminNearbyPlaces() {
  if (!auth.value?.token) return;
  adminNearbyPlacesLoading.value = true;
  adminNearbyPlacesError.value = "";
  try {
    const response = await fetch(`${apiBase}/api/admin/nearby-places`, {
      headers: {
        Authorization: `Bearer ${auth.value.token}`,
      },
    });
    const payload = await response.json();
    if (!response.ok) {
      adminNearbyPlacesError.value = payload.error || "Не удалось загрузить места рядом";
      return;
    }
    adminNearbyPlaces.value = payload.items || [];
    adminNearbyVenues.value = payload.venues || [];
  } catch (error) {
    adminNearbyPlacesError.value = error instanceof Error ? error.message : String(error);
  } finally {
    adminNearbyPlacesLoading.value = false;
  }
}

function onPickAdminNearbyImage(event) {
  const file = event.target.files?.[0];
  if (!file) return;
  adminNearbyPlaceForm.value.image = file;
  adminNearbyPlaceForm.value.clear_image = false;
  adminNearbyImagePreview.value = URL.createObjectURL(file);
  event.target.value = "";
}

function startEditAdminNearbyPlace(place) {
  adminNearbyPlaceEditId.value = place.place_id;
  adminNearbyImagePreview.value = place.image_url || "";
  adminNearbyPlaceForm.value = {
    venue_id: String(place.venue_id || ""),
    title: place.title || "",
    description: place.description || "",
    working_hours: place.working_hours || "",
    average_check: place.average_check || "",
    travel_time_minutes: place.travel_time_minutes || "",
    image: null,
    clear_image: false,
  };
}

function clearAdminNearbyImage() {
  adminNearbyPlaceForm.value.image = null;
  adminNearbyPlaceForm.value.clear_image = true;
  adminNearbyImagePreview.value = "";
}

async function submitAdminNearbyPlace() {
  if (!auth.value?.token) return;
  adminNearbyPlacesSuccess.value = "";
  adminNearbyPlacesError.value = "";
  const formData = new FormData();
  formData.append("venue_id", adminNearbyPlaceForm.value.venue_id);
  formData.append("title", adminNearbyPlaceForm.value.title);
  formData.append("description", adminNearbyPlaceForm.value.description);
  formData.append("working_hours", adminNearbyPlaceForm.value.working_hours);
  formData.append("average_check", adminNearbyPlaceForm.value.average_check);
  formData.append("travel_time_minutes", adminNearbyPlaceForm.value.travel_time_minutes);
  if (adminNearbyPlaceForm.value.image) {
    formData.append("image", adminNearbyPlaceForm.value.image);
  }
  if (adminNearbyPlaceForm.value.clear_image) {
    formData.append("clear_image", "1");
  }

  const isEdit = Boolean(adminNearbyPlaceEditId.value);
  const url = isEdit
    ? `${apiBase}/api/admin/nearby-places/${adminNearbyPlaceEditId.value}`
    : `${apiBase}/api/admin/nearby-places/create`;

  try {
    const response = await fetch(url, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${auth.value.token}`,
      },
      body: formData,
    });
    const payload = await response.json();
    if (!response.ok) {
      adminNearbyPlacesError.value = payload.error || "Не удалось сохранить место";
      return;
    }
    adminNearbyPlacesSuccess.value = isEdit ? "Место обновлено" : "Место добавлено";
    resetAdminNearbyPlaceForm();
    await loadAdminNearbyPlaces();
  } catch (error) {
    adminNearbyPlacesError.value = error instanceof Error ? error.message : String(error);
  }
}

async function deleteAdminNearbyPlace(placeId) {
  if (!auth.value?.token || !placeId) return;
  adminNearbyPlacesSuccess.value = "";
  adminNearbyPlacesError.value = "";
  try {
    const response = await fetch(`${apiBase}/api/admin/nearby-places/${placeId}`, {
      method: "DELETE",
      headers: {
        Authorization: `Bearer ${auth.value.token}`,
      },
    });
    const payload = await response.json();
    if (!response.ok) {
      adminNearbyPlacesError.value = payload.error || "Не удалось удалить место";
      return;
    }
    adminNearbyPlacesSuccess.value = "Место удалено";
    if (adminNearbyPlaceEditId.value === placeId) {
      resetAdminNearbyPlaceForm();
    }
    await loadAdminNearbyPlaces();
  } catch (error) {
    adminNearbyPlacesError.value = error instanceof Error ? error.message : String(error);
  }
}

function startPaymentTimer(expiresAtIso) {
  stopPaymentTimer();
  const update = () => {
    const expiresTs = Date.parse(expiresAtIso || "");
    if (!Number.isFinite(expiresTs)) {
      paymentCountdownSec.value = 0;
      stopPaymentTimer();
      return;
    }
    const left = Math.max(0, Math.floor((expiresTs - Date.now()) / 1000));
    paymentCountdownSec.value = left;
    if (left <= 0) {
      stopPaymentTimer();
      paymentPageError.value = "Время оплаты истекло. Бронирование отменено.";
      reservationPayment.value = null;
    }
  };
  update();
  paymentTimerHandle = setInterval(update, 1000);
}

function formatCountdown(totalSec) {
  const sec = Math.max(0, Number(totalSec) || 0);
  const mm = String(Math.floor(sec / 60)).padStart(2, "0");
  const ss = String(sec % 60).padStart(2, "0");
  return `${mm}:${ss}`;
}

function openTicketSelection(eventId) {
  if (!eventId) return;
  if (!auth.value?.token) {
    const path = `/event/${eventId}/tickets`;
    setPendingAuthRedirect(path);
    navigate("/login");
    return;
  }
  if (auth.value.role !== "user") {
    navigate("/cabinet");
    return;
  }
  navigate(`/event/${eventId}/tickets`);
}

async function loadTicketSelection(eventId) {
  if (!eventId) return;
  ticketSelectionLoading.value = true;
  ticketSelectionError.value = "";
  reservationError.value = "";
  reservationSuccess.value = "";
  selectedSeatIds.value = [];
  try {
    const { response, payload } = await fetchJsonWithRetry(`${apiBase}/api/events/${eventId}/seat-map`);
    if (!response.ok) {
      ticketSelectionError.value = payload.error || "Не удалось загрузить схему мест";
      return;
    }
    ticketSelectionData.value = payload;
    selectedTicketSessionId.value = payload.active_session_id || payload.sessions?.[0]?.session_id || null;
    selectedTicketTypeId.value =
      payload.sessions?.find((x) => x.session_id === selectedTicketSessionId.value)?.ticket_types?.[0]
        ?.ticket_type_id ||
      payload.sessions?.[0]?.ticket_types?.[0]?.ticket_type_id ||
      null;
  } catch (error) {
    ticketSelectionError.value = error instanceof Error ? error.message : String(error);
  } finally {
    ticketSelectionLoading.value = false;
  }
}

async function loadReservationPayment(reservationId) {
  if (!reservationId || !auth.value?.token) return;
  paymentPageLoading.value = true;
  paymentPageError.value = "";
  paymentPageSuccess.value = "";
  reservationPayment.value = null;
  selectedPaymentMethodId.value = null;
  stopPaymentTimer();
  try {
    await loadUserPaymentMethods();
    const response = await fetch(`${apiBase}/api/user/reservations/${reservationId}`, {
      headers: {
        Authorization: `Bearer ${auth.value.token}`,
      },
    });
    const payload = await response.json();
    if (!response.ok) {
      paymentPageError.value = payload.error || "Не удалось загрузить данные бронирования";
      return;
    }
    reservationPayment.value = payload;
    selectedPaymentMethodId.value = activeUserPaymentMethods.value[0]?.payment_method_id || null;
    startPaymentTimer(payload.expires_at);
  } catch (error) {
    paymentPageError.value = error instanceof Error ? error.message : String(error);
  } finally {
    paymentPageLoading.value = false;
  }
}

watch(selectedTicketSessionId, (sessionId) => {
  const session = ticketSessions.value.find((x) => x.session_id === sessionId);
  selectedTicketTypeId.value = session?.ticket_types?.[0]?.ticket_type_id || null;
  selectedSeatIds.value = [];
});

async function submitReservation() {
  if (!auth.value?.token) {
    setPendingAuthRedirect(currentPath.value);
    navigate("/login");
    return;
  }
  if (!ticketSelectionData.value?.event_id || !selectedTicketSessionId.value || !selectedTicketTypeId.value) {
    reservationError.value = "Недостаточно данных для бронирования";
    return;
  }
  if (!selectedSeatIds.value.length) {
    reservationError.value = "Выберите хотя бы одно место";
    return;
  }

  reservationLoading.value = true;
  reservationError.value = "";
  reservationSuccess.value = "";
  latestReservation.value = null;
  try {
    const response = await fetch(`${apiBase}/api/user/reservations`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${auth.value.token}`,
      },
      body: JSON.stringify({
        event_id: ticketSelectionData.value.event_id,
        session_id: selectedTicketSessionId.value,
        ticket_type_id: selectedTicketTypeId.value,
        seat_ids: selectedSeatIds.value,
      }),
    });
    const payload = await response.json();
    if (!response.ok) {
      reservationError.value = payload.error || "Не удалось создать бронирование";
      if (payload.unavailable_seat_ids?.length) {
        selectedSeatIds.value = selectedSeatIds.value.filter((sid) => !payload.unavailable_seat_ids.includes(sid));
      }
      return;
    }
    reservationSuccess.value = `Бронирование #${payload.reservation_id} создано до ${formatCabinetDate(payload.expires_at)}`;
    latestReservation.value = payload;
    await loadTicketSelection(ticketSelectionData.value.event_id);
  } catch (error) {
    reservationError.value = error instanceof Error ? error.message : String(error);
  } finally {
    reservationLoading.value = false;
  }
}

function goToPayment() {
  const reservationId = latestReservation.value?.reservation_id;
  if (!reservationId) return;
  navigate(`/reservations/${reservationId}/pay`);
}

async function submitReservationPayment() {
  if (!auth.value?.token) {
    setPendingAuthRedirect(currentPath.value);
    navigate("/login");
    return;
  }
  const reservationId = reservationPayment.value?.reservation_id || getReservationPaymentIdFromPath(currentPath.value);
  if (!reservationId) {
    paymentPageError.value = "Бронирование не найдено";
    return;
  }
  paymentSubmitting.value = true;
  paymentPageError.value = "";
  paymentPageSuccess.value = "";
  try {
    const response = await fetch(`${apiBase}/api/user/reservations/${reservationId}/pay`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${auth.value.token}`,
      },
      body: JSON.stringify({
        payment_method_id: selectedPaymentMethodId.value || null,
      }),
    });
    const payload = await response.json();
    if (!response.ok) {
      paymentPageError.value = payload.error || "Не удалось выполнить оплату";
      return;
    }
    paymentPageSuccess.value = `Оплата прошла успешно. Заказ #${payload.order_id}`;
    stopPaymentTimer();
    latestReservation.value = null;
    reservationPayment.value = null;
    setTimeout(() => navigate("/cabinet"), 700);
  } catch (error) {
    paymentPageError.value = error instanceof Error ? error.message : String(error);
  } finally {
    paymentSubmitting.value = false;
  }
}

async function loadPublicEventDetail(eventId) {
  if (!eventId) return;
  publicEventLoading.value = true;
  publicEventError.value = "";
  publicEvent.value = null;
  try {
    const { response, payload } = await fetchJsonWithRetry(`${apiBase}/api/events/${eventId}`);
    if (!response.ok) {
      publicEventError.value = payload.error || "Не удалось загрузить мероприятие";
      return;
    }
    publicEvent.value = payload;
  } catch (error) {
    publicEventError.value = error instanceof Error ? error.message : String(error);
  } finally {
    publicEventLoading.value = false;
  }
}

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

const calendarStart = new Date();
calendarStart.setHours(0, 0, 0, 0);
const calendarEnd = new Date(calendarStart);
calendarEnd.setDate(calendarEnd.getDate() + 365);
const calendarDays = buildCalendarDays(calendarStart, calendarEnd);
stickyMonthLabel.value = calendarDays[0]?.monthLabel || monthNames[new Date().getMonth()];

const monthStarts = computed(() => {
  const starts = [];
  for (let i = 0; i < calendarDays.length; i += 1) {
    if (i === 0 || calendarDays[i].monthKey !== calendarDays[i - 1].monthKey) {
      starts.push({
        monthKey: calendarDays[i].monthKey,
        label: calendarDays[i].monthLabel,
        startIndex: i,
      });
    }
  }
  return starts;
});

function findMonthByCellIndex(cellIndex) {
  const safe = Math.max(0, Math.min(cellIndex, calendarDays.length - 1));
  return calendarDays[safe]?.monthLabel || "";
}

function findMonthStartIndexByCell(cellIndex) {
  let idx = 0;
  for (let i = 0; i < monthStarts.value.length; i += 1) {
    if (monthStarts.value[i].startIndex <= cellIndex) idx = i;
    else break;
  }
  return idx;
}

function floatingMonthLeft(startIndex) {
  return startIndex * calendarStep.value - calendarScrollLeft.value;
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

function scrollCalendar(direction) {
  if (!calendarTrack.value) return;
  calendarTrack.value.scrollBy({ left: direction * 420, behavior: "smooth" });
}

let onPopState = null;
let onCalendarScroll = null;
let onWindowResize = null;
let boundCalendarTrack = null;

function detachCalendarListeners() {
  if (boundCalendarTrack && onCalendarScroll) {
    boundCalendarTrack.removeEventListener("scroll", onCalendarScroll);
  }
  if (onWindowResize) {
    window.removeEventListener("resize", onWindowResize);
  }
  boundCalendarTrack = null;
  onCalendarScroll = null;
  onWindowResize = null;
}

async function attachCalendarListenersIfNeeded() {
  if (currentPath.value !== "/") {
    detachCalendarListeners();
    return;
  }
  await nextTick();
  if (!calendarTrack.value) return;

  if (boundCalendarTrack === calendarTrack.value && onCalendarScroll && onWindowResize) {
    updateStickyMonth();
    return;
  }

  detachCalendarListeners();
  onCalendarScroll = () => updateStickyMonth();
  onWindowResize = () => updateStickyMonth();
  calendarTrack.value.addEventListener("scroll", onCalendarScroll, { passive: true });
  window.addEventListener("resize", onWindowResize);
  boundCalendarTrack = calendarTrack.value;
  updateStickyMonth();
}

onMounted(async () => {
  await nextTick();
  onPopState = () => {
    currentPath.value = window.location.pathname || "/";
    handleRoute();
  };
  window.addEventListener("popstate", onPopState);

  handleRoute();
  await attachCalendarListenersIfNeeded();
});

watch(currentPath, async () => {
  if (!isReservationPaymentPath.value) {
    stopPaymentTimer();
  }
  await attachCalendarListenersIfNeeded();
});

watch(adminTab, async (tab) => {
  if (tab === "refunds" && auth.value?.role === "admin") {
    await loadAdminRefunds();
    return;
  }
  if (tab === "event-moderation" && auth.value?.role === "admin") {
    await loadAdminModerationEvents();
    return;
  }
  if (tab === "nearby-places" && auth.value?.role === "admin") {
    await loadAdminNearbyPlaces();
  }
});

watch(
  () => auth.value?.role,
  async (role) => {
    if (role === "user") {
      await loadUserFavorites();
      return;
    }
    userFavorites.value = [];
    favoriteEventIds.value = [];
  }
);

onUnmounted(() => {
  if (onPopState) window.removeEventListener("popstate", onPopState);
  detachCalendarListeners();
  stopPaymentTimer();
});
</script>

<template>
  <div class="page-bg">
    <main v-if="currentPath === '/'" class="screen">
      <header class="header">
        <div class="logo-wrap">
          <span class="logo-star" aria-hidden="true"></span>
          <div class="logo-text">Путь</div>
        </div>

        <div class="search-box">
          <span class="search-icon">⌕</span>
          <input v-model="search" type="text" placeholder="Событие, Персона, Площадка" />
        </div>

        <div class="right-controls">
          <div class="city">{{ city }}</div>
          <button class="icon-btn" title="Карта" aria-label="Карта">
            <svg class="icon-svg" viewBox="0 0 24 24" aria-hidden="true">
              <path d="M12 21s7-7 7-12a7 7 0 1 0-14 0c0 5 7 12 7 12z" />
              <circle cx="12" cy="9" r="2.5" />
            </svg>
          </button>
          <button class="icon-btn" title="Избранное" aria-label="Избранное" @click="openFavoritesFromHeader">
            <svg class="icon-svg" viewBox="0 0 24 24" aria-hidden="true">
              <path
                d="M12 20.5 4.8 13.8A4.9 4.9 0 0 1 12 7.6a4.9 4.9 0 0 1 7.2 6.2L12 20.5z"
              />
            </svg>
          </button>
          <button
            class="icon-btn"
            title="Личный кабинет"
            aria-label="Личный кабинет"
            @click="openCabinetFromHeader"
          >
            <svg class="icon-svg" viewBox="0 0 24 24" aria-hidden="true">
              <circle cx="12" cy="8" r="3.5" />
              <path d="M5 19a7 7 0 0 1 14 0" />
            </svg>
          </button>
          <button class="icon-btn cart-btn" title="Корзина" aria-label="Корзина">
            <svg class="icon-svg" viewBox="0 0 24 24" aria-hidden="true">
              <circle cx="9" cy="19" r="1.5" />
              <circle cx="17" cy="19" r="1.5" />
              <path d="M3 5h2l2 10h10l2-7H7" />
            </svg>
          </button>
        </div>
      </header>

      <section class="hero">
        <img :src="heroBanner" alt="Баннер" />
      </section>

      <h1 class="title">Афиша Москвы</h1>

      <section class="calendar">
        <div class="calendar-wrap">
          <button class="cal-arrow" aria-label="Назад" @click="scrollCalendar(-1)">&#8249;</button>
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
            <div ref="stickyMonthRef" class="sticky-month" :style="{ left: `${stickyMonthLeft}px` }">
              {{ stickyMonthLabel }}
            </div>
            <div ref="calendarTrack" class="calendar-track">
              <div class="calendar-days">
                <button
                  v-for="d in calendarDays"
                  :key="d.key"
                  class="day-cell"
                  :class="{ weekend: d.weekend, selected: selectedDateKey === d.key }"
                  @click="toggleCalendarDate(d.key)"
                >
                  <span class="num">{{ d.day }}</span>
                  <span class="dow">{{ d.dow }}</span>
                </button>
              </div>
            </div>
          </div>
          <button class="cal-arrow" aria-label="Вперед" @click="scrollCalendar(1)">&#8250;</button>
        </div>
      </section>

      <section class="controls">
        <div class="left-controls">
          <button class="soft" @click="showFiltersPanel = !showFiltersPanel">
            Фильтры
          </button>
        </div>
      </section>

      <section v-if="showFiltersPanel" class="filters-panel">
        <div class="filters-grid">
          <label>
            Цена от
            <input v-model="filters.priceFrom" type="number" min="0" placeholder="0" />
          </label>
          <label>
            Цена до
            <input v-model="filters.priceTo" type="number" min="0" placeholder="10000" />
          </label>
          <label>
            Сортировка цены
            <select v-model="filters.priceSort">
              <option value="">Без сортировки</option>
              <option value="asc">По возрастанию</option>
              <option value="desc">По убыванию</option>
            </select>
          </label>
          <label>
            Возраст
            <select v-model="filters.ageLabel">
              <option value="">Любой возраст</option>
              <option v-for="option in ageOptions" :key="`filter-age-${option.label}`" :value="option.label">
                {{ option.label }}
              </option>
            </select>
          </label>
          <label>
            Место проведения
            <select v-model="filters.venueName">
              <option value="">Любая площадка</option>
              <option v-for="venueName in availableEventVenues" :key="`filter-venue-${venueName}`" :value="venueName">
                {{ venueName }}
              </option>
            </select>
          </label>
        </div>
        <div class="filters-actions">
          <button class="link-btn" @click="resetEventFilters">Сбросить</button>
        </div>
      </section>

      <section class="cards">
        <p v-if="publicEventsLoading">Загрузка мероприятий...</p>
        <p v-else-if="publicEventsError" class="error">{{ publicEventsError }}</p>
        <template v-else-if="filteredEvents.length">
          <article
            v-for="event in filteredEvents"
            :key="event.id"
            class="card main-event-card clickable"
            @click="navigate(`/event/${event.id}`)"
          >
            <button
              class="favorite-heart"
              :class="{ active: isFavoriteEvent(event.id) }"
              @click="toggleFavorite(event.id, $event)"
              aria-label="Избранное"
            >
              <svg viewBox="0 0 24 24" aria-hidden="true">
                <path d="M12 20.5 4.8 13.8A4.9 4.9 0 0 1 12 7.6a4.9 4.9 0 0 1 7.2 6.2L12 20.5z" />
              </svg>
            </button>
            <img
              v-if="event.cover_image_url"
              class="poster"
              :src="event.cover_image_url"
              :alt="event.title"
            />
            <div v-else class="poster poster-1"></div>
            <div v-if="event.price" class="price">ОТ {{ event.price }} ₽</div>
            <h2>{{ event.title }}</h2>
            <p>{{ event.date }}<br />{{ event.venue }}</p>
          </article>
        </template>
        <article v-else class="card">
          <div class="poster poster-1"></div>
          <h2>События не найдены</h2>
        </article>
      </section>
    </main>

    <main v-else-if="currentPath.startsWith('/event/') && !isTicketSelectionPath" class="screen event-screen">
      <header class="header">
        <div class="logo-wrap" @click="navigate('/')" style="cursor: pointer;">
          <span class="logo-star" aria-hidden="true"></span>
          <div class="logo-text">Путь</div>
        </div>

        <div class="search-box">
          <span class="search-icon">⌕</span>
          <input v-model="search" type="text" placeholder="Событие, Персона, Площадка" />
        </div>

        <div class="right-controls">
          <div class="city">{{ city }}</div>
          <button
            class="icon-btn"
            title="Личный кабинет"
            aria-label="Личный кабинет"
            @click="openCabinetFromHeader"
          >
            <svg class="icon-svg" viewBox="0 0 24 24" aria-hidden="true">
              <circle cx="12" cy="8" r="3.5" />
              <path d="M5 19a7 7 0 0 1 14 0" />
            </svg>
          </button>
        </div>
      </header>

      <p v-if="publicEventLoading">Загрузка мероприятия...</p>
      <p v-else-if="publicEventError" class="error">{{ publicEventError }}</p>
      <section v-else-if="publicEvent" class="event-detail-page">
        <button class="link-btn" @click="navigate('/')">← На главную</button>

        <h1 class="event-title">{{ publicEvent.title }}</h1>

        <div class="event-top-grid">
          <img
            v-if="publicEvent.cover_image_url"
            :src="publicEvent.cover_image_url"
            class="event-cover-large"
            alt="cover"
          />
          <div v-else class="event-cover-large no-cover">Без фото</div>

          <aside class="event-side">
            <div class="event-chip">{{ publicEvent.category_name || "Событие" }}</div>
            <div class="event-row"><b>Возраст:</b> {{ eventAgeLabel(publicEvent) }}</div>
            <div class="event-row"><b>Цена:</b> {{ formatPriceRu(activePublicMinPrice) }}</div>
            <div class="event-row"><b>Город:</b> {{ publicEvent.venue_city || "-" }}</div>
            <div class="event-row"><b>Адрес:</b> {{ publicEvent.venue_address || "-" }}</div>
            <div class="event-row">
              <b>Дата:</b>
              {{ activePublicSession ? formatEventDetailDate(activePublicSession.starts_at) : "Дата уточняется" }}
            </div>
            <button class="yellow-btn tickets-btn" @click="openTicketSelection(publicEvent.event_id)">
              Выбрать билеты
            </button>
          </aside>
        </div>

        <section class="event-tabs-row">
          <button
            class="event-tab-btn"
            :class="{ active: eventInfoTab === 'description' }"
            @click="eventInfoTab = 'description'"
          >
            Описание
          </button>
          <button
            class="event-tab-btn"
            :class="{ active: eventInfoTab === 'reviews' }"
            @click="eventInfoTab = 'reviews'"
          >
            Отзывы
          </button>
        </section>

        <section class="event-description-block">
          <template v-if="eventInfoTab === 'description'">
            <h2>Описание</h2>
            <p class="long-text">{{ publicEvent.description || "Описание отсутствует" }}</p>
          </template>

          <template v-else>
            <h2>Отзывы</h2>
            <div class="reviews-head">
              <div class="reviews-summary">
                <div class="reviews-average">
                  {{ reviewsAverage == null ? "—" : reviewsAverage.toFixed(1) }}
                </div>
                <div class="reviews-count">
                  {{ currentEventReviews.length ? `На основе ${currentEventReviews.length} оценок` : "Пока нет оценок" }}
                </div>
              </div>
              <div class="reviews-bars">
                <div v-for="row in reviewsDistribution" :key="row.stars" class="reviews-bar-row">
                  <div class="stars-label">{{ "★".repeat(row.stars) }}</div>
                  <div class="bar-track">
                    <div
                      class="bar-fill"
                      :style="{ width: `${reviewsMaxCount ? (row.count / reviewsMaxCount) * 100 : 0}%` }"
                    ></div>
                  </div>
                  <div class="bar-count">{{ row.count }}</div>
                </div>
              </div>
            </div>

            <div v-if="!currentEventReviews.length" class="reviews-empty">
              Отзывов по этому мероприятию пока нет.
            </div>

            <div v-else class="reviews-list">
              <article v-for="(review, idx) in currentEventReviews" :key="review.review_id || idx" class="review-card">
                <div class="review-top">
                  <div class="review-author">{{ review.author_name || "Пользователь" }}</div>
                  <div class="review-date">{{ formatReviewDate(review.created_at) }}</div>
                </div>
                <div class="review-rating">{{ "★".repeat(Math.max(1, Math.min(5, Math.round(Number(review.rating) || 0)))) }}</div>
                <p class="review-text">{{ review.text || "Без текста" }}</p>
              </article>
            </div>
          </template>
        </section>

        <section class="event-nearby-block">
          <h2 class="nearby-title">Места рядом</h2>
          <div v-if="publicEvent.nearby_places?.length" class="nearby-grid">
            <article v-for="place in publicEvent.nearby_places" :key="`nearby-${place.place_id}`" class="nearby-card">
              <img v-if="place.image_url" :src="place.image_url" :alt="place.title" class="nearby-card-image" />
              <div v-else class="nearby-card-image nearby-card-empty">Без фото</div>
              <div class="nearby-card-tags">
                <span v-if="place.average_check" class="nearby-chip">Ср чек {{ place.average_check }} ₽</span>
                <span v-if="place.travel_time_minutes" class="nearby-chip nearby-chip-light">
                  {{ place.travel_time_minutes }} мин
                </span>
              </div>
              <h3>{{ place.title }}</h3>
              <p>{{ place.description || "Описание отсутствует" }}</p>
              <div class="nearby-meta">
                <span v-if="place.working_hours">Часы работы: {{ place.working_hours }}</span>
                <span v-if="place.average_check">Средний чек: {{ place.average_check }} ₽</span>
              </div>
            </article>
          </div>
          <div v-else class="empty-nearby">Пока нет добавленных мест рядом</div>
        </section>
      </section>
    </main>

    <main v-else-if="isTicketSelectionPath" class="screen ticket-screen">
      <div class="ticket-breadcrumb">
        <button class="crumb-link" @click="navigate(`/event/${ticketSelectionData?.event_id || getEventTicketsIdFromPath(currentPath)}`)">
          ← Выбор мест - Бронирование
        </button>
      </div>

      <p v-if="ticketSelectionLoading">Загрузка схемы мест...</p>
      <p v-else-if="ticketSelectionError" class="error">{{ ticketSelectionError }}</p>

      <section v-else-if="ticketSelectionData" class="ticket-layout">
        <div class="ticket-left">
          <div class="ticket-left-head">
            <h2 class="ticket-map-title">Выбор мест</h2>
            <div class="ticket-timer">15:00</div>
          </div>

          <div class="hall-stage">СЦЕНА</div>
          <div class="seat-map">
            <div v-for="row in groupedSeats" :key="`row-${row.row}`" class="seat-row">
              <div class="row-label">{{ row.row }}</div>
              <div class="row-seats">
                <button
                  v-for="seat in row.seats"
                  :key="seat.seat_id"
                  class="seat-btn"
                  :class="{
                    selected: isSeatSelected(seat.seat_id),
                    unavailable: !seat.is_available,
                  }"
                  :disabled="!seat.is_available"
                  @click="toggleSeatSelection(seat)"
                >
                  {{ seat.seat_number }}
                </button>
              </div>
            </div>
          </div>

          <div class="seat-legend">
            <span class="legend-chip selected">Выбрано</span>
            <span class="legend-chip available">Доступно</span>
            <span class="legend-chip unavailable">Занято</span>
          </div>

          <button class="soft clear-seat-btn" @click="clearSeatSelection">Очистить выбор</button>
        </div>

        <aside class="ticket-right">
          <div class="ticket-event-card">
            <img
              v-if="ticketSelectionData.cover_image_url"
              class="ticket-event-cover"
              :src="ticketSelectionData.cover_image_url"
              :alt="ticketSelectionData.title"
            />
            <div v-else class="ticket-event-cover ticket-event-cover-fallback"></div>

            <div class="ticket-event-main">
              <h3>{{ ticketSelectionData.title }}</h3>
              <div class="ticket-event-meta">
                {{ activeTicketSession ? formatEventDetailDate(activeTicketSession.starts_at) : "Дата уточняется" }}
              </div>
              <div class="ticket-event-meta">{{ ticketSelectionData.venue_name }}, {{ ticketSelectionData.venue_address }}</div>
            </div>
          </div>

          <div class="ticket-controls">
            <label>
              Сеанс
              <select v-model.number="selectedTicketSessionId">
                <option v-for="session in ticketSessions" :key="session.session_id" :value="session.session_id">
                  {{ formatEventDetailDate(session.starts_at) }}
                </option>
              </select>
            </label>
            <label>
              Тип билета
              <select v-model.number="selectedTicketTypeId">
                <option
                  v-for="ticketType in activeTicketTypes"
                  :key="ticketType.ticket_type_id"
                  :value="ticketType.ticket_type_id"
                >
                  {{ ticketType.name }} · {{ ticketType.price }} {{ ticketType.currency }}
                </option>
              </select>
            </label>
          </div>

          <h2 class="ticket-order-title">Выбранные места</h2>
          <div v-if="selectedSeatItems.length" class="ticket-order-seats">
            <div v-for="seat in selectedSeatItems" :key="seat.seat_id" class="ticket-order-seat-row">
              <span>Ряд {{ seat.row_number }}, место {{ seat.seat_number }}</span>
              <span>{{ selectedTicketType ? `${selectedTicketType.price} ₽` : "—" }}</span>
            </div>
          </div>
          <div v-else class="ticket-order-empty">Пока не выбрано ни одного места</div>

          <div class="ticket-order-totals">
            <div class="ticket-order-line">
              <span>Цена билетов x{{ selectedSeatIds.length }}</span>
              <span>{{ reservationTotal == null ? "—" : `${reservationTotal} ₽` }}</span>
            </div>
            <div class="ticket-order-line">
              <span>Работа сервиса</span>
              <span>{{ reservationServiceFee }} ₽</span>
            </div>
            <div class="ticket-order-line total">
              <span>Итого</span>
              <span>{{ reservationGrandTotal == null ? "—" : `${reservationGrandTotal} ₽` }}</span>
            </div>
          </div>

          <button class="yellow-btn tickets-btn ticket-confirm-btn" :disabled="reservationLoading" @click="submitReservation">
            {{ reservationLoading ? "Бронируем..." : "Подтвердить бронирование" }}
          </button>
          <p v-if="reservationError" class="error">{{ reservationError }}</p>
          <p v-if="reservationSuccess" class="success">{{ reservationSuccess }}</p>
          <button
            v-if="latestReservation?.reservation_id"
            class="yellow-btn tickets-btn pay-btn"
            @click="goToPayment"
          >
            Оплатить
          </button>
        </aside>
      </section>
    </main>

    <main v-else-if="isReservationPaymentPath" class="screen payment-screen">
      <div class="ticket-breadcrumb">
        <button
          class="crumb-link"
          @click="navigate(reservationPayment?.event_id ? `/event/${reservationPayment.event_id}/tickets` : '/')"
        >
          ← Бронирование - Оплата
        </button>
      </div>

      <h1 class="payment-title">Оплата заказа</h1>
      <p class="payment-subtitle">Безопасная оплата</p>

      <p v-if="paymentPageLoading">Загрузка данных оплаты...</p>
      <p v-else-if="paymentPageError" class="error">{{ paymentPageError }}</p>

      <section v-else-if="reservationPayment" class="payment-layout">
        <section class="payment-left">
          <h2>Способ оплаты</h2>
          <div class="payment-methods-row">
            <button
              v-for="method in activeUserPaymentMethods"
              :key="method.payment_method_id"
              class="soft payment-method-btn"
              :class="{ active: selectedPaymentMethodId === method.payment_method_id }"
              @click="selectedPaymentMethodId = method.payment_method_id"
            >
              {{ method.card_brand || "Банковская карта" }} •••• {{ method.card_last4 || "0000" }}
            </button>
            <button class="soft payment-method-btn" @click="navigate('/cabinet')">Добавить карту</button>
          </div>

          <div class="payment-card-preview">
            <div class="payment-field">
              <span>Номер карты</span>
              <strong>{{ selectedPaymentMethod?.card_last4 ? `•••• •••• •••• ${selectedPaymentMethod.card_last4}` : "Не выбрано" }}</strong>
            </div>
            <div class="payment-field">
              <span>Срок действия</span>
              <strong>{{ selectedPaymentMethod?.expires_at || "--/--" }}</strong>
            </div>
            <div class="payment-field">
              <span>Владелец</span>
              <strong>{{ selectedPaymentMethod?.holder_name || (profile?.full_name || "Пользователь") }}</strong>
            </div>
          </div>

          <button
            class="yellow-btn payment-submit-btn"
            :disabled="paymentSubmitting || !selectedPaymentMethodId"
            @click="submitReservationPayment"
          >
            {{ paymentSubmitting ? "Оплачиваем..." : "Оплатить" }}
          </button>
          <p v-if="paymentPageSuccess" class="success">{{ paymentPageSuccess }}</p>
        </section>

        <aside class="payment-right">
          <div class="payment-timer">
            Оплатить до: <b>{{ formatCountdown(paymentCountdownSec) }}</b>
          </div>

          <div class="ticket-event-card">
            <img
              v-if="reservationPayment.cover_image_url"
              class="ticket-event-cover"
              :src="reservationPayment.cover_image_url"
              :alt="reservationPayment.title"
            />
            <div v-else class="ticket-event-cover ticket-event-cover-fallback"></div>
            <div class="ticket-event-main">
              <h3>{{ reservationPayment.title }}</h3>
              <div class="ticket-event-meta">{{ formatEventDetailDate(reservationPayment.starts_at) }}</div>
              <div class="ticket-event-meta">{{ reservationPayment.venue_city }}, {{ reservationPayment.venue_address }}</div>
            </div>
          </div>

          <h3 class="ticket-order-title">Бронирование #{{ reservationPayment.reservation_id }}</h3>
          <div class="ticket-order-seats">
            <div v-for="seat in reservationPayment.selected_seats" :key="seat.seat_id" class="ticket-order-seat-row">
              <span>Ряд {{ seat.row_number }}, место {{ seat.seat_number }}</span>
              <span>{{ reservationPayment.unit_price }} ₽</span>
            </div>
          </div>

          <div class="ticket-order-totals">
            <div class="ticket-order-line">
              <span>Цена билетов x{{ reservationPayment.qty }}</span>
              <span>{{ reservationPayment.total_amount }} ₽</span>
            </div>
            <div class="ticket-order-line">
              <span>Работа сервиса</span>
              <span>{{ serviceFeePerSeat * reservationPayment.qty }} ₽</span>
            </div>
            <div class="ticket-order-line total">
              <span>Итоговая стоимость</span>
              <span>{{ paymentTotalAmount == null ? "—" : `${paymentTotalAmount} ₽` }}</span>
            </div>
          </div>
        </aside>
      </section>
    </main>

    <main v-else-if="currentPath === '/login'" class="auth-screen">
      <section class="auth-card">
        <h1>Вход</h1>
        <label>
          Логин
          <input v-model="loginForm.login" type="text" autocomplete="off" />
        </label>
        <label>
          Пароль
          <input
            v-model="loginForm.password"
            type="password"
            autocomplete="new-password"
            @keyup.enter="submitLogin"
          />
        </label>
        <div class="login-actions">
          <button class="auth-submit" :disabled="loginLoading" @click="submitLogin">
            {{ loginLoading ? "Входим..." : "Войти" }}
          </button>
          <button class="link-btn" @click="navigate('/register')">Зарегистрироваться</button>
          <button class="link-btn" @click="navigate('/')">На главную</button>
        </div>
        <p v-if="loginError" class="error">{{ loginError }}</p>
      </section>
    </main>

    <main v-else-if="currentPath === '/register'" class="auth-screen">
      <section class="auth-card">
        <h1>Регистрация</h1>
        <label>
          ФИО
          <input v-model="registerForm.full_name" type="text" autocomplete="off" />
        </label>
        <label>
          Логин
          <input
            v-model="registerForm.login"
            type="text"
            autocomplete="off"
            placeholder="email или телефон"
          />
        </label>
        <label>
          Пароль
          <input
            v-model="registerForm.password"
            type="password"
            autocomplete="new-password"
            @keyup.enter="submitRegister"
          />
        </label>
        <div class="login-actions">
          <button class="auth-submit" :disabled="registerLoading" @click="submitRegister">
            {{ registerLoading ? "Регистрируем..." : "Зарегистрироваться" }}
          </button>
          <button class="link-btn" @click="navigate('/login')">Уже есть аккаунт</button>
          <button class="link-btn" @click="navigate('/')">На главную</button>
        </div>
        <p v-if="registerError" class="error">{{ registerError }}</p>
      </section>
    </main>

    <main v-else-if="currentPath === '/cabinet'" class="cabinet-screen">
      <section v-if="profile?.role === 'organizer'" class="admin-cabinet">
        <div class="cabinet-top">
          <div class="cabinet-breadcrumb">
            <button class="crumb-link" @click="navigate('/')">Главная</button>
            <span>- Личный кабинет</span>
          </div>
          <button class="link-btn top-exit" @click="logout">Выйти</button>
        </div>
        <h1 class="cabinet-title">Личный кабинет</h1>
        <p v-if="profileLoading">Загрузка профиля...</p>
        <p v-if="profileError" class="error">{{ profileError }}</p>
        <p v-if="organizerLoading">Загрузка данных компании...</p>
        <p v-if="organizerError" class="error">{{ organizerError }}</p>
        <p v-if="organizerSuccess" class="success">{{ organizerSuccess }}</p>

        <div class="cabinet-grid">
          <aside class="cabinet-menu">
            <button
              class="cabinet-menu-item"
              :class="{ active: organizerTab === 'events' }"
              @click="organizerTab = 'events'"
            >
              Мероприятия
            </button>
            <button
              class="cabinet-menu-item"
              :class="{ active: organizerTab === 'company' }"
              @click="organizerTab = 'company'"
            >
              Профиль компании
            </button>
            <button class="cabinet-menu-item" disabled>Верификация</button>
          </aside>

          <div class="cabinet-content">
            <section v-if="organizerTab === 'events'" class="cabinet-block">
              <div class="cabinet-block-head">
                <h2>Мероприятия</h2>
                <button class="auth-submit" @click="toggleCreateEventForm">
                  {{ showCreateEventForm ? "Отмена" : "Создать мероприятие" }}
                </button>
              </div>
              <div class="row-line"></div>

              <div v-if="showCreateEventForm" class="event-create-form">
                <h3 class="section-title">Основное</h3>
                <label>
                  Название мероприятия
                  <input v-model="newEvent.title" type="text" />
                </label>
                <label>
                  Описание мероприятия
                  <textarea v-model="newEvent.description" rows="5"></textarea>
                </label>
                <label>
                  Категория
                  <select v-model="newEvent.category_name">
                    <option disabled value="">Выберите категорию</option>
                    <option v-for="option in categoryOptions" :key="option" :value="option">
                      {{ option }}
                    </option>
                  </select>
                </label>

                <div class="age-section">
                  <div class="age-title">Возраст</div>
                  <div class="age-chips">
                    <button
                      v-for="option in ageOptions"
                      :key="option.label"
                      class="age-chip"
                      :class="{ active: selectedAgeOption === option.label }"
                      @click="selectedAgeOption = option.label"
                    >
                      {{ option.label }}
                    </button>
                  </div>
                </div>

                <label>
                  Город
                  <select v-model="newEvent.venue_city">
                    <option disabled value="">Выбрать</option>
                    <option v-for="city in cityOptions" :key="city" :value="city">
                      {{ city }}
                    </option>
                  </select>
                </label>
                <label>
                  Адрес
                  <select v-model="newEvent.venue_address" :disabled="!newEvent.venue_city">
                    <option disabled value="">Выбрать</option>
                    <option
                      v-for="address in addressOptionsByCity[newEvent.venue_city] || []"
                      :key="address"
                      :value="address"
                    >
                      {{ address }}
                    </option>
                  </select>
                </label>

                <div class="row-line"></div>
                <h3 class="section-title">Сеансы</h3>
                <div v-if="sessions.length" class="sessions-list">
                  <div v-for="(session, idx) in sessions" :key="`${session.date}-${idx}`" class="session-item">
                    <span>{{ formatSessionDate(session.date) }}</span>
                    <span>{{ formatSessionRange(session.start_time, session.end_time) }}</span>
                    <button class="mini-link" @click="removeSession(idx)" aria-label="Удалить сеанс">✕</button>
                  </div>
                </div>
                <div class="session-grid">
                  <label>
                    Дата
                    <input v-model="sessionDraft.date" type="date" />
                  </label>
                  <label>
                    Время начала
                    <input v-model="sessionDraft.start_time" type="time" />
                  </label>
                  <label>
                    Время окончания
                    <input v-model="sessionDraft.end_time" type="time" />
                  </label>
                  <button class="yellow-btn" @click="addSession">+ добавить сеанс</button>
                </div>

                <h3 class="section-title">Билеты</h3>
                <div v-if="ticketTypes.length" class="sessions-list">
                  <div v-for="(ticket, idx) in ticketTypes" :key="`${ticket.name}-${idx}`" class="session-item">
                    <span>{{ ticket.name }}</span>
                    <span>{{ ticket.price }} {{ ticket.currency }} / {{ ticket.qty_total || "в€ћ" }}</span>
                    <button class="mini-link" @click="removeTicketType(idx)" aria-label="Удалить билет">✕</button>
                  </div>
                </div>
                <div class="ticket-grid">
                  <label>
                    Тип билета
                    <input v-model="ticketDraft.name" type="text" placeholder="Например, Стандарт" />
                  </label>
                  <label>
                    Цена
                    <input v-model="ticketDraft.price" type="number" min="0" step="0.01" />
                  </label>
                  <label>
                    Количество
                    <input v-model="ticketDraft.qty_total" type="number" min="0" />
                  </label>
                </div>
                <button class="mini-link add-ticket" @click="addTicketType">+ Добавить тип билета</button>

                <h3 class="section-title">Фото карточки мероприятия</h3>
                <label class="upload-box compact file-upload">
                  <input ref="coverInputRef" type="file" accept="image/*" @change="onPickCoverFile" />
                  <span>Загрузите главное фото</span>
                  <div v-if="eventCoverPreview" class="preview-wrap cover-wrap">
                    <button class="preview-remove" @click.prevent="removeCoverImage">вњ•</button>
                    <img :src="eventCoverPreview" class="upload-preview cover" alt="cover" />
                  </div>
                </label>

                <h3 class="section-title">Галерея мероприятия</h3>
                <label class="upload-box compact file-upload">
                  <input
                    ref="galleryInputRef"
                    type="file"
                    accept="image/*"
                    multiple
                    @change="onPickGalleryFiles"
                  />
                  <span>Загрузите до 5 фото галереи</span>
                  <div v-if="eventGalleryItems.length" class="upload-gallery">
                    <div v-for="(img, idx) in eventGalleryItems" :key="`${img.url}-${idx}`" class="preview-wrap">
                      <button class="preview-remove" @click.prevent="removeGalleryImage(idx)">вњ•</button>
                      <img :src="img.url" class="upload-preview" alt="gallery" />
                    </div>
                  </div>
                </label>

                <div class="event-actions">
                  <button class="cancel-btn" @click="showCreateEventForm = false">Отмена</button>
                  <div class="event-actions-right">
                    <button class="auth-submit save-btn" @click="createOrganizerEvent('draft')">
                      Сохранить
                    </button>
                    <button class="yellow-btn publish" @click="createOrganizerEvent('published')">
                      Отправить на модерацию
                    </button>
                  </div>
                </div>

              </div>

              <p v-if="organizerEventsLoading">Загрузка мероприятий...</p>
              <p v-if="organizerEventsError" class="error">{{ organizerEventsError }}</p>
              <p v-if="!organizerEventsLoading && !organizerEvents.length">Пока нет мероприятий</p>

              <div v-if="organizerEvents.length" class="events-list cards-view">
                <button
                  v-for="event in organizerEvents"
                  :key="event.event_id"
                  class="event-item event-card"
                  @click="openOrganizerEventForEdit(event.event_id)"
                >
                  <img
                    v-if="event.cover_image_url"
                    :src="event.cover_image_url"
                    alt="cover"
                    class="event-card-cover"
                  />
                  <div v-else class="event-card-cover no-cover">Без фото</div>
                  <div class="event-card-title">{{ event.title }}</div>
                  <div class="event-meta">
                    Статус: {{ organizerEventStatusLabel(event.status) }}
                  </div>
                  <div class="event-meta">{{ event.category || "Без категории" }}</div>
                  <div v-if="event.status === 'rejected' && event.moderation_comment" class="event-meta reject-reason">
                    Причина: {{ event.moderation_comment }}
                  </div>
                </button>
              </div>

            </section>

            <template v-if="organizerTab === 'company'">
            <section class="cabinet-block">
              <div class="cabinet-block-head">
                <h2>Информация о компании</h2>
                <span class="status-pill">Информация видна на сайте</span>
                <button class="link-btn" @click="editCompany = !editCompany">
                  {{ editCompany ? "Отмена" : "Изменить" }}
                </button>
              </div>
              <div class="row-line"></div>
              <div class="cabinet-info-grid">
                <div>Название</div>
                <div v-if="!editCompany">{{ organizerCompany.display_name || "-" }}</div>
                <input v-else v-model="organizerCompany.display_name" type="text" />
                <div>Телефон</div>
                <div v-if="!editCompany">{{ organizerCompany.phone || "-" }}</div>
                <input v-else v-model="organizerCompany.phone" type="text" />
                <div>Telegram</div>
                <div v-if="!editCompany">{{ organizerCompany.telegram || "-" }}</div>
                <input v-else v-model="organizerCompany.telegram" type="text" />
                <div>Whatsapp</div>
                <div v-if="!editCompany">{{ organizerCompany.whatsapp || "-" }}</div>
                <input v-else v-model="organizerCompany.whatsapp" type="text" />
                <div>Сайт</div>
                <div v-if="!editCompany">{{ organizerCompany.website_url || "-" }}</div>
                <input v-else v-model="organizerCompany.website_url" type="text" />
                <div>Адрес</div>
                <div v-if="!editCompany">{{ organizerCompany.address_text || "-" }}</div>
                <input v-else v-model="organizerCompany.address_text" type="text" />
                <div>Контактное лицо</div>
                <div v-if="!editCompany">{{ organizerCompany.contact_person || "-" }}</div>
                <input v-else v-model="organizerCompany.contact_person" type="text" />
              </div>
              <button v-if="editCompany" class="auth-submit" @click="saveOrganizerSection('company')">
                Сохранить
              </button>
            </section>

            <section class="cabinet-block">
              <div class="cabinet-block-head">
                <h2>О компании</h2>
                <button class="link-btn" @click="editAbout = !editAbout">
                  {{ editAbout ? "Отмена" : "Изменить" }}
                </button>
              </div>
              <div class="row-line"></div>
              <p v-if="!editAbout" class="long-text">
                {{ organizerCompany.about_text || "Описание пока не заполнено" }}
              </p>
              <textarea
                v-else
                v-model="organizerCompany.about_text"
                class="about-textarea"
                rows="5"
              ></textarea>
              <button v-if="editAbout" class="auth-submit" @click="saveOrganizerSection('about')">
                Сохранить
              </button>
            </section>

            <section class="cabinet-block">
              <div class="cabinet-block-head">
                <h2>Реквизиты</h2>
                <button class="link-btn" @click="editDetails = !editDetails">
                  {{ editDetails ? "Отмена" : "Изменить" }}
                </button>
              </div>
              <div class="row-line"></div>
              <div class="cabinet-info-grid">
                <div>Краткое наименование</div>
                <div v-if="!editDetails">{{ organizerDetails.short_legal_name || "-" }}</div>
                <input v-else v-model="organizerDetails.short_legal_name" type="text" />
                <div>Полное наименование</div>
                <div v-if="!editDetails">{{ organizerDetails.full_legal_name || "-" }}</div>
                <input v-else v-model="organizerDetails.full_legal_name" type="text" />
                <div>Юридический адрес</div>
                <div v-if="!editDetails">{{ organizerDetails.legal_address || "-" }}</div>
                <input v-else v-model="organizerDetails.legal_address" type="text" />
                <div>ИНН</div>
                <div v-if="!editDetails">{{ organizerDetails.inn || "-" }}</div>
                <input v-else v-model="organizerDetails.inn" type="text" />
                <div>ОГРН</div>
                <div v-if="!editDetails">{{ organizerDetails.ogrn || "-" }}</div>
                <input v-else v-model="organizerDetails.ogrn" type="text" />
                <div>КПП</div>
                <div v-if="!editDetails">{{ organizerDetails.kpp || "-" }}</div>
                <input v-else v-model="organizerDetails.kpp" type="text" />
                <div>Дата регистрации</div>
                <div v-if="!editDetails">{{ organizerDetails.registration_date || "-" }}</div>
                <input v-else v-model="organizerDetails.registration_date" type="date" />
              </div>
              <button v-if="editDetails" class="auth-submit" @click="saveOrganizerSection('details')">
                Сохранить
              </button>
            </section>

            <section class="cabinet-block">
              <div class="cabinet-block-head">
                <h2>Верификация по документам</h2>
                <button class="auth-submit">Отправить</button>
              </div>
              <div class="row-line"></div>
              <div class="upload-box">Переместите файлы сюда или загрузите из документов</div>
            </section>
            </template>
          </div>
        </div>

      </section>

      <section v-else-if="profile?.role === 'user'" class="admin-cabinet">
        <div class="cabinet-top">
          <div class="cabinet-breadcrumb">
            <button class="crumb-link" @click="navigate('/')">Главная</button>
            <span>- Личный кабинет</span>
          </div>
          <button class="link-btn top-exit" @click="logout">Выйти</button>
        </div>
        <h1 class="cabinet-title">Личный кабинет</h1>
        <p v-if="profileLoading || userProfileLoading || userBookingsLoading || userPaymentsLoading || userPrivacyLoading">Загрузка профиля...</p>
        <p v-if="profileError" class="error">{{ profileError }}</p>
        <p v-if="userProfileError" class="error">{{ userProfileError }}</p>
        <p v-if="userBookingsError" class="error">{{ userBookingsError }}</p>
        <p v-if="userPaymentsError" class="error">{{ userPaymentsError }}</p>
        <p v-if="userPrivacyError" class="error">{{ userPrivacyError }}</p>
        <p v-if="userProfileSuccess" class="success">{{ userProfileSuccess }}</p>
        <p v-if="userPaymentsSuccess" class="success">{{ userPaymentsSuccess }}</p>
        <p v-if="userPrivacySuccess" class="success">{{ userPrivacySuccess }}</p>

        <div class="cabinet-grid">
          <aside class="cabinet-menu">
            <button
              class="cabinet-menu-item"
              :class="{ active: userCabinetTab === 'profile' }"
              @click="userCabinetTab = 'profile'"
            >
              Профиль
            </button>
            <button
              class="cabinet-menu-item"
              :class="{ active: userCabinetTab === 'current' }"
              @click="userCabinetTab = 'current'"
            >
              Текущие бронирования
            </button>
            <button
              class="cabinet-menu-item"
              :class="{ active: userCabinetTab === 'history' }"
              @click="userCabinetTab = 'history'"
            >
              История бронирований
            </button>
            <button
              class="cabinet-menu-item"
              :class="{ active: userCabinetTab === 'favorites' }"
              @click="userCabinetTab = 'favorites'"
            >
              Избранное
            </button>
            <button
              class="cabinet-menu-item"
              :class="{ active: userCabinetTab === 'payments' }"
              @click="userCabinetTab = 'payments'"
            >
              Платежные данные
            </button>
            <button
              class="cabinet-menu-item"
              :class="{ active: userCabinetTab === 'privacy' }"
              @click="userCabinetTab = 'privacy'"
            >
              Конфиденциальность
            </button>
          </aside>

          <div class="cabinet-content">
            <section v-if="userCabinetTab === 'profile'" class="cabinet-block">
              <div class="cabinet-block-head">
                <h2>Профиль</h2>
                <button class="link-btn" @click="userProfileEdit = !userProfileEdit">
                  {{ userProfileEdit ? "Отмена" : "Изменить" }}
                </button>
              </div>
              <div class="row-line"></div>
              <div class="cabinet-info-grid">
                <div>Имя</div>
                <div v-if="!userProfileEdit">{{ userProfileForm.first_name || "-" }}</div>
                <input v-else v-model="userProfileForm.first_name" type="text" />
                <div>Фамилия</div>
                <div v-if="!userProfileEdit">{{ userProfileForm.last_name || "-" }}</div>
                <input v-else v-model="userProfileForm.last_name" type="text" />
                <div>Телефон</div>
                <div v-if="!userProfileEdit">{{ userProfileForm.phone || "-" }}</div>
                <input v-else v-model="userProfileForm.phone" type="text" />
                <div>Почта</div>
                <div v-if="!userProfileEdit">{{ userProfileForm.email || "-" }}</div>
                <input v-else v-model="userProfileForm.email" type="email" />
              </div>
              <button v-if="userProfileEdit" class="auth-submit" :disabled="userProfileSaving" @click="saveUserProfile">
                {{ userProfileSaving ? "Сохраняем..." : "Сохранить" }}
              </button>
            </section>

            <section v-if="userCabinetTab === 'current'" class="cabinet-block">
              <div class="cabinet-block-head">
                <h2>Текущие бронирования</h2>
              </div>
              <div class="row-line"></div>
              <p v-if="!userCurrentBookings.length">Пока нет текущих бронирований</p>
              <div v-else class="user-booking-cards">
                <article
                  v-for="booking in userCurrentBookings"
                  :key="`cur-${booking.order_id || booking.reservation_id}`"
                  class="card main-event-card clickable user-booking-card"
                  @click="booking.event_id && navigate(`/event/${booking.event_id}`)"
                >
                  <img
                    v-if="booking.cover_image_url"
                    class="poster"
                    :src="booking.cover_image_url"
                    :alt="booking.event_title || 'Событие'"
                  />
                  <div v-else class="poster poster-1"></div>
                  <h2>{{ booking.event_title || "Событие" }}</h2>
                  <p>
                    {{ formatEventDateTime(booking.starts_at) }}<br />
                    {{ booking.venue_name || "-" }}
                  </p>
                  <div class="booking-meta-grid">
                    <div class="booking-muted">Статус: {{ bookingStatusLabel(booking.status) }}</div>
                    <div class="booking-muted">Билетов: {{ booking.ticket_qty || 0 }}</div>
                    <div class="booking-muted">Сумма: {{ booking.total_amount || 0 }} {{ booking.currency || "RUB" }}</div>
                    <div class="booking-muted">До события: {{ formatDaysLeft(booking.days_left) }}</div>
                    <div v-if="booking.refund?.status" class="booking-muted">
                      Возврат: {{ refundStatusLabel(booking.refund.status) }}
                    </div>
                    <div v-if="booking.refund?.status === 'rejected' && booking.refund?.admin_comment" class="booking-muted">
                      Причина: {{ booking.refund.admin_comment }}
                    </div>
                  </div>
                  <button class="yellow-btn booking-ticket-btn" @click="openTicketReceipt(booking, $event)">Билет</button>
                </article>
              </div>

              <div v-if="ticketReceiptBooking" class="receipt-overlay" @click="closeTicketReceipt">
                <div class="receipt-modal" @click.stop>
                  <button class="receipt-close" @click="closeTicketReceipt">×</button>
                  <h3>Кассовый чек</h3>
                  <div class="receipt-line"><span>Заказ:</span><b>#{{ ticketReceiptBooking.order_id }}</b></div>
                  <div class="receipt-line"><span>Событие:</span><b>{{ ticketReceiptBooking.event_title }}</b></div>
                  <div class="receipt-line"><span>Дата сеанса:</span><b>{{ formatEventDateTime(ticketReceiptBooking.starts_at) }}</b></div>
                  <div class="receipt-line"><span>Площадка:</span><b>{{ ticketReceiptBooking.venue_name || "-" }}</b></div>
                  <div class="receipt-line"><span>Статус:</span><b>{{ bookingStatusLabel(ticketReceiptBooking.status) }}</b></div>
                  <div class="receipt-divider"></div>
                  <div
                    v-for="(ticket, idx) in (ticketReceiptBooking.tickets || [])"
                    :key="`ticket-check-${idx}`"
                    class="receipt-line"
                  >
                    <span>
                      {{ ticket.ticket_type || "Билет" }}
                      <template v-if="ticket.row_number && ticket.seat_number">
                        · ряд {{ ticket.row_number }}, место {{ ticket.seat_number }}
                      </template>
                    </span>
                    <b>{{ ticket.unit_price }} {{ ticket.currency }}</b>
                  </div>
                  <div class="receipt-divider"></div>
                  <div class="receipt-line"><span>Количество билетов</span><b>{{ ticketReceiptBooking.ticket_qty || 0 }}</b></div>
                  <div class="receipt-line total"><span>ИТОГО</span><b>{{ ticketReceiptBooking.total_amount }} {{ ticketReceiptBooking.currency || "RUB" }}</b></div>
                  <div v-if="ticketReceiptBooking.refund?.status" class="receipt-line">
                    <span>Статус возврата</span>
                    <b>{{ refundStatusLabel(ticketReceiptBooking.refund.status) }}</b>
                  </div>
                  <div
                    v-if="ticketReceiptBooking.refund?.status === 'rejected' && ticketReceiptBooking.refund?.admin_comment"
                    class="receipt-line"
                  >
                    <span>Причина отказа</span>
                    <b>{{ ticketReceiptBooking.refund.admin_comment }}</b>
                  </div>
                  <button
                    v-if="!ticketReceiptBooking.refund || ticketReceiptBooking.refund.status === 'rejected'"
                    class="refund-btn"
                    :disabled="userRefundLoading"
                    @click="openRefundConfirm(ticketReceiptBooking)"
                  >
                    Вернуть билет
                  </button>
                  <p v-if="userRefundError" class="error">{{ userRefundError }}</p>
                  <p v-if="userRefundSuccess" class="success">{{ userRefundSuccess }}</p>
                  <div class="receipt-qr">QR</div>
                </div>
              </div>

              <div v-if="refundConfirmBooking" class="receipt-overlay" @click="closeRefundConfirm">
                <div class="refund-confirm-modal" @click.stop>
                  <h3>Подтверждение возврата</h3>
                  <p>Вы уверены, что хотите отправить заявку на возврат билета по заказу #{{ refundConfirmBooking.order_id }}?</p>
                  <div class="refund-confirm-actions">
                    <button class="link-btn" @click="closeRefundConfirm">Отмена</button>
                    <button class="refund-btn" :disabled="userRefundLoading" @click="requestRefundForBooking">
                      {{ userRefundLoading ? "Отправляем..." : "Подтвердить возврат" }}
                    </button>
                  </div>
                </div>
              </div>
            </section>

            <section v-if="userCabinetTab === 'history'" class="cabinet-block">
              <div class="cabinet-block-head">
                <h2>История бронирований</h2>
              </div>
              <div class="row-line"></div>
              <p v-if="!userHistoryBookings.length">Пока нет завершенных бронирований</p>
              <div v-else class="booking-list">
                <article v-for="order in userHistoryBookings" :key="`ord-${order.order_id}`" class="booking-card">
                  <div class="booking-head">
                    <div>Заказ #{{ order.order_id }}</div>
                    <div class="booking-muted">
                      {{ order.total_amount }} {{ order.currency }} В· {{ order.status }}
                    </div>
                  </div>
                  <div class="booking-muted">Создан: {{ formatCabinetDate(order.created_at) }}</div>
                  <div v-for="(ticket, idx) in order.tickets" :key="`ord-${order.order_id}-${idx}`" class="booking-item-row">
                    <div class="booking-item-title">{{ ticket.event_title || "Событие" }}</div>
                    <div class="booking-muted">{{ formatCabinetDate(ticket.starts_at) }} В· {{ ticket.venue_name || "-" }}</div>
                    <div class="booking-muted">{{ ticket.ticket_type || "Билет" }} · {{ ticket.unit_price }} {{ ticket.currency }}</div>
                  </div>
                </article>
              </div>
            </section>

            <section v-if="userCabinetTab === 'favorites'" class="cabinet-block">
              <div class="cabinet-block-head">
                <h2>Избранное</h2>
              </div>
              <div class="row-line"></div>
              <p v-if="userFavoritesLoading">Загрузка избранного...</p>
              <p v-if="userFavoritesError" class="error">{{ userFavoritesError }}</p>
              <p v-if="!userFavoritesLoading && !userFavorites.length">В избранном пока нет мероприятий</p>
              <div v-else class="user-booking-cards">
                <article
                  v-for="event in userFavorites"
                  :key="`fav-${event.event_id}`"
                  class="card main-event-card clickable"
                  @click="navigate(`/event/${event.event_id}`)"
                >
                  <button
                    class="favorite-heart active"
                    @click="toggleFavorite(event.event_id, $event)"
                    aria-label="Убрать из избранного"
                  >
                    <svg viewBox="0 0 24 24" aria-hidden="true">
                      <path d="M12 20.5 4.8 13.8A4.9 4.9 0 0 1 12 7.6a4.9 4.9 0 0 1 7.2 6.2L12 20.5z" />
                    </svg>
                  </button>
                  <img
                    v-if="event.cover_image_url"
                    class="poster"
                    :src="event.cover_image_url"
                    :alt="event.title"
                  />
                  <div v-else class="poster poster-1"></div>
                  <div v-if="event.min_price" class="price">ОТ {{ event.min_price }} ₽</div>
                  <h2>{{ event.title }}</h2>
                  <p>{{ formatEventDateTime(event.starts_at) }}<br />{{ event.venue_name || "-" }}</p>
                </article>
              </div>
            </section>

            <section v-if="userCabinetTab === 'payments'" class="cabinet-block">
              <div class="cabinet-block-head">
                <h2>Платежные данные</h2>
                <button class="auth-submit" @click="openAddPaymentEditor">Добавить карту</button>
              </div>
              <div class="row-line"></div>

              <div v-if="userPaymentEditorOpen" class="payment-form">
                <label>
                  Название банка/карты
                  <input v-model="userPaymentForm.card_brand" type="text" placeholder="Например: Альфа Банк" />
                </label>
                <label>
                  Номер карты (12 цифр)
                  <input v-model="userPaymentForm.card_number" type="text" maxlength="12" placeholder="000000000000" />
                </label>
                <div class="payment-form-grid">
                  <label>
                    Действителен до
                    <input v-model="userPaymentForm.expires_at" type="text" maxlength="5" placeholder="MM/YY" />
                  </label>
                  <label>
                    CVV
                    <div class="cvv-wrap">
                      <input
                        v-model="userPaymentForm.cvv_code"
                        :type="userPaymentShowCvv ? 'text' : 'password'"
                        maxlength="4"
                        placeholder="***"
                      />
                      <button class="link-btn" @click="userPaymentShowCvv = !userPaymentShowCvv">
                        {{ userPaymentShowCvv ? "Скрыть" : "Показать" }}
                      </button>
                    </div>
                  </label>
                </div>
                <label>
                  ФИО владельца карты
                  <input v-model="userPaymentForm.holder_name" type="text" placeholder="Иванов Иван Иванович" />
                </label>
                <div class="payment-form-actions">
                  <button class="auth-submit" :disabled="userPaymentsLoading" @click="saveUserPaymentMethod">
                    {{ userPaymentEditId ? "Изменить существующий" : "Добавить карту" }}
                  </button>
                  <button class="link-btn" @click="userPaymentEditorOpen = false; resetUserPaymentForm()">
                    Отменить
                  </button>
                </div>
              </div>

              <div class="payment-cards">
                <article
                  v-for="method in userPaymentMethods"
                  :key="`pm-${method.payment_method_id}`"
                  class="payment-card"
                >
                  <div class="payment-card-main">
                    <h3>{{ method.card_brand || "Банковская карта" }}</h3>
                    <p>**** **** **** {{ method.card_last4 || "0000" }}</p>
                  </div>
                  <div class="payment-card-actions">
                    <button class="link-btn" @click="startEditUserPayment(method)">Изменить существующий</button>
                    <button class="link-btn danger-link" @click="deleteUserPaymentMethod(method.payment_method_id)">
                      Удалить способ оплаты
                    </button>
                  </div>
                </article>
                <p v-if="!userPaymentMethods.length" class="booking-muted">Пока нет добавленных карт</p>
              </div>
            </section>

            <section v-if="userCabinetTab === 'privacy'" class="cabinet-block">
              <div class="cabinet-block-head">
                <h2>Конфиденциальность</h2>
              </div>
              <div class="row-line"></div>
              <div class="privacy-options">
                <label class="privacy-option">
                  <input v-model="userPrivacyForm.show_profile_in_reviews" type="checkbox" />
                  <span>Показывать профиль в отзывах</span>
                </label>
                <label class="privacy-option">
                  <input v-model="userPrivacyForm.allow_email_notifications" type="checkbox" />
                  <span>Разрешить email-уведомления</span>
                </label>
                <label class="privacy-option">
                  <input v-model="userPrivacyForm.allow_sms_notifications" type="checkbox" />
                  <span>Разрешить SMS-уведомления</span>
                </label>
              </div>
              <button class="auth-submit" :disabled="userPrivacySaving" @click="saveUserPrivacy">
                {{ userPrivacySaving ? "Сохраняем..." : "Сохранить" }}
              </button>
            </section>
          </div>
        </div>
      </section>

      <section v-else-if="profile?.role === 'admin'" class="auth-card admin-card">
        <div class="cabinet-top">
          <div class="cabinet-breadcrumb">
            <button class="crumb-link" @click="navigate('/')">Главная</button>
            <span>- Личный кабинет</span>
          </div>
          <button class="link-btn top-exit" @click="logout">Выйти</button>
        </div>
        <h1>Панель администратора</h1>
        <p v-if="profileLoading">Загрузка профиля...</p>
        <p v-if="profileError" class="error">{{ profileError }}</p>

        <div class="admin-tiles">
          <button
            class="admin-tile"
            :class="{ active: adminTab === 'create-user' }"
            @click="adminTab = 'create-user'"
          >
            Добавление нового пользователя
          </button>
          <button
            class="admin-tile"
            :class="{ active: adminTab === 'refunds' }"
            @click="adminTab = 'refunds'"
          >
            Заявки на возврат
          </button>
          <button
            class="admin-tile"
            :class="{ active: adminTab === 'event-moderation' }"
            @click="adminTab = 'event-moderation'"
          >
            Модерация мероприятий
          </button>
          <button
            class="admin-tile"
            :class="{ active: adminTab === 'nearby-places' }"
            @click="adminTab = 'nearby-places'"
          >
            Места рядом
          </button>
          <button class="admin-tile muted" disabled>Модерация организаторов (скоро)</button>
        </div>

        <div v-if="adminTab === 'create-user'" class="admin-panel">
          <h2>Создать пользователя</h2>
          <label>
            ФИО
            <input v-model="createUserForm.full_name" type="text" autocomplete="off" />
          </label>
          <label>
            Логин (email или телефон)
            <input v-model="createUserForm.login" type="text" autocomplete="off" />
          </label>
          <label>
            Пароль
            <input v-model="createUserForm.password" type="password" autocomplete="new-password" />
          </label>
          <label>
            Тип пользователя
            <select v-model="createUserForm.user_type">
              <option value="user">Пользователь</option>
              <option value="organizer">Организатор</option>
            </select>
          </label>
          <button class="auth-submit" :disabled="createUserLoading" @click="submitCreateUser">
            {{ createUserLoading ? "Создаем..." : "Создать" }}
          </button>
          <p v-if="createUserError" class="error">{{ createUserError }}</p>
          <p v-if="createUserSuccess" class="success">{{ createUserSuccess }}</p>
        </div>

        <div v-if="adminTab === 'refunds'" class="admin-panel">
          <h2>Заявки на возврат</h2>
          <p v-if="adminRefundsLoading">Загрузка заявок...</p>
          <p v-if="adminRefundsError" class="error">{{ adminRefundsError }}</p>
          <p v-if="adminRefundsSuccess" class="success">{{ adminRefundsSuccess }}</p>
          <p v-if="!adminRefundsLoading && !adminRefunds.length">Новых заявок нет</p>
          <div v-else class="booking-list">
            <article v-for="item in adminRefunds" :key="`refund-${item.refund_id}`" class="booking-card">
              <div class="booking-head">
                <div>Заявка #{{ item.refund_id }} · Заказ #{{ item.order_id }}</div>
                <div class="booking-muted">{{ item.amount }} {{ item.currency }}</div>
              </div>
              <div class="booking-muted">Пользователь: {{ item.user_name || item.user_login || "-" }}</div>
              <div class="booking-muted">Событие: {{ item.event_title || "-" }}</div>
              <div class="booking-muted">Билетов: {{ item.ticket_qty || 0 }}</div>
              <div class="booking-muted">Дата: {{ formatCabinetDate(item.starts_at) }}</div>
              <div class="payment-form-actions">
                <button class="auth-submit" @click="adminReviewRefund(item.refund_id, 'approve')">Одобрить</button>
              </div>
              <label>
                Причина отклонения
                <textarea v-model="adminRefundRejectComment[item.refund_id]" rows="2"></textarea>
              </label>
              <div class="payment-form-actions">
                <button class="link-btn" @click="adminReviewRefund(item.refund_id, 'reject')">Отклонить</button>
              </div>
            </article>
          </div>
        </div>

        <div v-if="adminTab === 'event-moderation'" class="admin-panel">
          <h2>Модерация мероприятий</h2>
          <p v-if="adminModerationEventsLoading">Загрузка мероприятий...</p>
          <p v-if="adminModerationEventsError" class="error">{{ adminModerationEventsError }}</p>
          <p v-if="adminModerationEventsSuccess" class="success">{{ adminModerationEventsSuccess }}</p>
          <p v-if="!adminModerationEventsLoading && !adminModerationEvents.length">
            Новых мероприятий на модерации нет
          </p>
          <div v-else class="booking-list">
            <article
              v-for="event in adminModerationEvents"
              :key="`moderation-${event.event_id}`"
              class="booking-card moderation-card"
            >
              <div class="booking-head">
                <div>Мероприятие #{{ event.event_id }} · {{ event.title }}</div>
                <div class="booking-muted">{{ organizerEventStatusLabel(event.status) }}</div>
              </div>
              <div class="moderation-grid">
                <div>
                  <div class="booking-muted">Организатор: {{ event.organizer?.display_name || "-" }}</div>
                  <div class="booking-muted">Логин: {{ event.organizer?.login || "-" }}</div>
                  <div class="booking-muted">Категория: {{ event.category_name || "-" }}</div>
                  <div class="booking-muted">Город: {{ event.venue_city || "-" }}</div>
                  <div class="booking-muted">Адрес: {{ event.venue_address || "-" }}</div>
                  <div class="booking-muted">
                    Возраст: {{ ageLabelFromRange(event.age_min, event.age_max) || "Не указан" }}
                  </div>
                </div>
                <img
                  v-if="event.cover_image_url"
                  :src="event.cover_image_url"
                  alt="cover"
                  class="moderation-cover"
                />
              </div>
              <div class="booking-item-title">Описание</div>
              <p class="long-text">{{ event.description || "Описание не заполнено" }}</p>
              <div class="booking-item-title">Сеансы</div>
              <div v-if="event.sessions?.length" class="sessions-list moderation-sessions">
                <div
                  v-for="session in event.sessions"
                  :key="`admin-session-${event.event_id}-${session.session_id}`"
                  class="session-item"
                >
                  <span>{{ formatCabinetDate(session.starts_at) }}</span>
                  <span>{{ session.ticket_types?.length || 0 }} типов билетов</span>
                </div>
              </div>
              <p v-else class="booking-muted">Сеансы не добавлены</p>
              <div class="payment-form-actions">
                <button class="auth-submit" @click="adminReviewEventModeration(event.event_id, 'publish')">
                  Опубликовать
                </button>
              </div>
              <label>
                Причина отклонения
                <textarea v-model="adminModerationRejectComment[event.event_id]" rows="3"></textarea>
              </label>
              <div class="payment-form-actions">
                <button class="link-btn" @click="adminReviewEventModeration(event.event_id, 'reject')">
                  Отклонить
                </button>
              </div>
            </article>
          </div>
        </div>

        <div v-if="adminTab === 'nearby-places'" class="admin-panel">
          <h2>Места рядом</h2>
          <p v-if="adminNearbyPlacesLoading">Загрузка мест...</p>
          <p v-if="adminNearbyPlacesError" class="error">{{ adminNearbyPlacesError }}</p>
          <p v-if="adminNearbyPlacesSuccess" class="success">{{ adminNearbyPlacesSuccess }}</p>
          <label>
            Площадка
            <select v-model="adminNearbyPlaceForm.venue_id">
              <option value="">Выберите площадку</option>
              <option v-for="venue in adminNearbyVenues" :key="`nearby-venue-${venue.venue_id}`" :value="String(venue.venue_id)">
                {{ venue.label }} · {{ venue.address }}
              </option>
            </select>
          </label>
          <label>
            Название места
            <input v-model="adminNearbyPlaceForm.title" type="text" />
          </label>
          <label>
            Описание
            <textarea v-model="adminNearbyPlaceForm.description" rows="3"></textarea>
          </label>
          <div class="moderation-grid nearby-form-grid">
            <label>
              Часы работы
              <input v-model="adminNearbyPlaceForm.working_hours" type="text" placeholder="10:00–22:00" />
            </label>
            <label>
              Средний чек
              <input v-model="adminNearbyPlaceForm.average_check" type="number" min="0" step="0.01" />
            </label>
            <label>
              Время пути, мин
              <input v-model="adminNearbyPlaceForm.travel_time_minutes" type="number" min="0" />
            </label>
          </div>
          <label>
            Картинка
            <input type="file" accept="image/*" @change="onPickAdminNearbyImage" />
          </label>
          <div v-if="adminNearbyImagePreview" class="nearby-admin-preview-wrap">
            <img :src="adminNearbyImagePreview" alt="preview" class="nearby-admin-preview" />
            <button class="link-btn" @click="clearAdminNearbyImage">Убрать картинку</button>
          </div>
          <div class="payment-form-actions">
            <button class="auth-submit" @click="submitAdminNearbyPlace">
              {{ adminNearbyPlaceEditId ? "Сохранить изменения" : "Добавить место" }}
            </button>
            <button class="link-btn" @click="resetAdminNearbyPlaceForm">Сбросить</button>
          </div>

          <div class="booking-list">
            <article v-for="place in adminNearbyPlaces" :key="`admin-nearby-${place.place_id}`" class="booking-card">
              <div class="booking-head">
                <div>{{ place.title }}</div>
                <div class="booking-muted">{{ place.venue_city }} · {{ place.venue_name }}</div>
              </div>
              <div class="moderation-grid">
                <div>
                  <div class="booking-muted">Адрес: {{ place.venue_address }}</div>
                  <div class="booking-muted">Часы работы: {{ place.working_hours || "-" }}</div>
                  <div class="booking-muted">Средний чек: {{ place.average_check ? `${place.average_check} ₽` : "-" }}</div>
                  <div class="booking-muted">Время пути: {{ place.travel_time_minutes ? `${place.travel_time_minutes} мин` : "-" }}</div>
                  <p class="long-text">{{ place.description || "Описание отсутствует" }}</p>
                </div>
                <img v-if="place.image_url" :src="place.image_url" alt="place" class="moderation-cover" />
              </div>
              <div class="payment-form-actions">
                <button class="link-btn" @click="startEditAdminNearbyPlace(place)">Изменить</button>
                <button class="link-btn danger-link" @click="deleteAdminNearbyPlace(place.place_id)">Удалить</button>
              </div>
            </article>
          </div>
        </div>

        <div v-if="profile" class="profile-grid">
          <div>Роль</div>
          <div>{{ profile.role }}</div>
          <div>ID</div>
          <div>{{ profile.id }}</div>
          <div>Логин</div>
          <div>{{ profile.login }}</div>
          <div>Статус</div>
          <div>{{ profile.status }}</div>
        </div>
      </section>

      <section v-else class="auth-card">
        <div class="cabinet-top">
          <div class="cabinet-breadcrumb">
            <button class="crumb-link" @click="navigate('/')">Главная</button>
            <span>- Личный кабинет</span>
          </div>
          <button class="link-btn top-exit" @click="logout">Выйти</button>
        </div>
        <h1>Личный кабинет</h1>
        <p v-if="profileLoading">Загрузка профиля...</p>
        <p v-if="profileError" class="error">{{ profileError }}</p>
        <div v-if="profile" class="profile-grid">
          <div>Роль</div>
          <div>{{ profile.role }}</div>
          <div>ID</div>
          <div>{{ profile.id }}</div>
          <div>Логин</div>
          <div>{{ profile.login }}</div>
          <div>Статус</div>
          <div>{{ profile.status }}</div>
          <template v-if="profile.role === 'user'">
            <div>Имя</div>
            <div>{{ profile.first_name }} {{ profile.last_name }}</div>
          </template>
          <template v-if="profile.role === 'organizer'">
            <div>Email</div>
            <div>{{ profile.email || '-' }}</div>
          </template>
        </div>
      </section>
    </main>

    <main v-else class="auth-screen">
      <section class="auth-card">
        <h1>Страница не найдена</h1>
        <button class="auth-submit" @click="navigate('/')">На главную</button>
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

* {
  box-sizing: border-box;
}

.page-bg {
  --accent: #ff7264;
  --text: #2c2c31;
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

.right-controls {
  display: flex;
  align-items: center;
  gap: 10px;
  justify-content: flex-end;
}

.icon-btn {
  position: relative;
  width: 34px;
  height: 34px;
  border: 0;
  background: transparent;
  color: #2f2f35;
  font-size: 30px;
  line-height: 1;
  cursor: pointer;
  padding: 0;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.cart-btn {
  width: 38px;
}

.icon-svg {
  width: 26px;
  height: 26px;
  fill: none;
  stroke: currentColor;
  stroke-width: 1.9;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.auth-btn {
  border: 0;
  border-radius: 12px;
  background: var(--accent);
  color: #fff;
  font-size: 18px;
  padding: 10px 14px;
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
  background: transparent;
  padding-right: 4px;
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
  background: transparent;
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

.filters-panel {
  margin-top: 12px;
  border: 1px solid #e7e2d5;
  border-radius: 20px;
  background: #fffaf1;
  padding: 16px 18px;
}

.filters-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
}

.filters-grid label {
  display: grid;
  gap: 6px;
  font-size: 16px;
  color: #2c2c31;
}

.filters-grid input,
.filters-grid select {
  border: 1px solid #ddd4be;
  border-radius: 12px;
  padding: 10px 12px;
  font-size: 16px;
  font-family: "Arista Pro", sans-serif;
  background: #fff;
}

.filters-actions {
  margin-top: 12px;
  display: flex;
  justify-content: flex-end;
}

.soft {
  border: 0;
  border-radius: 16px;
  padding: 12px 16px;
  font-family: "Arista Pro", sans-serif;
  font-size: 24px;
  background: #6b6c766e;
  color: #fff;
}

.cards {
  margin-top: 14px;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
  max-width: none;
}

.poster {
  width: 100%;
  aspect-ratio: 5 / 3;
  border-radius: 24px;
}

.poster-1 {
  background: linear-gradient(135deg, #2f6fa0, #5ba8d9);
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

.main-event-card {
  border: 1px solid #e6e6e6;
  border-radius: 24px;
  padding: 12px;
  background: #fff;
  position: relative;
}

.favorite-heart {
  position: absolute;
  right: 14px;
  top: 14px;
  width: 34px;
  height: 34px;
  border: 0;
  background: transparent;
  padding: 0;
  display: grid;
  place-items: center;
  cursor: pointer;
  z-index: 2;
}

.favorite-heart svg {
  width: 26px;
  height: 26px;
}

.favorite-heart path {
  fill: transparent;
  stroke: #2c2c31;
  stroke-width: 1.7;
}

.favorite-heart.active path {
  fill: #ff4f4f;
  stroke: #ff4f4f;
}

.clickable {
  cursor: pointer;
}

.event-detail-page {
  margin-top: 12px;
  display: grid;
  gap: 16px;
}

.event-title {
  margin: 0;
  font-size: clamp(46px, 5vw, 74px);
  font-weight: 400;
  line-height: 1.02;
  max-width: 980px;
}

.event-top-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(380px, 440px);
  gap: 20px;
  align-items: start;
}

.event-cover-large {
  width: 100%;
  max-height: 470px;
  object-fit: cover;
  border-radius: 24px;
  border: 1px solid #e6e6e6;
  background: #f3f3f3;
}

.event-side {
  background: #f4f4f4;
  border-radius: 16px;
  border: 1px solid #e4e4e4;
  padding: 14px;
  display: grid;
  gap: 10px;
}

.event-chip {
  display: inline-flex;
  width: fit-content;
  padding: 8px 12px;
  border-radius: 12px;
  background: #ffd039;
  font-weight: 700;
}

.event-row {
  font-size: 18px;
}

.tickets-btn {
  margin-top: 6px;
}

.ticket-screen {
  min-height: 100vh;
  padding-bottom: 12px;
}

.ticket-breadcrumb {
  margin-bottom: 12px;
}

.ticket-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(360px, 500px);
  gap: 16px;
  align-items: stretch;
  height: calc(100vh - 150px);
}

.ticket-left,
.ticket-right {
  background: #f6f6f8;
  border: 1px solid #f0d78a;
  border-radius: 22px;
  padding: 14px 16px;
  min-height: 0;
}

.ticket-left {
  display: flex;
  flex-direction: column;
}

.ticket-right {
  display: flex;
  flex-direction: column;
  overflow: auto;
}

.ticket-left-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
}

.ticket-map-title {
  margin: 0;
  font-size: 26px;
  font-weight: 700;
}

.ticket-timer {
  font-size: 24px;
  font-weight: 700;
  color: #3a3a45;
}

.ticket-title {
  margin: 0;
  font-size: 44px;
}

.ticket-subtitle {
  margin: 6px 0 14px;
  color: #666;
}

.ticket-controls {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  margin-bottom: 8px;
}

.ticket-controls label {
  display: grid;
  gap: 6px;
}

.ticket-controls select {
  border: 1px solid #ddd;
  border-radius: 10px;
  padding: 6px 8px;
  font-size: 14px;
  font-family: "Arista Pro", sans-serif;
}

.hall-stage {
  background: #f6f0de;
  color: #4d4330;
  text-align: center;
  padding: 7px;
  border-radius: 14px;
  margin: 8px 0 10px;
  font-weight: 700;
  letter-spacing: 0.5px;
  font-size: 14px;
}

.seat-map {
  display: grid;
  gap: 8px;
  flex: 1;
  min-height: 0;
  overflow: auto;
  padding-right: 2px;
}

.seat-row {
  display: grid;
  grid-template-columns: 34px 1fr;
  gap: 12px;
  align-items: center;
}

.row-label {
  color: #555;
  font-size: 14px;
  text-align: center;
}

.row-seats {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.seat-btn {
  min-width: 38px;
  height: 28px;
  border: 1px solid #b8c694;
  border-radius: 999px;
  background: #99c260;
  color: #2f2f35;
  font-size: 14px;
  line-height: 1;
  cursor: pointer;
}

.seat-btn.selected {
  background: #ffd039;
  color: #2f2f35;
  border-color: #ffd039;
}

.seat-btn.unavailable {
  background: #e3e7ef;
  color: #9a9a9a;
  border-color: #d8dde8;
  cursor: not-allowed;
}

.seat-legend {
  display: flex;
  gap: 8px;
  justify-content: center;
  margin: 10px 0 8px;
}

.legend-chip {
  border-radius: 999px;
  padding: 5px 12px;
  font-size: 13px;
}

.legend-chip.selected {
  background: #ffd039;
}

.legend-chip.available {
  background: #99c260;
}

.legend-chip.unavailable {
  background: #e3e7ef;
  color: #727784;
}

.clear-seat-btn {
  width: 100%;
  font-size: 18px;
  padding: 8px 10px;
}

.ticket-event-card {
  display: grid;
  grid-template-columns: 1fr 190px;
  gap: 10px;
  border: 1px solid #e2e2e2;
  border-radius: 14px;
  padding: 10px;
  background: #fff;
}

.ticket-event-cover {
  width: 100%;
  height: 128px;
  object-fit: cover;
  border-radius: 12px;
}

.ticket-event-cover-fallback {
  background: linear-gradient(135deg, #ececec, #dedede);
}

.ticket-event-main h3 {
  margin: 2px 0 6px;
  font-size: 24px;
  line-height: 1.02;
  font-weight: 700;
  overflow-wrap: anywhere;
}

.ticket-event-meta {
  font-size: 13px;
  color: #4f4f58;
  margin-bottom: 4px;
  line-height: 1.2;
}

.ticket-right .ticket-controls {
  margin: 10px 0;
}

.ticket-order-title {
  margin: 6px 0 6px;
  font-size: 26px;
  font-weight: 700;
}

.ticket-order-seats {
  background: #fff;
  border: 1px solid #d8d8d8;
  border-radius: 16px;
}

.ticket-order-seat-row {
  display: flex;
  justify-content: space-between;
  gap: 8px;
  padding: 10px 12px;
  font-size: 16px;
}

.ticket-order-seat-row + .ticket-order-seat-row {
  border-top: 1px solid #ececec;
}

.ticket-order-empty {
  color: #7d7d86;
  font-size: 14px;
  margin-bottom: 4px;
}

.ticket-order-totals {
  margin-top: 8px;
  border-top: 1px solid #e2e2e2;
  padding-top: 8px;
}

.ticket-order-line {
  margin-bottom: 4px;
  display: flex;
  justify-content: space-between;
  gap: 8px;
  font-size: 16px;
}

.ticket-order-line.total {
  font-weight: 700;
}

.ticket-confirm-btn {
  font-size: 18px;
  line-height: 1.15;
  margin-top: 6px;
  padding-top: 12px;
  padding-bottom: 12px;
}

.pay-btn {
  margin-top: 8px;
}

.payment-screen {
  min-height: 100vh;
  padding-bottom: 12px;
}

.payment-title {
  margin: 4px 0 2px;
  font-size: 34px;
  font-weight: 700;
}

.payment-subtitle {
  margin: 0 0 10px;
  color: #666;
}

.payment-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(360px, 520px);
  gap: 16px;
  align-items: stretch;
  height: calc(100vh - 210px);
}

.payment-left,
.payment-right {
  background: #f6f6f8;
  border: 1px solid #f0d78a;
  border-radius: 22px;
  padding: 14px 16px;
  min-height: 0;
}

.payment-left {
  display: flex;
  flex-direction: column;
}

.payment-right {
  overflow: auto;
}

.payment-left h2 {
  margin: 0 0 8px;
  font-size: 24px;
}

.payment-methods-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.payment-method-btn {
  font-size: 14px;
  padding: 8px 10px;
}

.payment-method-btn.active {
  background: #ffd039;
}

.payment-card-preview {
  margin-top: 12px;
  display: grid;
  gap: 8px;
  background: #fff;
  border: 1px solid #e6e6e6;
  border-radius: 14px;
  padding: 10px;
}

.payment-field {
  display: flex;
  justify-content: space-between;
  gap: 8px;
  font-size: 14px;
}

.payment-submit-btn {
  margin-top: auto;
  font-size: 18px;
}

.payment-timer {
  margin-bottom: 8px;
  font-size: 18px;
}

.event-tabs-row {
  display: flex;
  gap: 8px;
  align-items: end;
}

.event-tab-btn {
  border: 1px solid #d7d7d7;
  border-bottom: 0;
  border-top-left-radius: 12px;
  border-top-right-radius: 12px;
  background: #ececec;
  color: #2f2f35;
  padding: 10px 16px;
  font-family: "Arista Pro", sans-serif;
  font-size: 30px;
  line-height: 1;
  cursor: pointer;
}

.event-tab-btn.active {
  background: #fff;
  position: relative;
}

.event-tab-btn.active::after {
  content: "";
  position: absolute;
  left: 8px;
  right: 8px;
  bottom: -1px;
  height: 2px;
  background: #ffd039;
}

.event-description-block,
.event-nearby-block {
  background: #fff;
  border: 1px solid #ececec;
  border-radius: 16px;
  padding: 16px;
}

.event-description-block h2,
.event-nearby-block h2 {
  margin: 0 0 10px;
}

.nearby-title {
  margin: 0;
  font-family: "Airfool", sans-serif;
  font-size: clamp(52px, 6vw, 88px);
  font-weight: 400;
  line-height: 0.95;
  color: #ff7264;
}

.empty-nearby {
  min-height: 80px;
  display: flex;
  align-items: center;
  color: #7d7d84;
}

.nearby-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 360px));
  gap: 16px;
  align-items: start;
}

.nearby-card {
  border: 1px solid #ececec;
  border-radius: 18px;
  padding: 12px;
  display: grid;
  gap: 10px;
  background: #fffdf8;
  width: 100%;
  max-width: 360px;
}

.nearby-card-image {
  width: 100%;
  height: 180px;
  object-fit: contain;
  object-position: center;
  border-radius: 16px;
  background: #f2f2f2;
}

.nearby-card-empty {
  display: grid;
  place-items: center;
  color: #7d7d84;
}

.nearby-card-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.nearby-chip {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  border-radius: 999px;
  background: #ff7264;
  color: #fff;
  font-size: 14px;
}

.nearby-chip-light {
  background: #ffd039;
  color: #2c2c31;
}

.nearby-card h3 {
  margin: 0;
  font-size: 26px;
  line-height: 1;
}

.nearby-card p {
  margin: 0;
  color: #56565d;
}

.nearby-meta {
  display: grid;
  gap: 4px;
  font-size: 14px;
  color: #2c2c31;
}

.reviews-head {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 1.2fr;
  gap: 16px;
  margin-bottom: 14px;
}

.reviews-summary {
  background: #fafafa;
  border: 1px solid #ececec;
  border-radius: 12px;
  padding: 12px;
}

.reviews-average {
  font-size: 42px;
  line-height: 1;
  font-weight: 500;
}

.reviews-count {
  margin-top: 6px;
  color: #676774;
  font-size: 14px;
}

.reviews-bars {
  display: grid;
  gap: 6px;
}

.reviews-bar-row {
  display: grid;
  grid-template-columns: 76px 1fr 24px;
  gap: 8px;
  align-items: center;
}

.stars-label {
  font-size: 14px;
  color: #f3b21d;
  letter-spacing: 1px;
}

.bar-track {
  height: 6px;
  background: #ececec;
  border-radius: 999px;
}

.bar-fill {
  height: 100%;
  background: #f3b21d;
  border-radius: 999px;
}

.bar-count {
  text-align: right;
  color: #666;
  font-size: 13px;
}

.reviews-empty {
  border: 1px dashed #ddd;
  border-radius: 12px;
  color: #666;
  padding: 18px;
}

.reviews-list {
  display: grid;
  gap: 10px;
}

.review-card {
  border: 1px solid #ececec;
  border-radius: 12px;
  padding: 12px;
}

.review-top {
  display: flex;
  justify-content: space-between;
  gap: 10px;
}

.review-author {
  font-size: 20px;
  font-weight: 500;
}

.review-date {
  font-size: 14px;
  color: #666;
}

.review-rating {
  margin-top: 4px;
  color: #f3b21d;
  letter-spacing: 1px;
}

.review-text {
  margin: 8px 0 0;
  color: #333;
  line-height: 1.35;
}

.auth-screen {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 20px;
}

.cabinet-screen {
  min-height: 100vh;
  padding: 24px 32px 40px;
}

.auth-card {
  width: min(520px, 100%);
  background: #fff;
  border: 1px solid #ececec;
  border-radius: 16px;
  padding: 20px;
}

.auth-card h1 {
  margin: 0 0 12px;
  font-family: "Airfool", sans-serif;
  font-size: 48px;
  line-height: 1;
}

.hint {
  margin-top: 0;
  color: #666;
}

.auth-card label {
  display: grid;
  gap: 6px;
  margin-bottom: 10px;
  font-size: 20px;
}

.auth-card input {
  border: 1px solid #ddd;
  border-radius: 10px;
  padding: 10px 12px;
  font-size: 18px;
  font-family: "Arista Pro", sans-serif;
}

.auth-submit {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 140px;
  border: 0;
  border-radius: 12px;
  background: var(--accent);
  color: #fff;
  font-size: 18px;
  padding: 10px 14px;
  cursor: pointer;
  margin-top: 6px;
}

.auth-submit:disabled {
  opacity: 0.7;
  cursor: default;
}

.login-actions {
  margin-top: 6px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 14px;
}

.link-btn {
  border: 0;
  background: transparent;
  color: #2c2c31;
  text-decoration: underline;
  cursor: pointer;
  padding: 6px 0;
}

.error {
  color: #d33030;
}

.profile-grid {
  display: grid;
  grid-template-columns: 160px 1fr;
  gap: 8px;
  margin: 12px 0;
}

.admin-card {
  width: min(860px, 100%);
}

.admin-cabinet {
  max-width: 1860px;
  margin: 0 auto;
}

.cabinet-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.cabinet-breadcrumb {
  font-size: 16px;
  color: #575861;
  margin-bottom: 18px;
}

.crumb-link {
  border: 0;
  background: transparent;
  color: #2c2c31;
  text-decoration: underline;
  cursor: pointer;
  padding: 0;
  font-size: 16px;
  font-family: "Arista Pro", sans-serif;
}

.top-exit {
  margin-bottom: 18px;
}

.cabinet-title {
  margin: 0 0 16px;
  font-size: 34px;
  font-weight: 500;
}

.cabinet-grid {
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: 20px;
  align-items: start;
}

.cabinet-menu {
  background: #fff;
  border: 1px solid #ececec;
  border-radius: 16px;
  padding: 10px;
  display: grid;
  gap: 8px;
}

.cabinet-menu-item {
  border: 0;
  border-radius: 12px;
  background: #f4f5f8;
  color: #2c2c31;
  text-align: left;
  font-size: 18px;
  padding: 12px 14px;
  cursor: pointer;
}

.cabinet-menu-item.active {
  background: #2aa9ee;
  color: #fff;
}

.cabinet-menu-item:disabled {
  opacity: 0.6;
  cursor: default;
}

.cabinet-content {
  display: grid;
  gap: 18px;
}

.cabinet-block {
  background: #fff;
  border: 1px solid #ececec;
  border-radius: 20px;
  padding: 24px 26px;
}

.cabinet-block-head {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
}

.cabinet-block-head h2 {
  margin: 0;
  font-size: 22px;
  font-weight: 500;
}

.status-pill {
  display: inline-flex;
  align-items: center;
  border-radius: 16px;
  background: #ebf7ff;
  color: #2aa9ee;
  font-size: 13px;
  padding: 7px 10px;
}

.row-line {
  height: 1px;
  background: #ececec;
  margin: 16px 0;
}

.cabinet-info-grid {
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: 10px 18px;
}

.cabinet-info-grid > :nth-child(odd) {
  color: #6b6c76;
  font-weight: 500;
}

.cabinet-info-grid input {
  border: 1px solid #ddd;
  border-radius: 10px;
  padding: 8px 10px;
  font-size: 16px;
  font-family: "Arista Pro", sans-serif;
}

.payment-form {
  display: grid;
  gap: 10px;
}

.payment-form label {
  display: grid;
  gap: 6px;
  font-size: 16px;
}

.payment-form input {
  border: 1px solid #ddd;
  border-radius: 10px;
  padding: 8px 10px;
  font-size: 16px;
  font-family: "Arista Pro", sans-serif;
}

.payment-form-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.payment-form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.cvv-wrap {
  display: flex;
  align-items: center;
  gap: 8px;
}

.cvv-wrap .link-btn {
  text-decoration: none;
  color: #2aa9ee;
}

.payment-cards {
  margin-top: 16px;
  display: grid;
  gap: 12px;
}

.payment-card {
  border: 1px solid #ececec;
  border-radius: 14px;
  background: #f8f8f8;
  padding: 16px;
  display: flex;
  justify-content: space-between;
  gap: 14px;
  align-items: center;
}

.payment-card-main h3 {
  margin: 0 0 8px;
  font-size: 32px;
  font-weight: 500;
}

.payment-card-main p {
  margin: 0;
  font-size: 22px;
  letter-spacing: 1px;
}

.payment-card-actions {
  display: grid;
  gap: 8px;
  justify-items: end;
}

.danger-link {
  color: #2aa9ee;
}

.privacy-options {
  display: grid;
  gap: 12px;
  margin-bottom: 12px;
}

.privacy-option {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 18px;
}

.privacy-option input {
  width: 18px;
  height: 18px;
}

.booking-list {
  display: grid;
  gap: 10px;
}

.user-booking-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 12px;
}

.user-booking-card h2 {
  font-size: 30px;
}

.booking-meta-grid {
  margin-top: 8px;
  display: grid;
  gap: 2px;
}

.user-booking-card {
  position: relative;
  padding-bottom: 56px;
}

.booking-ticket-btn {
  position: absolute;
  right: 10px;
  bottom: 10px;
  width: auto;
  min-width: 96px;
  padding: 8px 14px;
  font-size: 16px;
}

.receipt-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.38);
  z-index: 120;
  display: grid;
  place-items: center;
  padding: 20px;
}

.receipt-modal {
  width: min(92vw, 420px);
  max-height: 90vh;
  overflow: auto;
  background: #fff;
  border-radius: 16px;
  padding: 16px 14px;
  border: 1px solid #e6e6e6;
  position: relative;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.22);
}

.receipt-close {
  position: absolute;
  right: 8px;
  top: 4px;
  border: 0;
  background: transparent;
  font-size: 26px;
  cursor: pointer;
  line-height: 1;
}

.receipt-modal h3 {
  margin: 2px 0 12px;
  text-align: center;
  font-size: 30px;
}

.receipt-line {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  font-size: 14px;
  margin-bottom: 6px;
}

.receipt-line span {
  color: #555;
}

.receipt-line b {
  text-align: right;
  max-width: 52%;
  overflow-wrap: anywhere;
}

.receipt-divider {
  border-top: 1px dashed #cecece;
  margin: 8px 0;
}

.receipt-line.total {
  font-size: 18px;
  font-weight: 700;
}

.receipt-qr {
  margin: 12px auto 0;
  width: 120px;
  height: 120px;
  border: 6px solid #111;
  display: grid;
  place-items: center;
  font-weight: 700;
  letter-spacing: 2px;
}

.refund-btn {
  margin-top: 10px;
  width: 100%;
  border: 0;
  border-radius: 10px;
  background: #e65353;
  color: #fff;
  font-size: 16px;
  padding: 10px 12px;
  cursor: pointer;
}

.refund-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.refund-confirm-modal {
  width: min(92vw, 420px);
  background: #fff;
  border-radius: 14px;
  border: 1px solid #e4e4e4;
  padding: 16px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.22);
}

.refund-confirm-modal h3 {
  margin: 0 0 8px;
  font-size: 26px;
}

.refund-confirm-modal p {
  margin: 0 0 12px;
  color: #555;
}

.refund-confirm-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.booking-card {
  border: 1px solid #e8e8e8;
  border-radius: 12px;
  padding: 12px;
  display: grid;
  gap: 8px;
}

.booking-head {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  align-items: center;
  font-size: 18px;
}

.booking-item-row {
  border-top: 1px solid #f0f0f0;
  padding-top: 8px;
  display: grid;
  gap: 3px;
}

.booking-item-title {
  font-size: 18px;
  font-weight: 500;
}

.booking-muted {
  color: #666;
  font-size: 14px;
}

.long-text {
  margin: 0;
  line-height: 1.45;
}

.about-textarea {
  width: 100%;
  border: 1px solid #ddd;
  border-radius: 10px;
  padding: 10px 12px;
  font-size: 16px;
  font-family: "Arista Pro", sans-serif;
  resize: vertical;
}

.upload-box {
  border: 1px dashed #2aa9ee;
  border-radius: 12px;
  background: #f4f8fc;
  color: #2aa9ee;
  padding: 40px 20px;
  text-align: center;
}

.event-create-form {
  display: grid;
  gap: 10px;
  margin-bottom: 14px;
}

.section-title {
  margin: 10px 0 2px;
  font-size: 22px;
  font-weight: 500;
}

.event-create-form label {
  display: grid;
  gap: 6px;
  font-size: 16px;
}

.event-create-form input,
.event-create-form textarea,
.event-create-form select {
  border: 1px solid #ddd;
  border-radius: 10px;
  padding: 9px 10px;
  font-size: 15px;
  font-family: "Arista Pro", sans-serif;
  background: #f8f8f8;
  color: #2c2c31;
}

.event-create-form select:disabled {
  opacity: 0.6;
}

.age-section {
  display: grid;
  gap: 8px;
}

.age-title {
  font-size: 16px;
  font-weight: 500;
}

.age-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.age-chip {
  border: 0;
  border-radius: 10px;
  background: #f2f2f2;
  color: #6a6b75;
  padding: 8px 14px;
  cursor: pointer;
  min-width: 62px;
  font-size: 15px;
}

.age-chip.active {
  background: #ffd64c;
  color: #1f1f1f;
}

.session-grid,
.ticket-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px;
  align-items: end;
}

.sessions-list {
  display: grid;
  gap: 8px;
}

.session-item {
  display: grid;
  grid-template-columns: 1fr 1fr auto;
  gap: 8px;
  border: 1px solid #e8e8e8;
  border-radius: 10px;
  padding: 10px 12px;
  background: #fafafa;
}

.mini-link {
  border: 0;
  background: transparent;
  text-decoration: none;
  color: #2c2c31;
  cursor: pointer;
  justify-self: end;
}

.yellow-btn {
  border: 0;
  border-radius: 10px;
  background: #f5cb25;
  color: #1f1f1f;
  padding: 10px 12px;
  cursor: pointer;
  font-weight: 500;
}

.add-ticket {
  justify-self: start;
  margin-top: -2px;
  color: #8a8b96;
  font-size: 16px;
  padding: 0;
}

.upload-box.compact {
  padding: 52px 20px;
}

.file-upload {
  cursor: pointer;
  display: grid;
  gap: 10px;
}

.file-upload input[type="file"] {
  display: none;
}

.upload-preview {
  width: 88px;
  height: 88px;
  object-fit: cover;
  border-radius: 8px;
  border: 1px solid #ddd;
}

.preview-wrap {
  position: relative;
  display: inline-block;
}

.cover-wrap {
  width: fit-content;
}

.preview-remove {
  position: absolute;
  top: -8px;
  right: -8px;
  width: 20px;
  height: 20px;
  border: 0;
  border-radius: 999px;
  background: #2c2c31;
  color: #fff;
  cursor: pointer;
  font-size: 14px;
  line-height: 20px;
  padding: 0;
  z-index: 2;
}

.upload-preview.cover {
  width: 220px;
  height: 120px;
}

.upload-gallery {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.event-actions {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  margin-top: 8px;
  align-items: center;
}

.event-actions-right {
  display: flex;
  gap: 10px;
  align-items: center;
}

.cancel-btn {
  border: 1px solid #ddd;
  border-radius: 10px;
  background: #fff;
  padding: 10px 18px;
  cursor: pointer;
  min-width: 120px;
}

.publish {
  min-width: 140px;
}

.save-btn {
  background: #efefef;
  color: #2c2c31;
}

.events-list {
  display: grid;
  gap: 8px;
}

.events-list.cards-view {
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 12px;
}

.event-item {
  border: 1px solid #e7e7e7;
  border-radius: 10px;
  padding: 10px 12px;
}

.event-card {
  text-align: left;
  cursor: pointer;
  background: #fff;
  border: 1px solid #e6e6e6;
  border-radius: 14px;
  padding: 10px;
}

.event-card-cover {
  width: 100%;
  height: 140px;
  object-fit: cover;
  border-radius: 10px;
  margin-bottom: 8px;
}

.event-card-cover.no-cover {
  display: grid;
  place-items: center;
  background: #f0f0f0;
  color: #777;
}

.event-details {
  margin-top: 12px;
}

.event-detail-grid {
  display: grid;
  gap: 8px;
  grid-template-columns: 1fr 1fr;
  margin-bottom: 10px;
}

.event-detail-cover {
  width: 100%;
  max-width: 520px;
  height: auto;
  border-radius: 12px;
  border: 1px solid #e6e6e6;
  margin: 8px 0;
}

.event-detail-gallery {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 10px;
}

.event-detail-gallery img {
  width: 120px;
  height: 80px;
  object-fit: cover;
  border-radius: 8px;
  border: 1px solid #ddd;
}

.event-card-title {
  font-size: 18px;
  font-weight: 500;
}

.event-meta {
  margin-top: 4px;
  color: #666;
  font-size: 14px;
}

.reject-reason {
  color: #c64232;
}

.admin-tiles {
  margin: 8px 0 14px;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
}

.admin-tile {
  border: 1px solid #e5e5e5;
  border-radius: 12px;
  background: #fff;
  color: #2c2c31;
  padding: 14px 12px;
  text-align: left;
  font-size: 17px;
  cursor: pointer;
}

.admin-tile.active {
  border-color: var(--accent);
  box-shadow: 0 0 0 1px var(--accent) inset;
}

.admin-tile.muted {
  color: #8a8b96;
  cursor: default;
}

.admin-panel {
  border: 1px solid #ededed;
  border-radius: 12px;
  padding: 14px;
  margin-bottom: 0;
}

.admin-panel h2 {
  margin: 0 0 10px;
  font-size: 28px;
  font-weight: 400;
}

.admin-panel label {
  display: grid;
  gap: 6px;
  margin-bottom: 10px;
  font-size: 18px;
}

.admin-panel input,
.admin-panel select,
.admin-panel textarea {
  border: 1px solid #ddd;
  border-radius: 10px;
  padding: 10px 12px;
  font-size: 16px;
  font-family: "Arista Pro", sans-serif;
}

.moderation-card {
  gap: 12px;
}

.moderation-grid {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
}

.moderation-cover {
  width: 180px;
  height: 120px;
  object-fit: cover;
  border-radius: 12px;
  border: 1px solid #e5e5e5;
  flex-shrink: 0;
}

.moderation-sessions {
  margin-bottom: 8px;
}

.nearby-form-grid {
  align-items: end;
}

.nearby-admin-preview-wrap {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.nearby-admin-preview {
  width: 160px;
  height: 100px;
  object-fit: cover;
  border-radius: 12px;
  border: 1px solid #e5e5e5;
}

.success {
  color: #1f8b3d;
}

.auth-actions-row {
  display: flex;
  gap: 12px;
  align-items: center;
}

@media (max-width: 1280px) {
  .screen {
    padding: 14px;
  }

  .search-box input {
    font-size: 22px;
  }

  .card h2 {
    font-size: 32px;
  }

  .admin-tiles {
    grid-template-columns: 1fr;
  }

  .cabinet-grid {
    grid-template-columns: 1fr;
  }

  .filters-grid {
    grid-template-columns: 1fr 1fr;
  }

  .cabinet-info-grid {
    grid-template-columns: 1fr;
  }

  .session-grid,
  .ticket-grid {
    grid-template-columns: 1fr;
  }

  .event-actions {
    flex-direction: column;
    align-items: stretch;
  }

  .event-actions-right {
    width: 100%;
    flex-direction: column;
  }

  .event-detail-grid {
    grid-template-columns: 1fr;
  }

  .event-top-grid {
    grid-template-columns: 1fr;
  }

  .ticket-layout {
    grid-template-columns: 1fr;
    height: auto;
  }

  .ticket-controls {
    grid-template-columns: 1fr;
  }

  .ticket-event-card {
    grid-template-columns: 1fr;
  }

  .payment-layout {
    grid-template-columns: 1fr;
    height: auto;
  }

  .ticket-event-main h3 {
    font-size: 42px;
  }

  .ticket-map-title {
    font-size: 34px;
  }

  .ticket-timer {
    font-size: 28px;
  }

  .reviews-head {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 760px) {
  .header {
    grid-template-columns: 1fr;
  }

  .right-controls {
    justify-content: flex-start;
  }

  .calendar {
    --day-cell: 48px;
    --day-gap: 2px;
  }

  .day-cell .num {
    font-size: 24px;
  }

  .hero {
    aspect-ratio: 16 / 9;
    border-radius: 24px;
  }

  .filters-grid {
    grid-template-columns: 1fr;
  }
}
</style>





