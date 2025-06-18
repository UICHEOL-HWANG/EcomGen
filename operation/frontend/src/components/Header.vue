<template>
  <header class="w-full p-4">
    <div class="bg-white border border-gray-200 rounded-2xl shadow-sm max-w-sm mx-auto">
      <div class="flex items-center justify-center py-3 px-4">
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