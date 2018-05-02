#!/usr/bin/ python
#vim: set fileencoding:utf-8

from flask import Flask, redirect
from com.free.ssr.action.ssr_login import sl
from com.free.ssr.action.order_action import sa
from com.free.ssr.action.job_timer import Job
import com.free.ssr.action.auth_filter as auth
# template_folder 指定存入模板的文件夹
app = Flask(__name__)

# 注册登录蓝图
app.register_blueprint(sl)
# 注册ssr操作蓝图
app.register_blueprint(sa)
# 注册在请求之前的处理方法
app.before_request(auth.auth_filter)


# 跳转到404页面
@sl.errorhandler(404)
def err(error):
    print(error)
    return redirect("static/pages/404.html")


# 跳转到错误页面
@sl.errorhandler(Exception)
def sys_err(error):
    print(error)
    return redirect("static/pages/error.html")

if __name__ == '__main__':
    # 启动定时任务
    Job.start()
    # debug模式
    # app.debug=True 或者app.run(debug=True)
    # port参数指定启动端口(可改为任意商品),host参数指主机ip
    app.run(host='localhost', port=80)
    # 导入webbrowser用于调用系统默认浏览器访问指定url
    # import webbrowser
    # webbrowser.open("http://localhost/index")
    