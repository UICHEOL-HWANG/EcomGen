<template>
  <div class="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
    <div class="bg-white rounded-2xl max-w-md w-full p-6 max-h-[90vh] overflow-y-auto">
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-lg font-bold text-gray-900">카메라로 촬영</h3>
        <button @click="closeCamera" class="text-gray-400 hover:text-gray-600 text-2xl leading-none">×</button>
      </div>

      <!-- 카메라 화면 -->
      <div class="relative mb-6">
        <div class="w-full aspect-square bg-gray-900 rounded-lg overflow-hidden">
          <video
            ref="videoRef"
            v-show="!capturedImage && cameraReady"
            autoplay
            playsinline
            muted
            class="w-full h-full object-cover"
          ></video>
          
          <!-- 로딩 상태 -->
          <div v-if="!cameraReady && !error" class="w-full h-full flex items-center justify-center">
            <div class="text-center text-white">
              <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto mb-4"></div>
              <p class="text-sm">카메라를 준비하고 있습니다...</p>
            </div>
          </div>
          
          <!-- 캡처된 이미지 -->
          <div v-if="capturedImage" class="w-full h-full">
            <img :src="capturedImage" alt="Captured" class="w-full h-full object-cover" />
          </div>
        </div>
        
        <!-- 카메라 전환 버튼 -->
        <button 
          v-if="devices.length > 1 && cameraReady && !capturedImage"
          @click="switchCamera"
          class="absolute top-3 right-3 w-12 h-12 bg-black bg-opacity-50 rounded-full flex items-center justify-center text-white hover:bg-opacity-70 transition"
        >
          <span class="text-lg">🔄</span>
        </button>
        
        <!-- 촬영 버튼 (상단에 고정) -->
        <button 
          v-if="!capturedImage && cameraReady"
          @click="capturePhoto"
          class="absolute bottom-4 left-1/2 transform -translate-x-1/2 w-16 h-16 bg-white rounded-full flex items-center justify-center shadow-lg hover:bg-gray-100 transition"
        >
          <span class="text-2xl">📸</span>
        </button>
      </div>

      <!-- 버튼들 -->
      <div class="space-y-3">
        <!-- 촬영된 사진 안내 -->
        <div v-if="capturedImage" class="text-center mb-2">
          <h4 class="text-sm font-medium text-gray-700">촬영된 사진</h4>
        </div>
        
        <!-- 재촬영 버튼 -->
        <button 
          v-if="capturedImage"
          @click="retakePhoto"
          class="w-full py-3 bg-gray-600 text-white font-medium rounded-lg hover:bg-gray-700 transition flex items-center justify-center gap-2"
        >
          <span>🔄</span>
          다시 촬영
        </button>

        <!-- 사용하기 버튼 -->
        <button 
          v-if="capturedImage"
          @click="usePhoto"
          :disabled="uploading"
          class="w-full py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 disabled:opacity-50 transition flex items-center justify-center gap-2"
        >
          <span v-if="uploading">⏳</span>
          <span v-else>✅</span>
          {{ uploading ? '업로드 중...' : '이 사진 사용하기' }}
        </button>

        <!-- 취소 버튼 -->
        <button 
          @click="closeCamera"
          class="w-full py-2 border border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50 transition"
        >
          취소
        </button>
      </div>

      <!-- 에러 메시지 -->
      <div v-if="error" class="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
        <p class="text-sm text-red-600">{{ error }}</p>
        <button 
          @click="initCamera"
          class="mt-2 px-3 py-1 bg-red-600 text-white text-xs rounded hover:bg-red-700 transition"
        >
          다시 시도
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const emit = defineEmits(['close', 'captured'])

// 상태 관리
const videoRef = ref(null)
const canvasRef = ref(null)
const devices = ref([])
const currentDeviceIndex = ref(0)
const stream = ref(null)
const cameraReady = ref(false)
const capturedImage = ref(null)
const uploading = ref(false)
const error = ref('')

// 카메라 초기화
const initCamera = async () => {
  try {
    error.value = ''
    cameraReady.value = false
    
    // 기존 스트림 정리
    if (stream.value) {
      stream.value.getTracks().forEach(track => track.stop())
    }
    
    // 카메라 장치 목록 가져오기
    await getDevices()
    
    // 카메라 스트림 시작
    await startCamera()
    
  } catch (err) {
    console.error('카메라 초기화 실패:', err)
    if (err.name === 'NotAllowedError') {
      error.value = '카메라 권한이 거부되었습니다. 브라우저 설정에서 카메라 권한을 허용해주세요.'
    } else if (err.name === 'NotFoundError') {
      error.value = '카메라를 찾을 수 없습니다.'
    } else {
      error.value = '카메라에 접근할 수 없습니다: ' + err.message
    }
  }
}

// 카메라 장치 목록 가져오기
const getDevices = async () => {
  try {
    const mediaDevices = await navigator.mediaDevices.enumerateDevices()
    devices.value = mediaDevices.filter(device => device.kind === 'videoinput')
    
    // 후면 카메라 우선 선택
    const backCameraIndex = devices.value.findIndex(device => 
      device.label.toLowerCase().includes('back') || 
      device.label.toLowerCase().includes('rear') ||
      device.label.toLowerCase().includes('environment')
    )
    
    currentDeviceIndex.value = backCameraIndex >= 0 ? backCameraIndex : 0
    
  } catch (err) {
    console.error('장치 목록 가져오기 실패:', err)
  }
}

// 카메라 스트림 시작
const startCamera = async () => {
  try {
    const constraints = {
      video: {
        deviceId: devices.value[currentDeviceIndex.value]?.deviceId,
        width: { ideal: 640 },
        height: { ideal: 640 },
        facingMode: devices.value.length > 1 ? undefined : 'environment'
      }
    }
    
    stream.value = await navigator.mediaDevices.getUserMedia(constraints)
    
    if (videoRef.value) {
      videoRef.value.srcObject = stream.value
      videoRef.value.onloadedmetadata = () => {
        cameraReady.value = true
      }
    }
    
  } catch (err) {
    throw err
  }
}

// 사진 촬영
const capturePhoto = () => {
  if (!videoRef.value || !cameraReady.value) return
  
  try {
    // Canvas 생성
    const canvas = document.createElement('canvas')
    const video = videoRef.value
    
    // 정사각형으로 크롭
    const size = Math.min(video.videoWidth, video.videoHeight)
    canvas.width = size
    canvas.height = size
    
    const ctx = canvas.getContext('2d')
    
    // 중앙에서 정사각형으로 크롭하여 그리기
    const startX = (video.videoWidth - size) / 2
    const startY = (video.videoHeight - size) / 2
    
    ctx.drawImage(video, startX, startY, size, size, 0, 0, size, size)
    
    // base64로 변환
    capturedImage.value = canvas.toDataURL('image/jpeg', 0.8)
    
    console.log('사진이 촬영되었습니다')
    
  } catch (err) {
    error.value = '사진 촬영에 실패했습니다.'
    console.error('촬영 에러:', err)
  }
}

// 재촬영
const retakePhoto = () => {
  capturedImage.value = null
}

// 사진 사용하기
const usePhoto = async () => {
  if (!capturedImage.value) return

  try {
    uploading.value = true
    
    // base64를 Blob으로 변환
    const response = await fetch(capturedImage.value)
    const blob = await response.blob()
    
    // File 객체 생성
    const file = new File([blob], 'camera-capture.jpg', { type: 'image/jpeg' })
    
    // 부모 컴포넌트로 파일 전달
    emit('captured', file)
    
  } catch (err) {
    error.value = '사진 처리에 실패했습니다.'
    console.error('사진 처리 에러:', err)
  } finally {
    uploading.value = false
  }
}

// 카메라 전환
const switchCamera = async () => {
  if (devices.value.length <= 1) return
  
  currentDeviceIndex.value = (currentDeviceIndex.value + 1) % devices.value.length
  await startCamera()
}

// 카메라 닫기
const closeCamera = () => {
  if (stream.value) {
    stream.value.getTracks().forEach(track => track.stop())
  }
  emit('close')
}

// 컴포넌트 마운트 시
onMounted(() => {
  initCamera()
})

// 컴포넌트 언마운트 시
onUnmounted(() => {
  if (stream.value) {
    stream.value.getTracks().forEach(track => track.stop())
  }
})
</script>

<style scoped>
.aspect-square {
  aspect-ratio: 1 / 1;
}
</style>
