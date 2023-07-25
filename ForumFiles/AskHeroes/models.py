from django.db import models
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models import Count
from django.contrib.auth.models import User
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField, SearchVector
from django.db.models.signals import post_save
from django.dispatch import receiver


class QuestionManager(models.Manager):
    def get_new_questions(self):
        return self.annotate(answers_count=Count("answers")).order_by("-publish_date")

    def get_hot_questions(self):
        return self.annotate(answers_count=Count("answers")).order_by("-rating")


class AnswerManager(models.Manager):
    def get_new_answers(self):
        return self.order_by("-publish_date")

    def get_most_rated_answers(self):
        return self.order_by("-rating")


class ProfileManager(models.Manager):
    def get_top_users(self, count: int):
        return self.annotate(
            rating=Count("answers_on_question") + Count("author_questions")
        ).order_by("-rating")[:count]


class Profile(models.Model):
    avatar_path = models.ImageField(
        blank=True, null=True, upload_to="avatars/%Y/%m/%d/", default="img_main.jpg"
    )
    nickname = models.CharField(max_length=20)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=False)

    objects = ProfileManager()


class QuestionRating(models.Model):
    vote = models.IntegerField(default=0)
    user = models.ForeignKey("Profile", on_delete=models.CASCADE)
    question = models.ForeignKey("Question", on_delete=models.CASCADE)

    class Meta:
        unique_together = ["user", "question"]


class Question(models.Model):
    author = models.ForeignKey(
        "Profile", on_delete=models.CASCADE, related_name="author_questions"
    )
    title = models.CharField(max_length=255)
    content = models.TextField(max_length=2048)
    publish_date = models.DateTimeField()
    rating = models.IntegerField(default=0)
    question_ratings = models.ManyToManyField(
        "Profile", through="QuestionRating", related_name="question_rating"
    )

    objects = QuestionManager()

    search_vector = SearchVectorField(null=True)

    def get_answers(self):
        return self.answer_set.get_new_questions()

    def update_rating(self):
        self.rating = 0
        for ratings in self.questionrating_set.all():
            self.rating += ratings.vote
        self.save()

    def update_search_vector(self):
        qs = Question.objects.filter(pk=self.pk)
        qs.update(search_vector=SearchVector("title", "content"))

    class Meta:
        indexes = [
            GinIndex(
                fields=[
                    "search_vector",
                ]
            ),
        ]


@receiver(post_save, sender=Question)
def post_save_artcile(sender, instance, created, update_fields, **kwargs):
    instance.update_search_vector()


class AnswerRating(models.Model):
    vote = models.IntegerField(default=0)
    user = models.ForeignKey("Profile", on_delete=models.CASCADE)
    answer = models.ForeignKey("Answer", on_delete=models.CASCADE)

    class Meta:
        unique_together = ["user", "answer"]


class Answer(models.Model):
    author = models.ForeignKey(
        "Profile", on_delete=models.CASCADE, related_name="answers_on_question"
    )
    content = models.CharField(max_length=2048)
    publish_date = models.DateTimeField()
    related_question = models.ForeignKey(
        "Question", on_delete=models.CASCADE, related_name="answers"
    )
    rating = models.IntegerField(default=0)
    correct_answer = models.BooleanField(default=False)
    answer_ratings = models.ManyToManyField("Profile", through="AnswerRating")

    objects = AnswerManager()

    def update_rating(self):
        self.rating = 0
        for ratings in self.answerrating_set.all():
            self.rating += ratings.vote
        self.save()


class TagsManager(models.Manager):
    def get_top_tags(self, count: int):
        three_months_ago = timezone.make_aware(
            datetime.now() - timedelta(days=90), timezone.get_current_timezone()
        )
        return self.annotate(
            questions_count=Count(
                "related_questions",
                filter=models.Q(related_questions__publish_date__gte=three_months_ago),
            )
        ).order_by("-questions_count")[:count]


class Tag(models.Model):
    tag_name = models.CharField(max_length=24)
    related_questions = models.ManyToManyField("Question", related_name="tags")

    objects = TagsManager()

    def get_related_questions(self):
        return self.related_questions.all()
