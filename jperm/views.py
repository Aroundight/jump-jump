# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db.models import Q
from django.http import HttpResponseBadRequest, HttpResponseNotAllowed
from paramiko import SSHException
from jperm.perm_api import *

#from juser.models import User, UserGroup
#from jasset.models import Asset, AssetGroup
#from jperm.models import PermRole, PermRule, PermSudo, PermPush
from jumpserver.models import Setting

from jperm.utils import gen_keys, trans_all
from jperm.ansible_api import MyTask
from jperm.perm_api import get_role_info, get_role_push_host
from jumpserver.api import my_render, get_object, CRYPTOR


# 设置PERM APP Log
from jumpserver.api import logger
#logger = set_log(LOG_LEVEL, filename='jumpserver_perm.log')


@require_role('admin')
def perm_role_list(request):
    """
    list role page
    """
    # 渲染数据
    header_title, path1, path2 = "系统用户", "系统用户管理", "查看系统用户"

    # 获取所有系统角色
    roles_list = PermRole.objects.all()
    role_id = request.GET.get('id')
    # TODO: 搜索和分页
    keyword = request.GET.get('search', '')
    if keyword:
        roles_list = roles_list.filter(Q(name=keyword))

    if role_id:
        roles_list = roles_list.filter(id=role_id)

    roles_list, p, roles, page_range, current_page, show_first, show_end = pages(roles_list, request)

    return my_render('jperm/perm_role_list.html', locals(), request)

@require_role('user')
def perm_role_get(request):
    return HttpResponse('www,root')
