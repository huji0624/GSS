import Vue from 'vue'
import App from './App.vue'
import './plugins/element.js'
import axios from 'axios';
import VueBus from 'vue-bus';

Vue.use(VueBus);

console.log("=====")
console.log(process.env.NODE_ENV)
if(process.env.NODE_ENV==="development"){
  axios.defaults.baseURL = 'http://localhost:8080';
}else{
  axios.defaults.baseURL = 'http://static.luckyhu.top:8080';
}
axios.defaults.withCredentials = true; // 允许携带cookie

Vue.config.productionTip = false

new Vue({
  render: h => h(App),
}).$mount('#app')
