import jwt
import time
import uuid
import django.contrib.auth as auth

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods, require_POST, require_GET
from django.views.decorators.csrf import csrf_protect
from django.http.response import JsonResponse
from django.http import HttpResponse, HttpResponseRedirect
from django.core.cache import cache
from django.urls import reverse
from django.forms import model_to_dict

from . import helpFunctions, models, forms
from cent import Client
from app.settings import CENTRIFUGO_API_KEY, CENTRIFUGO_SECRET_KEY, CENTRIFUGO_ADDRESS

POST_PER_PAGE = 7


@csrf_protect
@require_GET
def index(request):
    search_form = forms.SearchForm()
    return render(
        request,
        "index.html",
        {
            "search_form": search_form,
            "questions": helpFunctions.paginate(
                models.Question.objects.get_new_questions(),
                request,
                per_page=POST_PER_PAGE,
            ),
            "title": "New questions",
        },
    )


@csrf_protect
@require_GET
def hot(request):
    search_form = forms.SearchForm()
    return render(
        request,
        "index.html",
        {
            "search_form": search_form,
            "questions": helpFunctions.paginate(
                models.Question.objects.get_hot_questions(),
                request,
                per_page=POST_PER_PAGE,
            ),
            "title": "Hot questions",
        },
    )


@csrf_protect
@require_GET
def tag(request, tag_name):
    search_form = forms.SearchForm()
    return render(
        request,
        "index.html",
        {
            "search_form": search_form,
            "questions": helpFunctions.paginate(
                get_object_or_404(
                    models.Tag.objects, tag_name=tag_name
                ).get_related_questions(),
                request,
                per_page=POST_PER_PAGE,
            ),
            "tag": tag_name,
            "title": f"Tag: {tag_name}",
        },
    )


@csrf_protect
@require_http_methods(["GET", "POST"])
def search(request):
    if request.method == "POST":
        search_form = forms.SearchForm(request.POST)
        if not search_form.is_valid():
            return redirect(reverse("home"))
        else:
            if request.POST.get("search", "") == "":
                return render(
                    request,
                    "index.html",
                    {
                        "search_form": search_form,
                        "questions": helpFunctions.paginate(
                            [],
                            request,
                            per_page=POST_PER_PAGE,
                        ),
                        "query": "Your search request is empty!",
                        "title": "Search results error",
                    },
                )

            search_query = request.POST.get("search", "")
            return redirect(f"{request.path}?text={search_query}&page=1")

    search_query = request.GET.get("text", "")
    if search_query == "":
        return render(
            request,
            "index.html",
            {
                "search_form": forms.SearchForm(),
                "questions": helpFunctions.paginate(
                    [],
                    request,
                    per_page=POST_PER_PAGE,
                ),
                "query": "Your search request is empty!",
                "title": "Search results error",
            },
        )
    return render(
        request,
        "index.html",
        {
            "search_form": forms.SearchForm(),
            "questions": helpFunctions.paginate(
                models.Question.objects.get_search_query(search_query=search_query),
                request,
                per_page=POST_PER_PAGE,
            ),
            "query": search_query,
            "search_query": search_query,
            "title": "Search results",
        },
    )


@csrf_protect
@require_http_methods(["GET", "POST"])
def question(request, question_id):
    client = Client(
        f"http://{CENTRIFUGO_ADDRESS}/api", api_key=CENTRIFUGO_API_KEY, timeout=1
    )

    question = get_object_or_404(models.Question.objects, id=question_id)
    answers = question.answers.get_new_answers()
    channel_id = f"question_{question_id}"
    if request.method == "GET":
        answer_form = forms.AnswerForm()
        search_form = forms.SearchForm()
    else:
        if not request.user.is_authenticated:
            return redirect("/login/?next=" + request.path)

        answer_form = forms.AnswerForm(request.POST)
        search_form = forms.SearchForm(request.POST)
        answer = answer_form.create_answer(
            models.Profile.objects.get(user=request.user), question
        )
        if answer:
            client.publish(
                channel_id,
                {
                    "author_nickname": answer.author.nickname,
                    "publish_date": answer.publish_date.strftime("%d %B %Y, %H:%M"),
                    "answer": model_to_dict(answer, exclude=["publish_date", "author"]),
                    "answer_url": answer.author.avatar_path.url,
                },
            )
            return redirect(reverse("question", args=[question.id]) + "?page=1")

    return render(
        request,
        "question.html",
        {
            "form": answer_form,
            "search_form": search_form,
            "question": question,
            "answers": helpFunctions.paginate(answers, request, per_page=POST_PER_PAGE),
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
        search_form = forms.SearchForm()
    else:
        ask_form = forms.AskForm(request.POST)
        search_form = forms.SearchForm(request.POST)
        if ask_form.is_valid():
            question = ask_form.create_question(profile)
            if question:
                return redirect(reverse("question", args=[question.id]))
    return render(
        request,
        "ask.html",
        {
            "form": ask_form,
            "search_form": search_form,
            "user_nickname": profile.nickname,
            "title": "Ask question",
        },
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
        search_form = forms.SearchForm()
    else:
        settings_form = forms.SettingsForm(
            request.POST, files=request.FILES, instance=request.user
        )
        search_form = forms.SearchForm(request.POST)
        if settings_form.is_valid():
            if not helpFunctions.check_nickname(
                settings_form.cleaned_data["nickname"], request.user.username
            ):
                settings_form.save()
            else:
                settings_form.add_error("nickname", "This nickname already exist.")
    return render(
        request,
        "settings.html",
        {"form": settings_form, "search_form": search_form, "title": "User settings"},
    )


@csrf_protect
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
        search_form = forms.SearchForm()
        request.session["next_url"] = request.GET.get("next", "/")
        request.session.modified = True
    else:
        login_form = forms.LoginForm(request.POST)
        search_form = forms.SearchForm(request.POST)
        if login_form.is_valid():
            user = auth.authenticate(request=request, **login_form.cleaned_data)
            if user:
                auth.login(request, user)
                next_url = request.session.get("next_url", "/")
                return redirect(next_url)
            login_form.add_error(None, "Invalid username or password.")

    return render(
        request,
        "login.html",
        {"form": login_form, "search_form": search_form, "title": "Log in page"},
    )


@csrf_protect
@require_http_methods(["GET", "POST"])
def signup(request):
    if request.method == "GET":
        user_form = forms.UserForm()
        search_form = forms.SearchForm()
    else:
        user_form = forms.UserForm(
            request.POST, files=request.FILES, initial={"avatar": "img_main.jpg"}
        )
        if user_form.is_valid():
            if user_form.compare_passwords():
                profile = user_form.save()
                if profile:
                    auth.login(request, profile.user)

                return redirect(reverse("home"))

    return render(
        request,
        "signup.html",
        {"form": user_form, "search_form": search_form, "title": "Sign up page"},
    )


@csrf_protect
@require_POST
def popular_tags_and_top_users(request):
    return JsonResponse(
        {
            "popular_tags": cache.get("popular_tags")
            if cache.get("popular_tags") is not None
            else [tag.tag_name for tag in models.Tag.objects.get_top_tags(count=7)],
            "top_users": cache.get("top_users")
            if cache.get("top_users") is not None
            else [
                profile.nickname
                for profile in models.Profile.objects.get_top_users(count=5)
            ],
        }
    )


@csrf_protect
def is_authenticated(request):
    return JsonResponse({"is_authenticated": request.user.is_authenticated})


@csrf_protect
@login_required
@require_POST
def likes_and_dislikes_votes(request):
    dict_of_models = {"questions_id": models.Question, "answers_id": models.Answer}
    dict_of_models_rating = {
        "questions_id": models.QuestionRating,
        "answers_id": models.AnswerRating,
    }

    return JsonResponse(
        {
            object: helpFunctions.json_for_likes_and_dislikes(
                request=request,
                model=dict_of_models[object],
                rating_model=dict_of_models_rating[object],
                objects_id=request.POST.getlist(object, []),
                object=object[:-4],
            )
            for object in request.POST.keys()
        }
    )


@csrf_protect
@require_POST
def set_dates(request):
    dict_of_correspondences = {"question[]": models.Question, "answer[]": models.Answer}
    dates = []

    for object in request.POST:
        dates.extend(
            helpFunctions.get_publish_dates(
                dict_of_correspondences[object], request.POST.getlist(object, [])
            )
        )

    return JsonResponse({"dates": dates})


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


@csrf_protect
@require_POST
def instant_search(request):
    question_results = models.Question.objects.get_hot_questions().filter(
        search_vector=request.POST["query"]
    )[:5]
    return JsonResponse(
        {
            "question_results": [
                model_to_dict(
                    question,
                    exclude=[
                        "publish_date",
                        "author",
                        "search_vector",
                        "question_ratings",
                        "rating",
                    ],
                )
                for question in question_results
            ],
            "query": request.POST["query"],
        }
    )
