from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils import timezone


class Category(models.Model):
    """Категория товаров. Иерархическая структура."""
    name = models.CharField(
        'Название', max_length=150,
        help_text='Уникальное имя категории'
    )
    # Уникальный URL для SEO
    slug = models.SlugField('URL-адрес', max_length=160, unique=True)
    # Родительская категория для дерева. Может быть пустой для корня.
    parent = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='children',
        verbose_name='Родительская категория'
    )


    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """
        Автоматическое создание Slug перед сохранением.
        Если пользователь не указал slug вручную, он будет создан из имени.
        """
        if not self.slug or len(self.slug.strip()) == 0:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('category_detail', kwargs={'slug': self.slug})


class Product(models.Model):
    """Товар в каталоге."""
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    name = models.CharField('Название', max_length=255)
    slug = models.SlugField('URL-адрес', max_length=260, unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField('Цена', max_digits=10, decimal_places=2)
    available = models.BooleanField('В наличии', default=True)
    created_at = models.DateTimeField(default=timezone.now)  # Вместо auto_now_add
    updated_at = models.DateTimeField(null=True, blank=True)  # Обновляется вручную в методах save()

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

    def __str__(self):
        return f"{self.name} ({self.category})"

    def save(self, *args, **kwargs):
        """
        Аналогично Category: если slug не задан, создаем его из названия.
        """
        if not self.slug or len(self.slug.strip()) == 0:
            self.slug = slugify(self.name[:49]) + '-' + str(self.id)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'slug': self.slug})


class Order(models.Model):
    """Заказ покупателя."""
    STATUS_CHOICES = [
        ('NEW', 'Новый'),
        ('PAID', 'Оплачен'),
        ('SHIPPED', 'Отправлен'),
        ('COMPLETED', 'Завершен'),
    ]
    status = models.CharField(choices=STATUS_CHOICES, default='NEW', max_length=10)
    first_name = models.CharField('Имя', max_length=100)
    last_name = models.CharField('Фамилия', max_length=100)
    email = models.EmailField()
    address = models.TextField('Адрес доставки')
    total_price = models.DecimalField('Итоговая сумма', max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return f"Заказ №{self.pk}: {self.first_name} {self.last_name}"


class OrderItem(models.Model):
    """Позиция в заказе."""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def cost(self):
        """Рассчитывает общую стоимость позиции."""
        return self.price * self.quantity

    def __str__(self):
        return f'{self.product.name} x {self.quantity}'
