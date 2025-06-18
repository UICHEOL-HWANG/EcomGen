<template>
  <div id="app" class="min-h-screen bg-gray-50">
    <!-- 모바일 중심 컨테이너 -->
    <div class="max-w-sm mx-auto bg-gray-50 min-h-screen flex flex-col">
      <Header />
      <main class="flex-1 pb-20">
        <router-view />
      </main>
      <BottomNav />
    </div>
  </div>
</template>

<script setup>
import Header from '@/components/Header.vue'
import BottomNav from '@/components/BottomNav.vue'
</script>

<style>
body {
  margin: 0;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background-color: #f9fafb;
}

/* 스크롤바 숨기기 */
::-webkit-scrollbar {
  display: none;
}

* {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>