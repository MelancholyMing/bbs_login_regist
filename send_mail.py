import os
from django.core.mail import send_mail

os.environ['DJANGO_SETTINGS_MODULE'] = 'bbs.settings'

if __name__ == '__main__':
    email_title = 'hello,dear'
    email_content = 'i miss you'
    # email_from = 'xxx@sina.com'
    email_from = 'xxx@qq.com'
    email = ['xxx@sina.com']
    # email = ['xxx@qq.com']
    send_mail(email_title, email_content, email_from, email)
    # send_mail(
    #     'hello,dear',
    #     'hello you',
    #     'xxx@sina.com',
    #     ['xxx@qq.com']
    # )
