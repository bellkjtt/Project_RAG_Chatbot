from django import forms
from django.core.validators import FileExtensionValidator
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from selfchatgpt.models import QnaPost, QnAReply, Application


class CSVUploadForm(forms.Form):
    csv_file = forms.FileField(
        label="CSV 파일", validators=[FileExtensionValidator(["csv"])]
    )


class UserForm(UserCreationForm):
    email = forms.EmailField(label="이메일")

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")


class QnABoardPostForm(forms.ModelForm):
    class Meta:
        model = QnaPost
        fields = ["title", "content"]


class QnABoardPostReplyForm(forms.ModelForm):

    add_to_db = forms.BooleanField(required=False)

    class Meta:
        model = QnAReply
        fields = ["content"]


class ApplicationForm(forms.ModelForm):

    class Meta:
        model = Application
        fields = ["name", "essay", "dob", "track"]
