<script setup>
import { RouterView } from 'vue-router'
</script>

<template>
  <RouterView />
</template>

<style>
/*
  NO "scoped" here on purpose — these styles need to reach
  the #app div that Vue creates, which is outside our components.
*/
*, *::before, *::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

html, body, #app {
  width: 100%;
  min-height: 100vh;
}
</style>