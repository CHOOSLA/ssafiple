<template>
  <div ref="mapRef" class="route-mini-map"></div>
</template>

<script setup>
import { onMounted, ref, shallowRef, watch } from 'vue'
import { waitForKakao } from '@/utils/kakaoLoader'

const props = defineProps({
  path: { type: Array, default: () => [] }, // [{ lat, lng }, ...]
  segments: { type: Array, default: null } // [{ mode: 'walk'|'bus'|'subway', path: [{lat,lng}] }, ...]
})

const mapRef = ref(null)
const mapInstance = shallowRef(null)
let polylines = []
let markers = []

const SEGMENT_COLORS = {
  subway: '#3b82f6',
  bus: '#22c55e',
  walk: '#9ca3af'
}

const clearOverlays = () => {
  polylines.forEach(p => p.setMap(null))
  polylines = []
  markers.forEach(m => m.setMap(null))
  markers = []
}

const drawRoute = () => {
  if (!mapInstance.value || !window.kakao) return

  clearOverlays()

  if (props.segments && props.segments.length > 0) {
    const bounds = new window.kakao.maps.LatLngBounds()

    props.segments.forEach((segment) => {
      const segmentPath = (segment.path || []).map(p => new window.kakao.maps.LatLng(p.lat, p.lng))
      if (segmentPath.length === 0) return

      const polyline = new window.kakao.maps.Polyline({
        path: segmentPath,
        strokeWeight: 4,
        strokeColor: SEGMENT_COLORS[segment.mode] || SEGMENT_COLORS.walk,
        strokeOpacity: 0.9,
        strokeStyle: segment.mode === 'walk' ? 'shortdash' : 'solid'
      })
      polyline.setMap(mapInstance.value)
      polylines.push(polyline)
      segmentPath.forEach(pt => bounds.extend(pt))
    })

    if (!bounds.isEmpty()) {
      mapInstance.value.setBounds(bounds, 24, 24, 24, 24)
    }
    return
  }

  if (!props.path || props.path.length === 0) return

  const linePath = props.path.map(p => new window.kakao.maps.LatLng(p.lat, p.lng))

  const polyline = new window.kakao.maps.Polyline({
    path: linePath,
    strokeWeight: 4,
    strokeColor: '#f15b4c',
    strokeOpacity: 0.9,
    strokeStyle: 'solid'
  })
  polyline.setMap(mapInstance.value)
  polylines.push(polyline)

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

watch([() => props.path, () => props.segments], () => {
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
