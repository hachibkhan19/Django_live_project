from django.db import models
from django.urls import reverse
from ckeditor_uploader.fields import RichTextUploadingField
from django.contrib.auth.models import User


# Create your models here.
class Author(models.Model):
    name = models.ForeignKey(User, on_delete=models.CASCADE)
    details = models.TextField()
    image = models.FileField()

    def __str__(self):
        return self.name.username


class Category(models.Model):
    name = models.CharField(max_length=300)

    def __str__(self):
        return self.name


class Article(models.Model):
    article_author = models.ForeignKey(Author, on_delete=models.CASCADE)
    title = models.CharField(max_length=400)
    text = RichTextUploadingField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    image = models.FileField()
    posted_on = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True, auto_now_add=False)

    def __str__(self):
        return self.title

    def single_page_url(self):
        return reverse('blog:single_page', kwargs={'id': self.id})

    def article_author_url(self):
        return reverse('blog:article_author', kwargs={'name': self.article_author.name})

    def category_page_url(self):
        return reverse('blog:category', kwargs={'name': self.category.name})


class Comment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    text = models.TextField()
    name = models.CharField(max_length=200)
    email = models.EmailField(max_length=200)

    def __str__(self):
        return self.article.title
