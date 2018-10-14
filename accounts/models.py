from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.core.validators import RegexValidator
from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)
from .utils import code_generator

USERNAME_REGEX="^[A-Za-z0-9.+-]*$"

#this is our user model manager
class MyUserManager(BaseUserManager):
    def create_user(self, email, username, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            username=username,
            email=self.normalize_email(email)
            #date_of_birth=date_of_birth,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email,
            username,
            password=password,
            #date_of_birth=date_of_birth,
        )
        user.is_admin = True
        user.is_staff=True
        user.save(using=self._db)
        return user



#this is our user model
class MyUser(AbstractBaseUser):
    username=models.CharField(max_length=120,unique=True,validators=[RegexValidator(regex=USERNAME_REGEX,message="Username must be alphanumeric or contain . @ + -",code="invalid_username")])
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    #date_of_birth = models.DateField()
    zipcode=models.CharField(max_length=50,default="110030")
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    objects = MyUserManager()

    #makes username defined above as the username field
    USERNAME_FIELD = 'username'
    #makes email compulsory
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True
    def get_short_name(self):
        return self.email

    #if the user can change in django admin
    # @property
    # def is_staff(self):
    #     "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        # return self.is_admin


#extending our user model
class Profile(models.Model):
    user=models.OneToOneField(settings.AUTH_USER_MODEL)
    city=models.CharField(max_length=150,null=True,blank=True)

    def __str__(self):
        return str(self.user.username)



def post_save_user_model_receiver(sender,instance,created,*args,**kwargs):
# #     #this is for user model and not for profile
    if created:
        try:
            Profile.objects.create(user=instance)
            Activation.objects.create(user=instance)
        except:
            pass


post_save.connect(post_save_user_model_receiver,sender=settings.AUTH_USER_MODEL)

class Activation(models.Model):
    user=models.ForeignKey(settings.AUTH_USER_MODEL)
    key=models.CharField(max_length=120)
    expired=models.BooleanField(default=False)

    def save(self,*args,**kwargs):
        self.key=code_generator()
        super(Activation,self).save(*args,**kwargs)

def post_save_activation_receiver(sender,instance,created,*args,**kwargs):
# #     #this is for user model and not for profile
    if created:
        print("Email sent")
        print(instance.key)


post_save.connect(post_save_activation_receiver,sender=Activation)