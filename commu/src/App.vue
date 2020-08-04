<template>
  <div id="app">
    <!-- <Login/> -->
    <h3 style="margin:auto;">幽灵社区</h3>
    <el-container>
      <el-header><Topnavi v-on:tabtab="tabClick"/></el-header>
      <keep-alive>
        <component v-bind:is="currentTabComponent"></component>
      </keep-alive>
    </el-container>
  </div>
</template>

<script>
import Topnavi from './components/Topnavi.vue'
import Login from './components/Login.vue'
import Welcome from './components/Welcome.vue'

export default {
  name: 'app',
  components: {
    Topnavi,
    Login,
    Welcome,
  },
  methods:{
    tabClick:function(event){
      console.log("tabClickEV:"+event);
      this.currentTabComponent=event;
    },
  },
  data:function(){
    return {
      currentTabComponent:"Welcome",
      };
  }
}
</script>

<style>
#app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>
