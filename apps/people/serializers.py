from rest_framework import serializers
from django.contrib.auth.models import User
from apps.people.models import Account


class UserModelSerializer(serializers.ModelSerializer):
    """  """

    class Meta:
        model = User

        fields = ('id', 'first_name', 'last_name', 'email')


class AccountModelSerializer(serializers.ModelSerializer):
    """  """
    user = UserModelSerializer()

    class Meta:
        model = Account

        fields = ('id', 'user', 'phone_number', 'is_responder', 'responder_active', 'agency', 'role',
                  'citizen_notifications', 'firehose_notifications', 'default_eta')
