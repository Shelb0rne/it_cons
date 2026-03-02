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
const loginError = ref("");
const loginLoading = ref(false);

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

function navigate(path) {
  if (currentPath.value === path) return;
  history.pushState({}, "", path);
  currentPath.value = path;
  handleRoute();
}

function logout() {
  persistAuth(null);
  profile.value = null;
  navigate("/");
}

function openCabinetFromHeader() {
  if (auth.value) {
    navigate("/cabinet");
  } else {
    navigate("/login");
  }
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
    navigate("/cabinet");
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
      userCabinetTab.value = "profile";
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
  try {
    const sessionsForSubmit = collectSessionsForSubmit();
    if (status === "published" && sessionsForSubmit.length === 0) {
      organizerEventsError.value = "Для публикации добавьте хотя бы один сеанс.";
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
      adminTab.value = "dashboard";
    }
    loadProfile();
  }

  if (currentPath.value === "/admin") {
    navigate("/cabinet");
  }
}

const city = ref("Москва");
const search = ref("");
const selectedDateKey = ref("2026-03-11");
const calendarTrack = ref(null);
const stickyMonthRef = ref(null);
const stickyMonthLabel = ref("Февраль");
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

const filteredEvents = computed(() => {
  const q = search.value.trim().toLowerCase();
  if (!q) return events.value;
  return events.value.filter((e) =>
    `${e.title} ${e.venue}`.toLowerCase().includes(q)
  );
});

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
      venue: event.venue_name || event.venue_address || "-",
      price: event.min_price,
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

const calendarDays = buildCalendarDays(new Date(2026, 1, 20), new Date(2026, 11, 31));

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
  await attachCalendarListenersIfNeeded();
});

onUnmounted(() => {
  if (onPopState) window.removeEventListener("popstate", onPopState);
  detachCalendarListeners();
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
          <button class="icon-btn" title="Избранное" aria-label="Избранное">
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
                  @click="selectedDateKey = d.key"
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
          <button class="soft">Сортировка ∨</button>
          <button class="soft">Фильтры</button>
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

    <main v-else-if="currentPath.startsWith('/event/')" class="screen event-screen">
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
            <button class="yellow-btn tickets-btn">Выбрать билеты</button>
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
          <div class="empty-nearby"></div>
        </section>
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
          <button class="link-btn" @click="navigate('/')">На главную</button>
        </div>
        <p v-if="loginError" class="error">{{ loginError }}</p>
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
                      Опубликовать
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
                    Статус: {{ event.status }}
                  </div>
                  <div class="event-meta">{{ event.category || "Без категории" }}</div>
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
              <div v-else class="booking-list">
                <article v-for="booking in userCurrentBookings" :key="`res-${booking.reservation_id}`" class="booking-card">
                  <div class="booking-head">
                    <div>Бронирование #{{ booking.reservation_id }}</div>
                    <div class="booking-muted">До {{ formatCabinetDate(booking.expires_at) }}</div>
                  </div>
                  <div v-for="(item, idx) in booking.items" :key="`res-${booking.reservation_id}-${idx}`" class="booking-item-row">
                    <div class="booking-item-title">{{ item.event_title || "Событие" }}</div>
                    <div class="booking-muted">{{ formatCabinetDate(item.starts_at) }} В· {{ item.venue_name || "-" }}</div>
                    <div class="booking-muted">{{ item.ticket_type || "Билет" }}</div>
                  </div>
                </article>
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
          <button class="admin-tile muted" disabled>Управление событиями (скоро)</button>
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
.admin-panel select {
  border: 1px solid #ddd;
  border-radius: 10px;
  padding: 10px 12px;
  font-size: 16px;
  font-family: "Arista Pro", sans-serif;
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
}
</style>





