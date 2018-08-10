import datetime
import hashlib

from django.conf import settings
from django.shortcuts import render, redirect
from django.shortcuts import HttpResponse

from bbsapp.forms import UserForm, RegisterForm
from bbsapp.models import UserInfo, ConfirmString


# user_list = [
#     {'id': 500, "user": "melan", "pwd": "123"},
#     {'id': 400, "user": 'selan', "pwd": "123"}
# ]

def helw(req):
    return HttpResponse('''
    <!DOCTYPE html>
    <html lang='en'>
    <head>
        <meta charset='UTF-8'>
        <title>HELLO</title>
    </head>
    <body>
        <h1 style="background-color: lightpink;color: deeppink">hello world</h1>
    </body>
    </html>
    ''')


# Create your views here.
def secret(request):
    # return HttpResponse('hello world！')
    # return render(request, 'index.html')
    if request.method == 'POST':
        username = request.POST.get('username', None)
        password = request.POST.get('passwd', None)
        UserInfo.objects.create(name=username, password=password)

    user_list = UserInfo.objects.all()
    print(user_list)

    return render(request, 'secret.html', {"data": user_list})


def home(request):
    pass
    return render(request, 'login/home.html')


def login(request):
    # if request.method == 'POST':
    #     username = request.POST.get('username',None)
    #     password = request.POST.get('password',None)
    #     message = '所有字段都得填写'
    #     if username and password:
    #         username = username.strip()
    #         try:
    #             user = UserInfo.objects.get(name=username)
    #             if user.password == password:
    #                 return redirect('/home/')
    #             else:
    #                 message = '密码错误'
    #         except:
    #             message = '用户名不存在'
    #     return render(request,'login/login.html',{"message":message})
    # return render(request, 'login/login.html')
    if request.session.get('is_login', None):
        return redirect('/home/')
    if request.method == 'POST':
        login_form = UserForm(request.POST)
        message = '请检查填写内容'
        if login_form.is_valid():
            username = login_form.cleaned_data['username']
            password = login_form.cleaned_data['password']
            try:
                user = UserInfo.objects.get(name=username)
                if not user.has_confirmed:
                    message = '用户还未进行邮件确认'
                    return render(request, 'login/login.html', locals())
                if user.password == hash_code(password):
                    request.session['is_login'] = True
                    request.session['user_id'] = user.id
                    request.session['user_name'] = user.name
                    return redirect('/home/')
                else:
                    message = '密码错误'
            except:
                message = '用户名不存在'

        return render(request, 'login/login.html', locals())

    login_form = UserForm()
    return render(request, 'login/login.html', locals())


def make_confirm_string(user):
    now = datetime.datetime.now().strftime('%Y-&m-%d %H:%M:%S')
    code = hash_code(user.name, now)
    ConfirmString.objects.create(code=code, user=user)
    return code


def send_email(email, code):
    from django.core.mail import EmailMultiAlternatives

    subject = '天外来客'
    text_content = '''欢迎来访\
                    如果看到此消息，说明你的邮箱服务器不提供HTML功能，请联系管理员'''
    html_content = '''
                    <p>你好哇！李银河<a href="http://{}/confirm/?code={}" target=blank>耿耿星河</a>，\
                    九天揽月</p>
                    <p>点击链接完成注册确认</p>
                    <p>此链接有效期{}天</p>
    '''.format('127.0.0.1:8000', code, settings.CONFIRM_DAYS)
    msg = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()


def register(request):
    if request.session.get('is_login', None):
        return redirect('/home/')
    if request.method == 'POST':
        register_form = RegisterForm(request.POST)
        message = '请检查填写内容'
        if register_form.is_valid():
            username = register_form.cleaned_data['username']
            password1 = register_form.cleaned_data['password']
            password2 = register_form.cleaned_data['password2']
            email = register_form.cleaned_data['email']
            sex = register_form.cleaned_data['sex']

            if password1 != password2:
                message = '两次密码不一样'
                return render(request, 'login/register.html', locals())
            else:
                same_name_user = UserInfo.objects.filter(name=username)
                if same_name_user:
                    message = '用户名已存在'
                    return render(request, 'login/register.html', locals())
                same_email_user = UserInfo.objects.filter(email=email)
                if same_email_user:
                    message = '该邮箱已注册'
                    return render(request, 'login/register.html', locals())

                new_user = UserInfo()
                new_user.name = username
                new_user.password = hash_code(password1)
                new_user.email = email
                new_user.sex = sex
                new_user.save()

                code = make_confirm_string(new_user)
                send_email(email, code)
                message = '请前往注册邮件进行确认'
                return render(request, 'login/confirm.html', locals())
    register_form = RegisterForm()
    return render(request, 'login/register.html', locals())


def logout(request):
    if not request.session.get('is_login', None):
        return redirect('/home/')
    request.session.flush()
    # 或者
    # del request.session['is_login']
    # del request.session['user_id']
    # del request.session['username']
    return redirect('/home/')


def hash_code(s, salt='bbsapp'):
    h = hashlib.sha256()
    s += salt
    h.update(s.encode())
    return h.hexdigest()


def user_confirm(request):
    code = request.GET.get('code', None)
    message = '+++++++++++'
    try:
        confirm = ConfirmString.objects.get(code=code)
    except:
        message = '无效的确认请求'
        return render(request, 'login/confirm.html', locals())
    c_time = confirm.c_time
    now = datetime.datetime.now()
    print(now,type(now))
    print(c_time,type(c_time))
    print(datetime.timedelta(settings.CONFIRM_DAYS),type(datetime.timedelta(settings.CONFIRM_DAYS)))
    print(type(c_time + datetime.timedelta(settings.CONFIRM_DAYS)))

    if now > (c_time + datetime.timedelta(settings.CONFIRM_DAYS)).replace(tzinfo=None):  # replace(tzinfo=None)  去掉时区
        confirm.user.delete()
        message = '验证码过期'
        return render(request, 'login/confirm.html', locals())
    else:
        confirm.user.has_confirmed = True
        confirm.user.save()
        confirm.delete()
        message = '感谢注册，请登录'
        return render(request, 'login/confirm.html', locals())
