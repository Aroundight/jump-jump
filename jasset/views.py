## coding:utf-8

#from django.db.models import Q
#from jasset.asset_api import *
from jumpserver.api import require_role,pages, my_render
#from jumpserver.models import Setting
#from jasset.forms import AssetForm, IdcForm
#from jasset.models import Asset, IDC, AssetGroup, ASSET_TYPE, ASSET_STATUS
from jperm.perm_api import get_group_asset_perm, get_group_user_perm
from jperm.perm_api import Asset,AssetGroup,Rule
from ops_auth.auth import OpsAuthBackend

@require_role('admin')
def group_list(request):
    """
    list asset group
    列出资产组
    """
    header_title, path1, path2 = u'查看资产组', u'资产管理', u'查看资产组'
    keyword = request.GET.get('keyword', '')
    user_assets = Rule(request.user)
    asset_group_list = user_assets.asset_group
    group_id = request.GET.get('id')
    if group_id:
        group_id = int(group_id)
        asset_group_list = [x for x in user_assets.asset_group if x.id == group_id ]
    if keyword:
        asset_group_list = [x for x in user_assets.asset_group if keyword in x.name]

    asset_group_list, p, asset_groups, page_range, current_page, show_first, show_end = pages(asset_group_list, request)
    return my_render('jasset/group_list.html', locals(), request)

@require_role('user')
def asset_list(request):
    """
    asset list view
    """
    user_assets = Rule(request.user)
    header_title, path1, path2 = u'查看资产', u'资产管理', u'查看资产'
    username = request.user.username
    user_perm = request.session['role_id']
    idc_all = []
    asset_group_all = user_assets.asset_group
    asset_types = "server"
    asset_status = "active"
    idc_name = request.GET.get('idc', '')
    group_name = request.GET.get('group', '')
    asset_type = request.GET.get('asset_type', '')
    status = request.GET.get('status', '')
    keyword = request.GET.get('keyword', '')
    export = request.GET.get("export", False)
    group_id = request.GET.get("group_id", '')
    idc_id = request.GET.get("idc_id", '')
    asset_id_all = request.GET.getlist("id", '')
    asset_find = user_assets.assets
    if group_id:
        group_id = int(group_id)
        for x in user_assets.asset_group:
            if x.id == group_id:
                asset_find = x.asset_set 
    if idc_id:
        pass
    if idc_name:
        asset_find = asset_find.filter(idc__name__contains=idc_name)

    if group_name:
        for x in user_assets.asset_group:
            if x.name == group_name:
                asset_find = x.asset_set

    if asset_type:
        asset_find = asset_find.filter(asset_type__contains=asset_type)

    if status:
        asset_find = asset_find.filter(status__contains=status)

    if keyword:
        asset_find = [asset for asset in asset_find if keyword in asset.ip or keyword in asset.hostname or keyword in asset.role or keyword in asset.comment or keyword in asset.group ]
    if export:
        if asset_id_all:
            asset_find = []
            for asset in user.assets:
                if asset:
                    asset_find.append(asset)
        s = write_excel(asset_find)
        if s[0]:
            file_name = s[1]
        smg = u'excel文件已生成，请点击下载!'
        return my_render('jasset/asset_excel_download.html', locals(), request)
    assets_list, p, assets, page_range, current_page, show_first, show_end = pages(asset_find, request)
    if user_perm != 0:
        return my_render('jasset/asset_list.html', locals(), request)
    else:
        return my_render('jasset/asset_cu_list.html', locals(), request)


#@require_role('admin')
#def asset_edit_batch(request):
    #af = AssetForm()
    #name = request.user.username
    #asset_group_all = AssetGroup.objects.all()

    #if request.method == 'POST':
        #env = request.POST.get('env', '')
        #idc_id = request.POST.get('idc', '')
        #port = request.POST.get('port', '')
        #use_default_auth = request.POST.get('use_default_auth', '')
        #username = request.POST.get('username', '')
        #password = request.POST.get('password', '')
        #group = request.POST.getlist('group', [])
        #cabinet = request.POST.get('cabinet', '')
        #comment = request.POST.get('comment', '')
        #asset_id_all = unicode(request.GET.get('asset_id_all', ''))
        #asset_id_all = asset_id_all.split(',')
        #for asset_id in asset_id_all:
            #alert_list = []
            #asset = get_object(Asset, id=asset_id)
            #if asset:
                #if env:
                    #if asset.env != env:
                        #asset.env = env
                        #alert_list.append([u'运行环境', asset.env, env])
                #if idc_id:
                    #idc = get_object(IDC, id=idc_id)
                    #name_old = asset.idc.name if asset.idc else u''
                    #if idc and idc.name != name_old:
                        #asset.idc = idc
                        #alert_list.append([u'机房', name_old, idc.name])
                #if port:
                    #if unicode(asset.port) != port:
                        #asset.port = port
                        #alert_list.append([u'端口号', asset.port, port])

                #if use_default_auth:
                    #if use_default_auth == 'default':
                        #asset.use_default_auth = 1
                        #asset.username = ''
                        #asset.password = ''
                        #alert_list.append([u'使用默认管理账号', asset.use_default_auth, u'默认'])
                    #elif use_default_auth == 'user_passwd':
                        #asset.use_default_auth = 0
                        #asset.username = username
                        #password_encode = CRYPTOR.encrypt(password)
                        #asset.password = password_encode
                        #alert_list.append([u'使用默认管理账号', asset.use_default_auth, username])
                #if group:
                    #group_new, group_old, group_new_name, group_old_name = [], asset.group.all(), [], []
                    #for group_id in group:
                        #g = get_object(AssetGroup, id=group_id)
                        #if g:
                            #group_new.append(g)
                    #if not set(group_new) < set(group_old):
                        #group_instance = list(set(group_new) | set(group_old))
                        #for g in group_instance:
                            #group_new_name.append(g.name)
                        #for g in group_old:
                            #group_old_name.append(g.name)
                        #asset.group = group_instance
                        #alert_list.append([u'主机组', ','.join(group_old_name), ','.join(group_new_name)])
                #if cabinet:
                    #if asset.cabinet != cabinet:
                        #asset.cabinet = cabinet
                        #alert_list.append([u'机柜号', asset.cabinet, cabinet])
                #if comment:
                    #if asset.comment != comment:
                        #asset.comment = comment
                        #alert_list.append([u'备注', asset.comment, comment])
                #asset.save()

            #if alert_list:
                #recode_name = unicode(name) + ' - ' + u'批量'
                #AssetRecord.objects.create(asset=asset, username=recode_name, content=alert_list)
        #return my_render('jasset/asset_update_status.html', locals(), request)

    #return my_render('jasset/asset_edit_batch.html', locals(), request)


@require_role('admin')
def asset_detail(request):
    """
    Asset detail view
    """
    header_title, path1, path2 = u'主机详细信息', u'资产管理', u'主机详情'
    asset_id = request.GET.get('id', '')
    asset = get_object(Asset, id=asset_id)
    perm_info = get_group_asset_perm(asset)
    log = Log.objects.filter(host=asset.hostname)
    if perm_info:
        user_perm = []
        for perm, value in perm_info.items():
            if perm == 'user':
                for user, role_dic in value.items():
                    user_perm.append([user, role_dic.get('role', '')])
            elif perm == 'user_group' or perm == 'rule':
                user_group_perm = value
    print perm_info

    asset_record = AssetRecord.objects.filter(asset=asset).order_by('-alert_time')

    return my_render('jasset/asset_detail.html', locals(), request)


#@require_role('admin')
#def idc_list(request):
    #"""
    #IDC list view
    #"""
    #header_title, path1, path2 = u'查看IDC', u'资产管理', u'查看IDC'
    #posts = IDC.objects.all()
    #keyword = request.GET.get('keyword', '')
    #if keyword:
        #posts = IDC.objects.filter(Q(name__contains=keyword) | Q(comment__contains=keyword))
    #else:
        #posts = IDC.objects.exclude(name='ALL').order_by('id')
    #contact_list, p, contacts, page_range, current_page, show_first, show_end = pages(posts, request)
    #return my_render('jasset/idc_list.html', locals(), request)
