"""
URL configuration for app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from AskHeroes import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.index, name="home"),
    path("logout/", views.logout, name="logout"),
    path("hot/", views.hot, name="hot"),
    path("tag/<str:tag_name>/", views.tag, name="tag"),
    path("question/<int:question_id>/", views.question, name="question"),
    path("ask/", views.ask, name="ask"),
    path("profile/edit/", views.settings, name="settings"),
    path("login/", views.login, name="login"),
    path("signup/", views.signup, name="signup"),
    path("is_authenticated/", views.is_authenticated, name="is_authenticated/"),
    path(
        "likes_and_dislikes_votes/",
        views.likes_and_dislikes_votes,
        name="likes_and_dislikes_votes/",
    ),
    path(
        "correct_answers_votes/",
        views.correct_answers_votes,
        name="correct_answers_votes",
    ),
    path("vote_up/", views.vote_up, name="vote_up"),
    path("vote_down/", views.vote_down, name="vote_down"),
    path("choose_answer/", views.choose_answer, name="choose_answer"),
    path(
        "popular_tags_and_top_users/",
        views.popular_tags_and_top_users,
        name="popular_tags_and_top_users",
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
