from django.urls import path, re_path
from . import views
from django.contrib.auth import views as auth_views
from .forms import LoginForm

app_name = "The blog"

urlpatterns = [
    path('', views.index, name="index"),
    # path('posts/', views.post_list, name="post_list"),
    path('posts/', views.post_list, name="post_list"),
    path('category/<str:category>/', views.post_list, name="post_list_category"),
    re_path(r'tag/(?P<tag_slug>[-\w]+)/', views.post_list, name="post_list_by_tags"),
    re_path(r'posts/(?P<pk>[-\w]+)/(?P<slug>[-\w]+)/', views.post_detail, name="post_detail"),
    # path('posts/<str:category>/', views.post_list, name="post_list_category"),
    path('posts/<post_id>/comment/', views.post_comment, name="post_comment"),
    path('ticket/', views.ticket, name="ticket"),
    path('register/', views.register, name='register'),
    path('search/', views.post_search, name="post_search"),
    path('create_post/', views.create_post, name='create_post'),
    path('search/', views.post_search, name='post_search'),
    path('profile/', views.profile, name='profile'),
    path('profile/create_post/', views.create_post, name='create_post'),
    path('profile/delete_post/<post_id>/', views.delete_post, name='delete_post'),
    path('profile/edit-post/<post_id>/', views.edit_post, name='edit_post'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', views.log_out, name='logout'),
    path('password-change/', auth_views.PasswordChangeView.as_view(success_url='done'), name='password_change'),
    path('password-change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
    path('password-reset/', auth_views.PasswordResetView.as_view(success_url='done'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password-reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(success_url='/blog/password-reset/complete'),
         name='password_reset_confirm'),
    path('password-reset/complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('user/edit/', views.edit_user, name='edit_user'),
    path('users/@<user_name>/', views.user_profile, name='user_profile'),
    path('profile/show-comments/', views.show_comments, name='show-comments'),
    path('/follow/', views.user_follow, name='user_follow'),
    path('save-post/', views.save_post, name='save_post'),
    path('like-post/', views.like_post, name='like_post'),
    path('profile/saved_posts/', views.saved_posts, name='saved_posts'),
]
