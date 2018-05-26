# coding:utf-8
from django.shortcuts import render, redirect
from df_user import user_decorator
from df_user.models import *
from df_cart.models import *
from django.db import transaction
from .models import *
from datetime import datetime
from decimal import Decimal
from django.http import JsonResponse


@user_decorator.login
def order(request):
    # 查询用户对象
    user = UserInfo.objects.get(id=request.session['user_id'])
    # 根据提交查询购物车信息
    get = request.GET
    # 获取传入的商品id号，并且以列表形式返回
    cart_ids = get.getlist('cart_id')
    # 将元素转换成int类型
    cart_id_list = [int(item) for item in cart_ids]
    # 获取购物车对象，构成列表，作文上下文传入页面
    carts = CartInfo.objects.filter(id__in=cart_id_list)
    # 判断用户手机号是否为空，分别做展示
    if user.uphone != '':
        user.uphone = user.uphone[0:4] + \
            '****' + user.uphone[-4:]
    context = {
        'title': '提交订单',
        'page_name': 1,
        'carts': carts,
        'user': user,
        'cart_ids': ','.join(cart_ids),
    }
    return render(request, 'df_order/place_order.html', context=context)


@transaction.atomic()
@user_decorator.login
def order_handle(request):
    tran_id = transaction.savepoint()
    try:
        post = request.POST
        total = post.get('total')
        address = post.get('address')
        # 接收购物车id列表
        cart_ids = post.get('cart_ids')
        # 把u'1,3,5'先转成'utf-8'格式的字符串然后切分成[1,3,5]列表
        cart_ids = cart_ids.encode('utf-8').split(',')
        # print('cart_ids:', cart_ids)

        # 创建订单对象
        order = OrderInfo()
        now = datetime.now()
        uid = request.session['user_id']
        order.oid = '%s%d' % (now.strftime('%Y%m%d%H%M%S'), uid)
        order.ouser_id = uid
        order.odate = now.strftime('%Y %m %d %H:%M:%S')
        order.ototal = Decimal(total)
        order.oaddress = address
        order.save()

        # 遍历购物车中提交信息，创建订单详情表
        for cart_id in cart_ids:
            # 得到购物车对象
            cart = CartInfo.objects.get(id=int(cart_id))
            # 得到商品对象
            goods = cart.goods
            # 库存大于购买数量
            if goods.gstock >= cart.count:
                # 减少商品库存
                goods.gstock -= cart.count
                goods.save()
                # 创建订单详情对象
                detail = OrderDetailInfo()
                detail.order_id = order.oid
                detail.goods_id = goods.id
                detail.price = goods.gprice
                detail.count = cart.count
                detail.save()
                # 提交订单后应该删除该购物车对象
                cart.delete()
            else:
                # 如果库存不够，触发事务回滚，撤销操作
                transaction.savepoint_rollback(tran_id)
                # 返回json给前台提示失败
                return JsonResponse({'status': 0})
        transaction.savepoint_commit(tran_id)
        # 返回json给前台提示成功
        return JsonResponse({'status': 1})
    except Exception as e:
        print('-'*20+('%s' % e))
        transaction.savepoint_rollback(tran_id)
        # # 返回json给前台提示成功
        return JsonResponse({'status': 2})


@transaction.atomic()
@user_decorator.login
def pay(request, id):
    tran_id = transaction.savepoint()
    try:
        order = OrderInfo.objects.get(oid=id)
        order.oIspay = 1
        order.save()
        transaction.savepoint_commit(tran_id)
        return JsonResponse({'status': 1})
    except Exception as e:
        print('-'*20+('%s' % e))
        transaction.savepoint_rollback(tran_id)
        return JsonResponse({'status': 0})


@user_decorator.login
def viewlog(request, id):
    return render(request, 'df_order/viewlog.html', context={'oid': int(id)})




