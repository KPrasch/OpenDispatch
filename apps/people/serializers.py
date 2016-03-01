from rest_framework import serializers
from django.contrib.auth.models import User
from apps.people.models import Account


class UserModelSerializer(serializers.ModelSerializer):
    """  """

    class Meta:
        model = User

        fields = ('first_name', 'last_name', 'password', 'email',)
        write_only_fields = ('password',)
        read_only_fields = ('is_staff', 'is_superuser', 'is_active', 'date_joined',)

    def restore_object(self, attrs, instance=None):
        # call set_password on user object. Without this
        # the password will be stored in plain text.
        user = super(UserModelSerializer, self).restore_object(attrs, instance)
        user.set_password(attrs['password'])
        return user


class AccountModelSerializer(serializers.ModelSerializer):
    """  """
    user = UserModelSerializer()

    class Meta:
        model = Account

        fields = ('id', 'user', 'phone_number', 'is_responder', 'responder_active', 'agency', 'role',
                  'citizen_notifications', 'firehose_notifications', 'default_eta')
