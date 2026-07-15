<template>
  <div ref="mapRef" class="route-mini-map"></div>
</template>

<script setup>
import { onMounted, ref, shallowRef, watch } from 'vue'

const props = defineProps({
  path: { type: Array, default: () => [] } // [{ lat, lng }, ...]
})

const mapRef = ref(null)
const mapInstance = shallowRef(null)
let polyline = null
let markers = []

// 우측 메인 지도(KakaoMap.vue)가 이미 SDK 스크립트를 로드해두므로, 여기서는
// window.kakao.maps가 준비될 때까지 짧게 폴링만 하고 새로 스크립트를 삽입하지 않는다.
const waitForKakao = () => {
  return new Promise((resolve, reject) => {
    if (window.kakao && window.kakao.maps) {
      resolve()
      return
    }
    let attempts = 0
    const timer = setInterval(() => {
      attempts += 1
      if (window.kakao && window.kakao.maps) {
        clearInterval(timer)
        resolve()
      } else if (attempts > 50) {
        clearInterval(timer)
        reject(new Error('Kakao Maps SDK 로드 대기 시간 초과'))
      }
    }, 100)
  })
}

const drawRoute = () => {
  if (!mapInstance.value || !window.kakao) return

  if (polyline) {
    polyline.setMap(null)
    polyline = null
  }
  markers.forEach(m => m.setMap(null))
  markers = []

  if (!props.path || props.path.length === 0) return

  const linePath = props.path.map(p => new window.kakao.maps.LatLng(p.lat, p.lng))

  polyline = new window.kakao.maps.Polyline({
    path: linePath,
    strokeWeight: 4,
    strokeColor: '#f15b4c',
    strokeOpacity: 0.9,
    strokeStyle: 'solid'
  })
  polyline.setMap(mapInstance.value)

  const startMarker = new window.kakao.maps.Marker({ position: linePath[0] })
  const endMarker = new window.kakao.maps.Marker({ position: linePath[linePath.length - 1] })
  startMarker.setMap(mapInstance.value)
  endMarker.setMap(mapInstance.value)
  markers = [startMarker, endMarker]

  const bounds = new window.kakao.maps.LatLngBounds()
  linePath.forEach(pt => bounds.extend(pt))
  mapInstance.value.setBounds(bounds, 24, 24, 24, 24)
}

onMounted(async () => {
  try {
    await waitForKakao()
    if (!mapRef.value) return
    mapInstance.value = new window.kakao.maps.Map(mapRef.value, {
      center: new window.kakao.maps.LatLng(37.5665, 126.9780),
      level: 5
    })
    drawRoute()
  } catch (err) {
    console.error('RouteMiniMap 초기화 실패:', err)
  }
})

watch(() => props.path, () => {
  drawRoute()
})
</script>

<style scoped>
.route-mini-map {
  width: 100%;
  height: 320px;
  border-radius: 14px;
  overflow: hidden;
  border: 1px solid var(--border-color);
  background: var(--bg-color, #eef0ea);
}
</style>
