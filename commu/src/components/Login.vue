<template>
<el-dialog title="登录" :visible.sync="dialogFormVisible" :before-close="handleClose">
  <el-form :model="form">
    <el-form-item label="输入体验码:" >
      <el-input v-model="form.name" autocomplete="off"></el-input>
    </el-form-item>
  </el-form>
  <div slot="footer" class="dialog-footer">
    <el-button @click="cancelClick">取 消</el-button>
    <el-button type="primary" @click="confirmClick">确 定</el-button>
  </div>
</el-dialog>
</template>

<script>
import common from '../plugins/common';

export default {
  name: 'Login',
  props: {
  },
  created() {
    this.$bus.on('needlogin', this.needLoginEV);
    console.log("login created");
  },
  beforeDestroy() {
    this.$bus.off('needlogin', this.needLoginEV);
    console.log("login will destroy.");
  },
  methods:{
    handleClose:function(done){
      console.log("login close.");
      done();
    },
    confirmClick:function(){
      let out_this = this;
      common.post('/login', {
        vcode: out_this.form.name
      },function (response) {
        console.log(response);
        if(response.data.err){
          out_this.$message({
            message: '登录失败:'+response.data.err,
            type: 'error'
          });
        }else{
          out_this.$message({
            message: '登录成功!',
            type: 'success'
          });
          common.save("user",response.data);
        }
        
      },function (error) {
        console.log("error=====",error);
        out_this.$message({
          message: '登录失败'+error,
          type: 'error'
        });
      },function () {
        console.log("finally");
        out_this.dialogFormVisible = false;
      });
    },
    cancelClick:function(event){
      console.log(event);
      this.dialogFormVisible = false;
    },
    needLoginEV:function(done){
      console.log("needLoginEV call...",done)
      this.callback = done;
      this.dialogFormVisible = true;
    },
  },
  data: function(){
    return {
      dialogFormVisible: false,
      form:{
        name:"",
      }
    };
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
