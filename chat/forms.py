from django.contrib.auth.hashers import make_password
from django.forms import ModelForm, Form, CharField
from django.views.generic import FormView

from chat.models import CustomUser


class RegisterModelForm(ModelForm):
    class Meta:
        model = CustomUser
        fields = 'username','password'

    def clean_password(self):
        password = self.cleaned_data['password']
        password  = make_password(password)
        return password

class LoginForm(Form):
    username = CharField(required=True)
    password = CharField(required=True)
