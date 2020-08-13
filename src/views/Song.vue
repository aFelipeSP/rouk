<template>
  <div class="song">
    <div
      class="song-property"
      v-for="(value, key) in song"
      :key="key"
    >
      <b>{{key}}</b>{{value}}
    </div>
  </div>
</template>

<script>
export default {
}
</script>
