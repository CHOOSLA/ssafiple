<template>
  <div id="map-root" class="kakao-map-container"></div>
</template>

<script setup>
import { onMounted, ref, watch } from 'vue'
import { useMapStore } from '@/stores/mapStore'

const mapStore = useMapStore()
const mapInstance = ref(null)
const markers = ref([]) // 현재 그려진 마커(오버레이)들 보관

onMounted(() => {
  initMap()
})

const initMap = () => {
  // 이미 window.kakao가 존재하면 바로 로드
  if (window.kakao && window.kakao.maps) {
    renderMap()
    return
  }

  // 동적 스크립트 생성
  const script = document.createElement('script')
  script.type = 'text/javascript'
  const appKey = import.meta.env.VITE_KAKAO_MAP_KEY
  
  if (!appKey) {
    console.error("VITE_KAKAO_MAP_KEY 환경 변수가 없습니다.")
    return
  }
  
  script.src = `//dapi.kakao.com/v2/maps/sdk.js?appkey=${appKey}&libraries=services,clusterer&autoload=false`
  
  script.onload = () => {
    // autoload=false 옵션을 주었기 때문에 수동으로 load 호출
    window.kakao.maps.load(() => {
      renderMap()
    })
  }

  script.onerror = () => {
    console.error("Kakao Map API 스크립트 로드에 실패했습니다. 사이트 도메인 설정을 확인하세요.")
  }

  document.head.appendChild(script)
}

const renderMap = () => {
  const container = document.getElementById('map-root')
  if (!container) return

  const options = {
    center: new window.kakao.maps.LatLng(37.5665, 126.9780),
    level: 7
  }
  mapInstance.value = new window.kakao.maps.Map(container, options)
  console.log("카카오 지도가 성공적으로 렌더링되었습니다.")

  // 맵 인스턴스 렌더링 직후 현재 스토어에 있는 위치 핀 찍기
  drawMarkers(mapStore.locations)
}

// 카테고리별 컬러 매핑 (디자인 명세서 참조)
const catColors = {
  '관광지': '#f15b4c',
  '음식점': '#ef8a3c',
  '문화시설': '#3f8fd0',
  '쇼핑': '#8a6fd6',
  '숙박': '#5aa06a'
}

const drawMarkers = (locations) => {
  if (!mapInstance.value || !window.kakao) return

  // 기존 마커 전부 지도에서 제거
  markers.value.forEach(m => m.setMap(null))
  markers.value = []

  locations.forEach(loc => {
    // 위도 경도 유효성 검사
    if (!loc.latitude || !loc.longitude) return

    const position = new window.kakao.maps.LatLng(loc.latitude, loc.longitude)
    const color = catColors[loc.category] || '#f15b4c'

    // 커스텀 오버레이로 디자인 명세서의 마커 구현
    const content = document.createElement('div')
    content.style.cssText = `
      width: 28px; height: 28px;
      border-radius: 50% 50% 50% 0;
      transform: rotate(-45deg);
      background: ${color};
      border: 2.5px solid #fff;
      box-shadow: 0 4px 9px rgba(0,0,0,.3);
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
    `
    const innerDot = document.createElement('span')
    innerDot.style.cssText = `
      width: 9px; height: 9px;
      border-radius: 50%;
      background: #fff;
      transform: rotate(45deg);
    `
    content.appendChild(innerDot)

    // 마커 클릭 시 스토어 액션 (예: 선택한 장소 포커스) 연동
    content.onclick = () => {
      mapStore.selectLocation(loc)
      // 클릭한 핀으로 지도 중앙 이동
      mapInstance.value.panTo(position)
    }

    const overlay = new window.kakao.maps.CustomOverlay({
      position,
      content,
      yAnchor: 1 // 핀의 끝(뾰족한 부분)이 좌표를 가리키도록 설정
    })

    overlay.setMap(mapInstance.value)
    markers.value.push(overlay)
  })
}

// 스토어의 데이터 변경 감지 (검색, 필터링 등)
watch(() => mapStore.locations, (newLocations) => {
  drawMarkers(newLocations)
}, { deep: true })
</script>

<style scoped>
.kakao-map-container {
  width: 100%;
  height: 100%;
  /* 지도가 부드럽게 나타나도록 기본 스타일 지정 */
  background: var(--bg-color);
}
</style>
