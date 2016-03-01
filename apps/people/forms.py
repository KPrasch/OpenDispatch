from django.contrib.auth.models import User
from django.forms import ModelForm, RegexField, CharField, PasswordInput
from django.core.exceptions import ValidationError, ObjectDoesNotExist
import re

from apps.people.models import Account
from apps.map.models import UserLocation


class UserForm(ModelForm):
    username = RegexField(label="Username", max_length=30,
         regex=r'^[\w.@+-]+$', help_text = "My text",
         error_messages = {'invalid':
           "This value may contain only letters, numbers and @/./+/-/_ characters."
         }
    )
    password = CharField(label="Password",
                              widget=PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'first_name', 'last_name')

    def clean_username(self):
        username = self.cleaned_data['username']
        if not re.search(r'^\w+$', username):
            raise ValidationError(
                  'Username can contain only alphanumeric characters')
        try:
            User.objects.get(username=username)
        except ObjectDoesNotExist:
            return username
        raise ValidationError('Username is already taken')

    def save(self, commit=True):
        user = super(UserForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class AccountForm(ModelForm):
    class Meta:
        model = Account
        fields = ('phone_number',) #, 'agency', 'role')


class UserLocationForm(ModelForm):
    class Meta:
        model = UserLocation
        fields = ('title', 'description', 'category')




