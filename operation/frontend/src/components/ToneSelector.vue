<template>
  <div class="tone-selector">
    <h3 class="text-xl font-semibold mb-4 text-gray-800">톤 선택</h3>
    
    <!-- 선택된 톤 표시 -->
    <div v-if="selectedTone" class="mb-4 p-3 bg-green-50 border border-green-200 rounded-lg">
      <div class="flex items-center justify-between">
        <div>
          <span class="text-green-800 font-medium">선택된 톤: {{ getSelectedToneLabel() }}</span>
          <p class="text-green-600 text-sm mt-1">{{ getSelectedToneDescription() }}</p>
        </div>
        <button 
          @click="clearSelection"
          class="text-green-600 hover:text-green-800 text-lg leading-none"
        >
          ✕
        </button>
      </div>
    </div>

    <!-- 톤 옵션들 -->
    <div class="space-y-3">
      <div 
        v-for="tone in TONE_OPTIONS" 
        :key="tone.value"
        @click="selectTone(tone.value)"
        :class="[
          'p-4 border rounded-lg cursor-pointer transition-all duration-200',
          selectedTone === tone.value
            ? 'border-blue-500 bg-blue-50 shadow-md'
            : 'border-gray-200 hover:border-blue-300 hover:bg-blue-25'
        ]"
      >
        <div class="flex items-start">
          <!-- 라디오 버튼 스타일 -->
          <div class="flex-shrink-0 mt-1 mr-3">
            <div :class="[
              'w-4 h-4 rounded-full border-2 transition-colors',
              selectedTone === tone.value 
                ? 'border-blue-500 bg-blue-500' 
                : 'border-gray-300'
            ]">
              <div v-if="selectedTone === tone.value" class="w-2 h-2 bg-white rounded-full m-0.5"></div>
            </div>
          </div>
          
          <!-- 톤 내용 -->
          <div class="flex-1">
            <h4 :class="[
              'font-medium transition-colors',
              selectedTone === tone.value ? 'text-blue-800' : 'text-gray-800'
            ]">
              {{ tone.label }}
            </h4>
            <p :class="[
              'text-sm mt-1 transition-colors',
              selectedTone === tone.value ? 'text-blue-600' : 'text-gray-600'
            ]">
              {{ tone.description }}
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- 추천 톤 (선택사항) -->
    <div class="mt-6 p-4 bg-gray-50 rounded-lg">
      <h4 class="text-sm font-medium text-gray-700 mb-2">💡 톤 선택 가이드</h4>
      <ul class="text-sm text-gray-600 space-y-1">
        <li>• <strong>식품/유아용품</strong>: 따뜻한 엄마의 말투 추천</li>
        <li>• <strong>건강/유기농</strong>: 자연주의 감성 추천</li>
        <li>• <strong>패션/뷰티</strong>: 발랄하고 경쾌한 추천</li>
        <li>• <strong>전자제품</strong>: 전문적이고 깔끔한 추천</li>
      </ul>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { TONE_OPTIONS } from '@/constants/productOptions'

export default {
  name: 'ToneSelector',
  emits: ['update:modelValue'],
  props: {
    modelValue: {
      type: String,
      default: ''
    }
  },
  setup(props, { emit }) {
    const selectedTone = ref(props.modelValue)

    // 톤 선택
    const selectTone = (toneValue) => {
      selectedTone.value = toneValue
      emit('update:modelValue', toneValue)
    }

    // 선택 취소
    const clearSelection = () => {
      selectedTone.value = ''
      emit('update:modelValue', '')
    }

    // 선택된 톤의 라벨 가져오기
    const getSelectedToneLabel = () => {
      const tone = TONE_OPTIONS.find(t => t.value === selectedTone.value)
      return tone ? tone.label : ''
    }

    // 선택된 톤의 설명 가져오기
    const getSelectedToneDescription = () => {
      const tone = TONE_OPTIONS.find(t => t.value === selectedTone.value)
      return tone ? tone.description : ''
    }

    return {
      selectedTone,
      selectTone,
      clearSelection,
      getSelectedToneLabel,
      getSelectedToneDescription,
      TONE_OPTIONS
    }
  }
}
</script>

<style scoped>
.tone-selector {
  @apply w-full;
}
</style>
