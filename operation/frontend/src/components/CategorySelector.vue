<template>
  <div class="category-selector">
    <h3 class="text-xl font-semibold mb-4 text-gray-800">상품 카테고리 선택</h3>
    
    <!-- 선택된 카테고리 표시 -->
    <div v-if="selectedCategory" class="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
      <div class="flex items-center justify-between">
        <span class="text-blue-800 font-medium">선택된 카테고리: {{ selectedCategory }}</span>
        <button 
          @click="clearSelection"
          class="text-blue-600 hover:text-blue-800 text-lg leading-none"
        >
          ✕
        </button>
      </div>
    </div>

    <!-- 검색 박스 -->
    <div class="relative mb-4">
      <div class="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400">
        🔍
      </div>
      <input
        v-model="searchTerm"
        type="text"
        placeholder="카테고리 검색... (예: 우유, 과자, 가전)"
        class="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
      />
    </div>

    <!-- 인기 카테고리 -->
    <div v-if="!searchTerm" class="mb-6">
      <h4 class="text-sm font-medium text-gray-700 mb-3">🔥 인기 카테고리</h4>
      <div class="flex flex-wrap gap-2">
        <button
          v-for="category in POPULAR_CATEGORIES"
          :key="category"
          @click="selectCategory(category)"
          :class="[
            'px-3 py-2 text-sm rounded-full border transition-colors',
            selectedCategory === category
              ? 'bg-blue-500 text-white border-blue-500'
              : 'bg-gray-50 text-gray-700 border-gray-200 hover:bg-gray-100'
          ]"
        >
          {{ category }}
        </button>
      </div>
    </div>

    <!-- 그룹별 카테고리 (검색 없을 때) -->
    <div v-if="!searchTerm" class="space-y-4">
      <div 
        v-for="(categories, groupName) in CATEGORY_GROUPS" 
        :key="groupName" 
        class="border border-gray-200 rounded-lg"
      >
        <div class="bg-gray-50 px-4 py-3 border-b border-gray-200">
          <h4 class="font-medium text-gray-800">{{ groupName }}</h4>
        </div>
        <div class="p-3">
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
            <button
              v-for="category in categories"
              :key="category"
              @click="selectCategory(category)"
              :class="[
                'text-left px-3 py-2 text-sm rounded-md border transition-colors',
                selectedCategory === category
                  ? 'bg-blue-500 text-white border-blue-500'
                  : 'bg-white text-gray-700 border-gray-200 hover:bg-blue-50 hover:border-blue-300'
              ]"
            >
              {{ category }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 검색 결과 -->
    <div v-else class="border border-gray-200 rounded-lg">
      <div class="bg-gray-50 px-4 py-3 border-b border-gray-200">
        <h4 class="font-medium text-gray-800">
          검색 결과 ({{ filteredCategories.length }}개)
        </h4>
      </div>
      <div class="p-3">
        <div v-if="filteredCategories.length > 0" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
          <button
            v-for="category in filteredCategories"
            :key="category"
            @click="selectCategory(category)"
            :class="[
              'text-left px-3 py-2 text-sm rounded-md border transition-colors',
              selectedCategory === category
                ? 'bg-blue-500 text-white border-blue-500'
                : 'bg-white text-gray-700 border-gray-200 hover:bg-blue-50 hover:border-blue-300'
            ]"
          >
            {{ category }}
          </button>
        </div>
        <div v-else class="text-center py-8 text-gray-500">
          검색 결과가 없습니다. 다른 키워드로 검색해보세요.
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { CATEGORIES, CATEGORY_GROUPS, POPULAR_CATEGORIES } from '@/constants/productOptions'

export default {
  name: 'CategorySelector',
  emits: ['update:modelValue'],
  props: {
    modelValue: {
      type: String,
      default: ''
    }
  },
  setup(props, { emit }) {
    const searchTerm = ref('')
    const selectedCategory = ref(props.modelValue)

    // 필터링된 카테고리
    const filteredCategories = computed(() => {
      if (!searchTerm.value) return CATEGORIES
      return CATEGORIES.filter(category => 
        category.toLowerCase().includes(searchTerm.value.toLowerCase())
      )
    })

    // 카테고리 선택
    const selectCategory = (category) => {
      selectedCategory.value = category
      emit('update:modelValue', category)
    }

    // 선택 취소
    const clearSelection = () => {
      selectedCategory.value = ''
      emit('update:modelValue', '')
    }

    return {
      searchTerm,
      selectedCategory,
      filteredCategories,
      selectCategory,
      clearSelection,
      CATEGORIES,
      CATEGORY_GROUPS,
      POPULAR_CATEGORIES
    }
  }
}
</script>

<style scoped>
.category-selector {
  @apply w-full;
}
</style>
