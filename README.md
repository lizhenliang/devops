# 此练手项目已废弃，不再更新！

# 运行环境

Python2.7

Django1.9（pip install django==1.9）

依赖模块：

MySQLdb（apt-get install python-mysqldb）

# 部署步骤
1.下载源码

git clone https://github.com/lizhenliang/DevOps.git

cd DevOps

2.修改数据库连接地址

vi mysite/settings.py   

3.生成数据库表

python manage.py migrate 

4.修改salt rest api连接地址

vi devops/salt_api.py 

5.创建登录用户名

python manage.py createsuperuser 

6.启动服务

python manage.py runserver 0.0.0.0:8888 

7.数据库表生成图表测试数据

\#!/bin/bash  
HOST="192.168.1.10"  
USER="root"  
PASSWD="password"  
DB="devops_test"  
mysql -h$HOST -u$USER -p$PASSWD $DB -e "truncate web_access_count" &>/dev/null # 清空表  
DATE=$(date +"%F %T")  
ID=1  
for i in {1..100}; do  
&emsp;&emsp;&emsp;mysql -h$HOST -u$USER -p$PASSWD $DB -e "insert into web_access_count(id,insert_time,pv_number,uv_number) values ('$ID','$DATE','$RANDOM','$RANDOM')" &>/dev/null  
&emsp;&emsp;&emsp;let ID++  
&emsp;&emsp;&emsp;sleep 1  
done  

QQ技术群：323779636（Shell/Python运维开发群）
