<template>
  <div id="map-root" class="kakao-map-container"></div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useMapStore } from '@/stores/mapStore' // 나중에 핀 상태 등을 관리할 스토어

const mapInstance = ref(null)

onMounted(() => {
  initMap()
})

const initMap = () => {
  // kakao.maps가 index.html에서 로드되었는지 확인
  if (!window.kakao || !window.kakao.maps) {
    console.error("Kakao Map API가 로드되지 않았습니다.")
    return
  }

  // 지도를 그릴 컨테이너와 초기 옵션 설정
  const container = document.getElementById('map-root')
  const options = {
    // 서울 시청 좌표
    center: new window.kakao.maps.LatLng(37.5665, 126.9780),
    level: 7 // 초기 줌 레벨
  }

  // 지도 인스턴스 생성
  mapInstance.value = new window.kakao.maps.Map(container, options)

  // TODO: 이후 mapStore에 mapInstance를 넘기거나 핀(마커) 데이터를 받아와서 렌더링하는 로직 추가
}
</script>

<style scoped>
.kakao-map-container {
  width: 100%;
  height: 100%;
  /* 지도가 부드럽게 나타나도록 기본 스타일 지정 */
  background: var(--bg-color);
}
</style>
