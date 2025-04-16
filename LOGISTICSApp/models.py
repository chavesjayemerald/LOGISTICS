from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings 

# USER MANAGEMENT
class UserManager(BaseUserManager):
    def create_user(self, username=None, password=None, **extra_fields):
        if not username:
            username = "single_user"
        user = self.model(username=username, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.password = ""
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(username, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    STATUS_CHOICES = (
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    )

    GENDER_CHOICES = (
        ('Male', 'Male'),
        ('Female', 'Female'),
    )

    user_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=255, unique=True, null=True, blank=True, default="single_user")
    password = models.CharField(max_length=255, null=True, blank=True, default="")
    firstname = models.CharField(max_length=55)
    middlename = models.CharField(max_length=55, null=True, blank=True)
    lastname = models.CharField(max_length=55)
    email_address = models.EmailField(max_length=255, null=True, blank=True)
    contact_number = models.CharField(max_length=55, null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'username'

    objects = UserManager()

    groups = models.ManyToManyField(
        Group,
        related_name='custom_user_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups'
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_user_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions'
    )

    class Meta:
        db_table = 'tbl_users'

    def __str__(self):
        return f"{self.lastname}, {self.firstname}"
    

# STORAGE MANAGEMENT
class Repository(models.Model):
    repository_id = models.AutoField(primary_key=True)
    repository_name = models.CharField(max_length=255)

    class Meta:
        db_table = 'tbl_repositories'

    def __str__(self):
        return self.repository_name

class Classification(models.Model):
    class_id = models.AutoField(primary_key=True)
    class_name = models.CharField(max_length=255)

    class Meta:
        db_table = 'tbl_classifications'

    def __str__(self):
        return self.class_name

class Subclassification(models.Model):
    subclass_id = models.AutoField(primary_key=True)
    class_id = models.ForeignKey(Classification, on_delete=models.CASCADE, db_column='class_id')
    subclass_name = models.CharField(max_length=255)

    class Meta:
        db_table = 'tbl_subclassifications'

    def __str__(self):
        return self.subclass_name

class Subset(models.Model):
    subset_id = models.AutoField(primary_key=True)
    subclass_id = models.ForeignKey(Subclassification, on_delete=models.CASCADE, db_column='subclass_id')
    subset_name = models.CharField(max_length=255)

    class Meta:
        db_table = 'tbl_subsets'

    def __str__(self):
        return self.subset_name

class Stored(models.Model):
    SERIAL_CHOICES = [('ICS', 'ICS'), ('PAR', 'PAR')]
    store_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    repository_id = models.ForeignKey(Repository, on_delete=models.CASCADE, db_column='repository_id')
    class_id = models.ForeignKey(Classification, on_delete=models.CASCADE, db_column='class_id')
    subclass_id = models.ForeignKey(Subclassification, on_delete=models.CASCADE, db_column='subclass_id')
    subset_id = models.ForeignKey(Subset, on_delete=models.CASCADE, db_column='subset_id', blank=True, null=True)
    store_memo = models.CharField(max_length=255, blank=True, null=True)
    date_received = models.DateField()
    date_acquired = models.DateField()
    end_user = models.CharField(max_length=255)
    unit_quantity = models.BigIntegerField()
    amount = models.BigIntegerField()
    serial_type = models.CharField(max_length=3, choices=SERIAL_CHOICES)
    serial_number = models.BigIntegerField()

    class Meta:
        db_table = 'tbl_stored'

    def __str__(self):
        return f"{self.repository.repository_name} - {self.serial_type} #{self.serial_number}"
