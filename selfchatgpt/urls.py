# selfchatgpt/urls.py
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = "selfchatgpt"
urlpatterns = [
    path("", views.index, name="index"),
    path("chatbot/", views.chatbot, name="chatbot"),
    path("signup/", views.signup, name="signup"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    # qna 게시판
    path("qna/", views.post_list, name="post_list"),
    path("qna/create/", views.post_create, name="post_create"),
    path("qna/post/<int:post_id>/", views.post_detail, name="post_detail"),
    path("qna/post/<int:post_id>/reply", views.post_reply, name="post_reply"),
    # 지원
    path("apply/", views.apply, name="apply"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
