from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from rest_framework.exceptions import ValidationError
from django.utils.text import slugify
import uuid
from django.utils import timezone


def create_image_path_for_product(instance, filename):
    return "upload/products/product_{pk}/{filename}".format(
        pk=instance.pk, filename=filename
    )


def create_image_path_for_product_gallery(instance, filename):
    return "upload/products/gallery/{filename}".format(filename=filename)


def create_image_path_for_category(instance, filename):
    if instance.pk:
        return f"upload/categories/categoryproduct_{instance.pk}/{filename}"
    else:
        uuid_str = uuid.uuid4().hex
        return f"upload/categories/categoryproduct_{str(uuid.uuid4())}/{filename}"


def create_image_path_for_profile(instance, filename):
    return "upload/profiles/profile_{pk}/{filename}".format(
        pk=instance.pk, filename=filename
    )


class Profile(models.Model):
    def validate_image(fieldfile_obj):
        file_size = fieldfile_obj.file.size
        megabyte_limit = 150.0
        if file_size > megabyte_limit * 1024 * 1024:
            raise ValidationError(
                "Максимальный размер файла {}MB".format(str(megabyte_limit))
            )

    user = models.OneToOneField(
        User, unique=True, on_delete=models.CASCADE, related_name="profile"
    )
    username = models.CharField(
        default="-------",
        max_length=50,
        verbose_name="username",
        blank=True,
        null=True,
        unique=False,
    )
    full_name = models.CharField(
        default="не указано", max_length=50, verbose_name="ФИО пользователя", blank=True
    )
    phone = models.CharField(
        default="Не указано",
        max_length=30,
        verbose_name="номер телефона",
        blank=True,
        null=True,
    )
    email = models.EmailField(verbose_name="email пользователя", blank=True)
    avatar = models.ImageField(
        upload_to="catalog/files/",
        null=True,
        validators=[validate_image],
        default="catalog/files/ava-default.png",
    )

    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    basket = models.ForeignKey(
        "Basket",
        on_delete=models.CASCADE,
        related_name="profile",
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Профиль"
        verbose_name_plural = "Профили пользователей"

    def __str__(self):
        return self.username


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created and instance.is_superuser:
        Profile.objects.create(user=instance)


class Sales(models.Model):
    product = models.ForeignKey(
        "Product", on_delete=models.CASCADE, verbose_name="товар"
    )
    shop = models.ForeignKey("Shop", on_delete=models.CASCADE, verbose_name="магазин")
    count = models.IntegerField(default=0, verbose_name="количество товара по скидке")
    dateFrom = models.DateField()
    dateTo = models.DateField()

    class Meta:
        verbose_name = "Распродажа"
        verbose_name_plural = "Распродажа"


class CategoryProduct(models.Model):  # категория товаров
    title = models.TextField(max_length=50, verbose_name="название категории")
    image = models.FileField(upload_to=create_image_path_for_category, null=True)
    slug = models.SlugField(blank=True, verbose_name="символьный код")
    tags = models.ManyToManyField(
        "TagsFile", related_name="tags_in_category", blank=True, null=True
    )

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.title


class ProductImage(models.Model):
    product_ref = models.ForeignKey(
        "Product", on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(upload_to=create_image_path_for_product_gallery)

    class Meta:
        verbose_name = "галерея изображений"
        verbose_name_plural = "галереи изображений"

    def save(self, *args, **kwargs):
        if not self.pk:
            self.image.open()
            self.image.seek(0)
            self.image.name = create_image_path_for_product_gallery(
                self, self.image.name
            )
        super().save(*args, **kwargs)


class Product(models.Model):  # товар
    category = models.ForeignKey(
        "CategoryProduct", on_delete=models.CASCADE, verbose_name="категория товара"
    )
    shop = models.ForeignKey(
        "Shop", on_delete=models.CASCADE, verbose_name="магазин товара"
    )
    specifications = models.ForeignKey(
        "Specifications", on_delete=models.CASCADE, verbose_name="спецификация товара"
    )
    price = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="цена товара"
    )
    count = models.IntegerField(default=0, verbose_name="количество ")
    date = models.DateField(auto_now_add=True)
    title = models.TextField(max_length=50, verbose_name="название товара")
    description = models.TextField(max_length=100, verbose_name="описание товара")
    big_text = models.TextField(
        verbose_name="большой текст для карточки товара", blank=True, null=True
    )
    free_delivery = models.BooleanField(default=True)
    product_picture = models.ImageField(
        upload_to=create_image_path_for_product, null=True, blank=True
    )
    rating = models.IntegerField(
        default=0, verbose_name="счетчик покупок данного товара"
    )
    reviews = models.IntegerField(
        default=0, verbose_name="счетчик просмотров данного товара"
    )
    tags = models.ManyToManyField("TagsFile", related_name="tags")
    slug = models.SlugField(unique=True, max_length=255, blank=True)
    limited_edition = models.BooleanField(
        default=False, verbose_name="ограниченный тираж"
    )
    gallery = models.ManyToManyField(ProductImage, blank=True, related_name="products")

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

    def __str__(self):
        return self.title

    def upper_reviews_product(self):
        self.reviews += 1
        self.save()


@receiver(pre_save, sender=Product)
def pre_save_product(sender, instance, **kwargs):
    if not instance.slug:
        instance.slug = slugify(instance.title)


class LimitedOffer(models.Model):
    """Отдельный класс для уникальных предложений.
    Тип message используется для вывода специального текста
    в слайдер на главной странице!"""

    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="товар")
    new_price = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="новая цена"
    )
    message = models.CharField(
        max_length=500, verbose_name="описание", blank=True, null=True
    )
    duration = models.DurationField(verbose_name="время до конца акции")
    created_at = models.DateTimeField(
        default=timezone.now, verbose_name="Дата создания"
    )

    class Meta:
        verbose_name = "Специальное предложение"
        verbose_name_plural = "Специальные предложения"


class TagsFile(models.Model):
    tags_name = models.TextField(max_length=50, verbose_name="тэг товара")

    class Meta:
        verbose_name = "Тэг"
        verbose_name_plural = "Тэги"

    def __str__(self):
        return self.tags_name


class Shop(models.Model):
    shop_name = models.TextField(max_length=50, verbose_name="название магазина")

    class Meta:
        verbose_name = "магазин"
        verbose_name_plural = "магазины"

    def __str__(self):
        return self.shop_name


class Reviews(models.Model):  # отзыв
    product = models.ForeignKey(
        "Product",
        on_delete=models.CASCADE,
        verbose_name="товар",
        related_name="product_title_product_set",
    )
    author = models.ForeignKey(
        "Profile", on_delete=models.CASCADE, verbose_name="пользователь"
    )
    text = models.CharField(
        default="Не указано", max_length=100, verbose_name="текст отзыва", blank=True
    )
    create_at = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"

    def __str__(self):
        return self.text


class Specifications(models.Model):
    name = models.TextField(max_length=50, verbose_name="название")
    value = models.TextField(max_length=50, verbose_name="значение")

    class Meta:
        verbose_name = "Спецификация"
        verbose_name_plural = "Спецификации"

    def __str__(self):
        return self.name


class OrderHistory(models.Model):
    user_order = models.ForeignKey(
        "Profile", on_delete=models.CASCADE, verbose_name="пользователь", null=True
    )
    product_order = models.ManyToManyField(Product, verbose_name="товары")
    payment_date = models.DateField(auto_now_add=True)
    delivery_type = models.TextField(
        max_length=30, default="не указан", verbose_name="способ доставки"
    )
    payment_type = models.TextField(
        max_length=30, default="не указан", verbose_name="способ оплаты"
    )
    total_cost = models.IntegerField(default=0, verbose_name="общая стоимость заказа")
    status = models.TextField(
        max_length=30, default="не указан", verbose_name="статус оплаты"
    )
    city = models.TextField(
        max_length=30, default="не указан", verbose_name="город доставки"
    )
    address = models.TextField(
        max_length=30, default="не указан", verbose_name="адрес доставки"
    )
    order = models.ManyToManyField("Order", verbose_name="заказы")
    products = models.ManyToManyField(
        Product,
        through="OrderedProduct",
        verbose_name="товары",
        related_name="products_with_quantity",
    )
    confirmed = models.BooleanField(default=False, verbose_name="Подтвержден")

    class Meta:
        verbose_name = "История покупок"
        verbose_name_plural = "Истории покупок"

    def __str__(self):
        return self.user_order.username


class OrderedProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order = models.ForeignKey(OrderHistory, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)

    class Meta:
        verbose_name = "Заказанный товар"
        verbose_name_plural = "Заказанные товары"

    def cost_price(self):
        return self.product.price * self.quantity


class Order(models.Model):  # покупка товаров из корзины
    current_basket = models.ForeignKey(
        "Basket", on_delete=models.CASCADE, verbose_name="товары в корзине", null=False
    )
    date = models.DateField(auto_now_add=True)
    free_delivery = models.BooleanField(
        default=False, verbose_name="наличие бесплатной доставки"
    )

    class Meta:
        verbose_name = "Покупка"
        verbose_name_plural = "Покупки"

    def __str__(self):
        return f"Order {self.pk}"

    def create_order(self):
        order = Order.objects.create(
            current_basket=self.current_basket, free_delivery=self.free_delivery
        )
        basket_items = self.current_basket.items.all()
        for basket_item in basket_items:
            product = basket_item.product
            quantity = basket_item.product_quantity
            OrderItem.objects.create(order=order, product=product, quantity=quantity)
        self.current_basket.items.clear()


class Basket(models.Model):  # корзина пользователя
    username = models.OneToOneField(
        "Profile", unique=True, on_delete=models.CASCADE, related_name="profile"
    )
    create_at = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"

    def __str__(self):
        return f"Корзина: {self.username}"

    def count_products(self):
        return sum(item.product_quantity for item in self.items.all())

    def total_cost(self):
        return sum(
            item.product.price * item.product_quantity for item in self.items.all()
        )


class BasketItem(models.Model):
    """Связанная таблица, которая позволяет хранить товар, кол-во товара и саму корзину"""

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="basket_items"
    )
    product_quantity = models.PositiveIntegerField(default=0)
    basket = models.ForeignKey(Basket, on_delete=models.CASCADE, related_name="items")


class Payment(models.Model):
    number = models.IntegerField(default=0, verbose_name="номер счета")
    name = models.TextField(max_length=30, default="не указан")
    month = models.DateField(auto_now_add=True)
    year = models.DateField(auto_now_add=True)
    code = models.IntegerField(default=0, verbose_name="код оплаты")

    class Meta:
        verbose_name = "Оплата"
        verbose_name_plural = "Оплата"

    def __str__(self):
        return self.name
