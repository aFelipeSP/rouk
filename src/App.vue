<template>
  <div id="app">
    <router-view/>
  </div>
</template>

<script>
export default {
}
</script>

<style>
html, body {
  margin: 0px;
  height: 100%;
  width: 100%;
}

#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #495057;
  height: 100%;
}

.beam {
  font-size: 80%;
  padding: 5px 10px;
  border-radius: 9999999px;
}

/* width */
::-webkit-scrollbar {
  width: 12px;
}
/* Track */
::-webkit-scrollbar-track {
  background-color: transparent;
}
/* Handle */
::-webkit-scrollbar-thumb {
  background-color: #bbbbbb;
  border-radius: 100000px;
  background-clip: padding-box;
  border: 3px solid rgba(0, 0, 0, 0);
}
/* Handle on hover */
::-webkit-scrollbar-thumb:hover {
  background-color: #bbbbbb;
}
</style>
