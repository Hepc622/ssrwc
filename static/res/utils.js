/**
 * Created by Administrator on 2018/4/21.
 */
var utl = {
    //获取localStorage条目
    getItem:function(key){
        return JSON.parse(window.localStorage.getItem(key));
    },
    //设置localStorage条目
    setItem:function(key,value){
        window.localStorage.setItem(key,value);
    },
    //加载form表单
    formLoad:function(dom,data){
        for (var key in data){
            dom.find("input[name="+key+"]").val(data[key]);
            dom.find("select[name="+key+"]").val(data[key]);
            if(key.indexOf("Tm")!=-1){
                dom.find("input[name="+key+"]").val(utl.formatDate(data[key]));
            }
        }
    },
    //清楚表单数据
    formClear:function(dom){
        dom.find("input[type='text']").val("");
        dom.find("input[type='radio']").val("");
        dom.find("input[type='checkbox']").val("");
        dom.find("select").val("");
    },
    //没有权限重定向到登录
    auth:function(code){
        if(code==3){
            parent.window.location.href='/static/pages/login.html'
        }
    },
    formatDate:function(date,type){
        if(date){
            var fDate = new Date(date);
            var year = fDate.getFullYear();
            var month = fDate.getMonth()+1;
            var day = fDate.getDate();
            var hours = fDate.getHours();
            var minute = fDate.getMinutes();
            var millisecond = fDate.getMilliseconds();
            if(type=="yyyy-mm-dd"){
                return year+"-"+month+"-"+day;
            }else if(type=="yyyy-mm-dd hh:mm:ss"){
                return year+"-"+month+"-"+day+" "+hours+":"+minute+":"+millisecond;
            }else{
                return year+"-"+month+"-"+day;
            }
        }else{
            return "";
        }

    },
    formatMark:function(val){
        if(val == '1'){
            return '否'
        }else if(val == '0'){
            return '是'
        }else{
            return '否'
        }
    }
}