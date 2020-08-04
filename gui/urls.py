from django.urls import path, include
from . import views

app_name = 'gui'
urlpatterns = [
    path('global/codes/manage/', views.GlobalCodesManageView.as_view(), name='global-codes-manage'),
    path('user/manage/', views.UserManageView.as_view(), name='user-manage'),
    path('group/manage/', views.GroupManageView.as_view(), name='group-manage'),
    path('users/by/group/manage/', views.UsersByGroupManageView.as_view(), name='users-by-group-manage'),
    path('equip/base/info/manage/', views.EquipBaseInfoManageView.as_view(), name='equip-base-info-manage'),
    path('change/shifts/manage/', views.ChangeShiftsManageView.as_view(), name='change-shifts-manage'),
    path('factory/schedule/manage/', views.FactoryScheduleManageView.as_view(), name='factory-schedule-manage'),
    path('accounts/', include('django.contrib.auth.urls')),
    # 设备管理-设备种类
    path('equip/category/manage/', views.EquipCategoryManageView.as_view(), name='equip-category-manage'),
    # 设备管理-设备基础信息
    path('equip/manage/', views.EquipManageView.as_view(), name='equip-manage'),
    path('material/base/info/manage/', views.MaterialBaseInfoManageView.as_view(), name='material-base-info-manage')
]