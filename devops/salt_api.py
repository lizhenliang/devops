#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib, urllib2
import json
import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    # Legacy Python that doesn't verify HTTPS certificates by default
    pass
else:
    # Handle target environment that doesn't support HTTPS verification
    ssl._create_default_https_context = _create_unverified_https_context

class SaltAPI():
    def __init__(self):
        self.api_address = 'https://192.168.1.99:8000'
        self.api_user = 'admin'
        self.api_password = 'admin_pass'
    def token(self):
        params = {'eauth':'pam', 'username':self.api_user, 'password':self.api_password}
        url = self.api_address + '/login'
        urlencode = urllib.urlencode(params)
        headers = {'Accept': 'application/json'}     # 默认是json格式，可以不添加这个头信息
        req = urllib2.Request(url, urlencode, headers)
        html = urllib2.urlopen(req)
        content = json.loads(html.read())
        token = content["return"][0]["token"]
        return str(token)
    def execCmd(self, params):
        headers = {'Accept': 'application/json', 'X-Auth-Token':self.token()}
        url = self.api_address + '/'
        urlencode = urllib.urlencode(params)
        req = urllib2.Request(url, urlencode, headers)
        html = urllib2.urlopen(req)
        content = json.loads(html.read())
        return content['return'][0] #.replace('return:\n -',"")

    def execCmdNoArg(self, tgt, fun):
        params = {'client':'local', 'tgt':tgt, 'fun':fun}
        result = self.execCmd(params)
        return result
    def execCmdArg(self, tgt, fun, arg):
        params = {'client':'local', 'tgt':tgt, 'fun':fun, 'arg':arg}
        result = self.execCmd(params)
        return result
    def execCmdNodeGroup(self, fun, arg, node_group):
        params = {'client':'local', 'fun':fun, 'arg':arg, 'expr_form':node_group}
        result = self.execCmd(params)
        return result

    def allMinion(self):
        params = {'client':'wheel', 'fun':'key.list_all'}
        result = self.execCmd(params)
        minions = {}
        minions['accept'] = result['data']['return']['minions']
        minions['unaccept'] = result['data']['return']['minions_pre']
        return minions

    # 可接受列表
    def deleteKey(self, node_name):
        if isinstance(node_name, unicode):
            params = {'client':'wheel', 'fun':'key.delete', 'match':node_name}
            self.execCmd(params)
        elif isinstance(node_name, list):
            for node_name in node_name:
                params = {'client':'wheel', 'fun':'key.delete', 'match':node_name}
                self.execCmd(params)
        # result = self.execCmd(params)
        # return result['data']['success']   # 返回布尔值
    def acceptKey(self, node_name):
        if isinstance(node_name, unicode):
            params = {'client':'wheel', 'fun':'key.accept', 'match':node_name}
            self.execCmd(params)
        elif isinstance(node_name, list):
            for node_name in node_name:
                params = {'client':'wheel', 'fun':'key.accept', 'match':node_name}
                self.execCmd(params)

class HostInfo(SaltAPI):
    def disk(self, tgt):
        params = {'client':'local', 'tgt':tgt, 'fun':'disk.usage'}
        result = self.execCmd(params)[tgt]
        disk = {}
        for mounted, partition in result.items():
            fs = partition['filesystem']
            if fs.startswith("/dev"):
                total = '%.2f' %(float(partition['1K-blocks'])/1024/1024)
                avail = '%.2f' %(float(partition['available'])/1024/1024)
                # used = '%.2f' %(float(partition['used'])/1024/1024)
                # use_percent = partition['capacity']
                disk[fs] = {'mount': mounted, 'total': total, 'avail': avail}
            else:
                continue
        return disk

    def assetInfo(self, tgt):
        params = {'client':'local', 'tgt': tgt, 'fun': 'grains.items'}
        result = self.execCmd(params)[tgt]
        # return result
        public_nic = 'eth0'
        intranet_nic = 'lo'
        asset_info = {}
        if result['os'] == "CentOS":
            asset_info['public_ip'] = result['ip4_interfaces'][public_nic][0]
            asset_info['intranet_ip'] = result['ip4_interfaces'][intranet_nic][0]
        elif result['os'] == "Ubuntu":
            asset_info['public_ip'] = result['ip_interfaces'][public_nic][0]
            asset_info['intranet_ip'] = result['ip_interfaces'][intranet_nic][0]
        asset_info['host_name'] = result['nodename']
        asset_info['os'] = result['os'] + result['osrelease'] + '-' + result['osarch']
        asset_info['cpu_model'] = result['cpu_model']
        asset_info['cpu_thread_number'] = result['num_cpus']
        asset_info['memory'] = str(result['mem_total']) + "M"
        asset_info['disk'] = self.disk(tgt)
        asset_info['minion_id'] = result['id']
        return asset_info

if __name__ == "__main__":
    api = SaltAPI()
    # print api.acceptKey('client')
    api = HostInfo()
    print api.assetInfo('site01')
    # print api.allMinion()
    # print api.deleteKey('ubuntu')
    # print api.acceptKey('centos7')
    # print api.execCmdNoArg('*', 'disk.usage')
    # print api.execCmdNoArg('*', 'grains.items')
    # print api.execCmdArg('*', 'cmd.run', 'df -h')
    # print api.execCmdNodeGroup('cmd.run', 'df -h', 'test')
