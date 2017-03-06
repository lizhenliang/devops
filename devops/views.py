# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.conf import settings
from django.db.models import Q
from devops.models import *
from django.db import connection

import salt_api #,ssh_paramiko
import json, re, math

import ssl
ssl._create_default_https_context = ssl._create_unverified_context
# urllib.urlopen一个https的时候会验证一次SSL证书,当目标使用的是自签名的证书时就会抛出一个错误

table_name = 'web_access_count'
field_name = 'insert_time'
cursor = connection.cursor()

@login_required(login_url='login')
def index(request):
    sql = "select DATE_FORMAT(insert_time,'%Y-%m-%d') from web_access_count where DATE_SUB(CURDATE(),INTERVAL 1 DAY) = DATE(insert_time) LIMIT 1" #% (field_name, table_name, field_name)
    cursor.execute(sql)
    # date_time = cursor.fetchall()[0][0]
    date_time = '2016-10-09'

    sql = "select cast(sum(pv_number) as char(12)) from %s where DATE_SUB(CURDATE(),INTERVAL 1 DAY) = DATE(%s)" % (table_name, field_name)
    cursor.execute(sql)
    total_pv = cursor.fetchall()[0][0]

    sql = "select cast(sum(uv_number) as char(12)) from %s where DATE_SUB(CURDATE(),INTERVAL 1 DAY) = DATE(%s)" % (table_name, field_name)
    cursor.execute(sql)
    total_uv = cursor.fetchall()[0][0]

    total_puv = {}
    total_puv['date_time'] = date_time
    total_puv['total_pv'] = total_pv
    total_puv['total_uv'] = total_uv
    return render_to_response('index.html',{'total_puv': total_puv})

# @login_required()
def chartsData(request, period):
    date_time = []
    pv = []
    uv = []
    if period == "day":
        sql = "select DATE_FORMAT(insert_time,'%H:%i') from web_access_count where TO_DAYS(insert_time)=TO_DAYS(NOW())" #% (field_name, table_name, field_name)
        # sql = "select DATE_FORMAT(%s,'%H:%i') from %s where TO_DAYS(%s)=TO_DAYS(NOW())" % (field_name, table_name, field_name)
        cursor.execute(sql)
        for i in cursor.fetchall():
            date_time.append(i[0])
        sql = "select pv_number from %s where TO_DAYS(%s)=TO_DAYS(NOW())" % (table_name, field_name)
        cursor.execute(sql)
        for i in cursor.fetchall():
            pv.append(i[0])
        sql = "select uv_number from %s where TO_DAYS(%s)=TO_DAYS(NOW())" % (table_name, field_name)
        cursor.execute(sql)
        for i in cursor.fetchall():
            uv.append(i[0])
    elif period == "week":
        sql = "select DATE_FORMAT(insert_time,'%Y-%m-%d %H:%i') from web_access_count where DATE_SUB(CURDATE(),INTERVAL 7 DAY) <= DATE(insert_time)" #% (field_name, table_name, field_name)
        cursor.execute(sql)
        for i in cursor.fetchall():
            date_time.append(i[0])

        sql = "select pv_number from %s where DATE_SUB(CURDATE(),INTERVAL 7 DAY) <= DATE(%s)" % (table_name, field_name)
        cursor.execute(sql)
        for i in cursor.fetchall():
            pv.append(i[0])

        sql = "select uv_number from %s where DATE_SUB(CURDATE(),INTERVAL 7 DAY) <= DATE(%s)" % (table_name, field_name)
        cursor.execute(sql)
        for i in cursor.fetchall():
            uv.append(i[0])
    elif period == "month":
        sql = "select DATE_FORMAT(insert_time,'%Y-%m-%d %H:%i') from web_access_count where DATE_SUB(CURDATE(),INTERVAL 30 DAY) <= DATE(insert_time)" #% (field_name, table_name, field_name)
        cursor.execute(sql)
        for i in cursor.fetchall():
            date_time.append(i[0])

        sql = "select pv_number from %s where DATE_SUB(CURDATE(),INTERVAL 30 DAY) <= DATE(%s)" % (table_name, field_name)
        cursor.execute(sql)
        for i in cursor.fetchall():
            pv.append(i[0])

        sql = "select uv_number from %s where DATE_SUB(CURDATE(),INTERVAL 30 DAY) <= DATE(%s)" % (table_name, field_name)
        cursor.execute(sql)
        for i in cursor.fetchall():
            uv.append(i[0])

    charts_data = {}
    charts_data['date_time'] = date_time
    charts_data['pv'] = pv
    charts_data['uv'] = uv
    # 数据格式: {'date_time':['2016-08-13 08:29:00', '2016-08-13 08:30:00'],'pv':[3, 6, 12],'uv':[5, 2, 3]}
    return HttpResponse(json.dumps(charts_data))

@login_required()
def assetList(request, page):
    all_asset = AssetInfo.objects.all()
    all_asset_info = []
    for i in all_asset:
        all_asset_info.append({
            'id':i.id,
            'public_ip':i.public_ip,
            'intranet_ip':i.intranet_ip,
            'host_name':i.host_name,
            'os':i.os,
            'cpu_model':i.cpu_model,
            'cpu_thread_number':i.cpu_thread_number,
            'memory':i.memory,
            'disk':json.loads(str(i.disk).replace("'",'"').replace('u"','"')),  # 将unicode字符串转为字典，否则前端无法遍历
            'minion_id':i.minion_id
        })
    total_record = len(all_asset_info)
    if request.method == "GET":
        page = int(page)
        page_init = 5
        # all_asset_info = AssetInfo.objects.all()
        total_page = int(math.ceil(float(len(all_asset_info))/page_init))  # 进一法取整
        total_page_sequence = [ i for i in xrange(total_page)]
        start_page = page_init * page - page_init
        end_page = page_init * page
        asset_info = all_asset_info[start_page:end_page]
        return render_to_response('asset/asset_list.html',{'asset_info': asset_info,
                                                           'total_num': total_page_sequence,
                                                           'page': page,
                                                           'total_record':total_record}, RequestContext(request))
    elif request.method == "POST":
        search = request.POST.get('search')
        if search:
            result = all_asset.filter(Q(public_ip=search)|Q(intranet_ip=search)|Q(host_name=search))
            search_result = []
            for i in result:
                search_result.append({
                    'id':i.id,
                    'public_ip':i.public_ip,
                    'intranet_ip':i.intranet_ip,
                    'host_name':i.host_name,
                    'os':i.os,
                    'cpu_model':i.cpu_model,
                    'cpu_thread_number':i.cpu_thread_number,
                    'memory':i.memory,
                    'disk':json.loads(str(i.disk).replace("'",'"').replace('u"','"')),  # 将unicode字符串转为字典，否则前端无法遍历
                    'minion_id':i.minion_id
                })
            if len(search_result) == 0 :
                search_error = "请尝试公网IP/内网IP/主机名为查询条件!"
                return render_to_response('asset/asset_list.html',{'search_error': search_error}, RequestContext(request))
            return render_to_response('asset/asset_list.html',{'search_result': search_result}, RequestContext(request))
        else:
            search_error = "输入不能为空!"
            return render_to_response('asset/asset_list.html',{'search_error': search_error}, RequestContext(request))


@login_required()
def addHostAsset(request, tgt):
    sapi = salt_api.HostInfo()
    host_asset = sapi.assetInfo(tgt)
    # match_ip = re.findall(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', tgt)
    match_id = re.findall(r'^\d+$', tgt)
    # 如果传入的tgt值是IP就以IP为查询添加，否则以minion id为查询条件。有记录就更新，无就插入
    try:
        # if match_ip:
        #     update = AssetInfo.objects.get(public_ip=tgt)
        if match_id:
            update = AssetInfo.objects.get(id=tgt)
        else:
            update = AssetInfo.objects.get(minion_id=tgt)
        update.intranet_ip = host_asset['intranet_ip']
        update.host_name = host_asset['host_name']
        update.os = host_asset['os']
        update.cpu_model = host_asset['cpu_model']
        update.cpu_thread_number = host_asset['cpu_thread_number']
        update.memory = host_asset['memory']
        update.disk = host_asset['disk']
        update.minion_id = host_asset['minion_id']
        update.save()
    except:
        insert = AssetInfo.objects.create(
            public_ip=host_asset['public_ip'],
            intranet_ip = host_asset['intranet_ip'],
            host_name = host_asset['host_name'],
            os = host_asset['os'],
            cpu_model = host_asset['cpu_model'],
            cpu_thread_number = host_asset['cpu_thread_number'],
            memory = host_asset['memory'],
            disk = host_asset['disk'],
            minion_id = host_asset['minion_id'],
        )
        insert.save()
    # return HttpResponseRedirect('/asset/list/page=1')
def editHostAsset(request):
    # if request.method == "GET":
    #     return HttpResponseRedirect('/asset/list/page=1')
    if request.method == "POST":
        id = request.POST.get('id')
        update = AssetInfo.objects.get(id=id)
        update.intranet_ip = request.POST.get('public_ip')
        update.intranet_ip = request.POST.get('intranet_ip')
        update.host_name = request.POST.get('host_name')
        update.os = request.POST.get('os')
        update.cpu_model = request.POST.get('cpu_model')
        update.cpu_thread_number = request.POST.get('cpu_thread_number')
        update.memory = request.POST.get('memory')
        update.disk = request.POST.get('disk')
        update.save()

        return HttpResponseRedirect('/asset/list/page=1')

def delHostAsset(request, id):
    if isinstance(id, unicode):
        AssetInfo.objects.get(id=id).delete()
        # return HttpResponseRedirect('/asset/list')
    elif isinstance(id, list):
        for id in id:
            AssetInfo.objects.get(id=id).delete()
        # return HttpResponseRedirect('/asset/list')

# 手动添加
def addAsset(request):
    minion_id = request.GET['minion']
    if minion_id:
        try:
            addHostAsset(request, minion_id)
            return HttpResponseRedirect('/asset/list/page=1')
        except KeyError:
            error = "Minion ID不存在！"
            all_asset_info = AssetInfo.objects.all()
            return render_to_response('asset/asset_list.html', {'error': error,'all_asset_info': all_asset_info})
    else:
        error = "输入不能为空！"
        all_asset_info = AssetInfo.objects.all()
        return render_to_response('asset/asset_list.html', {'error': error,'all_asset_info': all_asset_info})

@login_required()
# 按钮操作
def assetAction(request):
    if request.method == "GET":
        return HttpResponseRedirect('/asset/list/page=1')
    if request.method == "POST":
        # 点击哪个按钮就会传过来那个值。另外调用函数时不用写render，在调用的函数里面写或window.location.href
        for key in request.POST:
            if key == "del_id":
                id = request.POST[key]
                delHostAsset(request, id)
            elif key == "refresh_mid":
                mid = request.POST[key]
                addHostAsset(request, mid)
                # return HttpResponseRedirect('/asset/list/page=1')
            # body: all_id%5B%5D=12&all_id%5B%5D=13
            elif request.body.startswith("del_all_id"):
                id_list = request.POST.getlist("del_all_id[]")   # 获取字典中的列表
                delHostAsset(request, id_list)
            elif request.body.startswith("refresh_all_id"):
                id_list = request.POST.getlist("refresh_all_id[]")
                for id in id_list:
                    addHostAsset(request, id)
                # return HttpResponseRedirect('/asset/list')

@login_required()
def minionList(request):
    if request.method == "GET":
        sapi = salt_api.SaltAPI()
        all_minion = sapi.allMinion()
        accept_minion = all_minion['accept']
        unaccept_minion = all_minion['unaccept']
        return render_to_response('salt/minion_list.html',{'accept_minion': accept_minion, 'unaccept_minion': unaccept_minion}, RequestContext(request))

@login_required()
def batchExecCmd(request):
    if request.method == 'GET':
        return render_to_response('salt/batch_exec_cmd.html', RequestContext(request))
    else:
        tgt = request.POST['salt_target']
        fun = request.POST['salt_fun']
        arg = request.POST['salt_arg']
        sapi = salt_api.SaltAPI()
        if arg:
            result = sapi.execCmdArg(tgt, fun, arg)
        else:
            result = sapi.execCmdNoArg(tgt, fun)
        result = json.dumps(result).replace('\\n', '<br/>').replace(',','<br/>').replace('{',' ').replace('}','')
        return render_to_response('salt/batch_exec_cmd.html',{'exec_result': result}, RequestContext(request))

def saltAction(request):
    if request.method == "POST":
        sapi = salt_api.SaltAPI()
        for key in request.POST:
            if key == "del_minion_id":
                minion_id = request.POST[key]
                sapi.deleteKey(minion_id)
                # return HttpResponseRedirect('/salt/minion_list')
            elif key == "accept_minion_id":
                minion_id = request.POST[key]
                sapi.acceptKey(minion_id)
                # return HttpResponseRedirect('/salt/minion_list')
            elif request.body.startswith("del_all_minion_id"):
                minion_id_list = request.POST.getlist('del_all_minion_id[]')
                sapi.deleteKey(minion_id_list)
                return "ok"
                # return HttpResponseRedirect('/salt/minion_list')
            elif request.body.startswith("accept_all_minion_id"):
                # print request.POST.getlist('accept_all_minion_id[]')
                minion_id_list = request.POST.getlist('accept_all_minion_id[]')
                sapi.acceptKey(minion_id_list)
                # return HttpResponseRedirect('/salt/minion_list')

@login_required()
def installSoft(request):
    # if request.method == "GET":
    return render_to_response('deploy/install_soft.html', RequestContext(request))

def sshConnectInfo(request):
    if request.method == "POST":
        info = {}
        for key in request.POST:
            info[key] = request.POST[key]
        # print info
        # return HttpResponseRedirect('/deploy/install_soft')
        hostname = info['hostname']
        port = int(info['port'])
        username = info['username']
        password = info['password']

        # if not hostname:
        #     print "no"
        #     hostname_error = "主机名不能为空！"
        #     return render_to_response('deploy/install_soft.html',{'hostname_error':hostname_error}, RequestContext(request))
        # if not port:
        #     port_error = "端口不能为空！"
        #     return render_to_response('deploy/install_soft.html',{'port_error':port_error}, RequestContext(request))
        # if not username:
        #     username_error = "用户名不能为空！"
        #     return render_to_response('deploy/install_soft.html',{'username_error':username_error}, RequestContext(request))
        # if not password:
        #     pass_error = "密码不能为空！"
        #     return render_to_response('deploy/install_soft.html',{'pass_error':pass_error}, RequestContext(request))

        ssh = ssh_paramiko.SSHConnect()

        if 'opt1' in info and 'opt1' in info:
            print("all ok")
            return HttpResponseRedirect('/deploy/install_soft', RequestContext(request))
                # ssh.uploadFile(hostname, port, username, password)
                # result = ssh.remoteExecCmd(hostname, port, username, password, '/bin/bash /tmp/zabbix_agent_install.sh')
                # return HttpResponseRedirect('/deploy/install_soft')
        else:
            if 'opt1' in info:
                print("opt1")
                return render_to_response('deploy/install_soft.html', RequestContext(request))
            elif 'opt2' in info:
                print("opt2")
                src_file = 'zabbix_agent_install.sh'
                dst_dir = '/tmp'
                ssh.uploadFile(hostname, port, username, password, src_file, dst_dir)
                result = ssh.remoteExecCmd(hostname, port, username, password, '/bin/bash %s/%s' % (dst_dir, src_file))
                for i in result:
                    print i.strip('\n')
                return render_to_response('deploy/install_soft.html', {'result':result}, RequestContext(request))
            else:
                print("all no")
                opt_error = "请选择要安装的软件！"
                return render_to_response('deploy/install_soft.html',{'opt_error':opt_error}, RequestContext(request))

def getLog(request):
    return render_to_response('log/view_log.html')

def login(request):
    if request.method == 'GET':
        return render_to_response('login.html',RequestContext(request))
    if request.method == 'GET':
        return render_to_response('login.html',RequestContext(request))
    else:
        username = request.POST.get('username')
        password = request.POST.get('password')
        # if username == "admin" and password == "pass":
        #     return HttpResponseRedirect('index')
        # else:
        #     return HttpResponseRedirect('login')
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return HttpResponseRedirect('index')
        else:
            error = "用户名或密码错误，请重新输入。"
            return render_to_response("login.html",{'error':error},RequestContext(request))

# @login_required  #只有用户在登录的情况下才能调用该视图，否则将自动重定向至登录页面。
def logout(request):
    auth.logout(request)
    return HttpResponseRedirect('login')