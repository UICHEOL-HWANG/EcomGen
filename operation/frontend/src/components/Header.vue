<template>
  <header class="sticky top-0 z-50 w-full p-4">
    <div class="bg-white border border-gray-200 rounded-2xl shadow-lg max-w-sm mx-auto">
      <div class="flex items-center justify-center py-4 px-4">
        <router-link 
          to="/"
          class="block hover:opacity-80 transition-opacity"
        >
          <img 
            src="@/assets/logo.png" 
            alt="Shoplingo" 
            class="h-8 w-auto cursor-pointer"
          />
        </router-link>
      </div>
    </div>
  </header>
</template>

<script setup>
// No logic needed for static header
</script>