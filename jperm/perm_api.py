# coding: utf-8

from django.db.models.query import QuerySet
from jumpserver.api import *
import uuid
import re

from jumpserver.models import Setting
#from jperm.models import PermRole, PermPush, PermRule
from ops_auth.HttpClient import HttpClient
from django.conf import settings
from jumpserver.api import logger

class PermRole(object):
    pass

class Asset(object):
    def __init__(self):
        self._ip = None
        self._hostname = None
        self._comment = None
        self.port = 22
        self._group = None
        self._role = None
        
    @property
    def ip(self):
        return self._ip
    @ip.setter
    def ip(self,value):
        self._ip = value
    
    @property
    def role(self):
        return self._role
    @role.setter
    def role(self,value):
        if isinstance(value,list):
            self._role = value
        else:
            raise ValueError,"need a list"
    
    @property
    def hostname(self):
        return self._hostname
    @hostname.setter
    def hostname(self,value):
        self._hostname = value   
    
    @property
    def comment(self):
        return self._comment
    @comment.setter
    def comment(self,value):
        self._comment = value
    
    @property
    def group(self):
        return self._group
    @group.setter
    def group(self,value):
        self._group = value    
    
    def __cmp__(self,s):
        if s.ip == self.ip:
            return 0
        elif self.ip > s.ip:
            return 1
        else:
            return -1

class AssetGroup(object):
    def __init__(self):
        self._id = None
        self._name = None
        self._comment = None
        self._asset_count = 0
        self._asset_set = []
    @property
    def id(self):
        return self._id
    @id.setter
    def id(self,value):
        self._id = value
    
    @property
    def name(self):
        return self._name
    @name.setter
    def name(self,value):
        self._name = value   
    
    @property
    def comment(self):
        return self._comment
    @comment.setter
    def comment(self,value):
        self._comment = value
    
    @property
    def asset_set(self):
        return self._asset_set
    @asset_set.setter
    def asset_set(self,value):
        self._asset_set = value
    @property
    def asset_count(self):
        return self._asset_count
    @asset_count.setter
    def asset_count(self,value):
        self._asset_count = value
    
    
    def __cmp__(self,s):
        if s.id == self.id:
            return 0
        elif self.id > s.id:
            return 1
        else:
            return -1
    def __str__(self):
        return self.name

class Rule(object):
    def __init__(self,user):
        self._asset_groups = []
        self._assets = []
        self._user = user.username
        self._user_obj = user
        self.asset_in_group={}
        self.get_all_asset_info()
    
    @property
    def asset_group(self):
        return self._asset_groups
    @asset_group.setter
    def asset_group(self,value):
        self._asset_groups = value
    
    @property
    def assets(self):
        return self._assets
    @assets.setter
    def assets(self,value):
        self._assets = value
    
    def get_all_asset_info(self,group=0):
        ret_t = []
        hc = HttpClient(ret_type="json")
        url = "%s?key=%s&user=%s"%(settings.OPS_HOST_IN_GROUP_URL, settings.OPS_KEY, self._user)
        logger.info("query url: %s",url)
        ret = hc.get(url)
        logger.info("query data is: %s",ret["data"])
        asset_groups = {}
        if ret and ret["statusCode"] == 200:
            _data = ret["data"]
            display_id  = 1
            for ip in _data:
                a = Asset()
                a.ip = ip
                a.hostname = _data[ip]["name"]
                a.comment = ""
                a.group = _data[ip]["group"]
                #####get data from ops api
                a.role = _data[ip]["user"]
                if a.group in asset_groups:
                    asset_groups[a.group].asset_set.append(a)
                else:
                    g = AssetGroup()
                    g.name = _data[ip]["group"]
                    g.id = display_id
                    g.comment = ""
                    g.asset_set = [a]
                    display_id += 1
                    asset_groups[a.group] = g
                    self.asset_group.append(g)
                self.assets.append(a)
            for group in self.asset_group:
                group.asset_count = len(group.asset_set)
    
    #def get_asset_rule(self):        
        #try:
            #hc = HttpClient(ret_type="json")
            #url = "%s?user=%s&key=%s"%(settings.OPS_USER_GROUP_URL, self._user_obj.username, settings.OPS_KEY)
            #ret = hc.get(url)
            #if ret["statusCode"] == 200:
                #self.app_id_map=dict([(rcd["name"],rcd["id"]) for rcd in ret["data"]])
                #display_id = 1
                #for _group in sorted(self.app_id_map):
                    #a=AssetGroup()
                    #a.id = self.app_id_map[_group]
                    #a.display_id = display_id
                    #a.name = _group
                    #a.comment = ""
                    
                    #t_assets = self.get_app_host_list(_group)
                    #if t_assets:
                        #self._assets.extend(t_assets)
                        #a.asset_set = t_assets
                        #a.asset_count = len(t_assets)
                        #self._asset_groups.update({a.id:a})
                        #self.asset_in_group.update({_group:t_assets})
                        #display_id += 1 
           
        #except Exception,e:
            #print(e)
            #import traceback
            #traceback.print_exc(e)
            #self.asset_group=[]


def get_group_user_perm(ob):
    """
    ob为用户或用户组
    获取用户、用户组授权的资产、资产组
    return:
    {’asset_group': {
            asset_group1: {'asset': [], 'role': [role1, role2], 'rule': [rule1, rule2]},
            asset_group2: {'asset: [], 'role': [role1, role2], 'rule': [rule1, rule2]},
            }
    'asset':{
            asset1: {'role': [role1, role2], 'rule': [rule1, rule2]},
            asset2: {'role': [role1, role2], 'rule': [rule1, rule2]},
            }
    },
    'rule':[rule1, rule2,]
    'role': {role1: {'asset': []}, 'asset_group': []}, role2: {}},
    }
    """
    perm = {}
    if isinstance(ob, User):
        rule = Rule(ob)
    perm = {"asset_group":rule.asset_group,
            "asset" : rule.assets,
            "rule":rule,
            }
    
    return perm


def get_group_asset_perm(ob):
    """
    ob为资产或资产组
    获取资产，资产组授权的用户，用户组
    return:
    {’user_group': {
            user_group1: {'user': [], 'role': [role1, role2], 'rule': [rule1, rule2]},
            user_group2: {'user: [], 'role': [role1, role2], 'rule': [rule1, rule2]},
            }
    'user':{
            user1: {'role': [role1, role2], 'rule': [rule1, rule2]},
            user2: {'role': [role1, role2], 'rule': [rule1, rule2]},
            }
        ]},
    'rule':[rule1, rule2,],
    }
    """
    perm = {}
    if isinstance(ob, Asset):
        rule_all = PermRule.objects.filter(asset=ob)
    elif isinstance(ob, AssetGroup):
        rule_all = PermRule.objects.filter(asset_group=ob)
    else:
        rule_all = []

    perm['rule'] = rule_all
    perm_user_group = perm['user_group'] = {}
    perm_user = perm['user'] = {}
    for rule in rule_all:
        user_groups = rule.user_group.all()
        users = rule.user.all()
        # 获取一个规则资产的用户
        for user in users:
            if perm_user.get(user):
                perm_user[user].get('role', set()).update(set(rule.role.all()))
                perm_user[user].get('rule', set()).add(rule)
            else:
                perm_user[user] = {'role': set(rule.role.all()), 'rule': set([rule])}

        # 获取一个规则资产授权的用户组
        for user_group in user_groups:
            user_group_users = user_group.user_set.all()
            if perm_user_group.get(user_group):
                perm_user_group[user_group].get('role', set()).update(set(rule.role.all()))
                perm_user_group[user_group].get('rule', set()).add(rule)
            else:
                perm_user_group[user_group] = {'role': set(rule.role.all()), 'rule': set([rule]),
                                               'user': user_group_users}

            # 将用户组中的资产添加到用户授权中
            for user in user_group_users:
                if perm_user.get(user):
                    perm_user[user].get('role', set()).update(perm_user_group[user_group].get('role', set()))
                    perm_user[user].get('rule', set()).update(perm_user_group[user_group].get('rule', set()))
                else:
                    perm_user[user] = {'role': perm_user_group[user_group].get('role', set()),
                                       'rule': perm_user_group[user_group].get('rule', set())}
    return perm


def user_have_perm(user, asset):
    user_perm_all = get_group_user_perm(user)
    user_assets = user_perm_all.get('asset').keys()
    if asset in user_assets:
        return user_perm_all.get('asset').get(asset).get('role')
    else:
        return []


def gen_resource(ob, perm=None):
    """
    ob为用户或资产列表或资产queryset, 如果同时输入用户和{'role': role1, 'asset': []}，则获取用户在这些资产上的信息
    生成MyInventory需要的 resource文件
    """
    res = []
    if isinstance(ob, dict):
        role = ob.get('role')
        asset_r = ob.get('asset')
        user = ob.get('user')
        if not perm:
            perm = get_group_user_perm(user)

        if role:
            roles = perm.get('role', {}).keys()  # 获取用户所有授权角色
            if role not in roles:
                return {}

            role_assets_all = perm.get('role').get(role).get('asset')  # 获取用户该角色所有授权主机
            assets = set(role_assets_all) & set(asset_r)  # 获取用户提交中合法的主机

            for asset in assets:
                asset_info = get_asset_info(asset)
                role_key = get_role_key(user, role)
                info = {'hostname': asset.hostname,
                        'ip': asset.ip,
                        'port': asset_info.get('port', 22),
                        'ansible_ssh_private_key_file': role_key,
                        'username': role.name,
                        # 'password': CRYPTOR.decrypt(role.password)
                       }

                if os.path.isfile(role_key):
                    info['ssh_key'] = role_key

                res.append(info)
        else:
            for asset, asset_info in perm.get('asset').items():
                if asset not in asset_r:
                    continue
                asset_info = get_asset_info(asset)
                try:
                    role = sorted(list(perm.get('asset').get(asset).get('role')))[0]
                except IndexError:
                    continue

                role_key = get_role_key(user, role)
                info = {'hostname': asset.hostname,
                        'ip': asset.ip,
                        'port': asset_info.get('port', 22),
                        'username': role.name,
                        'password': CRYPTOR.decrypt(role.password),
                        }
                if os.path.isfile(role_key):
                    info['ssh_key'] = role_key

                res.append(info)

    elif isinstance(ob, User):
        if not perm:
            perm = get_group_user_perm(ob)

        for asset, asset_info in perm.get('asset').items():
            asset_info = get_asset_info(asset)
            info = {'hostname': asset.hostname, 'ip': asset.ip, 'port': asset_info.get('port', 22)}
            try:
                role = sorted(list(perm.get('asset').get(asset).get('role')))[0]
            except IndexError:
                continue
            info['username'] = role.name
            info['password'] = CRYPTOR.decrypt(role.password)

            role_key = get_role_key(ob, role)
            if os.path.isfile(role_key):
                    info['ssh_key'] = role_key
            res.append(info)

    elif isinstance(ob, (list, QuerySet)):
        for asset in ob:
            info = get_asset_info(asset)
            res.append(info)
    logger.debug('生成res: %s' % res)
    return res


def get_object_list(model, id_list):
    """根据id列表获取对象列表"""
    object_list = []
    for object_id in id_list:
        if object_id:
            object_list.extend(model.objects.filter(id=int(object_id)))

    return object_list


def get_role_info(role_id, type="all"):
    """
    获取role对应的一些信息
    :return: 返回值 均为对象列表
    """
    # 获取role对应的授权规则
    role_obj = PermRole.objects.get(id=role_id)
    rule_push_obj = role_obj.perm_rule.all()
    # 获取role 对应的用户 和 用户组
    # 获取role 对应的主机 和主机组
    users_obj = []
    assets_obj = []
    user_groups_obj = []
    asset_groups_obj = []
    for push in rule_push_obj:
        for user in push.user.all():
            users_obj.append(user)
        for asset in push.asset.all():
            assets_obj.append(asset)
        for user_group in push.user_group.all():
            user_groups_obj.append(user_group)
        for asset_group in push.asset_group.all():
            asset_groups_obj.append(asset_group)

    if type == "all":
        return {"rules": set(rule_push_obj),
                "users": set(users_obj),
                "user_groups": set(user_groups_obj),
                "assets": set(assets_obj),
                "asset_groups": set(asset_groups_obj),
                }

    elif type == "rule":
        return set(rule_push_obj)
    elif type == "user":
        return set(users_obj)
    elif type == "user_group":
        return set(user_groups_obj)
    elif type == "asset":
        return set(assets_obj)
    elif type == "asset_group":
        return set(asset_groups_obj)
    else:
        return u"不支持的查询"


def get_role_push_host(role):
    """
    asset_pushed: {'success': push.success, 'key': push.is_public_key, 'password': push.is_password,
                   'result': push.result}
    asset_no_push: set(asset1, asset2)
    """
    # 计算该role 所有push记录 总共推送的主机
    pushs = PermPush.objects.filter(role=role)
    asset_all = Asset.objects.all()
    asset_pushed = {}
    for push in pushs:
        asset_pushed[push.asset] = {'success': push.success, 'key': push.is_public_key, 'password': push.is_password,
                                    'result': push.result}
    asset_no_push = set(asset_all) - set(asset_pushed.keys())
    return asset_pushed, asset_no_push


if __name__ == "__main__":
    print get_role_info(1)

