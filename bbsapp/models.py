from django.db import models


# Create your models here.

class UserInfo(models.Model):
    gender = (
        ('male', '男'),
        ('female', '女'),
        ('other', '保密')
    )

    name = models.CharField(max_length=128, unique=True)
    password = models.CharField(max_length=128)
    email = models.EmailField(unique=True)
    sex = models.CharField(max_length=32, choices=gender, default='保密')
    c_time = models.DateTimeField(auto_now_add=True)
    has_confirmed = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-c_time']
        verbose_name = '用户'
        verbose_name_plural = '用户'

class ConfirmString(models.Model):
    code = models.CharField(max_length=128)
    user = models.OneToOneField('UserInfo',on_delete=False,to_field=None)
    c_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.name+'：'+self.code

    class Meta:
        ordering = ['-c_time']
        verbose_name = '验证码'
        verbose_name_plural = '验证码'