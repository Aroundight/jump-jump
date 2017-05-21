import logging
from HttpClient import HttpClient
from HttpClient import urllib
import json
from django.conf import settings
logger = logging.getLogger(__name__)

class OpsAuthBackend: 
    '''
    ops auth backend
    '''

    def authenticate(self, username=None, password=None, **kwargs):
        '''
        return a user object
        a user object moust have property:
            username = ""
            password = ""
            email = ""
            first_name = ""
            last_name =""
            is_active = True
            is_superuser = False
            method:
                  is_authenticated
        '''

        if bool(password) or self.settings.PERMIT_EMPTY_PASSWORD:
            ops_user = User(self,username=username.strip())
            user = ops_user.authenticate(password)
        else:
            logger.debug('Rejecting empty password for %s' % username)
            user = None
        self.user = user

        return user
    
    def get_user(self, user_id):
        try:
            hc=HttpClient(ret_type="json")
            url = "%s?user=%s&key=%s"%(settings.OPS_USER_INFO_URL,user_id,settings.OPS_KEY)
            ret = hc.get(url)
            if ret["statusCode"] == 200 and ret["data"] and ret["data"]["status"] == "00":
                ret = ret["data"]["data"]
                user = User(backend=self, username=ret["loginname"])
                user.last_name = ret["usernme"]
                user.email = "%s@ofo.so"%ret["loginname"]
                user.is_active = True
                if ret["privilege"] == 1:
                    user.is_super = True
                    user.role = "root"
                    user.web_role = "SU"
                else:
                    user.is_super = False
                    user.role = "www"
                    user.web_role = "U"
                user.mobile = ret["mobile"]
                user.group = ret["usergroup"]
                user._is_authenticated = True
                return user
            return None
        except User.DoesNotExist:
            return None

class OpsUserGroups(object):
    """
    Represents the set of groups that a user belongs to.
    """
    def __init__(self, user):
        self._user = user
        self._group_type = None
        self._group_infos = None
        self._group_names = None

    def get_group_names(self):
        """
        Returns the set of Django group names that this user belongs to by
        virtue of LDAP group memberships.
        """
        if self._group_names is None:
            self._load_cached_attr("_group_names")

        if self._group_names is None:
            group_infos = self._get_group_infos()
            self._group_names = set(
                self._group_type.group_name_from_info(group_info)
                for group_info in group_infos
            )
            self._cache_attr("_group_names")

        return self._group_names

    def is_member_of(self, group_dn):
        """
        Returns true if our user is a member of the given group.
        """
        is_member = None

        # Normalize the DN
        group_dn = group_dn.lower()

        # If we have self._group_dns, we'll use it. Otherwise, we'll try to
        # avoid the cost of loading it.
        if self._group_dns is None:
            is_member = self._group_type.is_member(self._ldap_user, group_dn)

        if is_member is None:
            is_member = (group_dn in self.get_group_dns())

        logger.debug("%s is%sa member of %s", self._ldap_user.dn,
                     is_member and " " or " not ", group_dn)

        return is_member

    def _get_group_infos(self):
        """
        Returns a (cached) list of group_info structures for the groups that our
        user is a member of.
        """
        if self._group_infos is None:
            self._group_infos = self._group_type.user_groups(self._ldap_user,
                                                             self._group_search)

        return self._group_infos


class User(object):
    class DoesNotExist(Exception):
        pass
    class AuthenticationFailed(Exception):
        pass    
    def __init__(self,backend = None, username = None):
        self.backend = backend
        self._username = username
        self._email = None
        self._is_active = True
        self._first_name = None
        self._last_name = None
        self._is_superuser = None
        self._is_authenticated = False
        self._role = None
        self._mobile = None
        self._id = username
        self._web_role = None

    
    def _check_passwd(self, password):
        """
        Binds to the LDAP server with the user's DN and password. Raises
        AuthenticationFailed on failure.
        """
        self._user_attrs = ["username","cn","email","tel","is_active"]
        hc = HttpClient()
        hc.headers.pop("Content-Type")
        url = settings.OPS_USER_AUTH_URL
        data=urllib.urlencode({"user":self._username,"passwd":password,"key":settings.OPS_KEY})
        ret = hc.post(url,data)
        
        try:
            ret = json.loads(ret)
            if ret["statusCode"] == 200 and ret["data"]["login"] == 1:
                self.pk = ret["data"]["loginname"]
                self.id = self.pk
                if ret["data"]["privilege"] == 1:
                    self.is_super = True
                    self.role = "root"
                    self.web_role = "SU"
                else:
                    self.is_super = False
                    self.role = "rd"
                    self.web_role = "U"
                return
        except Exception,e:
            logger.exception(e)
            raise self.AuthenticationFailed("user/password error")
    
    
    def authenticate(self, password):
        global logger

        user = None

        try:
            self._check_passwd(password)
            self.is_authenticated = True

        except self.AuthenticationFailed as e:
            logger.debug(u"Authentication failed for %s: %s" % (self._username, e))
        except Exception:
            logger.exception(u"Caught Exception while authenticating %s",
                             self._username)
            raise

        return self    
     
    def is_authenticated(self):
        return self._is_authenticated
    
    def save(self,**kwargs):
        pass
    
    @property
    def username(self):
        return self._username
    
    @username.setter
    def username(self,value):
        self._username = value
    
    @property
    def email(self):
        return self._email
    
    @email.setter
    def email(self,value):
        self._email=value
        
    @property
    def last_name(self):
        return self._last_name
    
    @last_name.setter
    def last_name(self,value):
        self._flast_name=value  
    
    @property
    def first_name(self):
        return self._first_name
    
    @first_name.setter
    def first_name(self,value):
        self._first_name=value
    
    @property
    def is_active(self):
        return self._is_active
    
    @is_active.setter
    def is_active(self,value):
        self._is_active=value
    @property
    def role(self):
        return self._role
    
    @role.setter
    def role(self,value):
        self._role = value
    @property
    def web_role(self):
        return self._web_role
    
    @web_role.setter
    def web_role(self,value):
        self._web_role = value
        
    @property
    def is_super(self):
        try:
            if not self._is_superuser:
                infourl = settings.OPS_USER_INFO_URL
                data = "user=%s&key=%s"%(self.username,settings.OPS_KEY)
                url = "%s?%s"%(infourl,data)
                hc = HttpClient(ret_type="json")
                ret = hc.get(url)
                if ret and ret["statusCode"] == 200 and ret["data"]["status"] == "00" and ret["data"]["data"]["privilege"] == 1:
                    self._is_superuser = True
            return self._is_superuser
        except Exception,e:
            logger.exception(e)
            self._is_superuser = False
            return self._is_superuser
            
    
    @is_super.setter
    def is_super(self,value):
        self._is_super=value    
    
    @property
    def id(self):
        return self._id
    
    @id.setter
    def id(self,value):
        self._id = value
    
    @property
    def mobile(self):
        return self._mobile
    
    @mobile.setter
    def mobile(self,value):
        self._mobile = value    

class UserGroup(object):
    def __init__(self):
        self._name = None
    
    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self,value):
        self._name = value
    
    def is_member_of(self,user):
        pass
