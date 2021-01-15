from django.urls import path
from . import views

app_name = 'blogapp'

urlpatterns = [
    path('', views.index, name='index'),
    path('single_page/<int:id>', views.SinglePageView.as_view(), name='single_page'),
    path('article_author/<name>', views.AuthorView.as_view(), name='article_author'),
    path('category/<name>', views.CategoryView.as_view(), name='category'),
    path('category/', views.CategoryListView.as_view(), name='category'),
    path('create_new_category/', views.CreateNewCategoryView.as_view(), name='create_new_category'),
    path('update_category/<int:id>', views.UpdateCategory.as_view(), name='update_category'),
    path('delete_category/<int:id>', views.DeleteCategory.as_view(), name='delete_category'),
    path('create_new_article/', views.CreateNewArticleView.as_view(), name='create_new_article'),
    path('article_update/<int:id>', views.UpdateArticle.as_view(), name='article_update'),
    path('delete_article/<int:id>', views.DeleteArticle.as_view(), name='delete_article'),
    path('profile/', views.profile, name='profile'),
    path('registration/', views.RegisterView.as_view(), name='registration'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('pdf/<int:id>', views.render_pdf_view, name='pdf'),

]
