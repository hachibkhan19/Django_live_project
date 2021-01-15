from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Q
from django.views import View
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.models import User
from . forms import CreateNewArticleForm, AuthorForm, CommentForm, CategoryForm
from django.http import HttpResponse
from . models import Article, Author, Category, Comment
from django.template.loader import get_template
from xhtml2pdf import pisa


def index(request):
    article = Article.objects.all()
    search = request.GET.get('q')
    if search:
        article = Article.objects.filter(
            Q(title__icontains=search) |
            Q(text__icontains=search)
        )
    paginator = Paginator(article, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        "articles": page_obj
    }
    return render(request, 'index.html', context)


class SinglePageView(View):
    template_name = 'single.html'

    def get(self, request, id):
        article = get_object_or_404(Article, id=id)
        comment = Comment.objects.filter(article=id)
        first = Article.objects.first()
        last = Article.objects.last()
        related_articles = Article.objects.filter(category=article.category).exclude(id=id)[:8]
        form = CommentForm()
        context = {
            "article": article,
            "first": first,
            "last": last,
            "related_articles": related_articles,
            "form": form,
            "comments": comment
        }
        return render(request, self.template_name, context)

    def post(self, request, id):
        article = get_object_or_404(Article, id=id)
        form = CommentForm(request.POST or None)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.article = article
            instance.save()
            return redirect('blog:single_page', id=id)


class AuthorView(View):
    template_name = 'author.html'

    def get(self, request, name):
        article_auth = get_object_or_404(User, username=name)
        auth = get_object_or_404(Author, name=article_auth.id)
        article = Article.objects.filter(article_author=auth.id)
        paginator = Paginator(article, 16)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context = {
            "auth": auth,
            "articles": page_obj
        }
        return render(request, self.template_name, context)


class CategoryView(View):
    template_name = 'category.html'

    def get(self, request, name):
        cat = get_object_or_404(Category, name=name)
        article = Article.objects.filter(category=cat.id)
        search = request.GET.get('q')
        if search:
            article = Article.objects.filter(
                Q(title__icontains=search) |
                Q(text__icontains=search)
            )
        paginator = Paginator(article, 12)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context = {
            "articles": page_obj,
            "cat": cat
        }
        return render(request, self.template_name, context)


class CategoryListView(View):
    template_name = 'category_list.html'

    def get(self, request):
        if request.user.is_authenticated:
            category = Category.objects.all()
            paginator = Paginator(category, 12)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            context = {
                "categories": page_obj
            }
            return render(request, self.template_name, context)
        else:
            messages.error(request, "Please log in here first")
            return redirect('blog:login')


class CreateNewCategoryView(View):
    def get(self, request):
        form = CategoryForm()
        context = {
            "form": form
        }
        return render(request, 'create_new_category.html', context)

    def post(self, request):
        form = CategoryForm(request.POST or None)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.save()
            messages.success(request, 'Your category is created successfully.')
            return redirect('blog:category')


class UpdateCategory(View):
    def get(self, request, id):
        if request.user.is_authenticated:
            cat = get_object_or_404(Category, id=id)
            form = CategoryForm(instance=cat)
            context = {
                "form": form
            }
            return render(request, 'create_new_category.html', context)
        else:
            messages.error(request, "Please log in here first")
            return redirect('blog:login')

    def post(self, request, id):
        if request.user.is_authenticated:
            cat = get_object_or_404(Category, id=id)
            form = CategoryForm(request.POST or None, instance=cat)
            if form.is_valid():
                instance = form.save(commit=False)
                instance.cat = cat
                instance.save()
                messages.success(request, 'Your category is updated successfully.')
                return redirect('blog:category')


class DeleteCategory(View):
    def get(self, request, id):
        if request.user.is_authenticated:
            cat = get_object_or_404(Category, id=id)
            cat.delete()
            messages.success(request, 'Your category is deleted successfully.')
            return redirect('blog:category')
        else:
            messages.info(request, 'Please login for deleting category')
            return redirect('blog:login')


class CreateNewArticleView(View):
    template_name = 'create_new_article.html'

    def get(self, request):
        if request.user.is_authenticated:
            form = CreateNewArticleForm()
            context = {
                "form": form
            }
            return render(request, self.template_name, context)
        else:
            messages.info(request, 'Please login for creating a new article')
            return redirect('blog:login')

    def post(self, request):
        article_auth = get_object_or_404(Author, name=request.user.id)
        form = CreateNewArticleForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.article_author = article_auth
            instance.save()
            messages.success(request, 'Your article is created successfully.')
            return redirect('blog:profile')


def profile(request):
    if request.user.is_authenticated:
        user = get_object_or_404(User, id=request.user.id)
        article_auth = Author.objects.filter(name=user.id)
        if article_auth:
            author_user = get_object_or_404(Author, name=request.user.id)
            articles = Article.objects.filter(article_author=author_user.id)
            paginator = Paginator(articles, 20)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            context = {
                'articles': page_obj
            }
            return render(request, 'logged_in_author.html', context)
        else:
            form = AuthorForm(request.POST or None, request.FILES or None)
            if form.is_valid():
                instance = form.save(commit=False)
                instance.name = user
                instance.save()
                return redirect('blog:profile')
            context = {
                "form": form
            }
            return render(request, 'create_author.html', context)
    else:
        messages.error(request, "Please log in here first")
        return redirect('blog:login')


class UpdateArticle(View):
    template_name = 'create_new_article.html'

    def get(self, request, id):
        if request.user.is_authenticated:
            article = get_object_or_404(Article, id=id)
            form = CreateNewArticleForm(instance=article)
            context = {
                "form": form
            }
            return render(request, self.template_name, context)

        else:
            messages.info(request, 'Please login for updating article')
            return redirect('blog:login')

    def post(self, request, id):
        article_auth = get_object_or_404(Author, name=request.user.id)
        article = get_object_or_404(Article, id=id)
        form = CreateNewArticleForm(request.POST or None, request.FILES or None, instance=article)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.article_author = article_auth
            instance.save()
            messages.success(request, 'Your article is updated successfully.')
            return redirect('blog:profile')


class DeleteArticle(View):
    def get(self, request, id):
        if request.user.is_authenticated:
            article = get_object_or_404(Article, id=id)
            article.delete()
            messages.success(request, 'Your article is deleted successfully.')
            return redirect('blog:profile')
        else:
            messages.info(request, 'Please login for deleting article')
            return redirect('blog:login')


def render_pdf_view(request, id):
    template_name = 'pdf.html'
    article = get_object_or_404(Article, id=id)
    context = {'article': article}
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="article.pdf"'
    template = get_template(template_name)
    html = template.render(context)
    pisa_status = pisa.CreatePDF(
       html, dest=response)

    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response


class RegisterView(View):
    template_name = 'register.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if User.objects.filter(username=username).exists():
            messages.warning(request, 'Username already taken')
            return redirect('blog:registration')
        elif User.objects.filter(email=email).exists():
            messages.warning(request, 'Email already taken')
            return redirect('blog:registration')
        elif password1 != password2:
            messages.warning(request, 'Password not matching')
            return redirect('blog:registration')
        elif len(password1) < 8:
            messages.warning(request, 'Password too short')
            return redirect('blog:registration')
        else:
            user = User.objects.create_user(username=username, email=email, password=password1, first_name=first_name, last_name=last_name)
            user.save()
            messages.success(request, 'Your registration was completed successfully')
            return redirect('blog:login')


class LoginView(View):
    template_name = 'login.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('blog:index')
        else:
            return render(request, self.template_name)

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        auth = authenticate(request, username=username, password=password)
        if auth is not None:
            login(request, auth)
            return redirect('blog:index')
        else:
            messages.error(request, 'Please correct the error below.')
            return redirect('blog:login')


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('blog:index')
