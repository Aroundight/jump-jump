# coding: utf-8
# Author: Guanghongwei
# Email: ibuler@qq.com

# import random
# from Crypto.PublicKey import RSA
import uuid
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.db.models import Q
from juser.user_api import *
from jperm.perm_api import get_group_user_perm
import re
from ops_auth.auth import OpsAuthBackend

MAIL_FROM = EMAIL_HOST_USER


@require_role(role='super')
def group_list(request):
    """
    list user group
    用户组列表
    """
    header_title, path1, path2 = '查看用户组', '用户管理', '查看用户组'
    keyword = request.GET.get('search', '')
    user_group_list = UserGroup.objects.all().order_by('name')
    group_id = request.GET.get('id', '')

    if keyword:
        user_group_list = user_group_list.filter(Q(name__icontains=keyword) | Q(comment__icontains=keyword))

    if group_id:
        user_group_list = user_group_list.filter(id=int(group_id))

    user_group_list, p, user_groups, page_range, current_page, show_first, show_end = pages(user_group_list, request)
    return my_render('juser/group_list.html', locals(), request)


@require_role(role='super')
def user_list(request):
    user_role = {'SU': u'超级管理员', 'GA': u'组管理员', 'CU': u'普通用户'}
    header_title, path1, path2 = '查看用户', '用户管理', '用户列表'
    keyword = request.GET.get('keyword', '')
    gid = request.GET.get('gid', '')
    users_list = User.objects.all().order_by('username')

    if gid:
        user_group = UserGroup.objects.filter(id=gid)
        if user_group:
            user_group = user_group[0]
            users_list = user_group.user_set.all()

    if keyword:
        users_list = users_list.filter(Q(username__icontains=keyword) | Q(name__icontains=keyword)).order_by('username')

    users_list, p, users, page_range, current_page, show_first, show_end = pages(users_list, request)

    return my_render('juser/user_list.html', locals(), request)


@require_role(role='user')
def user_detail(request):
    header_title, path1, path2 = '用户详情', '用户管理', '用户详情'
    if request.session.get('role_id') == 0:
        user_id = request.user.id
    else:
        user_id = request.GET.get('id', '')

    user = OpsAuthBackend().get_user(user_id=user_id)
    if not user:
        return HttpResponseRedirect(reverse('user_list'))

    user_perm_info = get_group_user_perm(user)
    role_assets = user_perm_info.get('role')
    user_log_ten = Log.objects.filter(user=user.username).order_by('id')[0:10]
    user_log_last = Log.objects.filter(user=user.username).order_by('id')[0:50]
    user_log_last_num = len(user_log_last)

    return my_render('juser/user_detail.html', locals(), request)


@require_role('admin')
def send_mail_retry(request):
    uuid_r = request.GET.get('uuid', '1')
    user = get_object(User, uuid=uuid_r)
    msg = u"""
    跳板机地址： %s
    用户名：%s
    重设密码：%s/juser/password/forget/
    请登录web点击个人信息页面重新生成ssh密钥
    """ % (URL, user.username, URL)

    try:
        send_mail(u'邮件重发', msg, MAIL_FROM, [user.email], fail_silently=False)
    except IndexError:
        return Http404
    return HttpResponse('发送成功')


@require_role(role='user')
def regen_ssh_key(request):
    uuid_r = request.GET.get('uuid', '')
    user = get_object(User, uuid=uuid_r)
    if not user:
        return HttpResponse('没有该用户')

    username = user.username
    ssh_key_pass = PyCrypt.gen_rand_pass(16)
    gen_ssh_key(username, ssh_key_pass)
    return HttpResponse('ssh密钥已生成，密码为 %s, 请到下载页面下载' % ssh_key_pass)


@require_role(role='user')
def down_key(request):
    if is_role_request(request, 'super'):
        uuid_r = request.GET.get('uuid', '')
    else:
        uuid_r = request.user.uuid
    if uuid_r:
        user = get_object(User, uuid=uuid_r)
        if user:
            username = user.username
            private_key_file = os.path.join(KEY_DIR, 'user', username+'.pem')
            print private_key_file
            if os.path.isfile(private_key_file):
                f = open(private_key_file)
                data = f.read()
                f.close()
                response = HttpResponse(data, content_type='application/octet-stream')
                response['Content-Disposition'] = 'attachment; filename=%s' % os.path.basename(private_key_file)
                if request.user.role == 'CU':
                    os.unlink(private_key_file)
                return response
    return HttpResponse('No Key File. Contact Admin.')

