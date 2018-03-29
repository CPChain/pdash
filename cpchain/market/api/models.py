import datetime

import django
from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)


class MyUserManager(BaseUserManager):
    def create_user(self, public_key, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not public_key:
            raise ValueError('Users must have an public_key')

        user = self.model(
            public_key= public_key
            # email=self.normalize_email(email),
            # date_of_birth=date_of_birth,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, public_key, password):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            public_key=public_key
            # email,
            # password=password,
            # date_of_birth=date_of_birth,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        blank=True,
        unique=False,
    )
    date_of_birth = models.DateField(null=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    public_key = models.CharField(max_length=200, unique=True)
    created_date = models.DateTimeField('created date', default=datetime.datetime.now())
    active_date = models.DateTimeField('active date', default=datetime.datetime.now())
    status = models.IntegerField('0:normal,1:frozen,2:suspend,3.deleted', default=0)


    objects = MyUserManager()

    USERNAME_FIELD = 'public_key'
    REQUIRED_FIELDS = ['status']

    def __str__(self):
        return self.public_key

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin


class Product(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    owner_address = models.CharField(max_length=200)
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    price = models.FloatField()
    created_date = models.DateTimeField('date created', default=django.utils.timezone.now)
    expired_date = models.DateTimeField('date expired', null=True)
    verify_code = models.CharField(max_length=200, null=True)