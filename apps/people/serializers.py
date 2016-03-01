from rest_framework import serializers
from apps.people.models import Account


class AccountModelSerializer(serializers.ModelSerializer):
    """  """

    class Meta:
        model = Account

        fields = ('username', 'password', 'first_name', 'last_name', 'email', 'phone_number', 'is_responder', 'responder_active', 'agency', 'role',
                  'citizen_notifications', 'firehose_notifications', 'default_eta',)
        write_only_fields = ('password',)
        read_only_fields = ('is_staff', 'is_superuser', 'is_active', 'date_joined',)

    def create(self, validated_data):
        account = Account.objects.create_account(**validated_data)
        return account