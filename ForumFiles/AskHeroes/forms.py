import datetime
from django.utils import timezone
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.password_validation import validate_password
from django.forms import ValidationError
from . import models


class AnswerForm(forms.ModelForm):
    class Meta:
        model = models.Answer
        fields = ["content"]
        widgets = {
            "content": forms.Textarea(
                attrs={
                    "placeholder": "Your answer on current question",
                    "class": "ask_text-text",
                }
            )
        }

    def create_answer(self, profile, question):
        answer = self.save(commit=False)
        answer.author = profile
        answer.publish_date = timezone.make_aware(
            datetime.datetime.now(), timezone.get_current_timezone()
        )
        answer.related_question = question
        answer.save()
        return answer


class AskForm(forms.ModelForm):
    tags = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Tags of your question (maximum 3 tags)",
                "class": "ask_tags-text",
            }
        ),
    )

    class Meta:
        model = models.Question
        fields = ["title", "content"]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "placeholder": "Title of your question",
                    "class": "ask_title-text",
                }
            ),
            "content": forms.Textarea(
                attrs={
                    "placeholder": "Text of your question",
                    "rows": 60,
                    "cols": 36,
                    "class": "ask_text-text",
                }
            ),
        }

    def get_tags(self):
        tag_names = self.cleaned_data["tags"].split(",")
        self.cleaned_data.pop("tags")
        tag_objects = []
        for tag_name in tag_names:
            tag, created = models.Tag.objects.get_or_create(tag_name=tag_name.strip())
            tag_objects.append(tag)
        if len(tag_objects) >= 4 or len(tag_objects) == 0:
            self.add_error(
                "tags", "The question need at least one tag, but no more than three."
            )
            print(tag_objects)
            return None
        return tag_objects

    def create_question(self, profile):
        question_tags = self.get_tags()
        if question_tags is None:
            return None
        question = self.save(commit=False)
        question.author = profile
        question.publish_date = timezone.make_aware(
            datetime.datetime.now(), timezone.get_current_timezone()
        )
        question.save()
        question.tags.set(question_tags)
        return question


class LoginForm(forms.Form):
    username = forms.CharField(
        min_length=4,
        widget=forms.TextInput(
            attrs={"placeholder": "Your username", "class": "login_login"}
        ),
    )
    password = forms.CharField(
        min_length=4,
        widget=forms.PasswordInput(
            attrs={"placeholder": "Your password", "class": "login_password"}
        ),
    )


class UserForm(forms.ModelForm):
    repeated_password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Repeat your password",
                "class": "signup_repeat-password",
            }
        ),
    )

    avatar = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(
            attrs={"placeholder": "No file chosen", "id": "signup_imgInput"}
        ),
        initial="img_main.jpg",
    )

    nickname = forms.CharField(
        min_length=4,
        max_length=20,
        widget=forms.TextInput(
            attrs={"placeholder": "Your nickname", "class": "signup_nickname"}
        ),
    )

    def compare_passwords(self):
        if self.cleaned_data["password"] != self.cleaned_data["repeated_password"]:
            return False
        return True

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
            profile = models.Profile(
                user=user,
                avatar_path=self.cleaned_data["avatar"],
                nickname=self.cleaned_data["nickname"],
            )
            profile.save()
            return profile
        return user

    class Meta:
        model = models.User
        fields = [
            "username",
            "email",
            "password",
            "repeated_password",
            "avatar",
            "nickname",
        ]
        widgets = {
            "username": forms.TextInput(
                attrs={"placeholder": "Your username", "class": "signup_login"}
            ),
            "email": forms.EmailInput(
                attrs={"placeholder": "Your email", "class": "signup_email"}
            ),
            "password": forms.PasswordInput(
                attrs={"placeholder": "Your password", "class": "signup_password"}
            ),
        }


class SettingsForm(forms.ModelForm):
    nickname = forms.CharField(
        min_length=4,
        max_length=20,
        widget=forms.TextInput(attrs={"class": "settings_nickname"}),
    )

    avatar = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(
            attrs={"placeholder": "No file chosen", "id": "settings_imgInput"}
        ),
    )

    class Meta:
        model = models.User
        fields = ["email", "nickname", "avatar"]
        widgets = {"email": forms.EmailInput(attrs={"class": "settings_email"})}

    def save(self, commit=True):
        user = super().save(commit)
        profile = user.profile
        profile.nickname = self.cleaned_data["nickname"]
        if self.cleaned_data["avatar"] is not None:
            profile.avatar_path = self.cleaned_data["avatar"]
        profile.save()

        return profile
