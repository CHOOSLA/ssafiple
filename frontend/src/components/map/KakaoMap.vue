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
    console.warn("Kakao Map API가 아직 로드되지 않아 재시도합니다.")
    setTimeout(initMap, 200) // 약간의 지연 후 다시 시도
    return
  }

  // SDK가 완전히 준비되었을 때 지도를 생성하도록 보장
  window.kakao.maps.load(() => {
    const container = document.getElementById('map-root')
    const options = {
      // 서울 시청 좌표
      center: new window.kakao.maps.LatLng(37.5665, 126.9780),
      level: 7 // 초기 줌 레벨
    }

    // 지도 인스턴스 생성
    mapInstance.value = new window.kakao.maps.Map(container, options)
    console.log("카카오 지도가 성공적으로 렌더링되었습니다.")
  })
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
