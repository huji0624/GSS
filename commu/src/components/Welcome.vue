<template>
  <el-container>
    <!-- <el-aside width="200px">
    </el-aside> -->
    <el-main style="">
    
    <el-table
      :data="tableData"
      style="width: 70%;margin:auto;"
      header-cell-style="text-align :center;"
      cell-style="text-align :center;">
      <el-table-column
        prop="name"
        label="股票名">
      </el-table-column>
      <el-table-column
        prop="per"
        label="涨跌幅">
      </el-table-column>
      <el-table-column
        prop="hot"
        label="热度">
      </el-table-column>
    </el-table>
      
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
      tableData:[]
    }
  },
  created:function(){
    this.getList({})
  },
  methods:{
    getList:function(params){
      let out_this = this;
      common.get("hot",params,function(res){
        out_this.$message.success("OK.")
        let ret = res.data;
        ret = ret.sort(function(a,b){
          return b['hot']-a['hot']
        })
        out_this.tableData = ret;

        console.log(out_this.tableData)
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
