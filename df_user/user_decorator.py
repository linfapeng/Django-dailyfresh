# coding:utf-8
"""
此函数为装饰器，用来验证用户是否登录，并返回到对应的请求页面
当请求 http://127.0.0.1:8000/200/?type=10
request.path:表示当前路径，/200/
request.get_full_path(),:表示完整路径，/200/?type=10
"""
from django.http import HttpResponseRedirect


def login(func):
    def login_fun(request, *args, **kwargs):
        if request.session.has_key('user_id'):
            return func(request, *args, **kwargs)
        else:
            red = HttpResponseRedirect('/user/login/')
            red.set_cookie('url', request.get_full_path())
            return red
    return login_fun
