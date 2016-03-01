from rest_framework import serializers
from apps.people.models import Account


class AccountModelSerializer(serializers.ModelSerializer):
    """  """

    class Meta:
        model = Account

        fields = ('first_name', 'last_name', 'password', 'email', 'phone_number', 'is_responder', 'responder_active', 'agency', 'role',
                  'citizen_notifications', 'firehose_notifications', 'default_eta',)
        write_only_fields = ('password',)
        read_only_fields = ('is_staff', 'is_superuser', 'is_active', 'date_joined',)

    def restore_object(self, attrs, instance=None):
        # call set_password on user object. Without this
        # the password will be stored in plain text.
        account = super(UserModelSerializer, self).restore_object(attrs, instance)
        account.set_password(attrs['password'])
        return account

