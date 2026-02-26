<script setup>
import { onMounted, ref } from "vue";

const backendStatus = ref("loading");
const errorText = ref("");

onMounted(async () => {
  try {
    const apiBase = import.meta.env.VITE_API_BASE || "http://localhost:8000";
    const response = await fetch(`${apiBase}/health`);
    if (!response.ok) {
      backendStatus.value = "error";
      errorText.value = `HTTP ${response.status}`;
      return;
    }
    const data = await response.json();
    backendStatus.value = data.status || "ok";
  } catch (error) {
    backendStatus.value = "error";
    errorText.value = error instanceof Error ? error.message : String(error);
  }
});
</script>

<template>
  <main class="page">
    <h1>Vue Frontend is running</h1>
    <p>Backend (Django) health: <strong>{{ backendStatus }}</strong></p>
    <p v-if="errorText">Error: {{ errorText }}</p>
  </main>
</template>

<style scoped>
.page {
  font-family: Arial, sans-serif;
  margin: 40px;
}
</style>
