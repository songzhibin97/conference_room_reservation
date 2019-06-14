from django.shortcuts import render
from django.shortcuts import render, redirect, HttpResponse
# 导入modelform组件 使用modelform完成登录
from django.forms import ModelForm
from app01.models import Userinfo
# 导入modelform插件 别名wid
from django.forms import widgets as wid
# 引入Django自带的验证工具
from django.contrib import auth
# 引入定义model类
from app01 import models
# 引入datetime
import datetime
import json


# Create your views here.
# modelform 用于校验用户输入是否规范
class Login(ModelForm):
    class Meta:
        model = Userinfo
        fields = ['username', 'password']
        error_messages = {
            "username": {'required': "用户名不能为空"},
            "password": {'required': '密码不能为空'}
        }
        widgets = {
            "username": wid.TextInput(attrs={'class': 'form-control'}),
            "password": wid.PasswordInput(attrs={'class': 'form-control'})
        }
        labels = {
            'username': "用户名",
            'password': "密码"
        }


# 处理登录函数
def login(request):
    if request.method == "POST":
        # 使用form组件做校验
        # login_obj = Login(request.POST)
        # if login_obj.is_valid():  # 校验成功  ps 使用modelfrom 验证有bug 无法正常登录 提示用户名注册
        username = request.POST.get("username")
        password = request.POST.get("password")
        user_obj = auth.authenticate(username=username, password=password)  # 验证用户密码是否正确
        if user_obj:  # 登录成功
            auth.login(request, user_obj)  # 登录成功后吧用户信息写入request session中
            return HttpResponse('登录成功')
        else:
            return HttpResponse('用户名或密码错误')

    login_obj = Login()
    return render(request, 'login.html', {"login_obj": login_obj})


# 处理查看会议室详情视图
def conference_room(request):
    if request.method == 'POST':
        # 获取ajax传来的数据 传来的数据是bytes类型 先解码后json使用
        data = json.loads(request.body.decode('utf-8'))
        try:  # 如果有删除数据 循环data['del']后取到room_id 同事在循环room_id 从data['del']['room_id']取到time_id 从predetermine表中取出相应数据删除
            if data["del"]:
                for room_list in data["del"]:
                    for time_list in data["del"][room_list]:
                        models.Predetermine.objects.filter(room=room_list, time_choice=time_list).delete()
            # 如果有增加数据 循环data['del']后取到room_id 同事在循环room_id 从data['del']['room_id']取到time_id 从predetermine表中取出相应数据删除
            if data['add']:
                for room_list in data['add']:
                    for time_list in data['add'][room_list]:
                        models.Predetermine.objects.create(room_id=room_list, time_choice=time_list,
                                                           date=datetime.datetime.now().date(),
                                                           user_id=request.user.pk)
            return HttpResponse('提交成功')
        except Exception as e:
            print(e)
            return HttpResponse("保存出错啦")
    else:
        date = datetime.datetime.now().date()  # 返回当前日期时间的日期部分
        get_date = request.POST.get("date", date)  # 如果用户查询指定的日期则使用用户指定的日期 如果为指定则使用当天的日期
        conference_room = models.ConferenceRoom.objects.all()  # 获取所有会议室
        time_list = models.Predetermine.choice_time  # 获取可以预定的所有时间段
        predetermine_obj = models.Predetermine.objects.filter(date=get_date)  # 已日期筛选所有预定信息对象
        html = ''  # 创建一个空字符串 用于后面直接添加
        for room in conference_room:  # 循环会议室列表 拿出所有会议室
            html += '<tr><td>{}({})</td>'.format(room.name, room.num)  # 将会议室名称以及容纳人数存放在已定义的html字符串中
            for time in time_list:
                flag = False  # 设置标记位 如果会议室已有人预定则为true
                for predetermine in predetermine_obj:  # 循环预定对象
                    if predetermine.room_id == room.pk and predetermine.time_choice == time[0]:  # 如果条件满足说明已经被预定
                        flag = True  # 获取标记位信息 跳出循环 而predetermine 的值选定用户的信息
                        break
                if flag:  # 如果标记位满足则在html加入预定用户信息
                    if predetermine.user.username == request.user.username:  # 如果预定用户是当前登录用户的话 显示的为绿底 class selectable 为可选定属性 用于前端实现js效果
                        html += '<td room_id={} time_id={} class= "current_user selectable">{}</td>'.format(room.pk,
                                                                                                            time[0],
                                                                                                            predetermine.user.username)
                    else:  # 如果预定用户不是当前登录用户的话 显示的为蓝底
                        html += '<td room_id={} time_id={} class= "uncuurrent_user unselectable">{}</td>'.format(
                            room.pk,
                            time[0],
                            predetermine.user.username)
                else:
                    html += '<td room_id={} time_id={} class="selectable"></td>'.format(room.pk, time[0])
        html += '</tr>'
        return render(request, 'list_conference_room.html',
                      {"html": html, 'time_list': time_list, 'get_date': get_date})
