import re
import jwt
import time
import uuid

import django.contrib.auth as auth
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods, require_POST
from django.views.decorators.csrf import csrf_protect
from django.http.response import JsonResponse
from django.http import HttpResponse
from django.core.cache import cache
from django.urls import reverse
from django.forms import model_to_dict

from . import helpFunctions, models, forms
from cent import Client
from app.settings import CENTRIFUGO_API_KEY, CENTRIFUGO_SECRET_KEY, CENTRIFUGO_ADDRESS

client = Client(
    f"http://{CENTRIFUGO_ADDRESS}/api", api_key=CENTRIFUGO_API_KEY, timeout=1
)


def index(request):
    return render(
        request,
        "index.html",
        {
            "questions": helpFunctions.paginate(
                models.Question.objects.get_new_questions(), request, per_page=5
            ),
            "title": "New questions",
        },
    )


def hot(request):
    return render(
        request,
        "index.html",
        {
            "questions": helpFunctions.paginate(
                models.Question.objects.get_hot_questions(), request, per_page=5
            ),
            "title": "Hot questions",
        },
    )


def tag(request, tag_name):
    return render(
        request,
        "index.html",
        {
            "questions": helpFunctions.paginate(
                get_object_or_404(
                    models.Tag.objects, tag_name=tag_name
                ).get_related_questions(),
                request,
                per_page=5,
            ),
            "tag": tag_name,
            "title": f"Tag: {tag_name}",
        },
    )


@csrf_protect
@require_http_methods(["GET", "POST"])
def question(request, question_id):
    question = get_object_or_404(models.Question.objects, id=question_id)
    answers = question.answers.get_new_answers()
    channel_id = f"question_{question_id}"
    if request.method == "GET":
        answer_form = forms.AnswerForm()
    elif request.method == "POST":
        if not request.user.is_authenticated:
            return redirect("/login/?next=" + request.path)

        answer_form = forms.AnswerForm(request.POST)
        answer = answer_form.create_answer(
            models.Profile.objects.get(user=request.user), question
        )
        if answer:
            client.publish(
                channel_id,
                {
                    "answer": model_to_dict(answer, exclude=["publish_date", "author"]),
                    "answer_url": answer.author.avatar_path.url,
                },
            )
            return redirect(reverse("question", args=[question.id]))

    return render(
        request,
        "question.html",
        {
            "form": answer_form,
            "question": question,
            "answers": helpFunctions.paginate(answers, request, per_page=5),
            "title": f"Question №{question_id}",
            "server_address": CENTRIFUGO_ADDRESS,
            "cent_channel": channel_id,
            "secret_token": jwt.encode(
                {"sub": str(uuid.uuid4()), "exp": int(time.time()) + 10 * 60},
                CENTRIFUGO_SECRET_KEY,
                algorithm="HS256",
            ),
        },
    )


@csrf_protect
@login_required
@require_http_methods(["GET", "POST"])
def ask(request):
    profile = models.Profile.objects.get(user=request.user)
    if request.method == "GET":
        ask_form = forms.AskForm()
    elif request.method == "POST":
        ask_form = forms.AskForm(request.POST)
        if ask_form.is_valid():
            question = ask_form.create_question(profile)
            if question:
                return redirect(reverse("question", args=[question.id]))
    return render(
        request,
        "ask.html",
        {"form": ask_form, "user_nickname": profile.nickname, "title": "Ask question"},
    )


@csrf_protect
@login_required
@require_http_methods(["GET", "POST"])
def settings(request):
    if request.method == "GET":
        user = request.user
        settings_form = forms.SettingsForm(
            initial={"email": user.email, "nickname": user.profile.nickname}
        )
    elif request.method == "POST":
        settings_form = forms.SettingsForm(
            request.POST, files=request.FILES, instance=request.user
        )
        if settings_form.is_valid():
            settings_form.save()
            return redirect("settings")
    return render(
        request, "settings.html", {"form": settings_form, "title": "User settings"}
    )


@login_required
def logout(request):
    if not request.user.is_authenticated:
        return redirect("/login/")
    auth.logout(request)
    return redirect(request.META.get("HTTP_REFERER", "/"))


@csrf_protect
@require_http_methods(["GET", "POST"])
def login(request):
    if request.user.is_authenticated:
        return redirect("home")
    if request.method == "GET":
        login_form = forms.LoginForm()
        request.session["next_url"] = request.GET.get("next", "/")
    elif request.method == "POST":
        login_form = forms.LoginForm(request.POST)
        if login_form.is_valid():
            user = auth.authenticate(request=request, **login_form.cleaned_data)
            if user:
                auth.login(request, user)
                next_url = request.session.get("next_url", "/")
                del request.session["next_url"]
                return redirect(next_url)
            login_form.add_error(None, "Invalid username or password.")

    return render(request, "login.html", {"form": login_form, "title": "Log in page"})


@csrf_protect
@require_http_methods(["GET", "POST"])
def signup(request):
    if request.method == "GET":
        user_form = forms.UserForm()
    elif request.method == "POST":
        user_form = forms.UserForm(
            request.POST, files=request.FILES, initial={"avatar": "img_main.jpg"}
        )
        if user_form.is_valid():
            if user_form.compare_passwords():
                profile = user_form.save()
                if profile:
                    auth.login(request, profile.user)
                return redirect(reverse("home"))

    return render(request, "signup.html", {"form": user_form, "title": "Sign up page"})


@require_POST
def popular_tags_and_top_users(request):
    return JsonResponse(
        {
            "popular_tags": cache.get("popular_tags")
            if cache.get("popular_tags") is not None
            else [
                profile.nickname for profile in Profile.objects.get_top_users(count=5)
            ],
            "top_users": cache.get("top_users")
            if cache.get("top_users") is not None
            else [tag.tag_name for tag in Tag.objects.get_top_tags(count=7)],
        }
    )


@csrf_protect
def is_authenticated(request):
    return JsonResponse({"is_authenticated": request.user.is_authenticated})


@csrf_protect
@login_required
@require_POST
def likes_and_dislikes_votes(request):
    answers_id = request.POST.getlist("answers_id")
    questions_id = request.POST.getlist("questions_id")
    if len(answers_id) == 0:
        return JsonResponse(
            {
                "question_votes": {
                    question_id: models.QuestionRating.objects.get_or_create(
                        question=get_object_or_404(
                            models.Question.objects, id=int(question_id)
                        ),
                        user=request.user.profile,
                    )[0].vote
                    for question_id in questions_id
                },
                "answer_votes": {},
            }
        )
    return JsonResponse(
        {
            "question_votes": {
                question_id: models.QuestionRating.objects.get_or_create(
                    question=get_object_or_404(
                        models.Question.objects, id=int(question_id)
                    ),
                    user=request.user.profile,
                )[0].vote
                for question_id in questions_id
            },
            "answer_votes": {
                answer_id: models.AnswerRating.objects.get_or_create(
                    answer=get_object_or_404(models.Answer.objects, id=int(answer_id)),
                    user=request.user.profile,
                )[0].vote
                for answer_id in answers_id
            },
        }
    )


@csrf_protect
@login_required
@require_POST
def vote_up(request):
    question_id = request.POST.get("question_id", None)
    answer_id = request.POST.get("answer_id", None)
    if question_id is not None:
        new_rating, question_vote = helpFunctions.get_new_question_rating(
            question_id, request, vote=1
        )
        return JsonResponse({"new_rating": new_rating, "vote": question_vote})
    elif answer_id is not None:
        new_rating, answer_vote = helpFunctions.get_new_answer_rating(
            answer_id, request, vote=1
        )
        return JsonResponse({"new_rating": new_rating, "vote": answer_vote})


@csrf_protect
@login_required
@require_POST
def vote_down(request):
    question_id = request.POST.get("question_id", None)
    answer_id = request.POST.get("answer_id", None)
    if question_id is not None:
        new_rating, question_vote = helpFunctions.get_new_question_rating(
            question_id, request, vote=-1
        )
        return JsonResponse({"new_rating": new_rating, "vote": question_vote})
    elif answer_id is not None:
        new_rating, answer_vote = helpFunctions.get_new_answer_rating(
            answer_id, request, vote=-1
        )
        return JsonResponse({"new_rating": new_rating, "vote": answer_vote})


@csrf_protect
@require_POST
def correct_answers_votes(request):
    answers_id = request.POST.getlist("answers_id")
    question_id = request.POST["question_id"]
    question_author = get_object_or_404(
        models.Question.objects, id=int(question_id)
    ).author
    if request.user.is_authenticated:
        is_author = request.user.profile == question_author
    else:
        is_author = False
    return JsonResponse(
        {
            "is_author": is_author,
            "answers_choices": {
                answer_id: models.Answer.objects.get(id=answer_id).correct_answer
                for answer_id in answers_id
            },
        }
    )


@csrf_protect
@login_required
@require_POST
def choose_answer(request):
    choose_answer = models.Answer.objects.get(id=request.POST["answer_id"])
    if choose_answer.correct_answer:
        choose_answer.correct_answer = False
    else:
        choose_answer.correct_answer = True
    choose_answer.save()
    return JsonResponse({"new_choice": choose_answer.correct_answer})
