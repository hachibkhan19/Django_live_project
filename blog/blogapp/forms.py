from django import forms
from . models import Article, Author, Comment, Category


class CreateNewArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = [
            'title',
            'text',
            'category',
            'image'
        ]


class AuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = [
            'details',
            'image'
        ]


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = [
            'text',
            'name',
            'email'
        ]


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = [
            'name'
        ]
