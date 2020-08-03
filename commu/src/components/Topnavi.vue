<template>
<el-menu :default-active="activeIndex" class="el-menu-demo" mode="horizontal" @select="handleSelect">
  <el-menu-item index="Welcome">热门股票</el-menu-item>
  <!-- <el-button type="success" @click="loginClick">登录</el-button> -->
</el-menu>
</template>

<script>
import Vue from 'vue';

export default {
  name: 'TopNavi',
  props: {
  },
  data() {
    return {
      activeIndex: '1',
    };
  },
  methods: {
    handleSelect(key, keyPath){
      console.log(key, keyPath);
      this.$emit("tabtab",key);
    },
    loginClick(){
      Vue.bus.emit('needlogin');
    },
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
