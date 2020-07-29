from django.utils.decorators import method_decorator
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticatedOrReadOnly, DjangoModelPermissions
from rest_framework.viewsets import ModelViewSet

from basics.filters import EquipFilter, GlobalCodeTypeFilter, WorkScheduleFilter
from basics.models import GlobalCodeType, GlobalCode, WorkSchedule, EquipCategoryAttribute, Equip, SysbaseEquipLevel, \
    WorkSchedulePlan, ClassesDetail, PlanSchedule, EquipCategoryAttribute
from basics.serializers import GlobalCodeTypeSerializer, GlobalCodeSerializer,WorkScheduleSerializer, \
    EquipCategoryAttributeSerializer, EquipSerializer, SysbaseEquipLevelSerializer, WorkSchedulePlanSerializer, \
    WorkScheduleUpdateSerializer, ClassesDetailSerializer, PlanScheduleSerializer, EquipCreateAndUpdateSerializer, \
    EquipCategoryAttributeSerializer
from mes.common_code import return_permission_params, CommonDeleteMixin
from mes.derorators import api_recorder
from mes.permissions import PermissionClass
from mes.paginations import SinglePageNumberPagination


@method_decorator([api_recorder], name="dispatch")
class GlobalCodeTypeViewSet(CommonDeleteMixin, ModelViewSet):
    """
    list:
        公共代码类型列表
    create:
        创建公共代码类型
    update:
        修改公共代码类型
    destroy:
        删除公共代码类型
    """
    queryset = GlobalCodeType.objects.filter(delete_flag=False)
    serializer_class = GlobalCodeTypeSerializer
    model_name = queryset.model.__name__.lower()
    permission_classes = (IsAuthenticatedOrReadOnly,
                          PermissionClass(permission_required=return_permission_params(model_name)))
    filter_backends = (DjangoFilterBackend,)
    filter_class = GlobalCodeTypeFilter


@method_decorator([api_recorder], name="dispatch")
class GlobalCodeViewSet(CommonDeleteMixin, ModelViewSet):
    """
    list:
        公共代码列表
    create:
        创建公共代码
    update:
        修改公共代码
    destroy:
        删除公共代码
    """
    queryset = GlobalCode.objects.filter(delete_flag=False)
    serializer_class = GlobalCodeSerializer
    model_name = queryset.model.__name__.lower()
    permission_classes = (IsAuthenticatedOrReadOnly,
                          PermissionClass(permission_required=return_permission_params(model_name)))
    filter_backends = (DjangoFilterBackend,)
    pagination_class = SinglePageNumberPagination
    filter_fields = ('global_type_id', 'global_type__type_no',)


@method_decorator([api_recorder], name="dispatch")
class WorkScheduleViewSet(CommonDeleteMixin, ModelViewSet):
    """
    list:
        工作日程列表
    create:
        创建工作日程
    update:
        修改工作日程
    destroy:
        删除工作日程
    """
    queryset = WorkSchedule.objects.filter(delete_flag=False)
    serializer_class = WorkScheduleSerializer
    model_name = queryset.model.__name__.lower()
    permission_classes = (IsAuthenticatedOrReadOnly,
                          PermissionClass(permission_required=return_permission_params(model_name)))
    filter_backends = (DjangoFilterBackend,)
    filter_class = WorkScheduleFilter

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return WorkScheduleUpdateSerializer
        else:
            return WorkScheduleSerializer


class EquipCategoryViewSet(CommonDeleteMixin, ModelViewSet):
    """
    list:
        设备种类列表
    create:
        创建设备种类
    update:
        修改设备种类
    destroy:
        删除设备种类
    """
    queryset = EquipCategoryAttribute.objects.filter(delete_flag=False)
    serializer_class = EquipCategoryAttributeSerializer
    model_name = queryset.model.__name__.lower()
    permission_classes = (IsAuthenticatedOrReadOnly,
                          PermissionClass(permission_required=return_permission_params(model_name)))


@method_decorator([api_recorder], name="dispatch")
class EquipViewSet(CommonDeleteMixin, ModelViewSet):
    """
    list:
        设备列表
    create:
        创建设备
    update:
        修改设备
    destroy:
        删除设备
    """
    queryset = Equip.objects.filter(delete_flag=False)
    serializer_class = EquipSerializer
    model_name = queryset.model.__name__.lower()
    permission_classes = (IsAuthenticatedOrReadOnly,
                          PermissionClass(permission_required=return_permission_params(model_name)))
    filter_backends = (DjangoFilterBackend,)
    filter_class = EquipFilter

    def get_serializer_class(self):
        if self.action == 'create' or "update":
            return EquipCreateAndUpdateSerializer


@method_decorator([api_recorder], name="dispatch")
class EquipCategoryAttributeViewSet(CommonDeleteMixin, ModelViewSet):
    """
    list:
        设备分类属性列表
    create:
        创建设备分类属性
    update:
        修改设备分类属性
    destroy:
        删除设备分类属性
    """
    queryset = EquipCategoryAttribute.objects.filter(delete_flag=False)
    serializer_class = EquipCategoryAttributeSerializer
    model_name = queryset.model.__name__.lower()
    permission_classes = (IsAuthenticatedOrReadOnly,
                          PermissionClass(permission_required=return_permission_params(model_name)))


@method_decorator([api_recorder], name="dispatch")
class SysbaseEquipLevelViewSet(CommonDeleteMixin, ModelViewSet):
    """
    list:
        设备层次列表
    create:
        创建设备层次
    update:
        修改设备层次
    destroy:
        删除设备层次
    """
    queryset = SysbaseEquipLevel.objects.filter(delete_flag=False)
    serializer_class = SysbaseEquipLevelSerializer
    model_name = queryset.model.__name__.lower()
    permission_classes = (IsAuthenticatedOrReadOnly,
                          PermissionClass(permission_required=return_permission_params(model_name)))


@method_decorator([api_recorder], name="dispatch")
class WorkSchedulePlanViewSet(CommonDeleteMixin, ModelViewSet):
    """
    list:
        工作日程计划列表
    create:
        创建工作日程计划
    update:
        修改工作日程计划
    destroy:
        删除工作日程计划
    """
    queryset = WorkSchedulePlan.objects.filter(delete_flag=False)
    serializer_class = WorkSchedulePlanSerializer
    model_name = queryset.model.__name__.lower()
    permission_classes = (IsAuthenticatedOrReadOnly,
                          PermissionClass(permission_required=return_permission_params(model_name)))


@method_decorator([api_recorder], name="dispatch")
class ClassesDetailViewSet(CommonDeleteMixin, ModelViewSet):
    """
    list:
        班次条目列表
    create:
        创建班次条目
    update:
        修改班次条目
    destroy:
        删除班次条目
    """
    queryset = ClassesDetail.objects.filter(delete_flag=False)
    serializer_class = ClassesDetailSerializer
    model_name = queryset.model.__name__.lower()
    permission_classes = (IsAuthenticatedOrReadOnly,
                          PermissionClass(permission_required=return_permission_params(model_name)))


@method_decorator([api_recorder], name="dispatch")
class PlanScheduleViewSet(CommonDeleteMixin, ModelViewSet):
    """
    list:
        计划时间列表
    create:
        创建计划时间
    update:
        修改计划时间
    destroy:
        删除计划时间
    """
    queryset = PlanSchedule.objects.filter()
    serializer_class = PlanScheduleSerializer
    model_name = queryset.model.__name__.lower()
    permission_classes = (IsAuthenticatedOrReadOnly,
                          PermissionClass(permission_required=return_permission_params(model_name)))