<template>
  <el-container>
    <el-aside width="200px">
    </el-aside>
    <el-main>
    </el-main>
  </el-container>
</template>

<script>
import common from '../plugins/common';

export default {
  name: 'Welcome',
  props: {
  },
  data:function(){
    return {
    }
  },
  created:function(){
    this.getList({})
  },
  methods:{
    getList:function(params){
      let out_this = this;
      common.get("hot",params,function(res){
        if(res&&res.data.err===0){
          out_this.$message.success("OK.")
          out_this.tableData = res.data.data;
          console.log(out_this.tableData)
        }else{
          out_this.$message.error("err:"+JSON.stringify(res.data))
        }
      },function(err){
        out_this.$message.error("err:"+err)
      })
    },
    handleRefresh:function(){
      this.getList({key:this.searchKey})
    }
  },
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
