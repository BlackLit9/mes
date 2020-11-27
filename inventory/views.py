import datetime
import json
import logging
import random
import time

import requests
from django.db.models import Sum
from django.db.transaction import atomic
from django.shortcuts import render

# Create your views here.
from django.utils.decorators import method_decorator
from rest_framework import mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from basics.models import GlobalCode
from inventory.filters import InventoryLogFilter, StationFilter, PutPlanManagementLBFilter, PutPlanManagementFilter, \
    DispatchPlanFilter, DispatchLogFilter, DispatchLocationFilter
from inventory.models import InventoryLog, WarehouseInfo, Station, WarehouseMaterialType, DeliveryPlanStatus, \
    BzFinalMixingRubberInventoryLB, DeliveryPlanLB, DispatchPlan, DispatchLog, DispatchLocation
from inventory.models import DeliveryPlan, MaterialInventory
from inventory.serializers import PutPlanManagementSerializer, \
    OverdueMaterialManagementSerializer, WarehouseInfoSerializer, StationSerializer, WarehouseMaterialTypeSerializer, \
    PutPlanManagementSerializerLB, BzFinalMixingRubberLBInventorySerializer, DispatchPlanSerializer, \
    DispatchLogSerializer, DispatchLocationSerializer
from inventory.models import WmsInventoryStock
from inventory.serializers import BzFinalMixingRubberInventorySerializer, \
    WmsInventoryStockSerializer, InventoryLogSerializer
from inventory.utils import BaseUploader
from mes.common_code import SqlClient, CommonDeleteMixin
from mes.conf import WMS_CONF
from mes.derorators import api_recorder
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions

from recipe.models import ProductBatching, Material
from .models import MaterialInventory as XBMaterialInventory
from .models import BzFinalMixingRubberInventory
from .serializers import XBKMaterialInventorySerializer

logger = logging.getLogger('send.log')


@method_decorator([api_recorder], name="dispatch")
class MaterialInventoryView(GenericViewSet,
                            mixins.ListModelMixin, ):

    def get_queryset(self):
        return

    def data_adapt(self, instance):
        data = {
            "id": instance[8],
            "sn": instance[8],
            "material_no": instance[3],
            "material_name": instance[1],
            "material_type": instance[7],
            "qty": instance[0],
            "unit": instance[6],
            "unit_weight": instance[5],
            "total_weight": instance[2],
            "site": instance[4],
            "standard_flag": True if instance[9] else False,
        }
        return data

    def list(self, request, *args, **kwargs):
        params = request.query_params
        page = params.get("page", 1)
        page_size = params.get("page_size", 10)
        material_type = params.get("material_type")
        if material_type:
            sql = f"""select sum(tis.Quantity) qty, max(tis.MaterialName) material_name,
                           sum(tis.WeightOfActual) weight,tis.MaterialCode material_no,
                           max(tis.ProductionAddress) address, sum(tis.WeightOfActual)/sum(tis.Quantity) unit_weight,
                           max(tis.WeightUnit) unit, max(tim.MaterialGroupName) material_type,
                           Row_Number() OVER (order by tis.MaterialCode) sn, tis.StockDetailState status
                                from t_inventory_stock tis left join t_inventory_material tim on tim.MaterialCode=tis.MaterialCode
                            where tim.MaterialGroupName='{material_type}'
                            group by tis.MaterialCode, tis.StockDetailState;"""
        else:
            sql = f"""select sum(tis.Quantity) qty, max(tis.MaterialName) material_name,
                                       sum(tis.WeightOfActual) weight,tis.MaterialCode material_no,
                                       max(tis.ProductionAddress) address, sum(tis.WeightOfActual)/sum(tis.Quantity) unit_weight,
                                       max(tis.WeightUnit) unit, max(tim.MaterialGroupName) material_type,
                                       Row_Number() OVER (order by tis.MaterialCode) sn, tis.StockDetailState status
                                            from t_inventory_stock tis left join t_inventory_material tim on tim.MaterialCode=tis.MaterialCode
                                        group by tis.MaterialCode, tis.StockDetailState;"""
        try:
            st = (int(page) - 1) * int(page_size)
            et = int(page) * int(page_size)
        except:
            raise ValidationError("page/page_size异常，请修正后重试")
        else:
            if st not in range(0, 99999):
                raise ValidationError("page/page_size值异常")
            if et not in range(0, 99999):
                raise ValidationError("page/page_size值异常")
        sc = SqlClient(sql=sql, **WMS_CONF)
        temp = sc.all()
        count = len(temp)
        temp = temp[st:et]
        result = []
        for instance in temp:
            result.append(self.data_adapt(instance))
        sc.close()
        return Response({'results': result, "count": count})


@method_decorator([api_recorder], name="dispatch")
class ProductInventory(GenericViewSet,
                       mixins.ListModelMixin, ):

    def get_queryset(self):
        return

    def data_adapt(self, instance, material_type):
        material = instance[4].rstrip()
        temp_dict = {
            "sn": instance[5],
            "material_no": material,
            "material_name": material,
            "material_type": material_type,
            "qty": instance[1],
            "unit": "kg",
            "unit_weight": round(instance[2] / instance[1], 2),
            "total_weight": instance[2],
            "need_weight": instance[2],
            "standard_flag": True if instance[3] == "合格品" else False,
            "site": instance[0]
        }
        return temp_dict

    def list(self, request, *args, **kwargs):
        params = request.query_params
        page = params.get("page", 1)
        page_size = params.get("page_size", 10)
        stage = params.get("stage")
        try:
            st = (int(page) - 1) * int(page_size)
            et = int(page) * int(page_size)
        except:
            raise ValidationError("page/page_size异常，请修正后重试")
        else:
            if st not in range(0, 99999):
                raise ValidationError("page/page_size值异常")
            if et not in range(0, 99999):
                raise ValidationError("page/page_size值异常")
        stage_list = GlobalCode.objects.filter(use_flag=True, global_type__use_flag=True,
                                               global_type__type_name="胶料段次").values_list("global_name", flat=True)
        if stage:
            if stage not in stage_list:
                raise ValidationError("胶料段次异常请修正后重试")
            sql = f"""SELECT max(库房名称) as 库房名称, sum(数量) as 数量, sum(重量) as 重量, max(品质状态) as 品质状态, 物料编码, Row_Number() OVER (order by 物料编码) sn
                FROM v_ASRS_STORE_MESVIEW where 物料编码 like '%{stage}%' group by 物料编码"""
        else:
            sql = f"""SELECT max(库房名称) as 库房名称, sum(数量) as 数量, sum(重量) as 重量, max(品质状态) as 品质状态, 物料编码, Row_Number() OVER (order by 物料编码) sn
                FROM v_ASRS_STORE_MESVIEW group by 物料编码"""
        sc = SqlClient(sql=sql)
        temp = sc.all()
        result = []
        for instance in temp:
            try:
                material_type = instance[4].split("-")[1]
            except:
                material_type = instance[4]
            if stage:
                if material_type == stage:
                    self.data_adapt(instance, material_type)
                    result.append(self.data_adapt(instance, material_type))
            else:
                self.data_adapt(instance, material_type)
                result.append(self.data_adapt(instance, material_type))
        count = len(result)
        result = result[st:et]
        sc.close()
        return Response({'results': result, "count": count})


@method_decorator([api_recorder], name="dispatch")
class OutWorkFeedBack(APIView):

    # 出库反馈
    @atomic
    def post(self, request):
        """WMS->MES:任务编号、物料信息ID、物料名称、PDM号（促进剂以外为空）、批号、条码、重量、重量单位、
        生产日期、使用期限、托盘RFID、工位（出库口）、MES->WMS:信息接收成功or失败"""
        # 任务编号

        data = request.data
        # data = {'order_no':'20201114131845',"pallet_no":'20102494',
        #         'location':'二层前端','qty':'2','weight':'2.00',
        #         'quality_status':'合格','lot_no':'122222',
        #         'inout_num_type':'123456','fin_time':'2020-11-10 15:02:41'
        #         }
        if data:
            data.pop("status", None)
            order_no = data.get('order_no')
            if order_no:
                temp = InventoryLog.objects.filter(order_no=order_no).aggregate(all_qty=Sum('qty'))
                all_qty = temp.get("all_qty")
                if all_qty:
                    all_qty += int(data.get("qty"))
                else:
                    all_qty = int(data.get("qty"))
                dp_obj = DeliveryPlan.objects.filter(order_no=order_no).first()
                need_qty = dp_obj.need_qty if dp_obj else 2
                if int(all_qty) >= need_qty:  # 若加上当前反馈后出库数量已达到订单需求数量则改为(1:完成)
                    dp_obj.status = 1
                    dp_obj.finish_time = datetime.datetime.now()
                    dp_obj.save()
                    DeliveryPlanStatus.objects.create(warehouse_info=dp_obj.warehouse_info,
                                                      order_no=order_no,
                                                      order_type=dp_obj.order_type,
                                                      status=1,
                                                      created_user=dp_obj.created_user,
                                                      )
                il_dict = {}
                il_dict['warehouse_no'] = dp_obj.warehouse_info.no
                il_dict['warehouse_name'] = dp_obj.warehouse_info.name
                il_dict['inout_reason'] = dp_obj.inventory_reason
                il_dict['unit'] = dp_obj.unit
                il_dict['initiator'] = dp_obj.created_user
                il_dict['material_no'] = dp_obj.material_no
                il_dict['start_time'] = dp_obj.created_date
                il_dict['order_type'] = dp_obj.order_type
                material = Material.objects.filter(material_no=dp_obj.material_no).first()
                material_inventory_dict = {
                    "material": material,
                    "container_no": data.get("pallet_no"),
                    "site_id": 15,
                    "qty": data.get("qty"),
                    "unit": dp_obj.unit,
                    "unit_weight": float(data.get("weight")) / float(data.get("qty")),
                    "total_weight": data.get("weight"),
                    "quality_status": data.get("quality_status"),
                    "lot_no": data.get("lot_no"),
                    "location": "预留",
                    "warehouse_info": dp_obj.warehouse_info
                }
            else:
                raise ValidationError("订单号不能为空")
            try:
                InventoryLog.objects.create(**data, **il_dict)
                MaterialInventory.objects.create(**material_inventory_dict)
            except Exception as e:
                logger.error(e)
                result = {"99": "FALSE", f"message":"反馈失败，原因: {e}"}
            else:
                result = {"01":"TRUES", "message":"反馈成功，OK"}

            return Response(result)
        return Response({"99": "FALSE", "message":"反馈失败，原因: 未收到具体的出库反馈信息，请检查请求体数据"})


@method_decorator([api_recorder], name="dispatch")
class PutPlanManagement(ModelViewSet):
    queryset = DeliveryPlan.objects.filter().order_by("-created_date")
    serializer_class = PutPlanManagementSerializer
    filter_backends = [DjangoFilterBackend]
    filter_class = PutPlanManagementFilter

    def create(self, request, *args, **kwargs):
        data = request.data
        if not isinstance(data, list):
            raise ValidationError('参数错误')
        for item in data:
            s = PutPlanManagementSerializer(data=item, context={'request': request})
            if not s.is_valid():
                raise ValidationError(s.errors)
            s.save()
        return Response('新建成功')


@method_decorator([api_recorder], name="dispatch")
class OverdueMaterialManagement(ModelViewSet):
    queryset = MaterialInventory.objects.filter()
    serializer_class = OverdueMaterialManagementSerializer
    filter_backends = [DjangoFilterBackend]


@method_decorator([api_recorder], name="dispatch")
class MaterialInventoryManageViewSet(viewsets.ReadOnlyModelViewSet):
    """物料库存信息|线边库|终炼胶库|原材料库"""

    MODEL, SERIALIZER = 0, 1
    INVENTORY_MODEL_BY_NAME = {
        '线边库': [XBMaterialInventory, XBKMaterialInventorySerializer],
        '终炼胶库': [BzFinalMixingRubberInventory, BzFinalMixingRubberInventorySerializer],
        '帘布库': [BzFinalMixingRubberInventoryLB, BzFinalMixingRubberLBInventorySerializer],
        '原材料库': [WmsInventoryStock, WmsInventoryStockSerializer],
        '混炼胶库': [BzFinalMixingRubberInventory, BzFinalMixingRubberInventorySerializer],
    }
    permission_classes = (permissions.IsAuthenticated,)

    # filter_backends = (DjangoFilterBackend,)

    def divide_tool(self, index):
        warehouse_name = self.request.query_params.get('warehouse_name', None)
        if warehouse_name and warehouse_name in self.INVENTORY_MODEL_BY_NAME:
            return self.INVENTORY_MODEL_BY_NAME[warehouse_name][index]
        else:
            raise ValidationError('无此仓库名')

    def get_query_params(self):
        for query in 'material_type', 'container_no', 'material_no':
            yield self.request.query_params.get(query, None)

    def get_queryset(self):
        model = self.divide_tool(self.MODEL)
        queryset = None
        material_type, container_no, material_no = self.get_query_params()
        if model == XBMaterialInventory:
            queryset = model.objects.all()
        elif model == BzFinalMixingRubberInventory:
            # 出库计划弹框展示的库位数据需要更具库位状态进行筛选其他页面不需要
            if self.request.query_params.get("location_status"):
                queryset = model.objects.using('bz').filter(location_status="有货货位")
            else:
                queryset = model.objects.using('bz').all()
            quality_status = self.request.query_params.get('quality_status', None)
            if quality_status:
                queryset = queryset.filter(quality_status=quality_status)
        elif model == BzFinalMixingRubberInventoryLB:
            # 出库计划弹框展示的库位数据需要更具库位状态进行筛选其他页面不需要
            if self.request.query_params.get("location_status"):
                queryset = model.objects.using('lb').filter(location_status="有货货位")
            else:
                queryset = model.objects.using('lb').all()
            quality_status = self.request.query_params.get('quality_status', None)
            if quality_status:
                queryset = queryset.filter(quality_status=quality_status)
        if queryset:
            if material_type and model != BzFinalMixingRubberInventory:
                queryset = queryset.filter(material_type__icontains=material_type)
            if material_no:
                queryset = queryset.filter(material_no__icontains=material_no)
            if container_no:
                queryset = queryset.filter(container_no__icontains=container_no)
            return queryset
        if model == WmsInventoryStock:
            queryset = model.objects.using('wms').raw(WmsInventoryStock.get_sql(material_type, material_no))
        return queryset

    def get_serializer_class(self):
        return self.divide_tool(self.SERIALIZER)


@method_decorator([api_recorder], name="dispatch")
class InventoryLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = InventoryLog.objects.order_by('-start_time')
    serializer_class = InventoryLogSerializer
    permission_classes = (permissions.IsAuthenticated,)
    filter_backends = (DjangoFilterBackend,)
    filter_class = InventoryLogFilter


@method_decorator([api_recorder], name="dispatch")
class MaterialCount(APIView):

    def get(self, request):
        params = request.query_params
        store_name = params.get('store_name')
        if not store_name:
            raise ValidationError("缺少立库名参数，请检查后重试")
        if store_name == "终炼胶库":
            try:
                ret = BzFinalMixingRubberInventory.objects.using('bz').values('material_no').annotate(
                    all_qty=Sum('qty')).values('material_no', 'all_qty')
            except:
                raise ValidationError("终炼胶库连接失败")
        elif store_name == "混炼胶库":
            # TODO 暂时这么写
            try:
                ret = BzFinalMixingRubberInventory.objects.using('bz').values('material_no').annotate(
                    all_qty=Sum('qty')).values('material_no', 'all_qty')
            except:
                raise ValidationError("混炼胶库连接失败")
        elif store_name == "帘布库":
            try:
                ret = BzFinalMixingRubberInventoryLB.objects.using('lb').values('material_no').annotate(
                    all_qty=Sum('qty')).values('material_no', 'all_qty')
            except:
                raise ValidationError("帘布库库连接失败")
        # elif store_name == "原材料库":
        else:
            ret = []
        return Response(ret)


class ReversalUseFlagMixin:

    @action(detail=True, methods=['put'])
    def reversal_use_flag(self, request, pk=None):
        obj = self.get_object()
        obj.use_flag = not obj.use_flag
        obj.save()
        serializer = self.serializer_class(obj)
        return Response(serializer.data)


class AllMixin:

    def list(self, request, *args, **kwargs):
        if 'all' in self.request.query_params:
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        return super().list(request, *args, **kwargs)


@method_decorator([api_recorder], name="dispatch")
class WarehouseInfoViewSet(ReversalUseFlagMixin, AllMixin, viewsets.ModelViewSet):
    queryset = WarehouseInfo.objects.all()
    serializer_class = WarehouseInfoSerializer
    permission_classes = (permissions.IsAuthenticated,)
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ['name']

    @action(detail=False)
    def warehouse_names(self, request):
        names = WarehouseInfo.objects.values_list('name', flat=True).distinct()
        return Response(names)


@method_decorator([api_recorder], name="dispatch")
class StationInfoViewSet(ReversalUseFlagMixin, AllMixin, viewsets.ModelViewSet):
    queryset = Station.objects.all()
    serializer_class = StationSerializer
    permission_classes = (permissions.IsAuthenticated,)
    filter_backends = (DjangoFilterBackend,)
    filter_class = StationFilter


@method_decorator([api_recorder], name="dispatch")
class WarehouseMaterialTypeViewSet(ReversalUseFlagMixin, viewsets.ModelViewSet):
    queryset = WarehouseMaterialType.objects.all()
    serializer_class = WarehouseMaterialTypeSerializer
    permission_classes = (permissions.IsAuthenticated,)
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ['warehouse_info']


@method_decorator([api_recorder], name="dispatch")
class PutPlanManagementLB(ModelViewSet):
    queryset = DeliveryPlanLB.objects.filter().order_by("-created_date")
    serializer_class = PutPlanManagementSerializerLB
    filter_backends = [DjangoFilterBackend]
    filter_class = PutPlanManagementLBFilter

    def create(self, request, *args, **kwargs):
        data = request.data
        if isinstance(data, list):
            for item in data:
                s = PutPlanManagementSerializerLB(data=item, context={'request': request})
                if not s.is_valid():
                    raise ValidationError(s.errors)
                s.save()
        elif isinstance(data, dict):
            s = PutPlanManagementSerializerLB(data=data, context={'request': request})
            if not s.is_valid():
                raise ValidationError(s.errors)
            s.save()
        else:
            raise ValidationError('参数错误')
        return Response('新建成功')


@method_decorator([api_recorder], name="dispatch")
class DispatchPlanViewSet(ModelViewSet):
    """发货计划管理"""
    """
    发货终端设计67调用的接口在这
    6、发货页面：点击关闭调用改发货计划接口				
    7、发货页面：点击完成调用改发货计划接口				
    """
    queryset = DispatchPlan.objects.filter(delete_flag=False)
    serializer_class = DispatchPlanSerializer
    filter_backends = [DjangoFilterBackend]
    filter_class = DispatchPlanFilter

    def create(self, request, *args, **kwargs):
        data = request.data
        data['dispatch_user'] = request.user.username
        data['order_no'] = 'FH' + datetime.datetime.now().strftime('%Y%m%d%H%M%S') + str(
            random.randint(1, 99))
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.status in [2, 4]:
            instance.status = 5
            instance.last_updated_user = request.user
            instance.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            raise ValidationError('只有执行中和新建才可以关闭！')


class DispatchLocationViewSet(ModelViewSet):
    """目的地"""
    queryset = DispatchLocation.objects.filter(delete_flag=False)
    serializer_class = DispatchLocationSerializer
    filter_backends = [DjangoFilterBackend]
    filter_class = DispatchLocationFilter

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        if self.request.query_params.get('all'):
            data = queryset.values('id', 'name')
            return Response({'results': data})
        return super().list(self, request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.use_flag:
            instance.use_flag = False
        else:
            instance.use_flag = True
        return Response(status=status.HTTP_204_NO_CONTENT)


class DispatchLogViewSet(ModelViewSet):
    """发货履历管理"""
    """
        发货终端设计123调用的接口在这
        1、详情页： 调用 查询发货履历接口					
        2、撤销页查询：调用查询发货履历接口 参数为lotno					
        3、撤销页确认：调用新增发货履历接口					
    """
    queryset = DispatchLog.objects.filter(delete_flag=False)
    serializer_class = DispatchLogSerializer
    filter_backends = [DjangoFilterBackend]
    filter_class = DispatchLogFilter


class DispatchPlanList(APIView):
    """发货终端设计4"""
    """	4、发货页面：调用获取未完成单号接口获取单号列表					
    """

    # 伪代码
    def get(self, request):
        order_no_list = DispatchPlan.objects.filter(delete_flag=False).exclude(status=1).values_list('order_no',
                                                                                                     flat=True)
        return Response(order_no_list)


class DispatchPlanUpdate(APIView):
    """发货终端设计5"""
    """5、发货页面：每次扫码成功，更新已发数量和重量,后端需要写发货履历	
    """

    # 伪代码
    def get(self, request):
        dp_obj = DispatchPlan.objects.get(id=1)
        dl_dict = {'order_no': dp_obj.order_no,
                   'pallet_no': '这个字段不知道咋取',
                   'need_qty': dp_obj.need_qty,
                   'need_weight': dp_obj.need_weight,
                   'dispatch_type': dp_obj.dispatch_type,
                   'material_no': dp_obj.material_no,
                   'quality_status': '这个字段不知道咋取',
                   'lot_no': '这个字段不知道咋取',
                   'order_type': dp_obj.order_type,
                   'status': dp_obj.status,
                   'qty': dp_obj.qty,
                   'weight': dp_obj.qty * ProductBatching.objects.filter(
                       stage_product_batch_no=dp_obj.material_no).first().batching_weight,
                   'dispatch_location': dp_obj.dispatch_location,
                   'dispatch_user': dp_obj.dispatch_user,
                   'fin_time': dp_obj.fin_time
                   }
        DispatchLog.objects.create(**dl_dict)
        return Response('OK')
