from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings 
from django.db import models

def validate_image_size(value):
    if value.size > 1 * 512 * 512:
        raise ValidationError("The file size should not exceed 1MB.")

class TrustedDevice(models.Model):
    trusted_id = models.AutoField(primary_key=True)
    user = models.ForeignKey('LOGISTICSApp.User', on_delete=models.CASCADE)
    device_token = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField()

    class Meta:
        db_table = 'tbl_trusteddevice'

    def __str__(self):
        return f"{self.user.username} - {self.device_token}"


class Station(models.Model):
    station_id = models.AutoField(primary_key=True)
    station_name = models.CharField(max_length=255)

    class Meta:
        db_table = 'tbl_stations'

    def __str__(self):
        return self.station_name
    

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

    profile_picture = models.BinaryField(null=True, blank=True)
    user_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=255, unique=True, null=True, blank=True, default="single_user")
    password = models.CharField(max_length=255, null=True, blank=True, default="")
    firstname = models.CharField(max_length=55)
    middlename = models.CharField(max_length=55, null=True, blank=True)
    lastname = models.CharField(max_length=55)
    email_address = models.EmailField(max_length=255, null=True, blank=True)
    contact_number = models.CharField(max_length=55, null=True, blank=True)
    station_id = models.ForeignKey(Station, on_delete=models.CASCADE, db_column='station_id')
    rank = models.CharField(max_length=55, null=True, blank=True)
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
    

# ROLE MANAGEMENT
class Role(models.Model):
    role_id = models.AutoField(primary_key=True)
    role_name = models.CharField(max_length=55, unique=True)

    class Meta:
        db_table = 'tbl_roles'

    def __str__(self):
        return self.role_name

class UserRole(models.Model):
    userRole_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_roles')
    role = models.ForeignKey(Role, on_delete=models.CASCADE)

    class Meta:
        db_table = 'tbl_userroles'

    def __str__(self):
        return f"{self.user.user_id} - {self.role.role_name}"
    

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



# RIS MANAGEMENT
class RISClassification(models.Model):
    risclass_id = models.AutoField(primary_key=True)
    risclass_name = models.CharField(max_length=255)

    class Meta:
        db_table = 'tbl_risclassifications'

    def __str__(self):
        return self.risclass_name

class RISSubclassification(models.Model):
    rissubclass_id = models.AutoField(primary_key=True)
    risclass_id = models.ForeignKey(RISClassification, on_delete=models.CASCADE, db_column='risclass_id')
    rissubclass_name = models.CharField(max_length=255)

    class Meta:
        db_table = 'tbl_rissubclassifications'

    def __str__(self):
        return self.rissubclass_name

class RIS(models.Model):
    ris_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    repository_id = models.ForeignKey(Repository, on_delete=models.CASCADE, db_column='repository_id')
    risclass_id = models.ForeignKey(RISClassification, on_delete=models.CASCADE, db_column='risclass_id')
    rissubclass_id = models.ForeignKey(RISSubclassification, on_delete=models.CASCADE, db_column='rissubclass_id')
    ris_memo = models.CharField(max_length=255, blank=True, null=True)
    date_received = models.DateField()
    date_acquired = models.DateField()
    end_user = models.CharField(max_length=255)
    unit_quantity = models.BigIntegerField()
    amount = models.BigIntegerField()

    class Meta:
        db_table = 'tbl_ris'

    def __str__(self):
        return f"{self.repository.repository_name}"


# LOT MANAGEMENT    

class Ownership(models.Model):
    owner_id = models.AutoField(primary_key=True)
    owner_name = models.CharField(max_length=255)

    class Meta:
        db_table = 'tbl_ownerships'

    def __str__(self):
        return self.owner_name
    

class Area(models.Model):
    area_id = models.AutoField(primary_key=True)
    area_name = models.CharField(max_length=255)

    class Meta:
        db_table = 'tbl_areas'

    def __str__(self):
        return self.area_name
    

class LOTClassification(models.Model):
    lotclass_id = models.AutoField(primary_key=True)
    lotclass_name = models.CharField(max_length=255)

    class Meta:
        db_table = 'tbl_lotclassifications'

    def __str__(self):
        return self.lotclass_name


class LOT(models.Model):
    lot_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    lotclass_id = models.ForeignKey(LOTClassification, on_delete=models.CASCADE, db_column='lotclass_id')
    station_id = models.ForeignKey(Station, on_delete=models.CASCADE, db_column='station_id')
    owner_id = models.ForeignKey(Ownership, on_delete=models.CASCADE, db_column='owner_id')
    area_id = models.ForeignKey(Area, on_delete=models.CASCADE, db_column='area_id')
    lot_memo = models.CharField(max_length=255, blank=True, null=True)
    date_received = models.DateField()
    date_acquired = models.DateField()

    class Meta:
        db_table = 'tbl_lots'

    def __str__(self):
        return f"{self.lotclass_id} - {self.station}"
    

# BUILDING MANAGEMENT
class BuildingClassification(models.Model):
    buildingclass_id = models.AutoField(primary_key=True)
    buildingclass_name = models.CharField(max_length=255)

    class Meta:
        db_table = 'tbl_buildingclassifications'

    def __str__(self):
        return self.buildingclass_name


class Building(models.Model):
    building_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    buildingclass_id = models.ForeignKey(BuildingClassification, on_delete=models.CASCADE, db_column='buildingclass_id')
    station_id = models.ForeignKey(Station, on_delete=models.CASCADE, db_column='station_id')
    owner_id = models.ForeignKey(Ownership, on_delete=models.CASCADE, db_column='owner_id')
    area_id = models.ForeignKey(Area, on_delete=models.CASCADE, db_column='area_id')
    building_memo = models.CharField(max_length=255, blank=True, null=True)
    date_received = models.DateField()
    date_acquired = models.DateField()

    class Meta:
        db_table = 'tbl_buildings'

    def __str__(self):
        return f"{self.buildingclass_id} - {self.station}"


# PARKING MANAGEMENT
class Location(models.Model):
    location_id = models.AutoField(primary_key=True)
    location_name = models.CharField(max_length=255)

    class Meta:
        db_table = 'tbl_locations'

    def __str__(self):
        return self.location_name
    

class Vehicle(models.Model):
    vehicle_id = models.AutoField(primary_key=True)
    vehicle_name = models.CharField(max_length=255)

    class Meta:
        db_table = 'tbl_vehicles'

    def __str__(self):
        return self.vehicle_name


class Parking(models.Model):
    parking_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    location_id = models.ForeignKey(Location, on_delete=models.CASCADE, db_column='location_id')
    vehicle_id = models.ForeignKey(Vehicle, on_delete=models.CASCADE, db_column='vehicle_id')
    unit_quantity = models.BigIntegerField()
    parking_memo = models.CharField(max_length=255, blank=True, null=True)
    date_received = models.DateField()
    date_acquired = models.DateField()

    class Meta:
        db_table = 'tbl_parkings'

    def __str__(self):
        return f"{self.parking_id} - {self.location}"