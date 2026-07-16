<template>
  <div class="map-wrapper">
    <div id="map-root" class="kakao-map-container"></div>
    
    <!-- 지도를 너무 넓게 축소했을 때 지도 위에 뜨는 플로팅 안내 배너 -->
    <Transition name="fade">
      <div v-if="mapStore.isZoomOutTooMuch" class="floating-zoom-warning">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line><line x1="11" y1="8" x2="11" y2="14"></line><line x1="8" y1="11" x2="14" y2="11"></line>
        </svg>
        <div class="text">
          <p>{{ $t('map.zoomWarningTitle') }}</p>
          <span>{{ $t('map.zoomWarningDesc') }}</span>
        </div>
      </div>
    </Transition>

    <!-- 내 위치로 이동 버튼 -->
    <button class="my-location-btn" @click="moveToMyLocation" :title="$t('map.myLocationTitle')">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="12" cy="12" r="10"></circle>
        <circle cx="12" cy="12" r="3"></circle>
      </svg>
    </button>

    <!-- 카테고리 필터: 좌측 목록 패널 바깥, 지도 뷰포트 좌측 상단에 플로팅 -->
    <CategoryFilter
      :left="categoryFilterLeft"
      :selected="mapStore.categoryFilter"
      @select="handleCategorySelect"
    />
  </div>
</template>

<script setup>
import { onMounted, onUnmounted, shallowRef, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useMapStore } from '@/stores/mapStore'
import CategoryFilter from '@/components/map/CategoryFilter.vue'

const mapStore = useMapStore()
const router = useRouter()
const { t } = useI18n()
// 지도 인스턴스, 클러스터러, 마커 같은 무거운 객체는 Vue의 Proxy(반응성) 래핑을 피해야 렉이 안 걸립니다.
const mapInstance = shallowRef(null)
const clustererInstance = shallowRef(null)
let markers = [] // 단순 배열로 관리
let selectedOverlay = null // 선택된 장소 고정 오버레이
let nameLabelOverlays = [] // 확대 시 나타날 이름 텍스트 오버레이
let activeHoverOverlay = null // 현재 떠 있는 Hover 오버레이 (단일 유지)
let spiderfiedMarkers = [] // 거미줄처럼 펼쳐진(Spiderfied) 상태의 마커들
let pendingLocations = null // 펼침 상태 중 도착한 새 장소 데이터 (원상복구 시점에 반영)
let idleTimer = null // 맵 조작 이벤트 디바운싱용 타이머
let routePolylines = [] // 길찾기 경로 폴리라인
let routeEndpointMarkers = [] // 길찾기 출발/도착 마커

const routeLineStyles = {
  car: { color: '#f15b4c', weight: 5, style: 'solid' },
  walk: { color: '#8f9aa8', weight: 5, style: 'shortdash' },
  bus: { color: '#22c55e', weight: 7, style: 'solid' },
  subway: { color: '#2563eb', weight: 7, style: 'solid' },
}

const isValidRoutePoint = (point) => {
  const lat = Number(point?.lat)
  const lng = Number(point?.lng)
  return Number.isFinite(lat)
    && Number.isFinite(lng)
    && lat >= 33
    && lat <= 39
    && lng >= 124
    && lng <= 132
}

const toKakaoLinePath = (path) => {
  return (path || [])
    .filter(isValidRoutePoint)
    .map(p => new window.kakao.maps.LatLng(Number(p.lat), Number(p.lng)))
}

const clearRouteOverlays = () => {
  routePolylines.forEach(polyline => polyline.setMap(null))
  routePolylines = []
  routeEndpointMarkers.forEach(marker => marker.setMap(null))
  routeEndpointMarkers = []
}

// 좌측 패널(App.vue의 .left-panel, 채팅 도메인 파일) 너비를 App.vue 수정 없이 추적하기 위한 상태.
// 카테고리 필터 버튼의 좌측 위치 계산에만 사용 — 리사이즈 드래그에도 실시간으로 따라가도록 ResizeObserver 사용.
const leftPanelWidth = ref(550)
const categoryFilterLeft = ref(550 + 16)
let panelResizeObserver = null

const syncCategoryFilterLeft = () => {
  categoryFilterLeft.value = leftPanelWidth.value + 16
}

// 현재 지도 뷰포트의 bounds/시각적 중심을 fetchLocations용 파라미터로 변환 (idle 핸들러와 동일 로직 공유)
const getCurrentBoundsParams = () => {
  if (!mapInstance.value) return null
  const bounds = mapInstance.value.getBounds()
  if (!bounds) return null

  const sw = bounds.getSouthWest()
  const ne = bounds.getNorthEast()
  const physicalCenter = mapInstance.value.getCenter()

  const proj = mapInstance.value.getProjection()
  let visualCenter = physicalCenter
  if (proj) {
    const panelWidth = leftPanelWidth.value
    let point = proj.pointFromCoords(physicalCenter)
    point.x = point.x + (panelWidth / 2)
    visualCenter = proj.coordsFromPoint(point)
  }

  return {
    sw_lat: sw.getLat(),
    sw_lng: sw.getLng(),
    ne_lat: ne.getLat(),
    ne_lng: ne.getLng(),
    center_lat: visualCenter.getLat(),
    center_lng: visualCenter.getLng()
  }
}

// 카테고리 필터 클릭 핸들러: 필터 상태를 갱신하고, 현재 보이는 범위 기준으로 재조회
// (검색어가 있다면 함께 유지하여 지도/목록 모두 갱신)
const handleCategorySelect = (category) => {
  mapStore.setCategoryFilter(category)
  const bboxParams = getCurrentBoundsParams()
  mapStore.fetchLocations(category, mapStore.searchQuery || null, bboxParams)
}

// HTML5 Geolocation API로 내 위치 찾기
const moveToMyLocation = () => {
  if (navigator.geolocation) {
    // 사용자가 권한을 허용하면 콜백 실행
    navigator.geolocation.getCurrentPosition(
      (position) => {
        const lat = position.coords.latitude
        const lng = position.coords.longitude
        const moveLatLon = new window.kakao.maps.LatLng(lat, lng)
        
        if (mapInstance.value) {
          // 약간 확대된 상태(레벨 4)로 부드럽게 이동
          mapInstance.value.setLevel(4)
          
          // 왼쪽 패널 너비를 고려하여 시각적 중앙으로 이동
          const proj = mapInstance.value.getProjection()
          const panel = document.querySelector('.left-panel') || document.querySelector('.place-list-panel')
          const panelWidth = panel ? panel.offsetWidth : 550
          
          if (proj) {
            let point = proj.pointFromCoords(moveLatLon)
            point.x = point.x - (panelWidth / 2)
            mapInstance.value.panTo(proj.coordsFromPoint(point))
          } else {
            mapInstance.value.panTo(moveLatLon)
          }
        }
      },
      (error) => {
        console.error(error)
        alert(t('map.geoErrorAlert'))
      },
      {
        enableHighAccuracy: true,
        timeout: 5000,
        maximumAge: 0
      }
    )
  } else {
    alert(t('map.geoUnsupportedAlert'))
  }
}

// 부드러운 마커(와 이름 라벨) 이동을 위한 애니메이션 함수
const animateMarkerTo = (marker, startPos, endPos, duration = 250) => {
  if (!mapInstance.value) return
  const proj = mapInstance.value.getProjection()
  if (!proj) return
  
  const startPoint = proj.pointFromCoords(startPos)
  const endPoint = proj.pointFromCoords(endPos)
  const startTime = performance.now()
  
  const step = (currentTime) => {
    let progress = (currentTime - startTime) / duration
    if (progress > 1) progress = 1
    
    // easeOutQuad (부드럽게 감속)
    const easing = 1 - (1 - progress) * (1 - progress)
    const currentX = startPoint.x + (endPoint.x - startPoint.x) * easing
    const currentY = startPoint.y + (endPoint.y - startPoint.y) * easing
    
    const currentLatLng = proj.coordsFromPoint(new window.kakao.maps.Point(currentX, currentY))
    marker.setPosition(currentLatLng)
    
    // 이름 텍스트 라벨이 있다면 같이 이동
    if (marker.nameLabelRef) {
      marker.nameLabelRef.setPosition(currentLatLng)
    }
    
    // 만약 현재 이동 중인 마커가 선택된 장소라면, 큰 고정 팝업(selectedOverlay)도 같이 이동
    if (selectedOverlay && mapStore.selectedLocation?.id === marker.locData?.id) {
      selectedOverlay.setPosition(currentLatLng)
    }
    
    if (progress < 1) {
      requestAnimationFrame(step)
    }
  }
  requestAnimationFrame(step)
}

const resetSpiderfiedMarkers = () => {
  spiderfiedMarkers.forEach(m => {
    animateMarkerTo(m, m.getPosition(), m.originalPosition, 200)
    m.isSpiderfied = false

    // 원상복구 시 z-index 되돌리기
    m.setZIndex(0)
    if (m.nameLabelRef) m.nameLabelRef.setZIndex(900)
  })
  spiderfiedMarkers = []

  // 펼침 도중 도착해서 보류해 둔 장소 데이터가 있으면 이제 반영
  // (drawMarkers 내부에서 이 함수가 다시 불려도 pendingLocations는 이미 null이라 재귀되지 않음)
  if (pendingLocations) {
    const locs = pendingLocations
    pendingLocations = null
    drawMarkers(locs)
  }
}

onMounted(() => {
  initMap()
  setupLeftPanelTracking()
})

onUnmounted(() => {
  if (panelResizeObserver) {
    panelResizeObserver.disconnect()
    panelResizeObserver = null
  }
})

// App.vue(채팅 도메인 파일)를 직접 수정하지 않고, DOM에서 .left-panel을 찾아 ResizeObserver로
// 너비 변화(드래그 리사이즈 포함)를 실시간 추적한다. 기존 idle/클릭 핸들러들이 쓰는
// querySelector('.left-panel') 패턴과 동일한 셀렉터를 재사용한다.
const setupLeftPanelTracking = () => {
  const panel = document.querySelector('.left-panel') || document.querySelector('.place-list-panel')
  if (!panel) return

  leftPanelWidth.value = panel.offsetWidth
  syncCategoryFilterLeft()

  panelResizeObserver = new ResizeObserver((entries) => {
    for (const entry of entries) {
      leftPanelWidth.value = entry.contentRect.width
      syncCategoryFilterLeft()
    }
  })
  panelResizeObserver.observe(panel)
}

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
    level: 5 // 처음 진입 시 핀이 바로 보이도록 레벨을 5(좁은 범위)로 설정
  }
  mapInstance.value = new window.kakao.maps.Map(container, options)
  
  // 마커 클러스터러 생성 (네이버 부동산 스타일)
  clustererInstance.value = new window.kakao.maps.MarkerClusterer({
    map: mapInstance.value,
    averageCenter: true, // 클러스터에 포함된 마커들의 평균 위치를 클러스터 마커 위치로 설정
    minLevel: 3,         // 더 확대해야 풀리도록(3레벨부터 클러스터링) 설정
    gridSize: 80,        // 기본값 60보다 반경을 넓혀서 더 많은 핀을 한 덩어리로 잘 묶게 만듦
    disableClickZoom: true, // 기본 줌인 기능을 끄고 수동으로 시각적 중앙을 맞춰 줌인할 예정
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
  
  // 클러스터링이 완료될 때마다 라벨을 갱신 (클러스터 밖으로 튕겨나온 낱개 핀만 라벨 표시)
  window.kakao.maps.event.addListener(clustererInstance.value, 'clustered', () => {
    updateNameLabels()
  })
  
  // 클러스터 클릭 시 시각적 중앙(왼쪽 패널 고려)으로 줌 인 하는 커스텀 로직
  window.kakao.maps.event.addListener(clustererInstance.value, 'clusterclick', (cluster) => {
    const panel = document.querySelector('.left-panel') || document.querySelector('.place-list-panel')
    const panelWidth = panel ? panel.offsetWidth : 550
    
    // 클러스터에 포함된 마커들의 영역(바운더리)을 구합니다.
    const bounds = cluster.getBounds()
    
    // 카카오맵의 setBounds는 인자로 padding(상, 우, 하, 좌)을 받습니다.
    // 왼쪽 패널 너비만큼 좌측 패딩을 주고, 나머지 면에도 넉넉한 여백(100px)을 주어 
    // 마커들이 패널을 피해 오른쪽 빈 공간의 딱 정가운데에 알맞은 크기로 꽉 차게 렌더링되게 만듭니다.
    mapInstance.value.setBounds(bounds, 100, 100, 100, panelWidth + 100)
  })
  
  // 줌 컨트롤 추가 (우측 상단으로 이동 - AI 챗봇 버튼과 겹침 방지)
  const zoomControl = new window.kakao.maps.ZoomControl()
  mapInstance.value.addControl(zoomControl, window.kakao.maps.ControlPosition.TOPRIGHT)

  console.log("카카오 지도가 성공적으로 렌더링되었습니다.")

  // 맵 인스턴스 렌더링 직후 현재 스토어에 있는 위치 핀 찍기
  drawMarkers(mapStore.locations)
  
  // 지도가 이동/확대/축소 완료될 때(idle)마다 화면에 보이는 범위 내 장소만 검색 (디바운스 적용)
  window.kakao.maps.event.addListener(mapInstance.value, 'idle', () => {
    if (idleTimer) clearTimeout(idleTimer)
    
    idleTimer = setTimeout(() => {
      const bounds = mapInstance.value.getBounds()
      if (!bounds) return
      
      const sw = bounds.getSouthWest()
      const ne = bounds.getNorthEast()
      const physicalCenter = mapInstance.value.getCenter()
      const currentLevel = mapInstance.value.getLevel()
      
      // 줌 레벨이 7 이상(너무 넓음)이면 핀 로드 생략하고 안내문구 표시
      if (currentLevel >= 7) {
        mapStore.isZoomOutTooMuch = true
        mapStore.locations = [] // 화면 핀 지우기
        return
      }
      mapStore.isZoomOutTooMuch = false
      
      // 왼쪽 패널(Left Panel) 너비를 고려한 시각적 중앙(Visual Center) 계산
      const proj = mapInstance.value.getProjection()
      let visualCenter = physicalCenter
      if (proj) {
        const panel = document.querySelector('.left-panel') || document.querySelector('.place-list-panel')
        // 패널이 없으면 기본 550px 가정, 시각적 중앙은 실제 중심보다 패널 절반만큼 우측에 위치
        const panelWidth = panel ? panel.offsetWidth : 550
        let point = proj.pointFromCoords(physicalCenter)
        point.x = point.x + (panelWidth / 2)
        visualCenter = proj.coordsFromPoint(point)
      }
      
      // 현재 선택된 카테고리 필터를 유지한 채로 화면 범위 내 장소를 다시 조회
      mapStore.fetchLocations(mapStore.categoryFilter, null, {
        sw_lat: sw.getLat(),
        sw_lng: sw.getLng(),
        ne_lat: ne.getLat(),
        ne_lng: ne.getLng(),
        center_lat: visualCenter.getLat(),
        center_lng: visualCenter.getLng()
      })
    }, 300) // 0.3초 동안 추가 이동이 없으면 한 번만 API 호출
  })

  // 지도 빈 공간 클릭 시 펼쳐진 마커들 원상복구
  window.kakao.maps.event.addListener(mapInstance.value, 'click', () => {
    resetSpiderfiedMarkers()
  })

  // 줌 레벨이 변경될 때(확대/축소) 장소 이름 라벨 표시 여부 업데이트
  window.kakao.maps.event.addListener(mapInstance.value, 'zoom_changed', () => {
    resetSpiderfiedMarkers() // 줌 변경 시에도 원상복구
    updateNameLabels()
  })

  // 지도 생성 직후 데이터를 가져오도록 idle 이벤트를 1회 강제 트리거
  setTimeout(() => {
    if (mapInstance.value) {
      window.kakao.maps.event.trigger(mapInstance.value, 'idle')
    }
  }, 100)
}

const updateNameLabels = () => {
  if (!mapInstance.value) return
  const currentLevel = mapInstance.value.getLevel()
  const showLabels = currentLevel <= 5 // 레벨 5 이하일 때 낱개로 튀어나온 핀에 라벨 표시 가능
  
  nameLabelOverlays.forEach(item => {
    const marker = markers.find(m => m.locData.id === item.id)
    const isMarkerVisible = marker && marker.getMap() !== null
    
    // 마커가 클러스터에 안 묶이고 화면에 보일 때만 라벨 표시 (선택된 장소는 제외)
    if (showLabels && isMarkerVisible && mapStore.selectedLocation?.id !== item.id) {
      item.overlay.setMap(mapInstance.value)
    } else {
      item.overlay.setMap(null)
    }
  })
}

// 카테고리별 컬러 매핑 (디자인 명세서 참조)
const catColors = {
  '관광지': '#f15b4c',
  '문화시설': '#3f8fd0',
  '쇼핑': '#8a6fd6',
  '숙박': '#5aa06a',
  '레포츠': '#1abc9c',
  '축제공연행사': '#e0507a',
  '여행코스': '#c9a227'
}

const drawMarkers = (locations) => {
  if (!mapInstance.value || !window.kakao || !clustererInstance.value || !Array.isArray(locations)) return

  // 기존 핀(마커) 메모리에서 완전히 지우기 (버그 방지)
  markers.forEach(m => m.setMap(null))
  
  // 기존 클러스터러 초기화
  clustererInstance.value.clear()
  markers = []
  
  // 데이터 갱신 시(이동/확대 등) 기존에 남아있는 오버레이들 완벽 클린업
  nameLabelOverlays.forEach(item => item.overlay.setMap(null))
  nameLabelOverlays = []
  
  if (activeHoverOverlay) {
    activeHoverOverlay.setMap(null)
    activeHoverOverlay = null
  }
  
  resetSpiderfiedMarkers()

  locations.forEach(loc => {
    // 위도 경도 유효성 검사
    if (!loc.latitude || !loc.longitude) return

    const position = new window.kakao.maps.LatLng(loc.latitude, loc.longitude)
    const color = catColors[loc.category] || '#f15b4c'

    // CustomOverlay는 클러스터링 시 내부 DOM 에러(Cannot read properties of null)를 유발하므로, 
    // SVG 이미지를 Data URI로 변환하여 정식 Marker와 MarkerImage를 사용합니다.
    const svgString = `
      <svg xmlns="http://www.w3.org/2000/svg" width="34" height="42" viewBox="0 0 34 42">
        <path d="M17 0C7.6 0 0 7.6 0 17c0 12.8 17 25 17 25s17-12.2 17-25C34 7.6 26.4 0 17 0z" fill="${color}" stroke="#ffffff" stroke-width="2.5"/>
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
    marker.originalPosition = position
    marker.locData = loc

    // 마커 클릭 이벤트 바인딩 (Spiderfier 로직 적용)
    window.kakao.maps.event.addListener(marker, 'click', () => {
      const proj = mapInstance.value.getProjection()
      if (!proj) return
      
      const clickedPoint = proj.pointFromCoords(marker.originalPosition)
      if (!clickedPoint) {
        // 애니메이션 도중 클릭하여 좌표 계산이 안 되면 바로 라우터 강제 이동 처리
        mapStore.selectLocation(loc)
        router.push(`/locations/${loc.id}/posts`)
        return
      }
      
      // 픽셀 거리 30 이내로 겹치는 마커 찾기
      const overlappingMarkers = markers.filter(m => {
        const p = proj.pointFromCoords(m.originalPosition)
        if (!p) return false
        const dx = p.x - clickedPoint.x
        const dy = p.y - clickedPoint.y
        return Math.sqrt(dx*dx + dy*dy) < 30
      })

      // 이미 펼쳐진 상태이거나, 겹치는 마커가 자신뿐이라면 -> 찐 클릭(게시판 이동)
      if (marker.isSpiderfied || overlappingMarkers.length <= 1) {
        resetSpiderfiedMarkers()
        
        // mapStore에 선택을 알리면 알아서 watch 훅에서 부드러운 화면 이동 및 줌인을 수행합니다.
        mapStore.selectLocation(loc)
        
        router.push(`/locations/${loc.id}/posts`)
      } else {
        // 겹쳐진 핀이 여러 개라면 방사형(거미줄)으로 촤라락 펼치기
        resetSpiderfiedMarkers()
        
        const angleStep = (Math.PI * 2) / overlappingMarkers.length
        const radius = 45 // 45픽셀 밖으로 원형 배치
        
        overlappingMarkers.forEach((m, idx) => {
          const angle = idx * angleStep
          const nx = clickedPoint.x + Math.cos(angle) * radius
          const ny = clickedPoint.y + Math.sin(angle) * radius
          const newPos = proj.coordsFromPoint(new window.kakao.maps.Point(nx, ny))
          
          animateMarkerTo(m, m.originalPosition, newPos, 300)
          m.isSpiderfied = true
          
          // 펼쳐진 핀이 다른 핀들보다 앞에 보이도록 z-index 상승
          m.setZIndex(100)
          if (m.nameLabelRef) m.nameLabelRef.setZIndex(950)
          
          spiderfiedMarkers.push(m)
        })
      }
    })

    // 지도 확대 시 보일 장소 이름 텍스트 라벨 생성
    const nameLabel = new window.kakao.maps.CustomOverlay({
      content: `<div class="marker-name-label">${loc.name}</div>`,
      position: position,
      yAnchor: 2.8, // 핀보다 위에 위치
      zIndex: 900
    });
    nameLabelOverlays.push({ id: loc.id, overlay: nameLabel })
    
    // 애니메이션 헬퍼에서 접근 가능하도록 참조 저장
    marker.nameLabelRef = nameLabel

    // Hover (마우스 오버) 이벤트 바인딩: 커스텀 오버레이로 사진/설명 Pane 띄우기
    window.kakao.maps.event.addListener(marker, 'mouseover', () => {
      // 기존에 떠 있던 다른 장소의 hover 오버레이 무조건 제거
      if (activeHoverOverlay) {
        activeHoverOverlay.setMap(null);
      }
      
      // 호버 시 현재 지역명 라벨 숨김
      nameLabel.setMap(null);

      // 이미지가 없으면 기본 회색 박스
      const imageUrl = loc.image_url || '';
      const imageTag = imageUrl ? `<div class="hover-image" style="background-image: url('${imageUrl}')"></div>` : `<div class="hover-image no-img">${t('map.noPhoto')}</div>`;

      const content = `
        <div class="hover-pane">
          ${imageTag}
          <div class="hover-info">
            <div class="hover-title">${loc.name}</div>
            <div class="hover-category" style="color: ${color}">${t(`common.category.${loc.category || '기타'}`)}</div>
          </div>
        </div>
      `;

      activeHoverOverlay = new window.kakao.maps.CustomOverlay({
        content: content,
        position: marker.getPosition(), // 애니메이션 이동 상태 고려해 marker의 현재 좌표
        yAnchor: 1.3, // 핀 바로 위에 적당히 뜨도록 위치 조정
        zIndex: 1100 // 선택된 오버레이(1000)보다 높게 설정하여 안 가려지도록 함
      });
      
      activeHoverOverlay.setMap(mapInstance.value);
    });

    // mouseout 이벤트에 삭제 로직 바인딩 (재선언 방지 위해 밖으로 분리)
    window.kakao.maps.event.addListener(marker, 'mouseout', () => {
      if (activeHoverOverlay) {
        activeHoverOverlay.setMap(null);
        activeHoverOverlay = null;
      }
      // 아웃 시 선택된 장소가 아니고, 마커가 화면에 보이며 줌 레벨이 5 이하일 때 복구
      if (mapStore.selectedLocation?.id !== loc.id && marker.getMap() !== null && mapInstance.value.getLevel() <= 5) {
        nameLabel.setMap(mapInstance.value);
      }
    });

    // 개별적으로 setMap() 하지 않고 배열에만 모음
    markers.push(marker)
  })

  // 클러스터러에 마커들을 한 번에 추가
  clustererInstance.value.addMarkers(markers)
  
  // 방금 만든 라벨들에 대해 현재 줌 레벨 기준으로 표시 여부 초기 판별
  updateNameLabels()
}

// 스토어의 데이터 변경 감지 (검색, 필터링 등)
watch(() => mapStore.locations, (newLocations) => {
  // 핀이 방사형으로 펼쳐진(spiderfied) 도중에 재그리기가 끼어들면 펼침이 즉시 초기화됨
  // (idle 디바운스 + API 지연으로 뒤늦게 도착한 응답이 대표 케이스) — 원상복구 시점까지 보류
  if (spiderfiedMarkers.length > 0) {
    pendingLocations = newLocations
    return
  }
  drawMarkers(newLocations)
}, { deep: true })

// 왼쪽 목록 등에서 장소 선택 시 지도 중심 부드럽게 이동 및 오버레이 띄우기
watch(() => mapStore.selectedLocation, (loc) => {
  if (selectedOverlay) {
    selectedOverlay.setMap(null)
    selectedOverlay = null
  }
  
  if (loc && loc.latitude && loc.longitude && mapInstance.value) {
    const position = new window.kakao.maps.LatLng(loc.latitude, loc.longitude)
    
    const panel = document.querySelector('.left-panel') || document.querySelector('.place-list-panel')
    const panelWidth = panel ? panel.offsetWidth : 550
    
    // 멀리서(레벨 5 이상) 보고 있었다면 핀이 있는 곳을 중심으로 먼저 줌 인 하고, 그 핀을 중앙으로 당겨옵니다.
    const currentLevel = mapInstance.value.getLevel()
    if (currentLevel > 4) {
      mapInstance.value.setLevel(4, { animate: true, anchor: position })
      
      // 줌 애니메이션이 안정된 직후 시각적 중앙으로 당겨오기
      setTimeout(() => {
        const proj = mapInstance.value.getProjection()
        if (proj) {
          let point = proj.pointFromCoords(position)
          point.x = point.x - (panelWidth / 2)
          mapInstance.value.panTo(proj.coordsFromPoint(point))
        } else {
          mapInstance.value.panTo(position)
        }
      }, 250)
    } else {
      // 이미 충분히 가깝다면 바로 시각적 중앙으로 당겨오기
      const proj = mapInstance.value.getProjection()
      if (proj) {
        let point = proj.pointFromCoords(position)
        point.x = point.x - (panelWidth / 2)
        mapInstance.value.panTo(proj.coordsFromPoint(point))
      } else {
        mapInstance.value.panTo(position)
      }
    }
    
    // 오버레이 생성 및 표시
    const color = catColors[loc.category] || '#f15b4c'
    const imageUrl = loc.image_url || ''
    const imageTag = imageUrl ? `<div class="hover-image" style="background-image: url('${imageUrl}')"></div>` : `<div class="hover-image no-img">${t('map.noPhoto')}</div>`
    const content = `
      <div class="hover-pane">
        ${imageTag}
        <div class="hover-info">
          <div class="hover-title">${loc.name}</div>
          <div class="hover-category" style="color: ${color}">${t(`common.category.${loc.category || '기타'}`)}</div>
        </div>
      </div>
    `
    selectedOverlay = new window.kakao.maps.CustomOverlay({
      content: content,
      position: position,
      yAnchor: 1.3, // 핀과 적당한 간격
      zIndex: 1000
    })
    selectedOverlay.setMap(mapInstance.value)
    
    // 선택된 마커의 텍스트 라벨 숨기기 및 이전 선택 라벨 복구 (updateNameLabels 재호출)
    updateNameLabels()
  }
}, { immediate: true })

// 길찾기(경로 안내) 결과가 스토어에 채워지면 지도에 폴리라인으로 그리기
watch(() => mapStore.routePath, (path) => {
  if (!mapInstance.value) return

  // 이전 경로/마커 정리
  clearRouteOverlays()

  if (!path || path.length === 0) return

  const allLinePoints = []
  const segments = mapStore.routeMode === 'transit' ? mapStore.routeSegments : null

  if (segments?.length) {
    segments.forEach((segment) => {
      const linePath = toKakaoLinePath(segment.path)
      if (linePath.length < 2) return

      const style = routeLineStyles[segment.mode] || routeLineStyles.walk
      const polyline = new window.kakao.maps.Polyline({
        path: linePath,
        strokeWeight: style.weight,
        strokeColor: style.color,
        strokeOpacity: 0.9,
        strokeStyle: style.style
      })
      polyline.setMap(mapInstance.value)
      routePolylines.push(polyline)
      allLinePoints.push(...linePath)
    })
  } else {
    const linePath = toKakaoLinePath(path)
    if (linePath.length < 2) return

    const style = routeLineStyles.car
    const polyline = new window.kakao.maps.Polyline({
      path: linePath,
      strokeWeight: style.weight,
      strokeColor: style.color,
      strokeOpacity: 0.85,
      strokeStyle: style.style
    })
    polyline.setMap(mapInstance.value)
    routePolylines.push(polyline)
    allLinePoints.push(...linePath)
  }

  if (allLinePoints.length < 2) return

  // 출발/도착 지점 마커 표시
  const startMarker = new window.kakao.maps.Marker({ position: allLinePoints[0] })
  const endMarker = new window.kakao.maps.Marker({ position: allLinePoints[allLinePoints.length - 1] })
  startMarker.setMap(mapInstance.value)
  endMarker.setMap(mapInstance.value)
  routeEndpointMarkers = [startMarker, endMarker]

  // 경로 전체가 화면에 들어오도록 범위 조정
  const bounds = new window.kakao.maps.LatLngBounds()
  allLinePoints.forEach(pt => bounds.extend(pt))
  mapInstance.value.setBounds(bounds)
})
</script>

<style scoped>
.map-wrapper {
  position: relative;
  width: 100%;
  height: 100%;
}

.kakao-map-container {
  width: 100%;
  height: 100%;
  /* 지도가 부드럽게 나타나도록 기본 스타일 지정 */
  background: var(--bg-color);
}

/* 플로팅 줌 안내 배너 CSS */
.floating-zoom-warning {
  position: absolute;
  top: 24px;
  /* 화면이 왼쪽 패널(550px 고정)로 가려지므로, 우측 텅 빈 공간의 정확한 정중앙 좌표 설정 */
  /* 550px + (100vw - 550px) / 2 = 50vw + 275px */
  left: calc(50% + 275px); 
  transform: translateX(-50%);
  background: rgba(28, 27, 26, 0.85); /* 다크 모드 풍의 반투명 배경 */
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  padding: 12px 20px;
  border-radius: 30px;
  display: flex;
  align-items: center;
  gap: 12px;
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.25);
  z-index: 20;
  pointer-events: none; /* 클릭 방해 금지 */
}

.floating-zoom-warning svg {
  width: 20px;
  height: 20px;
  color: #fff;
}

.floating-zoom-warning .text p {
  font-weight: 700;
  font-size: 14px;
  color: #fff;
  margin: 0 0 2px 0;
}

.floating-zoom-warning .text span {
  font-size: 12px;
  color: #d1cfc7;
}

/* 뷰 트랜지션 (나타나고 사라질 때 부드럽게) */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(-10px);
}

/* 내 위치 버튼 CSS */
.my-location-btn {
  position: absolute;
  right: 20px;
  bottom: 30px;
  width: 44px;
  height: 44px;
  background: #fff;
  border: 1px solid #eceae6;
  border-radius: 50%;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  cursor: pointer;
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #1c1b1a;
  transition: all 0.2s ease;
}

.my-location-btn:hover {
  background: #f4f2ee;
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
}

.my-location-btn svg {
  width: 22px;
  height: 22px;
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

/* 카카오맵이 CustomOverlay 콘텐츠를 감싸는 무명 래퍼 div가 마우스 이벤트를 가로채므로,
   내부 콘텐츠의 pointer-events: none만으로는 부족하다. 래퍼까지 이벤트를 통과시켜야
   라벨이나 팝업에 가려진 다른 핀들도 hover가 가능해진다. */
:deep(div:has(> .marker-name-label)),
:deep(div:has(> .hover-pane)) {
  pointer-events: none;
}

:deep(.marker-name-label) {
  background: rgba(255, 255, 255, 0.95);
  padding: 4px 9px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 700;
  color: #1c1b1a;
  box-shadow: 0 3px 8px rgba(0,0,0,0.16);
  border: 1px solid #eceae6;
  white-space: nowrap;
  pointer-events: none; /* 클릭 방해 금지 */
}
</style>
