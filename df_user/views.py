# coding:utf-8
from django.shortcuts import render, redirect
from models import *
from hashlib import sha1
from django.http import JsonResponse, HttpResponseRedirect
import user_decorator
from df_goods.models import *
from df_order.models import *
from django.core.paginator import Paginator


def register(request):
    return render(request, 'df_user/register.html', context={'title': '-注册'})


def register_handle(request):
    # 接收用户输入
    post = request.POST
    name = post.get('user_name')
    pwd = post.get('pwd')
    cpwd = post.get('cpwd')
    email = post.get('email')
    # 判断两次密码是否相同
    if cpwd != pwd:
        return redirect('/user/register/')
    # 对密码进行sha1加密
    m = sha1()
    m.update(pwd)
    pwdsha1 = m.hexdigest()
    # 保存用户信息
    user = UserInfo()
    user.uname = name
    user.upwd = pwdsha1
    user.uemail = email
    user.save()

    return redirect('/user/login/')


# 查询用户名是否存在
def register_exist(request):
    uname = request.GET.get('uname')
    count = UserInfo.objects.filter(uname=uname).count()
    return JsonResponse({'count': count})


def login(request):
    # 如果用户名cookie存在则获取，否则设置默认值为空
    uname = request.COOKIES.get('uname', '')
    # 为错误提示标志设置默认值，防止js判断找不到出错
    context = {'title': '用户登录', 'error_name': 0, 'error_pwd':0, 'uname': uname}
    return render(request, 'df_user/login.html', context=context)


def login_handle(request):
    # 接收请求信息
    post = request.POST
    name = post.get('username')
    pwd = post.get('pwd')
    remember = post.get('remember')
    # 根据用户名查询对象
    users = UserInfo.objects.filter(uname=name)  # []
    # 长度为一，表示查到用户
    if len(users) == 1:
        m = sha1()
        m.update(pwd)
        # 密码相等表示输入正确，此时转到用户中心页面
        if m.hexdigest() == users[0].upwd:
            # 首先从cookies获取用户请求过来的路径， 如果没有，默认为'/'
            url = request.COOKIES.get('url', '/')
            # 回到请求过来的页面，手动构造一个重定向对象，为记住用户名设置cookie
            red = HttpResponseRedirect(url)
            # 如果勾选记住用户名，remember值为1，此时设置cookie值为用户名，
            if remember != 0:
                red.set_cookie('uname', name)
            # 否则修改cookie值为'',立即失效
            else:
                red.set_cookie('uname', '', max_age=-1)
            # 设置session会话，当其他的页面跳转到此页面时用来判断是否登录，提高查询效率
            request.session['user_id'] = users[0].id
            request.session['user_name'] = name
            return red
        # 否则提示密码输入错误信息,重新登录
        else:
            context = {'title': '用户登录', 'error_name': 0, 'error_pwd':1, 'uname': name, 'upwd': pwd}
            return render(request, 'df_user/login.html', context=context)
    # 否则提示用户名输入错误信息,重新登录
    else:
        context = {'title': '用户登录', 'error_name': 1, 'error_pwd':0, 'uname': name, 'upwd': pwd}
        return render(request, 'df_user/login.html', context=context)


# 清除session转向首页
def logout(request):
    request.session.flush()
    return redirect('/')


@user_decorator.login
def user_center_info(request):
    user_email = UserInfo.objects.get(id=request.session['user_id']).uemail
    user_name = request.session['user_name']
    user_address = UserInfo.objects.get(id=request.session['user_id']).uaddress

    # 获取最近浏览的商品cookies，如果没有则设为空字符串
    goods_ids = request.COOKIES.get('goods_ids', '')
    goods_list = []
    if goods_ids == '':
        goods_list = GoodsInfo.objects.order_by('-id')[0:5]
    else:
        # 切分为列表[id1,id2...]
        goods_idsl = goods_ids.split(',')
        # 如果换成GoodsInfo.objects.filter(id__in=goods_idsl)，查询结果不是用户浏览的顺序
        for goods_id in goods_idsl:
            goods_list.append(GoodsInfo.objects.get(id=int(goods_id)))

    context = {
        'title': '个人信息',
        'user_email': user_email,
        'user_name': user_name,
        'page_name': 1,
        'goods_list': goods_list,
        'user_address': user_address,
    }
    return render(request, 'df_user/user_center_info.html', context=context)


@user_decorator.login
def user_center_order(request, pindex):
    uid = request.session['user_id']
    orders = OrderInfo.objects.filter(ouser_id=uid)
    # for test
    # for order in orders:
    #     for detail in order.orderdetailinfo_set.all():
    #         print(detail.goods.gtitle)

    paginator = Paginator(orders, 2)
    page = paginator.page(int(pindex))
    plist = paginator.page_range

    context = {
        'title': '全部订单', 'page_name': 1, 'page': page, 'plist': plist,
    }
    return render(request, 'df_user/user_center_order.html', context=context)


@user_decorator.login
def user_center_site(request):
    user = UserInfo.objects.get(id=request.session['user_id'])
    if request.method == 'POST':
        post = request.POST
        user.ushou = post.get('shou')
        user.uaddress = post.get('address')
        user.uemail = post.get('email')
        user.uphone = post.get('phone')
        user.save()
    context = {'title': '收货地址', 'user': user, 'page_name': 1}
    return render(request, 'df_user/user_center_site.html', context=context)
















