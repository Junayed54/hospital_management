from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class CustomUserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError("The Phone Number field is required")
        extra_fields.setdefault('is_active', True)
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(phone_number, password, **extra_fields)


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Position(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name="positions")
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    class Meta:
        unique_together = ('department', 'name')  # Position names must be unique within a department.

    def __str__(self):
        return f"{self.name} ({self.department.name})"


class CustomUser(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('doctor', 'Doctor'),
        ('patient', 'Patient'),
        ('staff', 'Staff'),
        ('admin', 'Admin'),
    )
    
    phone_number = models.CharField(max_length=15, unique=True)
    email = models.EmailField(unique=True, blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='patient')
    department = models.ForeignKey(
        Department, on_delete=models.SET_NULL, null=True, blank=True, related_name="users"
    )  # Optional department field
    position = models.ForeignKey(
        Position, on_delete=models.SET_NULL, null=True, blank=True, related_name="users"
    )  # Optional position field
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(
        max_length=10,
        choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')],
        blank=True
    )
    address = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_staff = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []
    
    objects = CustomUserManager()

    def __str__(self):
        role_str = f"{self.role} - {self.department.name}" if self.department else self.role
        return f"{self.phone_number} ({role_str})"


class User(CustomUser):  # Concrete implementation
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
