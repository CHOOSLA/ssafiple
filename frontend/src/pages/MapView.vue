<template>
  <div class="map-view-container">
    <PlaceListPanel />
  </div>
</template>

<script setup>
import PlaceListPanel from '@/components/map/PlaceListPanel.vue'
</script>

<style scoped>
.map-view-container {
  height: 100%;
  display: flex;
  flex-direction: column;
}
</style>
