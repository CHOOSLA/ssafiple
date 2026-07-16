// 우측 메인 지도(KakaoMap.vue)가 이미 SDK 스크립트를 로드해두므로, 여기서는
// window.kakao.maps가 준비될 때까지 짧게 폴링만 하고 새로 스크립트를 삽입하지 않는다.
export function waitForKakao() {
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
