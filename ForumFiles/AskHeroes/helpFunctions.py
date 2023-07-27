from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from . import models


def paginate(objects_list, request, per_page=10):
    pagination = Paginator(objects_list, per_page)
    page_number = request.GET.get("page")
    return pagination.get_page(page_number)


def get_new_question_rating(question_id: int, request, vote: int):
    question = models.Question.objects.get(id=question_id)
    question_vote, created = models.QuestionRating.objects.get_or_create(
        question=question, user=request.user.profile
    )
    if question_vote.vote == vote:
        question_vote.vote = 0
    else:
        question_vote.vote = vote
    question_vote.save()
    question.update_rating()
    return question.rating, question_vote.vote


def get_new_answer_rating(answer_id: int, request, vote: int):
    answer = models.Answer.objects.get(id=answer_id)
    answer_vote, created = models.AnswerRating.objects.get_or_create(
        answer=answer, user=request.user.profile
    )
    if answer_vote.vote == vote:
        answer_vote.vote = 0
    else:
        answer_vote.vote = vote
    answer_vote.save()
    answer.update_rating()
    return answer.rating, answer_vote.vote


def get_question_vote(question, user):
    if models.QuestionRating.objects.filter(
        question=question, user=user.profile
    ).exists():
        return models.QuestionRating.objects.get(
            question=question, user=user.profile
        ).vote
    return 0


def check_nickname(nickname, username):
    profile = models.Profile.objects.filter(nickname=nickname)
    return profile.exists() and username != profile[0].user.username


def get_publish_dates(model, objects_id):
    return [
        object.publish_date.strftime("%d %B %Y, %H:%M") + " UTC"
        for object in model.objects.in_bulk(map(int, objects_id)).values()
    ]


def json_for_likes_and_dislikes(request, model, rating_model, objects_id, object):
    if object == "question":
        return {
            object_id: rating_model.objects.get_or_create(
                user=request.user.profile,
                question=get_object_or_404(model.objects, id=int(object_id)),
            )[0].vote
            for object_id in objects_id
        }
    elif object == "answer":
        return {
            object_id: rating_model.objects.get_or_create(
                user=request.user.profile,
                answer=get_object_or_404(model.objects, id=int(object_id)),
            )[0].vote
            for object_id in objects_id
        }
