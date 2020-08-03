import axios from 'axios';
import Vue from 'vue';

function LoginProcess(done){
    Vue.bus.emit('needlogin',done);
}

var common = {};
common.post = function(url,para,suc,err,final){
    axios.post(url,para).then(function(res){
        console.log(res)
        if(res.data.err===2){
            LoginProcess(function(){
                console.log("login ok.")
            });
            err(res.data);
        }else{
            suc(res);
        }
    }).catch(err).finally(final);
}

common.get = function(url,para,suc,err,final){
    axios.get(url,{params:para}).then(function(res){
        console.log(res)
        if(res.data.err===2){
            LoginProcess(function(){
                console.log("login ok.")
            });
            err(res.data);
        }else{
            suc(res);
        }
    }).catch(err).finally(final);
}

common.save = function(key,obj){
    if(typeof(obj)==="number"||typeof(obj)==="string"||typeof(obj)==="boolean"){
        localStorage.setItem(key,obj);
    }else{
        const parsed = JSON.stringify(obj);
        localStorage.setItem(key+"@json", parsed);
    }
};
common.load = function(key){
    let it = localStorage.getItem(key+"@json");
    if(it){
        try {
            return JSON.parse(it);
        } catch(e) {
            return null;
        }
    }else{
        return localStorage.getItem(key);
    }
};

// common.get('/adduser', {
//   name: 'test'
// },function (response) {
//   console.log(response);
// },function (error) {
//   console.log("error=====",error);
// },function () {
//   console.log("finally");
// });

// common.post('/adduser', {
//   name: 'test'
// },function (response) {
//   console.log(response);
// },function (error) {
//   console.log("error=====",error);
// },function () {
//   console.log("finally");
// });

export default common;