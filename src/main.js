import Vue from 'vue'
import App from './App.vue'
import './registerServiceWorker'
import router from './router.js'
import store from './store.js'
import { initSSE } from './sse.js'
import './assets/style'

import axios from 'axios'
// axios.defaults.baseURL = 'http://127.0.0.1:5000/'

axios.interceptors.request.use(function (config) {
  store.commit('loading', true)
  return config
}, function (error) {
  store.commit('loading', false)
  return Promise.reject(error)
});

axios.interceptors.response.use(function (response) {
  store.commit('loading', false)
  return response
}, function (error) {
  store.commit('loading', false)
  return Promise.reject(error)
})

Vue.config.productionTip = false

new Vue({
  router,
  store,
  render: h => h(App),
  mounted () {
    initSSE()
  }
}).$mount('#app')
