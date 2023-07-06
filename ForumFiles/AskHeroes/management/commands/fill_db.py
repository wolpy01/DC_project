from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from AskHeroes.models import *
from faker import Faker
import random
import pytz


class Command(BaseCommand):
    help = 'This script is filling the base.'

    def add_arguments(self, parser):
        parser.add_argument('--ratio', type=int)

    def handle(self, *args, **kwargs):
        ratio = kwargs['ratio']
        self.create_users(ratio)
        self.create_profiles(ratio)
        self.create_questions(ratio * 10)
        self.create_answers(ratio * 100)
        self.create_tags(ratio)
        self.add_tags_to_questions()
        self.create_questions_rating(ratio * 100)
        self.create_answers_rating(ratio * 100)
        self.calculate_questions_rating()
        self.calculate_answers_rating()

    def create_users(self, users_count):
        faker = Faker('la')
        users = [
            User(username=faker.user_name() + str(i),
                 password=make_password(faker.word()),
                 email=faker.email())
            for i in range(users_count)
        ]
        User.objects.bulk_create(users)

    def create_profiles(self, users_count):
        users = User.objects.all()
        faker = Faker('la')
        profiles = [
            Profile(user=users[i], nickname=(faker.user_name() + str(i))[-20:])
            for i in range(users_count)
        ]
        Profile.objects.bulk_create(profiles)

    def create_questions(self, questions_count):
        faker = Faker('la')
        users = Profile.objects.all()
        questions = [
            Question(author=random.choice(users),
                     title=faker.sentence(), content=faker.text(),
                     publish_date=timezone.make_aware(faker.date_time_this_year(), timezone.get_current_timezone()))
            for _ in range(questions_count)
        ]
        Question.objects.bulk_create(questions)

    def create_answers(self, answers_count):
        faker = Faker('la')
        users = Profile.objects.all()
        questions = Question.objects.all()
        answers = [
            Answer(author=random.choice(users),
                   content=faker.text(),
                   publish_date=timezone.make_aware(faker.date_time_this_year(), timezone.get_current_timezone()),
                   related_question=random.choice(questions),
                   correct_answer=False)
            for _ in range(answers_count)
        ]
        Answer.objects.bulk_create(answers)

    def create_tags(self, tags_count):
        faker = Faker('la')
        tags = [
            Tag(tag_name=faker.word() + str(i))
            for i in range(tags_count)
        ]
        Tag.objects.bulk_create(tags)

    def add_tags_to_questions(self):
        questions = Question.objects.all()
        tags = Tag.objects.all()
        for i in range(len(questions)):
            tags_for_question = [tags[i % len(tags)]]
            for _ in range(random.randint(0, 2)):
                random_tag = random.choice(tags)
                if random_tag not in tags_for_question:
                    tags_for_question.append(random_tag)
            questions[i].tags.add(*tags_for_question)
        Question.objects.update()

    def create_questions_rating(self, questions_votes_count):
        questions = Question.objects.all()
        users = Profile.objects.all()
        votes_count, i = 0, 0
        while votes_count < questions_votes_count:
            rating_for_questions = []
            for question in questions:
                rating_for_questions.append(QuestionRating(question=question, user=users[i],
                                                           vote=random.choice((-1, 0, 1))))
                votes_count += 1
            i += 1
            QuestionRating.objects.bulk_create(rating_for_questions)

    def create_answers_rating(self, answers_vote_count):
        answers = Answer.objects.all()
        users = Profile.objects.all()
        votes_count, i = 0, 0
        while votes_count < answers_vote_count:
            rating_for_answers = []
            for answer in answers:
                rating_for_answers.append(AnswerRating(answer=answer, user=users[i],
                                                       vote=random.choice((-1, 0, 1)),
                                                       ))
                votes_count += 1
            i += 1
            AnswerRating.objects.bulk_create(rating_for_answers)

    def calculate_questions_rating(self):
        questions = Question.objects.all()
        for question in questions:
            question.update_rating()

    def calculate_answers_rating(self):
        answers = Answer.objects.all()
        for answer in answers:
            answer.update_rating()
