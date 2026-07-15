<template>
  <div id="map-root" class="kakao-map-container"></div>
</template>

<script setup>
import { onMounted, shallowRef, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useMapStore } from '@/stores/mapStore'

const mapStore = useMapStore()
const router = useRouter()
// 지도 인스턴스, 클러스터러, 마커 같은 무거운 객체는 Vue의 Proxy(반응성) 래핑을 피해야 렉이 안 걸립니다.
const mapInstance = shallowRef(null)
const clustererInstance = shallowRef(null)
let markers = [] // 단순 배열로 관리

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
  
  // 마커 클러스터러 생성 (네이버 부동산 스타일)
  clustererInstance.value = new window.kakao.maps.MarkerClusterer({
    map: mapInstance.value,
    averageCenter: true, // 클러스터에 포함된 마커들의 평균 위치를 클러스터 마커 위치로 설정
    minLevel: 5,         // 클러스터 할 최소 지도 레벨 
    disableClickZoom: false, // 클러스터 마커 클릭 시 줌 인
    styles: [{
      width: '40px', height: '40px',
      background: 'rgba(241, 91, 76, 0.9)', /* var(--accent) 색상 */
      borderRadius: '50%',
      color: '#fff',
      textAlign: 'center',
      fontWeight: 'bold',
      lineHeight: '40px',
      fontSize: '14px',
      boxShadow: '0 4px 10px rgba(0,0,0,0.2)',
      border: '2px solid #fff'
    }]
  })
  
  // 줌 컨트롤 추가 (우측 상단으로 이동 - AI 챗봇 버튼과 겹침 방지)
  const zoomControl = new window.kakao.maps.ZoomControl()
  mapInstance.value.addControl(zoomControl, window.kakao.maps.ControlPosition.TOPRIGHT)

  console.log("카카오 지도가 성공적으로 렌더링되었습니다.")

  // 맵 인스턴스 렌더링 직후 현재 스토어에 있는 위치 핀 찍기
  drawMarkers(mapStore.locations)
  
  // 지도가 이동/확대/축소 완료될 때(idle)마다 화면에 보이는 범위 내 장소만 검색
  window.kakao.maps.event.addListener(mapInstance.value, 'idle', () => {
    const bounds = mapInstance.value.getBounds()
    const sw = bounds.getSouthWest()
    const ne = bounds.getNorthEast()
    
    mapStore.fetchLocations(null, null, {
      sw_lat: sw.getLat(),
      sw_lng: sw.getLng(),
      ne_lat: ne.getLat(),
      ne_lng: ne.getLng()
    })
  })
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
  if (!mapInstance.value || !window.kakao || !clustererInstance.value || !Array.isArray(locations)) return

  // 기존 클러스터러 및 마커 배열 초기화
  clustererInstance.value.clear()
  markers = []

  locations.forEach(loc => {
    // 위도 경도 유효성 검사
    if (!loc.latitude || !loc.longitude) return

    const position = new window.kakao.maps.LatLng(loc.latitude, loc.longitude)
    const color = catColors[loc.category] || '#f15b4c'

    // CustomOverlay는 클러스터링 시 내부 DOM 에러(Cannot read properties of null)를 유발하므로, 
    // SVG 이미지를 Data URI로 변환하여 정식 Marker와 MarkerImage를 사용합니다.
    const svgString = `
      <svg xmlns="http://www.w3.org/2000/svg" width="34" height="42" viewBox="0 0 34 42">
        <path d="M17 0C7.6 0 0 7.6 0 17c0 12.8 17 25 17 25s17-12.2 17-25C34 7.6 26.4 0 17 0z" fill="${color}" stroke="#ffffff" stroke-width="2.5" filter="drop-shadow(0px 4px 4px rgba(0,0,0,0.3))"/>
        <circle cx="17" cy="17" r="5" fill="#ffffff"/>
      </svg>
    `.trim()
    const svgUrl = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(svgString)
    
    // 카카오맵 마커 이미지 생성
    const markerImage = new window.kakao.maps.MarkerImage(
      svgUrl,
      new window.kakao.maps.Size(34, 42),
      { offset: new window.kakao.maps.Point(17, 42) } // 마커 좌표에 일치시킬 이미지 안의 좌표 (뾰족한 끝)
    )

    const marker = new window.kakao.maps.Marker({
      position,
      image: markerImage
    })

    // 마커 클릭 이벤트 바인딩 (카카오맵 정식 이벤트)
    window.kakao.maps.event.addListener(marker, 'click', () => {
      mapStore.selectLocation(loc)
      
      // 왼쪽 패널(Left Panel) 너비를 고려한 시각적 중앙(Visual Center) 이동 알고리즘
      const panel = document.querySelector('.left-panel')
      const panelWidth = panel ? panel.offsetWidth : 550 // 기본값
      
      const proj = mapInstance.value.getProjection()
      // 1. 마커의 지리 좌표를 화면 픽셀 좌표(Point)로 변환
      let point = proj.pointFromCoords(position)
      
      // 2. 패널에 가려지지 않는 영역의 정중앙에 마커가 오려면, 
      // 마커를 화면 중심보다 (패널너비 / 2) 만큼 오른쪽(시각적 중심)에 두어야 함.
      // 따라서 지도의 중심 좌표는 마커 위치보다 (패널너비 / 2) 만큼 왼쪽(-x)으로 이동해야 합니다.
      point.x = point.x - (panelWidth / 2)
      
      // 3. 계산된 픽셀 좌표를 다시 지리 좌표(LatLng)로 변환
      const offsetLatLng = proj.coordsFromPoint(point)
      
      // 4. 오프셋이 적용된 새로운 중심으로 부드럽게 이동
      mapInstance.value.panTo(offsetLatLng)
      
      // 장소 선택 후 게시판 화면으로 이동
      router.push(`/locations/${loc.id}/posts`)
    })

    // Hover (마우스 오버) 이벤트 바인딩: 커스텀 오버레이로 사진/설명 Pane 띄우기
    let hoverOverlay = null;
    window.kakao.maps.event.addListener(marker, 'mouseover', () => {
      if (hoverOverlay) hoverOverlay.setMap(null);

      // 이미지가 없으면 기본 회색 박스
      const imageUrl = loc.image_url || '';
      const imageTag = imageUrl ? `<div class="hover-image" style="background-image: url('${imageUrl}')"></div>` : `<div class="hover-image no-img">사진 없음</div>`;

      const content = `
        <div class="hover-pane">
          ${imageTag}
          <div class="hover-info">
            <div class="hover-title">${loc.name}</div>
            <div class="hover-category" style="color: ${color}">${loc.category}</div>
          </div>
        </div>
      `;

      hoverOverlay = new window.kakao.maps.CustomOverlay({
        content: content,
        position: position,
        yAnchor: 1.5, // 핀 바로 위에 뜨도록 위치 조정
        zIndex: 999
      });
      
      hoverOverlay.setMap(mapInstance.value);

      // mouseout 이벤트에 삭제 로직 바인딩
      window.kakao.maps.event.addListener(marker, 'mouseout', () => {
        if (hoverOverlay) {
          hoverOverlay.setMap(null);
        }
      });
    });

    // 개별적으로 setMap() 하지 않고 배열에만 모음
    markers.push(marker)
  })

  // 클러스터러에 마커들을 한 번에 추가
  clustererInstance.value.addMarkers(markers)
}

// 스토어의 데이터 변경 감지 (검색, 필터링 등)
watch(() => mapStore.locations, (newLocations) => {
  drawMarkers(newLocations)
}, { deep: true })

// 왼쪽 목록 등에서 장소 선택 시 지도 중심 부드럽게 이동
watch(() => mapStore.selectedLocation, (loc) => {
  if (loc && loc.latitude && loc.longitude && mapInstance.value) {
    const position = new window.kakao.maps.LatLng(loc.latitude, loc.longitude)
    const panel = document.querySelector('.left-panel')
    const panelWidth = panel ? panel.offsetWidth : 550
    
    const proj = mapInstance.value.getProjection()
    if (proj) {
      let point = proj.pointFromCoords(position)
      point.x = point.x - (panelWidth / 2)
      mapInstance.value.panTo(proj.coordsFromPoint(point))
    } else {
      mapInstance.value.panTo(position)
    }
  }
})
</script>

<style scoped>
.kakao-map-container {
  width: 100%;
  height: 100%;
  /* 지도가 부드럽게 나타나도록 기본 스타일 지정 */
  background: var(--bg-color);
}

/* Yelp 스타일 커스텀 오버레이 팝업 CSS */
/* 주의: scoped CSS에서는 카카오맵이 동적으로 삽입하는 DOM요소에 스타일이 안 먹을 수 있으므로 :deep() 사용 */
:deep(.hover-pane) {
  width: 220px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(28, 27, 26, 0.2);
  overflow: hidden;
  border: 1px solid #eceae6;
  font-family: inherit;
  transform: translateY(-10px); /* 핀 위로 살짝 띄우기 */
  pointer-events: none; /* 마우스 이벤트가 팝업 아래 지도로 통과되도록 */
}

:deep(.hover-image) {
  width: 100%;
  height: 120px;
  background-size: cover;
  background-position: center;
  background-color: #f4f2ee;
}

:deep(.hover-image.no-img) {
  display: flex;
  align-items: center;
  justify-content: center;
  color: #a8a49b;
  font-size: 13px;
  font-weight: 500;
}

:deep(.hover-info) {
  padding: 12px 14px;
}

:deep(.hover-title) {
  font-weight: 700;
  font-size: 15px;
  color: #1c1b1a;
  margin-bottom: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

:deep(.hover-category) {
  font-size: 12px;
  font-weight: 600;
}
</style>
