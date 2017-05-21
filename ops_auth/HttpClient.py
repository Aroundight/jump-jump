#!/bin/env python
#-*- coding: utf-8 -*-
import urllib2
import urllib
import cookielib
import re
import time
import os
import json
import copy
import unittest
import logging
import base64
logger_g = logging.getLogger(__name__)
formatter = logging.Formatter('%(name)s: %(levelname)s-%(message)s') 
console = logging.StreamHandler()  
console.setLevel(logging.DEBUG) 
console.setFormatter(formatter)
logger_g.addHandler(console)


class HttpClient(object):
    def __init__(self,ret_type=None,output=None,logger=None):
        global logger_g
        self.ret_type = ret_type
        if logger:
            self.logger = logger;
        else:
            self.logger = logger_g
        self.output=output;
        
        self.DEBUG=False
        
        self.cookieJar=cookielib.CookieJar()
        self.opener=None
        
        
        self.headers ={
            #"Accept-Encoding": "gzip, deflate, sdch",
            "Accept-Language": "zh-CN,zh;",
            "Accept": "*/*",
            "X-Requested-With": "XMLHttpRequest",
            "User-Agent": "HttpClient/1.1"
        }
        if "json"==ret_type:
            self.headers["Content-Type"]="application/json";
        else:
            self.headers["Content-Type"]="application/octet-stream";

    def post(self,url,data=None,header=None):
        if not header:
            header=self.headers
        
        proxy = urllib2.ProxyHandler({'http': '127.0.0.1:8080'})
        
        if self.DEBUG:
            self.opener=urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookieJar),proxy)
        else:
            self.opener=urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookieJar));
        if data == None:
            req=urllib2.Request(url=url,headers=headers);
        else:
            req=urllib2.Request(url,data,header)
        result=self.opener.open(req,timeout=30).read();
        if self.DEBUG:
            self.logger.info("in post return : {0}".format(result))
        if result =="":
            return "";
        else:
            if self.ret_type == "json":
                return json.loads(result);
            else:
                return result
    
    def get(self,url):
        try:
            proxy = urllib2.ProxyHandler({'http': '127.0.0.1:8080'})
            
            if self.DEBUG:
                self.opener=urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookieJar),proxy)
            else:
                self.opener=urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookieJar))
            import copy
            req=urllib2.Request(url=url,headers=self.headers);
            self.response =self.opener.open(req,timeout=60);
            result = self.response.read()
            if result =="":
                return "";
            if self.ret_type=="json":
                return json.loads(result);
            elif self.ret_type=="txt":
                return result;
            elif self.ret_type==None:
                if self.output == None:
                    open(os.path.basename(url.split("?")[0]),"w+").write(result);
                    self.logger.info("download file form {0} saved to {1}".format(url,os.path.join(os.path.realpath(os.path.curdir),os.path.basename(url.split("?")[0]))));
                else:
                    open(self.output,"w+").write(result);
                    self.logger.info("download file form {0} saved to {1}".format(url,self.output));
        except Exception,e:
            self.logger.exception(e);



class Test(unittest.TestCase):
    def test_download(self):
        import logging
        from logging.handlers import TimedRotatingFileHandler
        logger = logging.getLogger("test-download");
        logger.setLevel(logging.DEBUG)
        ch = TimedRotatingFileHandler("/var/log/http-request.log","M",1,10)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(process)d - %(funcName)s - %(lineno)d  - %(levelname)s - %(message)s')  
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        hcli=HttpClient(logger=logger)
        hcli.get("https://github.com/tabish121/pyActiveMQ/archive/master.zip")
    def test_post(self):
        pass
    
    def test_get_basic_auth(self):
        url="http://192.168.1.130:15672/api/queues"
        user = "admin"
        password = "Ofo@Rabbit"
        hcli=HttpClient(ret_type="json")
        hashStr = base64.b64encode('%s:%s'%(user,password))
        hcli.headers.update({"Authorization": "Basic %s"% hashStr})        
        hcli.get(url)
        


if __name__ == "__main__":
    unittest.main();
