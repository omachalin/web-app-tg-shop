# views.py
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from django.http import JsonResponse
from .models import Product, Category, Tag
import telebot
from django.views.decorators.csrf import csrf_exempt
from .bot_handlers import bot


def product_list(request):
    categories = Category.objects.filter(product__isnull=False).distinct().order_by('name')

    products = Product.objects.all() \
        .select_related('preview_fk', 'sticker_type_fk') \
        .prefetch_related(
            'tags',
            'categories',
            'attachments__attachment',
        )

    category_id_filter = request.GET.get('category_id')
    product_name_filter = request.GET.get('product_name')
    tag_id_filter = request.GET.get('tag_id')

    if category_id_filter:
        products = products.filter(categories__id=category_id_filter).distinct()
    if product_name_filter:
        products = products.filter(name__icontains=product_name_filter)
    if tag_id_filter:
        products = products.filter(tags__id=tag_id_filter)

    try:
        offset = int(request.GET.get('offset', 0))
    except ValueError:
        offset = 0
    try:
        limit = int(request.GET.get('limit', 20))
    except ValueError:
        limit = 20

    products = products.order_by('order')
    products = products[offset:offset + limit]

    return render(request, 'main/catalog_list.html', {
        'products': products,
        'categories': categories,
    })


def search_product_list(request):
    category_ids_filter = request.GET.get('category_ids')
    product_name_filter = request.GET.get('product_name')
    order_by = request.GET.get('order_by', 'name')

    if order_by not in ['name', '-name']:
        order_by = 'name'

    products = Product.objects.all() \
        .select_related('preview_fk', 'sticker_type_fk') \
        .prefetch_related(
            'tags',
            'categories',
            'attachments__attachment',
        )

    if category_ids_filter:
        category_ids = [tid for tid in category_ids_filter.split(',') if tid]
        if category_ids:
            products = products.filter(categories__id__in=category_ids).distinct()
    if product_name_filter:
        products = products.filter(name__icontains=product_name_filter)

    products = products.order_by(order_by)

    html = render_to_string('main/product_list.html', {'products': products}, request=request)
    return JsonResponse({'html': html})


def product_detail(request, pk):
    product = get_object_or_404(
        Product.objects.select_related('preview_fk', 'sticker_type_fk').prefetch_related(
            'categories',
            'attachments__attachment',
            'tags'
        ),
        pk=pk
    )

    tags = product.get_tags()

    return render(
        request,
        'main/product_detail.html',
        {'product': product, 'tags': tags}
    )


@csrf_exempt
def telegram_webhook(request):
    if request.method == 'POST':
        json_str = request.body.decode('utf-8')
        update = telebot.types.Update.de_json(json_str)
        bot.process_new_updates([update])
    return JsonResponse({'status': 'ok'})
