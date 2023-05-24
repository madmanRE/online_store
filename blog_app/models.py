from django.db import models
from django.db.models import Count
from my_store_app.models import Profile
from transliterate import slugify as make_slug


def create_image_path_for_article(instance, filename):
    return "upload/articles/article_{pk}/{filename}".format(
        pk=instance.pk, filename=filename
    )


class Theme(models.Model):
    title = models.CharField(max_length=30)
    slug = models.SlugField(max_length=90, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = make_slug(self.title)
        super().save(*args, **kwargs)

    def count_articles(self):
        return self.articles.count()

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Тема"
        verbose_name_plural = "Темы"



class Article(models.Model):
    title = models.CharField(max_length=50)
    text = models.TextField(max_length=50000)
    author = models.ForeignKey(Profile, on_delete=models.CASCADE, blank=True)
    date = models.DateField(auto_now_add=True)
    theme = models.ForeignKey(Theme, on_delete=models.CASCADE, related_name='articles')
    slug = models.SlugField(max_length=90, unique=True, blank=True)
    image = models.ImageField(upload_to=create_image_path_for_article, null=True, default=None, blank=True)
    rating = models.PositiveIntegerField(null=True, blank=True, default=0)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = make_slug(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "статья"
        verbose_name_plural = "статьи"

    def count_rating(self):
        self.rating += 1
