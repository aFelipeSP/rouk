import Vue from 'vue'
import App from './App.vue'
import './registerServiceWorker'
import router from './router'
import store from './store'
import axios from 'axios'
import { initSSE } from './sse.js'

axios.defaults.baseURL = 'http://127.0.0.1:5000/'
Vue.config.productionTip = false

initSSE()

new Vue({
  router,
  store,
  render: h => h(App)
}).$mount('#app')
