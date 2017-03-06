# -*- coding:utf-8 -*-
from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)
import hashlib
# Create your models here.
# 继承管理类
class MyUserManager(BaseUserManager):
    # 创建用户
    def create_user(self, email, username, password, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        user = self.model(
            email = self.normalize_email(email),
            username = username,
            **extra_fields
        )
        user.set_password(password)    #自动添加一个password字段，并加密密码
        user.save(using=self._db)
        return user
    # 创建超级管理员
    def create_superuser(self, email, username, password, **extra_fields):
        user = self.create_user(
            email,
            username=username,
            password=password,
            **extra_fields
        )
        user.is_admin = True
        user.save(using=self._db)
        return user
class User(AbstractBaseUser):
    username = models.CharField(max_length=50, unique=True, verbose_name=u'用户名')
    email = models.EmailField(max_length=150)
    register_time = models.DateTimeField(verbose_name=u'注册时间',null=True)
    last_login_time = models.DateTimeField(verbose_name=u'最后登录时间',null=True)
    last_login_ip = models.GenericIPAddressField(verbose_name=u'最后登录IP',null=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=True)

    # 自动添加一个last_login字段，最后登录时间

    objects = MyUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        db_table = "user"

class AssetInfo(models.Model):
    public_ip = models.CharField(max_length=100, verbose_name=u'公网IP')
    intranet_ip = models.CharField(max_length=100, verbose_name=u'内网IP')
    host_name = models.CharField(max_length=50, verbose_name=u'主机名')
    os = models.CharField(max_length=50, verbose_name=u'操作系统')
    cpu_model = models.CharField(max_length=100, verbose_name=u'CPU型号')
    cpu_thread_number = models.PositiveIntegerField(verbose_name=u'CPU线程数')
    memory = models.CharField(max_length=50, verbose_name=u'内存')
    disk = models.TextField(verbose_name=u'磁盘')
    minion_id = models.CharField(max_length=50, null=True)
    class Meta:
        db_table = "asset_info"

class Charts(models.Model):
    insert_time = models.CharField(max_length=50)
    pv_number = models.IntegerField()
    uv_number = models.IntegerField()
    class Meta:
        db_table = "web_access_count"

# class MinionInfo(models.Model):
#     asset_info= models.ManyToManyField(AssetInfo)
#     key_status = models.CharField(max_length=50)
#     port = models.IntegerField()
#     username = models.CharField(max_length=50)
#     password = models.CharField(max_length=100)
