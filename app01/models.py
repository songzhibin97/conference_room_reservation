from django.db import models

# Create your models here.
# 引入扩展自带user表的原类
from django.contrib.auth.models import AbstractUser


# 扩展自带的user表
class Userinfo(AbstractUser):
    phone = models.CharField(max_length=32)  # 扩充自带的user表电话选项

    def __str__(self):
        return self.username


# 创建会议室表
class ConferenceRoom(models.Model):
    name = models.CharField(max_length=32)  # 会议室名称
    num = models.IntegerField()  # 会议室容最大纳人数

    def __str__(self):
        return self.name


# 创建会议室预定表
class Predetermine(models.Model):
    user = models.ForeignKey(to=Userinfo)  # 预定用户 与userinfo表外键关联
    room = models.ForeignKey(to=ConferenceRoom)  # 预定会议室与ConferenceRoom外键关联
    date = models.DateField()  # 预定日期
    choice_time = (  # 用于预定时间 IntegerField中choice属性展现select选项
        (1, '8:00'),
        (2, '9:00'),
        (3, '10:00'),
        (4, '11:00'),
        (5, '12:00'),
        (6, '13:00'),
        (7, '14:00'),
        (8, '15:00'),
        (9, '16:00'),
        (10, '17:00'),
        (11, '18:00'),
        (12, '19:00'),
        (13, '20:00'),
        (14, '21:00'),
        (15, '22:00')
    )
    time_choice = models.IntegerField(choices=choice_time)  # 用于选择某时间段的会议室

    class Meta:
        unique_together = (  # 设置 会议室 时期 时间段 联合唯一
            ('room', 'date', 'time_choice')
        )

    def __str__(self):
        return str(self.user.username) + '预定了' + str(self.room.name)
