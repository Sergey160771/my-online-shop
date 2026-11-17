from django.shortcuts import render, get_object_or_404
from .models import Category, Product
import json
from django.http import HttpResponse


def product_list(request):
    """
    Главная страница: вывод всех доступных товаров.
    """
    # Получаем все товары, которые есть в наличии, отсортированные по дате создания
    products = Product.objects.filter(available=True).order_by('-created_at')
    context = {
        'products': products,
        'page_title': 'Главная'
    }
    return render(request, 'shop/product/list.html', context)


def product_detail(request, slug):
    """
    Страница конкретного товара.
    """
    # get_object_or_404 — если товара с таким адресом нет, сервер выдаст красивую страницу 404
    product = get_object_or_404(Product, slug=slug)
    context = {
        'product': product,
        'page_title': product.name
    }
    return render(request, 'shop/product/detail.html', context)


def category_list(request):
    """
    Страница со списком всех категорий (карта сайта).
    """
    categories = Category.objects.all()
    context = {
        'categories': categories,
        'page_title': 'Категории'
    }
    return render(request, 'shop/category/list.html', context)


def category_detail(request, slug):
    """
    Страница конкретной категории со списком её товаров.
    """
    category = get_object_or_404(Category, slug=slug)
    # Достаем товары именно этой категории через связь related_name
    products = category.products.filter(available=True).order_by('-created')
    context = {
        'category': category,
        'products': products,
        'page_title': category.name
    }
    return render(request, 'shop/category/detail.html', context)


def add_to_cart(request):
    """Добавляет товар в сессию через HTMX."""
    if request.method == "POST":
        data = json.loads(request.body.decode("utf-8"))
        product_id = int(data.get('product_id'))

        cart = request.session.get('cart', {})

        try:
            product = Product.objects.get(id=product_id)

            item_data = {
                "id": product.id,
                "name": product.name,
                "price": float(product.price),
                "quantity": 1
            }

            cart[str(product_id)] = item_data
            request.session['cart'] = cart

            count = len(cart.keys())
            html_response = f"<span class='text-blue-700 font-bold'>{count}</span>"
            return HttpResponse(html_response)  # Возвращает HTML-фрагмент для обновления UI

        except Product.DoesNotExist:
            pass  # Игнорируем несуществующие товары

    return HttpResponse(status=400)
