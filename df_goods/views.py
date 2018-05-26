# coding:utf-8
from django.shortcuts import render
from models import *
from django.core.paginator import Paginator
from df_cart.models import CartInfo
from haystack.views import SearchView


def get_cart_count(request):
    # 如果用户登录读取购物车数量
    if request.session.has_key('user_id'):
        return CartInfo.objects.filter(user_id=request.session['user_id']).count()
    else:
        return 0


def index(request):
    # 查询各分类最新（最后添加的）4条，最热（点击量最大）4条
    typelist = TypeInfo.objects.all()
    type0 = typelist[0].goodsinfo_set.order_by('-id')[0:4]
    type01 = typelist[0].goodsinfo_set.order_by('-gclick')[0:4]
    type1 = typelist[1].goodsinfo_set.order_by('-id')[0:4]
    type11 = typelist[1].goodsinfo_set.order_by('-gclick')[0:4]
    type2 = typelist[2].goodsinfo_set.order_by('-id')[0:4]
    type21 = typelist[2].goodsinfo_set.order_by('-gclick')[0:4]
    type3 = typelist[3].goodsinfo_set.order_by('-id')[0:4]
    type31 = typelist[3].goodsinfo_set.order_by('-gclick')[0:4]
    type4 = typelist[3].goodsinfo_set.order_by('-id')[0:4]
    type41 = typelist[4].goodsinfo_set.order_by('-gclick')[0:4]
    type5 = typelist[5].goodsinfo_set.order_by('-id')[0:4]
    type51 = typelist[5].goodsinfo_set.order_by('-gclick')[0:4]

    cart_count = get_cart_count(request)
    context = {
        'title': '首页', 'guest_cart': 1,
        'type0': type0, 'type01': type01,
        'type1': type1, 'type11': type11,
        'type2': type2, 'type21': type21,
        'type3': type3, 'type31': type31,
        'type4': type4, 'type41': type41,
        'type5': type5, 'type51': type51,
        'cart_count': cart_count,
    }
    return render(request, 'df_goods/index.html', context)


def list(request, tid, pindex, sort):
    typeinfo = TypeInfo.objects.get(pk=int(tid))
    news = typeinfo.goodsinfo_set.order_by('-id')[0:2]
    # 默认最新
    if sort == '1':
        goods_list = GoodsInfo.objects.filter(gtype_id=int(tid)).order_by('-id')
    # 价格
    elif sort == '2':
        goods_list = GoodsInfo.objects.filter(gtype_id=int(tid)).order_by('-gprice')
    # 人气
    else:
        goods_list = GoodsInfo.objects.filter(gtype_id=int(tid)).order_by('-gclick')

    paginator = Paginator(goods_list, 15)
    page = paginator.page(int(pindex))
    plist = paginator.page_range

    cart_count = get_cart_count(request)
    context = {
        'title': typeinfo.ttitle, 'guest_cart': 1,
        'page': page, 'paginator': paginator,
        'typeinfo': typeinfo, 'sort': sort,
        'news': news, 'plist': plist,
        'cart_count': cart_count,
    }
    return render(request, 'df_goods/list.html', context)


def detail(request, id):
    goods = GoodsInfo.objects.get(pk=int(id))
    goods.gclick += 1
    goods.save()
    news = goods.gtype.goodsinfo_set.order_by('-id')[0:2]

    cart_count = get_cart_count(request)
    context = {
        'title': goods.gtype.ttitle, 'guest_cart': 1,
        'goods': goods, 'news': news, 'id': id,
        'cart_count': cart_count,
    }
    response = render(request, 'df_goods/detail.html', context)

    # 记录最近浏览的商品，在用户中心使用
    # 获取最近浏览的商品cookies，如果没有设为空字符串
    goods_ids = request.COOKIES.get('goods_ids', '')
    # 将int类型的id转为字符串类型
    goods_id = '%d' % goods.id
    # 如果有浏览记录，
    if goods_ids != '':
        # 把字符串goods_ids拆分为[id1,id2...]列表
        goods_idsl = goods_ids.split(',')
        # 如果商品已经被记录，就删除该商品，重新添加
        if goods_idsl.count(goods_id) >= 1:
            goods_idsl.remove(goods_id)
        # 添加到第一个位置
        goods_idsl.insert(0, goods_id)
        # 只维护五个商品，如果超出就删除最后一个
        if len(goods_idsl) >= 6:
            del goods_idsl[5]
        # 最后拼接为字符串存储
        goods_ids = ','.join(goods_idsl)
    else:
        # 如果没有浏览记录则直接添加
        goods_ids = goods_id

    # 写入cookies
    response.set_cookie('goods_ids', goods_ids)
    return response


class MySearchView(SearchView):
    def extra_context(self):
        context = super(MySearchView, self).extra_context()
        context['title'] = '搜索'
        context['guest_cart'] = 1
        context['cart_count'] = get_cart_count(self.request)
        return context





