#from juser.models import User
#from jasset.models import Asset
from jumpserver.api import *
from ops_auth.auth import OpsAuthBackend
from jperm.perm_api import Rule,Asset


def name_proc(request):
    user_id = request.user.id
    role_id = {'SU': 2, 'GA': 1, 'CU': 0}.get(request.user.web_role, 0)
    # role_id = 'SU'
    asset = Rule(request.user)
    host_total_num = len(asset.assets)
    host_active_num = len(asset.assets)
    asset_group_total_num = len(asset.asset_group)
    request.session.set_expiry(3600)
    request.session.role_id = role_id

    info_dic = {'session_user_id': user_id,
                'session_role_id': role_id,
                'host_total_num': host_total_num,
                'host_active_num': host_active_num,
                'asset_group_total_num' : asset_group_total_num,
                }

    return info_dic

