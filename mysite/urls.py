from django.conf.urls import url
# from django.contrib import admin
from devops import views
import devops.views
urlpatterns = [
    # url(r'^admin/', include(admin.site.urls)),
    url(r'^$', views.login),
    url(r'^index$', views.index),
    url(r'^login$', views.login),
    url(r'^charts/data-period=(\w+)', views.chartsData, name="charts_data"),
    url(r'^asset/list/page=(\d+)$', views.assetList, name="asset_list"),
    url(r'^asset/add$', views.addAsset, name="asset_add"),
    url(r'^asset/edit$', views.editHostAsset, name="asset_edit"),
    url(r'^asset/action$', views.assetAction, name="asset_action"),
    # url(r'^asset/delete_id=(\d+)', views.delAsset, name="asset_delete"),
    url(r'^salt/minion_list$', views.minionList, name="salt_minion_list"),
    url(r'^salt/batch_exec_cmd$', views.batchExecCmd, name="salt_batch_exec_cmd"),
    url(r'^salt/action$', views.saltAction, name="salt_action"),
]