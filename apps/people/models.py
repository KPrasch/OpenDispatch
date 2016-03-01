from django.contrib.auth.models import User
from django.contrib.gis.measure import D
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.utils.http import urlquote
from django.utils.translation import ugettext_lazy as _
from django.core.mail import send_mail
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.models import BaseUserManager


class AccountManager(BaseUserManager):

    def _create_account(self, email, password,
                     is_staff, is_superuser, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        now = timezone.now()
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        account = self.model(email=email,
                          is_staff=is_staff, is_active=True,
                          is_superuser=is_superuser, last_login=now,
                          date_joined=now, **extra_fields)
        account.set_password(password)
        account.save(using=self._db)
        return account

    def create_account(self, email, password=None, **extra_fields):
        return self._create_account(email, password, False, False,
                                 **extra_fields)

    def create_superaccount(self, email, password, **extra_fields):
        return self._create_account(email, password, True, True,
                                 **extra_fields)

ROLES = (
    ('Medical Responder', 'Medical Responder'),
    ('Firefighter', 'Firefighter'),
    ('Administrator', 'Administrator'),
    ('Radio Hobbiest', 'Radio Hobbiest'),
    ('Law Enforcement', 'Law Enforcement'),
    ('Public Works', 'Public Works'),
    ('Other Government Employee', 'Other Government Employee'),
    ('Technical', 'Technical')
)


class Account(AbstractBaseUser, PermissionsMixin):
    """
    A fully featured User model with admin-compliant permissions that uses
    a full-length email field as the username.

    Email and password are required. Other fields are optional.
    """
    email = models.EmailField(_('email address'), max_length=254, unique=True)
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    username = models.CharField(max_length=64)
    phone_number = PhoneNumberField(blank=True, default=None)
    is_responder = models.BooleanField(default=False)
    responder_active = models.BooleanField(default=False)
    agency = models.CharField(max_length=64, blank=True, null=True)
    role = models.CharField(choices=ROLES, max_length=256, blank=True, null=True)
    citizen_notifications = models.BooleanField(default=False)
    firehose_notifications = models.BooleanField(default=False, editable=False)
    default_eta = models.PositiveIntegerField(blank=True, null=True)

    is_staff = models.BooleanField(_('staff status'), default=False,
        help_text=_('Designates whether the user can log into this admin '
                    'site.'))
    is_active = models.BooleanField(_('active'), default=True,
        help_text=_('Designates whether this user should be treated as '
                    'active. Unselect this instead of deleting accounts.'))
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = AccountManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['username', 'email', 'password']

    class Meta:
        verbose_name = _('account')
        verbose_name_plural = _('accounts')

    def get_absolute_url(self):
        return "/accounts/%s/" % urlquote(self.email)

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        "Returns the short name for the user."
        return self.first_name

    def email_user(self, subject, message, from_email=None):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email])

