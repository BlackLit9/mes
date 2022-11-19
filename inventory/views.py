import copy
import datetime
import decimal
import json
import logging
import math
import random
import re
import time
from io import BytesIO
from operator import itemgetter

import pandas as pd
import requests
import xlwt
import xmltodict
from django.core.paginator import Paginator
from django.db.models import Sum, Count, Q, F, Max, FloatField, Min
from django.db.transaction import atomic
from django.forms import model_to_dict
from django.http import HttpResponse

from django.utils.decorators import method_decorator
from rest_framework import mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.mixins import UpdateModelMixin, RetrieveModelMixin
from rest_framework.generics import ListAPIView, GenericAPIView
from rest_framework.mixins import ListModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from basics.models import GlobalCode, WorkSchedulePlan
from equipment.utils import gen_template_response
from inventory.filters import StationFilter, PutPlanManagementLBFilter, PutPlanManagementFilter, \
    DispatchPlanFilter, DispatchLogFilter, DispatchLocationFilter, PutPlanManagementFinalFilter, \
    MaterialPlanManagementFilter, BarcodeQualityFilter, CarbonPlanManagementFilter, \
    MixinRubberyOutBoundOrderFilter, FinalRubberyOutBoundOrderFilter, DepotSiteDataFilter, DepotDataFilter, \
    SulfurResumeFilter, DepotSulfurFilter, PalletDataFilter, DepotResumeFilter, SulfurDepotSiteFilter, SulfurDataFilter, \
    OutBoundDeliveryOrderFilter, OutBoundDeliveryOrderDetailFilter, WmsNucleinManagementFilter

from inventory.models import InventoryLog, WarehouseInfo, Station, WarehouseMaterialType, \
    BzFinalMixingRubberInventoryLB, DeliveryPlanLB, DispatchPlan, DispatchLog, DispatchLocation, \
    MixGumOutInventoryLog, MixGumInInventoryLog, DeliveryPlanFinal, MaterialOutPlan, BarcodeQuality, \
    MaterialOutHistory, FinalGumOutInventoryLog, Depot, \
    DepotSite, DepotPallt, Sulfur, SulfurDepot, SulfurDepotSite, MaterialInHistory, \
    CarbonOutPlan, FinalRubberyOutBoundOrder, MixinRubberyOutBoundOrder, FinalGumInInventoryLog, OutBoundDeliveryOrder, \
    OutBoundDeliveryOrderDetail, WMSReleaseLog, WmsInventoryMaterial, WMSMaterialSafetySettings, WmsNucleinManagement, \
    WMSExceptHandle, MaterialOutHistoryOther, MaterialOutboundOrder, MaterialEntrance, HfBakeMaterialSet, HfBakeLog, \
    WMSOutboundHistory, CancelTask, ProductInventoryLocked, ProductStockDailySummary, THOutHistory, THInHistory, \
    THOutHistoryOther
from inventory.models import DeliveryPlan, MaterialInventory
from inventory.serializers import PutPlanManagementSerializer, \
    OverdueMaterialManagementSerializer, WarehouseInfoSerializer, StationSerializer, WarehouseMaterialTypeSerializer, \
    PutPlanManagementSerializerLB, BzFinalMixingRubberLBInventorySerializer, DispatchPlanSerializer, \
    DispatchLogSerializer, DispatchLocationSerializer, PutPlanManagementSerializerFinal, \
    InventoryLogOutSerializer, MixinRubberyOutBoundOrderSerializer, FinalRubberyOutBoundOrderSerializer, \
    MaterialPlanManagementSerializer, BarcodeQualitySerializer, WmsStockSerializer, InOutCommonSerializer, \
    CarbonPlanManagementSerializer, DepotModelSerializer, DepotSiteModelSerializer, DepotPalltModelSerializer, \
    SulfurResumeModelSerializer, DepotSulfurInfoModelSerializer, PalletDataModelSerializer, DepotResumeModelSerializer, \
    SulfurDepotModelSerializer, SulfurDepotSiteModelSerializer, SulfurDataModelSerializer, DepotSulfurModelSerializer, \
    DepotPalltInfoModelSerializer, OutBoundDeliveryOrderSerializer, OutBoundDeliveryOrderDetailSerializer, \
    OutBoundTasksSerializer, WmsInventoryMaterialSerializer, WmsNucleinManagementSerializer, \
    MaterialOutHistoryOtherSerializer, MaterialOutHistorySerializer, WMSExceptHandleSerializer, \
    BzMixingRubberInventorySearchSerializer, BzFinalRubberInventorySearchSerializer, \
    OutBoundDeliveryOrderUpdateSerializer, ProductInOutHistorySerializer, OutBoundDeliveryOrderDetailListSerializer, \
    THInOutCommonSerializer, THOutHistoryOtherSerializer, THOutHistorySerializer
from inventory.models import WmsInventoryStock
from inventory.serializers import BzFinalMixingRubberInventorySerializer, \
    WmsInventoryStockSerializer, InventoryLogSerializer
from mes import settings
from mes.common_code import SqlClient, response
from mes.conf import WMS_CONF, TH_CONF, WMS_URL, TH_URL, HF_CONF, JZ_EQUIP_NO
from mes.derorators import api_recorder
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions

from mes.paginations import SinglePageNumberPagination
from mes.permissions import PermissionClass
from mes.settings import DEBUG, DATABASES
from plan.models import ProductClassesPlan, BatchingClassesPlan
from production.models import PalletFeedbacks, TrainsFeedbacks
from quality.deal_result import receive_deal_result
from quality.models import LabelPrint, MaterialDealResult, LabelPrintLog, ExamineMaterial, \
    MaterialSingleTypeExamineResult, WMSMooneyLevel, MaterialInspectionRegistration
from quality.serializers import MaterialDealResultListSerializer
from quality.utils import update_wms_quality_result
from recipe.models import MaterialAttribute
from terminal.models import LoadMaterialLog, WeightBatchingLog, WeightPackageLog, BarCodeTraceDetail, ReportWeight, JZReportWeight
from terminal.utils import get_real_ip, get_current_factory_date
from .conf import IS_BZ_USING
from .conf import wms_ip, wms_port, cb_ip, cb_port
from .models import MaterialInventory as XBMaterialInventory
from .models import BzFinalMixingRubberInventory
from .serializers import XBKMaterialInventorySerializer
from .utils import OUTWORKUploader, OUTWORKUploaderLB, HFSystem

logger = logging.getLogger('send_log')


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
        material_no = params.get("material_no")
        filter_str = ""
        if material_type:
            if filter_str:
                filter_str += f" and tim.MaterialGroupName like '%%{material_type}%%'"
            else:
                filter_str += f" where tim.MaterialGroupName like '%%{material_type}%%'"
        if material_no:
            if filter_str:
                filter_str += f" and tis.MaterialCode like '%%{material_no}%%'"
            else:
                filter_str += f" where tis.MaterialCode like '%%{material_no}%%'"
        sql = f"""select sum(tis.Quantity) qty, max(tis.MaterialName) material_name,
                       sum(tis.WeightOfActual) weight,tis.MaterialCode material_no,
                       max(tis.ProductionAddress) address, sum(tis.WeightOfActual)/sum(tis.Quantity) unit_weight,
                       max(tis.StandardUnit) unit, max(tim.MaterialGroupName) material_type,
                       Row_Number() OVER (order by tis.MaterialCode) sn, tis.StockDetailState status
                            from t_inventory_stock tis left join t_inventory_material tim on tim.MaterialCode=tis.MaterialCode
                        {filter_str}
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
            "standard_flag": instance[3],
            "site": instance[0]
        }
        return temp_dict

    def list(self, request, *args, **kwargs):
        params = request.query_params
        page = params.get("page", 1)
        page_size = params.get("page_size", 10)
        stage = params.get("stage")
        material_no = params.get("material_no")
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
        filter_str = ""
        if stage:
            if stage not in stage_list:
                raise ValidationError("胶料段次异常请修正后重试")
            if filter_str:
                filter_str += f" AND 物料编码 like '%{stage}%'"
            else:
                filter_str += f" where 物料编码 like '%{stage}%'"
        if material_no:
            if filter_str:
                filter_str += f" AND 物料编码 like '%{material_no}%'"
            else:
                filter_str += f" where 物料编码 like '%{material_no}%'"
        sql = f"""SELECT max(库房名称) as 库房名称, sum(数量) as 数量, sum(重量) as 重量, 品质等级, 物料编码, Row_Number() OVER (order by 物料编码) sn
            FROM v_ASRS_STORE_MESVIEW {filter_str} group by 物料编码, 品质等级 order by 物料编码"""
        sql_all = """SELECT sum(数量) FROM v_ASRS_STORE_MESVIEW"""
        sql_fm = """SELECT sum(数量) FROM v_ASRS_STORE_MESVIEW where 物料编码 like '%FM%'"""
        sc = SqlClient(sql=sql)
        sc_fm = SqlClient(sql=sql_fm)
        sc_all = SqlClient(sql=sql_all)
        fm_count = sc_fm.all()[0][0]
        other_count = sc_all.all()[0][0] - fm_count
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
        return Response({'results': result, "count": count, "fm_count": fm_count, "other_count": other_count})


@method_decorator([api_recorder], name="dispatch")
class OutWorkFeedBack(APIView):
    """{"order_no": "ZJO202109060057",
     "pallet_no": "20104101",
     "location": "2-3-5-1",
     "qty": 1,
     "weight": 700.0,
     "quality_status": "2",
     "lot_no": "88888888",
     "inventory_type": "生产出库",
     "fin_time": "2021-09-07T00: 32:27.4085235Z",
     "status": "- 无 - "}"""

    # 出库反馈
    def post(self, request):
        logger.info('北自出库反馈数据：{}'.format(request.data))
        data = self.request.data
        if data:
            lot_no = data.get("lot_no", "99999999")  # 给一个无法查到的lot_no
            order_no = data.get('order_no')
            if order_no:
                dp_obj = OutBoundDeliveryOrderDetail.objects.filter(order_no=order_no).first()
                if dp_obj:
                    dp_obj.status = 3
                    dp_obj.finish_time = datetime.datetime.now()
                    dp_obj.save()
                    OutBoundDeliveryOrderDetail.objects.filter(
                        # location=dp_obj.location,
                        status=2,
                        pallet_no=dp_obj.pallet_no
                        # outbound_delivery_order__warehouse=dp_obj.outbound_delivery_order.warehouse
                    ).update(status=3)
                    # try:
                    #     depot_name = '混炼线边库区' if dp_obj.outbound_delivery_order.warehouse == '混炼胶库' else "终炼线边库区"
                    #     depot_site_name = '混炼线边库位' if dp_obj.outbound_delivery_order.warehouse == '混炼胶库' else "终炼线边库位"
                    #     depot, _ = Depot.objects.get_or_create(depot_name=depot_name,
                    #                                            description=depot_name)
                    #     depot_site, _ = DepotSite.objects.get_or_create(depot=depot,
                    #                                                     depot_site_name=depot_site_name,
                    #                                                     description=depot_site_name)
                    #     DepotPallt.objects.create(enter_time=datetime.datetime.now(),
                    #                               pallet_status=1,
                    #                               pallet_data=PalletFeedbacks.objects.filter(lot_no=dp_obj.lot_no).first(),
                    #                               depot_site=depot_site
                    #                               )
                    # except Exception:
                    #     pass
                else:
                    return Response({"99": "FALSE", "message": "该订单非mes下发订单"})
                station = dp_obj.outbound_delivery_order.station
                station_dict = {
                    "一层前端": 3,
                    "一层后端": 4,
                    "二层前端": 5,
                    "二层后端": 6,
                    "炼胶#出库口#1": 7,
                    "炼胶#出库口#2": 8,
                    "炼胶#出库口#3": 9,
                    "帘布#出库口#0": 10
                }
                try:
                    label = receive_deal_result(lot_no)
                    if label:
                        LabelPrint.objects.create(label_type=station_dict.get(station), lot_no=lot_no, status=0,
                                                  data=label)
                        try:
                            LabelPrintLog.objects.create(
                                result=MaterialDealResult.objects.filter(lot_no=lot_no).first(),
                                created_user=dp_obj.outbound_delivery_order.created_user.username,
                                location=station)
                        except Exception:
                            pass
                except AttributeError as a:
                    logger.error(f"条码错误{a}")
                except Exception as e:
                    logger.error(f"未知错误{e}")
                return Response({"01": "TRUES", "message": "反馈成功，OK"})
            else:
                raise ValidationError("订单号不能为空")
        return Response({"99": "FALSE", "message": "反馈失败，原因: 未收到具体的出库反馈信息，请检查请求体数据"})


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
        '终炼胶库': [BzFinalMixingRubberInventoryLB, BzFinalMixingRubberLBInventorySerializer],
        '帘布库': [BzFinalMixingRubberInventoryLB, BzFinalMixingRubberLBInventorySerializer],
        '原材料库': [WmsInventoryStock, WmsInventoryStockSerializer],
        '混炼胶库': [BzFinalMixingRubberInventory, BzFinalMixingRubberInventorySerializer],
        '炭黑库': [WmsInventoryStock, WmsInventoryStockSerializer],
    }
    permission_classes = (permissions.IsAuthenticated,)

    # filter_backends = (DjangoFilterBackend,)

    def divide_tool(self, index):
        warehouse_name = self.request.query_params.get('warehouse_name', None)
        if warehouse_name and warehouse_name in self.INVENTORY_MODEL_BY_NAME:
            return self.INVENTORY_MODEL_BY_NAME[warehouse_name][index]
        else:
            raise ValidationError(f'该仓库请移步{warehouse_name}专项页面查看')

    def get_query_params(self):
        for query in ('material_type', 'container_no', 'material_no', "order_no", "location", 'tunnel', 'lot_no'):
            yield self.request.query_params.get(query, None)

    def get_queryset(self):
        warehouse_name = self.request.query_params.get('warehouse_name', None)
        quality_status = self.request.query_params.get('quality_status', None)
        lot_existed = self.request.query_params.get('lot_existed')
        # 终炼胶，帘布库区分 货位地址开头1-4终炼胶   5-6帘布库
        model = self.divide_tool(self.MODEL)
        queryset = None
        material_type, container_no, material_no, order_no, location, tunnel, lot_no = self.get_query_params()
        if model == XBMaterialInventory:
            queryset = model.objects.all()
        elif model == BzFinalMixingRubberInventory:
            # 出库计划弹框展示的库位数据需要更具库位状态进行筛选其他页面不需要
            # if self.request.query_params.get("location_status"):
            #     queryset = model.objects.using('bz').filter(location_status=self.request.query_params.get("location_status"))
            # else:
            queryset = model.objects.using('bz').all().order_by('in_storage_time')
            if quality_status:
                queryset = queryset.filter(quality_level=quality_status)
        elif model == BzFinalMixingRubberInventoryLB:
            # 出库计划弹框展示的库位数据需要更具库位状态进行筛选其他页面不需要
            # if self.request.query_params.get("location_status"):
            #     queryset = model.objects.using('lb').filter(location_status=self.request.query_params.get("location_status"))
            # else:
            queryset = model.objects.using('lb').order_by('in_storage_time')
            if lot_existed:
                if lot_existed == '1':
                    queryset = queryset.exclude(lot_no__isnull=True)
                else:
                    queryset = queryset.filter(lot_no__isnull=True)
            if warehouse_name == "帘布库":
                queryset = queryset.filter(store_name="帘布库")
                status_dict = {"合格品": "一等品", "不合格品": "三等品", "一等品": "一等品", "三等品": "三等品"}
                if quality_status:
                    queryset = queryset.filter(quality_level=status_dict.get(quality_status, "一等品"))
            else:
                queryset = queryset.filter(store_name="炼胶库")
                if quality_status:
                    queryset = queryset.filter(quality_level=quality_status)
        if queryset:
            if material_type and model not in [BzFinalMixingRubberInventory, XBMaterialInventory,
                                               BzFinalMixingRubberInventoryLB]:
                queryset = queryset.filter(material_type__icontains=material_type)
            if material_type and model == XBMaterialInventory:
                queryset = queryset.filter(material__material_type__global_name__icontains=material_type)
            if material_no:
                queryset = queryset.filter(material_no__icontains=material_no)
            if container_no:
                queryset = queryset.filter(container_no__icontains=container_no)
            if order_no and model in [BzFinalMixingRubberInventory, BzFinalMixingRubberInventoryLB]:
                queryset = queryset.filter(bill_id__icontains=order_no)
            if location:
                queryset = queryset.filter(location__icontains=location)
            if tunnel:
                queryset = queryset.filter(location__istartswith=tunnel)
            if lot_no:
                queryset = queryset.filter(lot_no__icontains=lot_no)
            return queryset
        if model == WmsInventoryStock:
            quality_status = {"合格品": 1, "不合格品": 2, None: 1, "": 1}[quality_status]
            if warehouse_name == "原材料库":
                queryset = model.objects.using('wms').raw(
                    WmsInventoryStock.get_sql(material_type, material_no, container_no, order_no, location, tunnel,
                                              quality_status, lot_no))
            else:
                queryset = model.objects.using('cb').raw(
                    WmsInventoryStock.get_sql(material_type, material_no, container_no, order_no, location, tunnel,
                                              quality_status, lot_no))
        return queryset

    def get_serializer_class(self):
        return self.divide_tool(self.SERIALIZER)


@method_decorator([api_recorder], name="dispatch")
class InventoryLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = InventoryLog.objects.order_by('-start_time')
    serializer_class = InventoryLogSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        filter_dict = {}
        store_name = self.request.query_params.get("warehouse_name", '混炼胶库')
        start_time = self.request.query_params.get("start_time")
        end_time = self.request.query_params.get("end_time")
        task_start_st = self.request.query_params.get("task_start_st")
        task_start_et = self.request.query_params.get("task_start_et")
        task_end_st = self.request.query_params.get("task_end_st")
        task_end_et = self.request.query_params.get("task_end_et")
        location = self.request.query_params.get("location")
        material_no = self.request.query_params.get("material_no")
        e_material_no = self.request.query_params.get("e_material_no")
        material_name = self.request.query_params.get("material_name")
        quality_status = self.request.query_params.get("quality_status")
        order_no = self.request.query_params.get("order_no")
        lot_no = self.request.query_params.get("lot_no")
        pallet_no = self.request.query_params.get("pallet_no")
        order_type = self.request.query_params.get("order_type")
        batch_no = self.request.query_params.get("batch_no")
        l_batch_no = self.request.query_params.get("l_batch_no")
        is_entering = self.request.query_params.get("is_entering")
        tunnel = self.request.query_params.get("tunnel")
        task_status = self.request.query_params.get("task_status")
        if location:
            filter_dict.update(location__icontains=location)
        if material_no:
            filter_dict.update(material_no__icontains=material_no)
        if e_material_no:
            filter_dict.update(material_no=e_material_no)
        if order_no:
            filter_dict.update(order_no__icontains=order_no)
        if lot_no:
            filter_dict.update(lot_no__icontains=lot_no)
        if pallet_no:
            filter_dict.update(pallet_no__icontains=pallet_no)
        if store_name == "混炼胶库":
            if start_time:
                filter_dict.update(start_time__gte=start_time)
            if end_time:
                filter_dict.update(start_time__lte=end_time)
            if tunnel:
                filter_dict.update(location__startswith='{}-'.format(tunnel))
            if order_type == "出库":
                if self.request.query_params.get("type") == "正常出库":
                    actual_type = "生产出库"
                    filter_dict.update(inout_num_type=actual_type)
                elif self.request.query_params.get("type") == "指定出库":
                    actual_type = "快检出库"
                    filter_dict.update(inout_num_type=actual_type)
                else:
                    actual_type = "生产出库"
                temp_set = list(MixGumOutInventoryLog.objects.using('bz').filter(**filter_dict).order_by('-start_time'))
                # 目前先只查北自出入库履历
                # filter_dict.pop("inout_num_type", None)
                # temp_set += list(InventoryLog.objects.filter(warehouse_name=store_name, inventory_type=actual_type,
                #                                              **filter_dict).order_by('-start_time'))
                return temp_set
            else:
                return MixGumInInventoryLog.objects.using('bz').filter(**filter_dict)
        elif store_name == "终炼胶库":
            if start_time:
                filter_dict.update(start_time__gte=start_time)
            if end_time:
                filter_dict.update(start_time__lte=end_time)
            if tunnel:
                filter_dict.update(location__startswith='{}-'.format(tunnel))
            if order_type == "出库":
                # if self.request.query_params.get("type") == "正常出库":
                #     actual_type = "生产出库"
                #     filter_dict.update(inout_num_type=actual_type)
                # elif self.request.query_params.get("type") == "指定出库":
                #     actual_type = "快检出库"
                #     filter_dict.update(inout_num_type=actual_type)
                # else:
                #     actual_type = "生产出库"
                return FinalGumOutInventoryLog.objects.using('lb').filter(**filter_dict).filter(material_no__icontains="M").order_by('-start_time')
            else:
                return FinalGumInInventoryLog.objects.using('lb').filter(**filter_dict).filter(material_no__icontains="M").order_by('-start_time')
        elif store_name == "帘布库":
            if start_time:
                filter_dict.update(start_time__gte=start_time)
            if end_time:
                filter_dict.update(start_time__lte=end_time)
            if order_type == "出库":
                # if self.request.query_params.get("type") == "正常出库":
                #     actual_type = "生产出库"
                #     filter_dict.update(inout_num_type=actual_type)
                # elif self.request.query_params.get("type") == "指定出库":
                #     actual_type = "快检出库"
                #     filter_dict.update(inout_num_type=actual_type)
                # else:
                #     actual_type = "生产出库"
                return FinalGumOutInventoryLog.objects.using('lb').filter(**filter_dict).filter(
                    Q(location__startswith=5) |
                    Q(location__startswith=6)).order_by('-start_time')
            else:
                return FinalGumInInventoryLog.objects.using('lb').filter(
                    **filter_dict).filter(Q(location__startswith=5) |
                                          Q(location__startswith=6)
                                          ).order_by('-start_time')
        elif store_name in ("原材料库", '炭黑库'):
            database = 'wms' if store_name == '原材料库' else 'cb'
            if order_type == "出库":
                if database == 'wms':
                    queryset = MaterialOutHistory.objects.using(database).order_by('id')
                else:
                    queryset = THOutHistory.objects.using(database).order_by('id')
            else:
                if database == 'wms':
                    queryset = MaterialInHistory.objects.using(database).order_by('id')
                else:
                    queryset = THInHistory.objects.using(database).order_by('id')
            if start_time:
                filter_dict.update(task__start_time__gte=start_time)
            if end_time:
                filter_dict.update(task__start_time__lte=end_time)
            if task_start_st:
                filter_dict.update(task__last_time__gte=task_start_st)
            if task_start_et:
                filter_dict.update(task__last_time__lte=task_start_et)
            if task_end_st:
                filter_dict.update(task__fin_time__gte=task_end_st)
            if task_end_et:
                filter_dict.update(task__fin_time__lte=task_end_et)
            if material_name:
                filter_dict.update(material_name__icontains=material_name)
            if batch_no:
                filter_dict.update(batch_no=batch_no)
            if l_batch_no:
                filter_dict.update(batch_no__icontains=l_batch_no)
            if tunnel:
                filter_dict['location__startswith'] = 'ZCM-{}'.format(tunnel)
            if is_entering:
                if is_entering == 'Y':
                    queryset = queryset.filter(pallet_no__startswith=5)
                elif is_entering == 'N':
                    queryset = queryset.exclude(pallet_no__startswith=5)
            if task_status:
                queryset = queryset.filter(task_status=task_status)
            if quality_status:
                status_map = {'1': "合格品", '2': "抽检中", '3': "不合格品", '4': "过期", '5': "待检"}
                task_nos = list(WMSOutboundHistory.objects.filter(
                    quality_status=status_map.get(quality_status)
                ).values_list('task_no', flat=True))
                filter_dict['order_no__in'] = task_nos
            return queryset.filter(**filter_dict)
        else:
            return []

    def get_serializer_class(self):
        store_name = self.request.query_params.get("warehouse_name", "混炼胶库")
        serializer_dispatch = {
            "混炼胶库": InventoryLogSerializer,
            "终炼胶库": InventoryLogSerializer,
            "原材料库": InOutCommonSerializer,
            "炭黑库": THInOutCommonSerializer,
            "帘布库": InventoryLogSerializer
        }
        return serializer_dispatch.get(store_name)

    def export_xls(self, result):
        response = HttpResponse(content_type='application/vnd.ms-excel')
        filename = '物料出入库履历'
        response['Content-Disposition'] = u'attachment;filename= ' + filename.encode('gbk').decode(
            'ISO-8859-1') + '.xls'
        # 创建一个文件对象
        wb = xlwt.Workbook(encoding='utf8')
        # 创建一个sheet对象
        sheet = wb.add_sheet('出入库信息', cell_overwrite_ok=True)
        style = xlwt.XFStyle()
        style.alignment.wrap = 1

        columns = ['No', '类型', '出入库单号', '质检条码', '托盘号', '机台', '时间/班次', '车号', '物料编码', '出入库原因',
                   '出入库类型', '出入库数', '单位', '重量', '发起人', '发起时间', '完成时间']
        # 写入文件标题
        for col_num in range(len(columns)):
            sheet.write(0, col_num, columns[col_num])
            # 写入数据
        data_row = 1
        for i in result:
            sheet.write(data_row, 0, result.index(i) + 1)
            sheet.write(data_row, 1, i['order_type'])
            sheet.write(data_row, 2, i['order_no'])
            sheet.write(data_row, 3, i['lot_no'])
            sheet.write(data_row, 4, i['pallet_no'])
            sheet.write(data_row, 5, i['product_info']['equip_no'])
            sheet.write(data_row, 6, i['product_info']['classes'])
            sheet.write(data_row, 7, i['product_info']['memo'])
            sheet.write(data_row, 8, i['material_no'])
            sheet.write(data_row, 9, i['inout_reason'])
            sheet.write(data_row, 10, i['inout_num_type'])
            sheet.write(data_row, 11, i['qty'])
            sheet.write(data_row, 12, i['unit'])
            sheet.write(data_row, 13, i['weight'])
            sheet.write(data_row, 14, i['initiator'])
            sheet.write(data_row, 15, i['start_time'])
            sheet.write(data_row, 16, i['fin_time'])
            data_row = data_row + 1
        # 写出到IO
        output = BytesIO()
        wb.save(output)
        # 重新定位到开始
        output.seek(0)
        response.write(output.getvalue())
        return response

    def export_xls2(self, result):
        response = HttpResponse(content_type='application/vnd.ms-excel')
        filename = '物料出入库履历'
        response['Content-Disposition'] = u'attachment;filename= ' + filename.encode('gbk').decode(
            'ISO-8859-1') + '.xls'
        # 创建一个文件对象
        wb = xlwt.Workbook(encoding='utf8')
        # 创建一个sheet对象
        sheet = wb.add_sheet('出入库信息', cell_overwrite_ok=True)
        style = xlwt.XFStyle()
        style.alignment.wrap = 1

        columns = ['序号', '出库单据号', '下架任务号', '巷道编码', '追踪码', '识别卡ID', '库位码', '物料名称', '物料编码',
                   '批次号', '创建时间', '状态', '创建人', '数量', '重量', '件数', '唛头重量']
        # 写入文件标题
        for col_num in range(len(columns)):
            sheet.write(0, col_num, columns[col_num])
            # 写入数据
        data_row = 1
        for i in result:
            sheet.write(data_row, 0, result.index(i) + 1)
            sheet.write(data_row, 1, i['task_no'])
            sheet.write(data_row, 2, i['order_no'])
            sheet.write(data_row, 3, i['location'][4])
            sheet.write(data_row, 4, i['lot_no'])
            sheet.write(data_row, 5, i['pallet_no'])
            sheet.write(data_row, 6, i['location'])
            sheet.write(data_row, 7, i['material_name'])
            sheet.write(data_row, 8, i['material_no'])
            sheet.write(data_row, 9, i['batch_no'])
            sheet.write(data_row, 10, i['start_time'])
            sheet.write(data_row, 11, i['task_status_name'])
            sheet.write(data_row, 12, i['initiator'])
            sheet.write(data_row, 13, i['qty'])
            sheet.write(data_row, 14, i['weight'])
            sheet.write(data_row, 15, i['sl'])
            sheet.write(data_row, 15, i['zl'])
            data_row = data_row + 1
        # 写出到IO
        output = BytesIO()
        wb.save(output)
        # 重新定位到开始
        output.seek(0)
        response.write(output.getvalue())
        return response

    def list(self, request, *args, **kwargs):
        export = self.request.query_params.get('export', None)
        store_name = self.request.query_params.get("warehouse_name", "混炼胶库")
        queryset = self.filter_queryset(self.get_queryset())
        if export:
            serializer = self.get_serializer(self.get_queryset(), many=True)
            if store_name in ('混炼胶库', '终炼胶库', '帘布库'):
                return self.export_xls(serializer.data)
            else:
                return self.export_xls2(serializer.data)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            if store_name in ('原材料库', '炭黑库'):
                task_nos = [item['order_no'] for item in serializer.data]
                test_data = dict(WMSOutboundHistory.objects.filter(task_no__in=task_nos).values_list('task_no', 'quality_status'))
                for item in serializer.data:
                    item['quality_status'] = test_data.get(item['order_no'], None)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


@method_decorator([api_recorder], name="dispatch")
class AdditionalPrintDetailView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        data = self.request.query_params
        location = data.get('location')
        material_no = data.get('material_no')
        start_time = data.get('start_time')
        initiator = data.get('initiator')
        weight = data.get('weight')
        pallet_no = data.get('pallet_no')
        type = data.get('type')
        lot_no = data.get('lot_no') if data.get('lot_no') != '88888888' else \
            re.sub('-| |:', '', start_time[2:]) + type + location.replace('-', '')
        label = receive_deal_result(lot_no)
        if not label:
            label = {
                "id": None, "day_time": start_time[:10], "product_no": material_no, "equip_no": "", "lot_no": lot_no,
                "residual_weight": None, "actual_weight": weight, "operation_user": initiator, "actual_trains": "",
                "classes_group": "", "valid_time": "", "range_showed": 0, "deal_suggestion": "", "deal_user": "",
                "deal_time": "", "production_factory_date": start_time[:10], "deal_result": "",
                "test": {"test_status": "", "test_factory_date": "", "test_class": "", "pallet_no": pallet_no,
                         "test_user": ""},
                "print_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "mtr_list": {"trains": [], "table_head": []}
            }
            # 未快检的正常条码
            data = PalletFeedbacks.objects.filter(lot_no=lot_no).first()
            if data:
                # 获取班组
                record = ProductClassesPlan.objects.filter(plan_classes_uid=data.plan_classes_uid).first()
                group = '' if not record else record.work_schedule_plan.group.global_name
                label.update({'equip_no': data.equip_no, 'classes_group': f'{data.classes}/{group}',
                              'actual_trains': f'{data.begin_trains}/{data.end_trains}'})
        else:
            label = json.loads(label)
        return Response(label)


@method_decorator([api_recorder], name="dispatch")
class AdditionalPrintView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    # 补打印
    def post(self, request):
        """WMS->MES:任务编号、物料信息ID、物料名称、PDM号（促进剂以外为空）、批号、条码、重量、重量单位、
        生产日期、使用期限、托盘RFID、工位（出库口）、MES->WMS:信息接收成功or失败"""
        data = self.request.data
        station_dict = {
            "一层前端": 3,
            "一层后端": 4,
            "二层前端": 5,
            "二层后端": 6,
            "炼胶#出库口#1": 7,
            "炼胶#出库口#2": 8,
            "炼胶#出库口#3": 9,
            "帘布#出库口#0": 10
        }
        for single_data in data:
            # 有条码直接打印, 无条码生成新码
            enable_ip = single_data.pop('enable_ip', '')
            location = single_data.get('location')
            station = single_data.get('station')
            material_no = single_data.get('material_no')
            start_time = single_data.get('start_time')
            initiator = single_data.get('initiator')
            weight = single_data.get('weight')
            pallet_no = single_data.get('pallet_no')
            type = single_data.get('type')
            lot_no = single_data.get('lot_no') if single_data.get('lot_no') != '88888888' else \
                re.sub('-| |:', '', single_data["start_time"][2:]) + type + location.replace('-', '')
            label = receive_deal_result(lot_no)
            if not label:
                label = {
                    "id": None, "day_time": start_time[:10], "product_no": material_no, "equip_no": "",
                    "residual_weight": None, "actual_weight": weight, "operation_user": initiator, "actual_trains": "",
                    "classes_group": "", "valid_time": "", "range_showed": 0, "deal_suggestion": "", "deal_user": "",
                    "deal_time": "", "production_factory_date": start_time[:10], "deal_result": "", "lot_no": lot_no,
                    "test": {"test_status": "", "test_factory_date": "", "test_class": "", "pallet_no": pallet_no,
                             "test_user": ""},
                    "print_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "mtr_list": {"trains": [], "table_head": []}
                }
                # 未快检的正常条码
                data = PalletFeedbacks.objects.filter(lot_no=lot_no).first()
                if data:
                    # 获取班组
                    record = ProductClassesPlan.objects.filter(plan_classes_uid=data.plan_classes_uid).first()
                    group = '' if not record else record.work_schedule_plan.group.global_name
                    label.update({"equip_no": data.equip_no, "classes_group": f"{data.classes}/{group}",
                                  "actual_trains": f"{data.begin_trains}/{data.end_trains}"})
                label = json.dumps(label)
            ip_address = get_real_ip(self.request.META) if enable_ip else None
            LabelPrint.objects.create(label_type=station_dict.get(station), lot_no=lot_no, status=0, data=label, ip_address=ip_address)
        return Response('下发打印完成')


@method_decorator([api_recorder], name="dispatch")
class MaterialCount(APIView):

    def get(self, request):
        params = request.query_params
        store_name = params.get('store_name')
        status = params.get("status")
        if not store_name:
            raise ValidationError("缺少立库名参数，请检查后重试")
        filter_dict = {}
        if status:
            filter_dict.update(quality_level=status)
        if store_name == "终炼胶库":
            try:
                ret = BzFinalMixingRubberInventoryLB.objects.using('lb').filter(**filter_dict).filter(
                    store_name="炼胶库").values(
                    'material_no').annotate(
                    all_qty=Sum('qty'), all_weight=Sum('total_weight')).values('material_no', 'all_qty', 'all_weight')
            except Exception as e:
                raise ValidationError(f"终炼胶库连接失败: {e}")
        elif store_name == "混炼胶库":
            try:
                ret = BzFinalMixingRubberInventory.objects.using('bz').filter(
                    **filter_dict).values(
                    'material_no').annotate(
                    all_qty=Sum('qty'), all_weight=Sum('total_weight')).values('material_no', 'all_qty', 'all_weight')
            except Exception as e:
                raise ValidationError(f"混炼胶库连接失败:{e}")
        elif store_name == "帘布库":
            try:
                filter_dict.pop("quality_level", None)
                if status:
                    filter_dict["quality_status"] = status
                ret = BzFinalMixingRubberInventoryLB.objects.using('lb').filter(**filter_dict).filter(
                    store_name="帘布库").values(
                    'material_no', 'material_name').annotate(
                    all_qty=Sum('qty'), all_weight=Sum('total_weight')).values('material_no', 'all_qty',
                                                                               'material_name', 'all_weight')
            except:
                raise ValidationError("帘布库连接失败")
        elif store_name == "原材料库":
            status_map = {"合格": 1, "不合格": 2}
            try:
                ret = WmsInventoryStock.objects.using('wms').values(
                    'material_no', 'material_name').annotate(
                    all_weight=Sum('total_weight')).values('material_no', 'material_name', 'all_weight')
            except:
                raise ValidationError("原材料库连接失败")
        elif store_name == "炭黑库":
            status_map = {"合格": 1, "不合格": 2}
            try:
                ret = WmsInventoryStock.objects.using('cb').values(
                    'material_no', 'material_name').annotate(
                    all_weight=Sum('total_weight')).values('material_no', 'material_name', 'all_weight')
            except:
                raise ValidationError("原材料库连接失败")
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
    # permission_classes = (permissions.IsAuthenticated,)  # 不需要登录，出库看板有使用
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
class DispatchPlanViewSet(ModelViewSet):
    """
    list:
        发货计划列表
    create:
        新建发货计划
    retrieve:
        发货计划详情
    update:
        修改发货计划
    destroy:
        关闭发货计划
    """
    queryset = DispatchPlan.objects.filter(delete_flag=False).order_by('-created_date')
    serializer_class = DispatchPlanSerializer
    filter_backends = [DjangoFilterBackend]
    filter_class = DispatchPlanFilter
    permission_classes = (IsAuthenticated,)

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


@method_decorator([api_recorder], name="dispatch")
class DispatchLocationViewSet(ModelViewSet):
    """目的地"""
    queryset = DispatchLocation.objects.filter(delete_flag=False)
    serializer_class = DispatchLocationSerializer
    filter_backends = [DjangoFilterBackend]
    filter_class = DispatchLocationFilter
    permission_classes = (IsAuthenticated,)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        if self.request.query_params.get('all'):
            data = queryset.values('id', 'name', 'use_flag')
            return Response({'results': data})
        return super().list(self, request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.use_flag:
            instance.use_flag = False
        else:
            instance.use_flag = True
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


@method_decorator([api_recorder], name="dispatch")
class DispatchLogView(ListAPIView):
    """
    list:
        发货履历列表
    create:
        新建/撤销发货
    """
    queryset = DispatchLog.objects.filter(delete_flag=False)
    serializer_class = DispatchLogSerializer
    filter_backends = [DjangoFilterBackend]
    filter_class = DispatchLogFilter
    permission_classes = (IsAuthenticated,)


@method_decorator([api_recorder], name="dispatch")
class InventoryLogOutViewSet(ModelViewSet):
    """混炼胶库出库履历视图"""
    queryset = InventoryLog.objects.filter(order_type='出库').order_by('-fin_time')
    serializer_class = InventoryLogOutSerializer
    filter_backends = [DjangoFilterBackend]
    pagination_class = SinglePageNumberPagination
    # filter_class = MixGumOutInventoryLogFilter
    permission_classes = (IsAuthenticated,)

    @action(methods=['get'], detail=False, permission_classes=[IsAuthenticated], url_path='inventory-now',
            url_name='inventory-now')
    def inventory_now(self, request, pk=None):
        """当前出库信息"""
        mixing_finished = self.request.query_params.get('mixing_finished', None)
        if mixing_finished:
            if mixing_finished == "终炼":
                il_obj = InventoryLog.objects.filter(order_type='出库', material_no__icontains="FM").last()
            elif mixing_finished == "混炼":
                il_obj = InventoryLog.objects.exclude(material_no__icontains="FM").filter(order_type='出库').last()
        else:
            raise ValidationError('参数不全')
        if il_obj:
            result = {'order_no': il_obj.order_no, 'material_no': il_obj.material_no,
                      'lot_no': il_obj.lot_no, 'location': il_obj.location}
        else:
            result = None
        return Response({'results': result})

    @action(methods=['get'], detail=False, permission_classes=[IsAuthenticated], url_path='inventory-today',
            url_name='inventory-today')
    def inventory_today(self, request, pk=None):
        """今日出库量"""
        mixing_finished = self.request.query_params.get('mixing_finished', None)
        if mixing_finished:
            if mixing_finished == "终炼":
                il_set = InventoryLog.objects.filter(order_type='出库', fin_time__date=datetime.date.today(),
                                                     material_no__icontains="FM").values(
                    'material_no').annotate(sum_qty=Sum('qty'))
            elif mixing_finished == "混炼":
                il_set = InventoryLog.objects.exclude(material_no__icontains="FM").filter(order_type='出库',
                                                                                          fin_time__date=datetime.date.today()).values(
                    'material_no').annotate(sum_qty=Sum('qty'))
        else:
            raise ValidationError('参数不全')
        return Response({'results': il_set})

    def get_queryset(self):
        queryset = super(InventoryLogOutViewSet, self).get_queryset()
        mixing_finished = self.request.query_params.get('mixing_finished', None)
        if mixing_finished:
            if mixing_finished == "终炼":
                queryset = queryset.filter(material_no__icontains="FM").all()
            elif mixing_finished == "混炼":
                queryset = queryset.exclude(material_no__icontains="FM").all()
        else:
            raise ValidationError('参数不全')
        return queryset


@method_decorator([api_recorder], name="dispatch")
class MaterialInventoryAPIView(APIView):

    def get(self, request):
        """库存信息"""
        lot_no = self.request.query_params.get('lot_no', None)
        if not lot_no:
            raise ValidationError('lot_no参数必填')
        model_list = [XBMaterialInventory, BzFinalMixingRubberInventory, BzFinalMixingRubberInventoryLB,
                      WmsInventoryStock]
        # 线边库  炼胶库  帘布库  原材料库
        query_list = []
        for model in model_list:
            if model == XBMaterialInventory:
                queryset = model.objects.filter(lot_no=lot_no).values('material__material_type',
                                                                      'material__material_no',
                                                                      'lot_no', 'container_no', 'location', 'qty',
                                                                      'unit',
                                                                      'unit_weight', 'quality_status')
                for xbi_obj in queryset:
                    xbi_obj.update({'material_type': xbi_obj.pop("material__material_type")})
                    xbi_obj.update({'material_no': xbi_obj.pop("material__material_no")})
            elif model == BzFinalMixingRubberInventory:
                try:
                    queryset = model.objects.using('bz').filter(lot_no=lot_no).values(
                        'material_no',
                        'lot_no', 'container_no', 'location',
                        'qty',
                        'quality_status', 'total_weight')
                except:
                    raise ValidationError('bz混炼胶库连接失败')
                for bz_dict in queryset:
                    try:
                        mt = bz_dict['material_no'].split("-")[1]
                    except:
                        mt = bz_dict['material_no']
                    unit = 'kg'
                    unit_weight = str(round(bz_dict['total_weight'] / bz_dict['qty'], 3))
                    bz_dict['material_type'] = mt
                    bz_dict['unit'] = unit
                    bz_dict['unit_weight'] = unit_weight
            elif model == BzFinalMixingRubberInventoryLB:
                try:
                    queryset = model.objects.using('lb').filter(lot_no=lot_no).values('material_no',
                                                                                      'lot_no', 'container_no',
                                                                                      'location',
                                                                                      'qty',
                                                                                      'quality_status', 'total_weight')
                except:
                    raise ValidationError('bz帘布连接失败')
                for bz_dict in queryset:
                    try:
                        mt = bz_dict['material_no'].split("-")[1]
                    except:
                        mt = bz_dict['material_no']
                    unit = 'kg'
                    unit_weight = str(round(bz_dict['total_weight'] / bz_dict['qty'], 3))
                    bz_dict['material_type'] = mt
                    bz_dict['unit'] = unit
                    bz_dict['unit_weight'] = unit_weight

            elif model == WmsInventoryStock:
                try:
                    queryset = model.objects.using('wms').filter(lot_no=lot_no).values(
                        'material_no',
                        'lot_no', 'location',
                        'qty',
                        'unit',
                        'quality_status', )
                except:
                    raise ValidationError('wms原材料库连接失败')
                for bz_dict in queryset:
                    try:
                        mt = bz_dict['material_no'].split("-")[1]
                    except:
                        mt = bz_dict['material_no']
                    container_no = None
                    unit_weight = None
                    bz_dict['material_type'] = mt  # 表里是有的 但是加上这个字段就会报错
                    bz_dict['container_no'] = container_no
                    bz_dict['unit_weight'] = unit_weight
            if queryset:
                query_list.extend(queryset)

        # 分页
        page = self.request.query_params.get("page", 1)
        page_size = self.request.query_params.get("page_size", 10)
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
        count = len(query_list)
        result = query_list[st:et]
        return Response({'results': result, "count": count})


@method_decorator([api_recorder], name="dispatch")
class MixinRubberyOutBoundOrderViewSet(GenericViewSet, ListModelMixin, UpdateModelMixin, RetrieveModelMixin):
    """
    list:
        混炼胶出库单列表
    update
         出库/关闭出库
    """
    queryset = MixinRubberyOutBoundOrder.objects.filter().order_by("-created_date")
    serializer_class = MixinRubberyOutBoundOrderSerializer
    filter_backends = [DjangoFilterBackend]
    filter_class = MixinRubberyOutBoundOrderFilter
    permission_classes = (IsAuthenticated,)


@method_decorator([api_recorder], name="dispatch")
class FinalRubberyOutBoundOrderViewSet(GenericViewSet, ListModelMixin, UpdateModelMixin, RetrieveModelMixin):
    """
    list:
        终炼胶出库单列表
    update
         出库/关闭出库
    """
    queryset = FinalRubberyOutBoundOrder.objects.filter().order_by("-created_date")
    serializer_class = FinalRubberyOutBoundOrderSerializer
    filter_backends = [DjangoFilterBackend]
    filter_class = FinalRubberyOutBoundOrderFilter
    permission_classes = (IsAuthenticated,)


@method_decorator([api_recorder], name="dispatch")
class PutPlanManagement(ModelViewSet):
    """
    list:
        混炼胶出库计划列表
    create:
        新建出库计划
    update:
        人工出库/修改出库数据/关闭出库订单
    """
    queryset = DeliveryPlan.objects.filter().order_by("-created_date")
    serializer_class = PutPlanManagementSerializer
    filter_backends = [DjangoFilterBackend]
    filter_class = PutPlanManagementFilter
    permission_classes = (IsAuthenticated,)

    @atomic()
    def create(self, request, *args, **kwargs):
        data = request.data
        order = MixinRubberyOutBoundOrder.objects.create(warehouse_name='混炼胶库',
                                                         order_type='指定出库',
                                                         order_no=''.join(str(time.time()).split('.')),
                                                         created_user=self.request.user)
        if isinstance(data, list):
            for item in data:
                item['outbound_order'] = order.id
            s = PutPlanManagementSerializer(data=data, context={'request': request}, many=True)
            if not s.is_valid():
                raise ValidationError(s.errors)
            s.save()
        elif isinstance(data, dict):
            data['outbound_order'] = order.id
            s = PutPlanManagementSerializer(data=data, context={'request': request})
            if not s.is_valid():
                raise ValidationError(s.errors)
            s.save()
        else:
            raise ValidationError('参数错误')
        return Response('新建成功')


@method_decorator([api_recorder], name="dispatch")
class PutPlanManagementLB(ModelViewSet):
    queryset = DeliveryPlanLB.objects.filter().order_by("-created_date")
    serializer_class = PutPlanManagementSerializerLB
    filter_backends = [DjangoFilterBackend]
    filter_class = PutPlanManagementLBFilter
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        data = request.data
        if isinstance(data, list):
            s = PutPlanManagementSerializerLB(data=data, context={'request': request}, many=True)
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
class PutPlanManagementFianl(ModelViewSet):
    """
    list:
        终炼胶出库计划列表
    create:
        新建出库计划
    update:
        人工出库/修改出库数据/关闭出库订单
    """

    queryset = DeliveryPlanFinal.objects.filter().order_by("-created_date")
    serializer_class = PutPlanManagementSerializerFinal
    filter_backends = [DjangoFilterBackend]
    filter_class = PutPlanManagementFinalFilter
    permission_classes = (IsAuthenticated,)

    @atomic()
    def create(self, request, *args, **kwargs):
        data = request.data
        order = FinalRubberyOutBoundOrder.objects.create(warehouse_name='混炼胶库',
                                                         order_type='指定出库',
                                                         order_no=''.join(str(time.time()).split('.')),
                                                         created_user=self.request.user)
        if isinstance(data, list):
            for item in data:
                item['outbound_order'] = order.id
            s = PutPlanManagementSerializerFinal(data=data, context={'request': request}, many=True)
            if not s.is_valid():
                raise ValidationError(s.errors)
            s.save()
        elif isinstance(data, dict):
            data['outbound_order'] = order.id
            s = PutPlanManagementSerializerFinal(data=data, context={'request': request})
            if not s.is_valid():
                raise ValidationError(s.errors)
            s.save()
        else:
            raise ValidationError('参数错误')
        return Response('新建成功')


@method_decorator([api_recorder], name="dispatch")
class MaterialPlanManagement(ModelViewSet):
    queryset = MaterialOutPlan.objects.filter().order_by("-created_date")
    serializer_class = MaterialPlanManagementSerializer
    filter_backends = [DjangoFilterBackend]
    filter_class = MaterialPlanManagementFilter
    permission_classes = (IsAuthenticated,)

    @action(methods=['get'], detail=False, permission_classes=[IsAuthenticated], url_path='stations',
            url_name='stations')
    def get(self, request, *args, **kwargs):
        url = f"http://{cb_ip}:{cb_port}/entrance/GetOutEntranceInfo"
        ret = requests.get(url)
        data = ret.json()
        rep = [{"station_no": x.get("entranceCode"),
                "station": x.get("name")} for x in data.get("datas", {})]
        return Response(rep)

    def create(self, request, *args, **kwargs):
        data = request.data
        if isinstance(data, list):
            s = MaterialPlanManagementSerializer(data=data, context={'request': request}, many=True)
            if not s.is_valid():
                raise ValidationError(s.errors)
            s.save()
        elif isinstance(data, dict):
            s = MaterialPlanManagementSerializer(data=data, context={'request': request})
            if not s.is_valid():
                raise ValidationError(s.errors)
            s.save()
        else:
            raise ValidationError('参数错误')
        return Response('新建成功')


@method_decorator([api_recorder], name="dispatch")
class CarbonPlanManagement(ModelViewSet):
    queryset = CarbonOutPlan.objects.filter().order_by("-created_date")
    serializer_class = CarbonPlanManagementSerializer
    filter_backends = [DjangoFilterBackend]
    filter_class = CarbonPlanManagementFilter
    permission_classes = (IsAuthenticated,)

    @action(methods=['get'], detail=False, permission_classes=[IsAuthenticated], url_path='stations',
            url_name='stations')
    def get(self, request, *args, **kwargs):
        url = f"http://{wms_ip}:{wms_port}/entrance/GetOutEntranceInfo"
        ret = requests.get(url)
        data = ret.json()
        rep = [{"station_no": x.get("entranceCode"),
                "station": x.get("name")} for x in data.get("datas", {})]
        return Response(rep)

    def create(self, request, *args, **kwargs):
        data = request.data
        if isinstance(data, list):
            s = CarbonPlanManagementSerializer(data=data, context={'request': request}, many=True)
            if not s.is_valid():
                raise ValidationError(s.errors)
            s.save()
        elif isinstance(data, dict):
            s = CarbonPlanManagementSerializer(data=data, context={'request': request})
            if not s.is_valid():
                raise ValidationError(s.errors)
            s.save()
        else:
            raise ValidationError('参数错误')
        return Response('新建成功')


@method_decorator([api_recorder], name="dispatch")
class MateriaTypeNameToAccording(APIView):
    # materia_type_name_to_according
    """根据物料类型和编码找到存在的仓库表"""

    def get(self, request):
        material_type = self.request.query_params.get('material_type')
        material_no = self.request.query_params.get('material_no')
        if not all([material_no, material_type]):
            raise ValidationError('物料名称和物料类型都必传！')
        warehouse_name_list = WarehouseMaterialType.objects.filter(
            material_type__global_name=material_type).values_list(
            'warehouse_info__name', flat=True).distinct()
        if not warehouse_name_list:
            raise ValidationError('该物料类型没有对应的仓库')
        warehouse_name_according = {'线边库': MaterialInventory,
                                    '原材料库': WmsInventoryStock,
                                    '混炼胶库': BzFinalMixingRubberInventory,
                                    '帘布库': BzFinalMixingRubberInventoryLB,
                                    '终炼胶库': BzFinalMixingRubberInventory}
        according_list = []
        for warehouse_name in warehouse_name_list:
            materia_no_filte = {}
            if warehouse_name_according[warehouse_name] == MaterialInventory:
                materia_no_filte['material__material_no'] = material_no
            else:
                materia_no_filte['material_no'] = material_no
            if warehouse_name_according[warehouse_name].objects.filter(**materia_no_filte).exists():
                according_list.append(warehouse_name_according[warehouse_name].__name__)
        return Response(according_list)


@method_decorator([api_recorder], name="dispatch")
class SamplingRules(APIView):

    def get(self, request, *args, **kwargs):
        params = request.query_params
        material_no = params.get("material_no")
        material_name = params.get("material_name")
        filter_dict = {}
        if material_no:
            filter_dict.update(material__material_no=material_no)
        if material_name:
            filter_dict.update(material__material_name=material_name)
        queryset = MaterialAttribute.objects.filter(**filter_dict).order_by("id")
        if not queryset.exists():
            raise ValidationError(f"{material_no}|{material_name}未能在MES中检索到")
        instance = queryset.last()
        return Response({"result": {"material_no": material_no,
                                    "material_name": material_name,
                                    "sampling_rate": instance.sampling_rate}})


@method_decorator([api_recorder], name="dispatch")
class BarcodeQualityViewSet(ModelViewSet):
    queryset = BarcodeQuality.objects.filter()
    serializer_class = BarcodeQualitySerializer
    filter_backends = [DjangoFilterBackend]
    filter_class = (BarcodeQualityFilter)
    permission_classes = (IsAuthenticated,)
    pagination_class = SinglePageNumberPagination

    def list(self, request, *args, **kwargs):
        params = request.query_params
        material_type = params.get("material_type")
        material_no = params.get("material_no")
        lot_no = params.get("lot_no")
        page = params.get("page", 1)
        page_size = params.get("page_size", 10)
        mes_set = self.queryset.values('lot_no', 'quality_status')
        quality_dict = {_.get("lot_no"): _.get('quality_status') for _ in mes_set}
        try:
            wms_set = WmsInventoryStock.objects.using('wms').raw(
                WmsInventoryStock.quality_sql(material_type, material_no, lot_no))
            p = Paginator(wms_set, page_size)
            s = WmsStockSerializer(p.page(page), many=True, context={"quality_dict": quality_dict})
            data = s.data
            return Response({"results": data, "count": p.count})
        except AttributeError:
            raise ValidationError("网络拥堵，数据还未返回")
        except TypeError:
            raise ValidationError("网络拥堵，数据还未返回")

    def create(self, request, *args, **kwargs):
        data = dict(request.data)
        lot_no = data.pop("lot_no", None)
        obj, flag = self.queryset.update_or_create(defaults=data, lot_no=lot_no)
        if flag:
            return Response("补充条码状态成功")
        else:
            return Response("更新条码状态成功")

    @action(methods=['get'], detail=False, permission_classes=[IsAuthenticated], url_path='export',
            url_name='export')
    def export(self, request):
        """备品备件导入模板"""
        response = HttpResponse(content_type='application/vnd.ms-excel')
        filename = '物料条码信息数据导出'
        response['Content-Disposition'] = 'attachment;filename= ' + filename.encode('gbk').decode(
            'ISO-8859-1') + '.xls'
        # 创建工作簿
        style = xlwt.XFStyle()
        style.alignment.wrap = 1
        ws = xlwt.Workbook(encoding='utf-8')

        # 添加第一页数据表
        w = ws.add_sheet('物料条码信息')  # 新建sheet（sheet的名称为"sheet1"）
        # for j in [1, 4, 5, 7]:
        #     first_col = w.col(j)
        #     first_col.width = 256 * 20
        # 写入表头
        w.write(0, 0, u'该数据仅供参考')
        title_list = [u'No', u'物料类型', u'物料编码', u'物料名称', u'条码', u'托盘号', u'库存数', u'单位重量(kg)', u'总重量', u'品质状态']
        for title in title_list:
            w.write(1, title_list.index(title), title)
        temp_write_list = []
        count = 1
        mes_set = self.queryset.values('lot_no', 'quality_status')
        quality_dict = {_.get("lot_no"): _.get('quality_status') for _ in mes_set}
        try:
            wms_set = WmsInventoryStock.objects.using('wms').raw(WmsInventoryStock.quality_sql())
        except:
            raise ValidationError("网络拥堵，请稍后重试")
        s = WmsStockSerializer(wms_set, many=True, context={"quality_dict": quality_dict})
        for q in s.data:
            total_weight = q.get('total_weight')
            qty = q.get('qty')
            if total_weight and qty:
                unit_weight = float(total_weight) / float(qty)
            else:
                unit_weight = 0
            line_list = [count, q.get('material_type'), q.get('material_no'), q.get('material_name'),
                         q.get('lot_no'), q.get('container_no'), qty, round(unit_weight, 3),
                         total_weight, q.get('quality') if q.get('quality') else None]
            temp_write_list.append(line_list)
            count += 1
        n = 2  # 行数
        for y in temp_write_list:
            m = 0  # 列数
            for x in y:
                w.write(n, m, x)
                m += 1
            n += 1
        output = BytesIO()
        ws.save(output)
        # 重新定位到开始
        output.seek(0)
        response.write(output.getvalue())
        return response


@method_decorator([api_recorder], name="dispatch")
class MaterialTraceView(APIView):

    def get(self, request):
        lot_no = request.query_params.get("lot_no")
        if not lot_no:
            raise ValidationError("请输入条码进行查询")
        rep = {}
        # 采样
        rep["material_sample"] = None
        # 入库
        material_in = MaterialInHistory.objects.using('wms').filter(lot_no=lot_no). \
            values("lot_no", "material_no", "material_name", "location", "pallet_no",
                   "task__initiator", "supplier", "batch_no", "task__fin_time").last()
        if material_in:
            temp_time = material_in.pop("task__fin_time", datetime.datetime.now())
            work_schedule_plan = WorkSchedulePlan.objects.filter(
                start_time__lte=temp_time,
                end_time__gte=temp_time,
                plan_schedule__work_schedule__work_procedure__global_name='密炼').select_related(
                "classes",
                "plan_schedule"
            ).order_by("id").last()
            if work_schedule_plan:
                current_class = work_schedule_plan.classes.global_name
                material_in["classes_name"] = current_class
            else:
                material_in["classes_name"] = "早班"
            material_in["time"] = temp_time.strftime('%Y-%m-%d %H:%M:%S')
            rep["material_in"] = [material_in]
        else:
            rep["material_in"] = []
        # 出库
        material_out = MaterialOutHistory.objects.using('wms').filter(lot_no=lot_no). \
            values("lot_no", "material_no", "material_name", "location", "pallet_no",
                   "task__initiator", "supplier", "batch_no", "task__fin_time").last()
        if material_out:
            temp_time = material_out.pop("task__fin_time", datetime.datetime.now())
            work_schedule_plan = WorkSchedulePlan.objects.filter(
                start_time__lte=temp_time,
                end_time__gte=temp_time,
                plan_schedule__work_schedule__work_procedure__global_name='密炼').select_related(
                "classes",
                "plan_schedule"
            ).order_by("id").last()
            if work_schedule_plan:
                current_class = work_schedule_plan.classes.global_name
                material_in["classes_name"] = current_class
            else:
                material_in["classes_name"] = "早班"
            rep["material_out"] = [material_out]
        else:
            rep["material_out"] = []
        # 称量投入
        weight_log = WeightBatchingLog.objects.filter(bra_code=lot_no). \
            values("bra_code", "material_no", "equip_no", "tank_no", "created_user__username", "created_date",
                   "batch_classes").last()
        if weight_log:
            temp_time = weight_log.pop("created_date", datetime.datetime.now())
            weight_log["time"] = temp_time.strftime('%Y-%m-%d %H:%M:%S')
            weight_log["classes_name"] = weight_log.pop("batch_classes", "早班")
        else:
            weight_log = {}
        rep["material_weight"] = [weight_log]
        # 密炼投入
        load_material = LoadMaterialLog.objects.using("SFJ").filter(bra_code=lot_no) \
            .values("material_no", "bra_code", "weight_time", "feed_log__equip_no",
                    "feed_log__batch_group", "feed_log__batch_classes").last()
        if load_material:
            temp_time = load_material.pop("weight_time", datetime.datetime.now())
            load_material["time"] = temp_time.strftime('%Y-%m-%d %H:%M:%S')
            load_material["classes_name"] = load_material.pop("feed_log__batch_classes", "早班")
            rep["material_load"] = [load_material]
        else:
            rep["material_load"] = []
        return Response(rep)


@method_decorator([api_recorder], name="dispatch")
class ProductTraceView(APIView):
    inventory = {
        "终炼胶库": ('lb', []),
        "混炼胶库": ("bz", []),
    }

    def get(self, request):
        #  11个条目
        lot_no = request.query_params.get("lot_no")
        if not lot_no:
            raise ValidationError("请输入条码进行查询")
        rep = {"material_in": [], "material_out": []}
        product_trace = PalletFeedbacks.objects.filter(lot_no=lot_no).values()
        if not product_trace:
            raise ValidationError("无法查询到该追踪码对应的胶料数据")
        pallet_feed = product_trace.last()
        plan_no = pallet_feed.get("plan_classes_uid")
        product_no = pallet_feed.get("product_no")
        begin_trains = pallet_feed.get("begin_trains")
        end_trains = pallet_feed.get("end_trains")
        trains_list = [x for x in range(begin_trains, end_trains + 1)]
        lml_set = LoadMaterialLog.objects.using("SFJ").filter(feed_log__trains__in=trains_list,
                                                              feed_log__plan_classes_uid=plan_no).distinct()
        bra_code_list = list(lml_set.values_list("bra_code", flat=True))
        # 密炼投入
        material_load = lml_set.values("bra_code", "material_no", "feed_log__equip_no", "weight_time",
                                       "feed_log__batch_group", "feed_log__batch_classes")
        rep["material_load"] = list(material_load)
        # 料包产出
        weight_package = WeightPackageLog.objects.filter(bra_code__in=bra_code_list). \
            values("bra_code", "material_no", "equip_no", "batch_group", "created_date", "batch_classes")
        rep["weight_package"] = list(weight_package)
        # 称量投入
        weight_load = WeightBatchingLog.objects.filter(bra_code__in=bra_code_list). \
            values("bra_code", "material_no", "equip_no", "tank_no", "batch_group", "created_date", "batch_classes")
        rep["weight_load"] = list(weight_load)
        if "FM" in product_no:
            db_rubber = "bz"
        else:
            # db = "lb
            db_rubber = "bz"
        # 收皮产出追溯
        rep["pallet_feed"] = list(product_trace)
        if not product_trace:
            raise ValidationError("查不到该条码对应胶料")
        plan = ProductClassesPlan.objects.filter(plan_classes_uid=plan_no).last()
        if plan:
            product = plan.product_batching

            # 配方创建
            product_info = model_to_dict(product)
            temp_time = product.created_date
            work_schedule_plan = WorkSchedulePlan.objects.filter(
                start_time__lte=temp_time,
                end_time__gte=temp_time,
                plan_schedule__work_schedule__work_procedure__global_name='密炼').select_related(
                "classes",
                "plan_schedule"
            ).order_by("id").last()
            if work_schedule_plan:
                current_class = work_schedule_plan.classes.global_name
                product_info["classes_name"] = current_class
            else:
                product_info["classes_name"] = "早班"
            product_info["created_date"] = temp_time
        else:
            product = None
            product_info = {}
        rep["product_info"] = [product_info]
        # 配料详情
        if product:
            product_details = product.batching_details.filter(
                delete_flag=False
            ).values("product_batching__stage_product_batch_no", "material__material_no", "actual_weight")
        else:
            product_details = []
        rep["product_details"] = list(product_details)
        # 胶料计划
        plan_info = ProductClassesPlan.objects.filter(plan_classes_uid=plan_no).values("plan_classes_uid",
                                                                                       "equip__equip_no",
                                                                                       "product_batching__stage_product_batch_no",
                                                                                       "plan_trains", "created_date",
                                                                                       "last_updated_date",
                                                                                       "work_schedule_plan__classes__global_name")
        trains_temp = TrainsFeedbacks.objects.filter(plan_classes_uid=plan_no).order_by('id')
        start_time = trains_temp.first().begin_time if trains_temp.first() else None
        end_time = trains_temp.first().end_time if trains_temp.last() else None
        plan_info = plan_info.last()
        if plan_info:
            plan_info.update(start_time=start_time, end_time=end_time)
        rep["plan_info"] = [plan_info]
        # 小料计划
        batch_plan = BatchingClassesPlan.objects.filter(weigh_cnt_type__product_batching=product,
                                                        work_schedule_plan=plan.work_schedule_plan). \
            values("plan_batching_uid", "weigh_cnt_type__product_batching__equip__equip_no",
                   "created_date", "last_updated_date", "work_schedule_plan__classes__global_name")
        rep["batch_plan"] = list(batch_plan)
        # 收皮入库
        product_in = MixGumInInventoryLog.objects.using(db_rubber).filter(lot_no=lot_no).values()
        temp = product_in.last()
        if temp:
            temp_time = product_info.get("start_time", datetime.datetime.now())
            work_schedule_plan = WorkSchedulePlan.objects.filter(
                start_time__lte=temp_time,
                end_time__gte=temp_time,
                plan_schedule__work_schedule__work_procedure__global_name='密炼').select_related(
                "classes",
                "plan_schedule"
            ).order_by("id").last()
            if work_schedule_plan:
                current_class = work_schedule_plan.classes.global_name
                temp["classes_name"] = current_class
            else:
                temp["classes_name"] = "早班"
            rep["product_in"] = [temp]
        else:
            rep["product_in"] = []
        # 胶片发货
        dispatch_log = DispatchLog.objects.filter(lot_no=lot_no).values()
        temp = dispatch_log.last()
        if temp:
            temp_time = product_info.get("order_created_time", datetime.datetime.now())
            work_schedule_plan = WorkSchedulePlan.objects.filter(
                start_time__lte=temp_time,
                end_time__gte=temp_time,
                plan_schedule__work_schedule__work_procedure__global_name='密炼').select_related(
                "classes",
                "plan_schedule"
            ).order_by("id").last()
            if work_schedule_plan:
                current_class = work_schedule_plan.classes.global_name
                temp["classes_name"] = current_class
            else:
                temp["classes_name"] = "早班"
            rep["dispatch_log"] = [temp]
        else:
            rep["dispatch_log"] = []
        return Response(rep)


@method_decorator([api_recorder], name="dispatch")
class BarcodeTraceView(APIView):

    permission_classes = (IsAuthenticated,)

    def get(self, request):
        data = self.request.query_params
        trace_flag, bra_code, trace_material, st, et = data.get('trace_flag'), data.get('bra_code'), data.get('trace_material'), data.get('st'), data.get('et')
        filter_kwargs, results = {}, []
        if trace_flag == '0':  # 原材料到胶料
            supplier, batch_no, se, ee = data.get('supplier'), data.get('batch_no'), data.get('se'), data.get('ee')
            if bra_code:
                filter_kwargs['bra_code__icontains'] = bra_code
            if trace_material:
                filter_kwargs['scan_material_record__icontains'] = trace_material
            if supplier:
                filter_kwargs['supplier__icontains'] = supplier
            if batch_no:
                filter_kwargs['batch_no__icontains'] = batch_no
            if st:
                filter_kwargs['product_time__gte'] = st
            if et:
                filter_kwargs['product_time__lte'] = et
            if se:
                filter_kwargs['erp_in_time__gte'] = se
            if ee:
                filter_kwargs['erp_in_time__lte'] = ee
            records = BarCodeTraceDetail.objects.filter(**filter_kwargs, display=True).order_by('scan_material_record').values()
            for i in records:
                product_time = None if not i['product_time'] else i['product_time'].strftime('%Y-%m-%d %H:%M:%S')
                erp_in_time = None if not i['erp_in_time'] else i['erp_in_time'].strftime('%Y-%m-%d %H:%M:%S')
                begin_time = None if not i['begin_time'] else i['begin_time'].strftime('%Y-%m-%d %H:%M:%S')
                end_time = None if not i['end_time'] else i['end_time'].strftime('%Y-%m-%d %H:%M:%S')
                arrange_rubber_time = None if not i['arrange_rubber_time'] else i['arrange_rubber_time'].strftime('%Y-%m-%d %H:%M:%S')
                i.update({'product_time': product_time, 'erp_in_time': erp_in_time, 'begin_time': begin_time, 'end_time': end_time,
                          'arrange_rubber_time': arrange_rubber_time})
                results.append(i)
        elif trace_flag == '1':  # 胶料到原材料
            classes, equip_no, sc, ec = data.get('classes'), data.get('equip_no'), data.get('sc'), data.get('ec')
            if bra_code:
                p_infos = PalletFeedbacks.objects.filter(lot_no__icontains=bra_code).values('plan_classes_uid', 'begin_trains', 'end_trains')
                id_list = []
                for i in p_infos:
                    s_ids = TrainsFeedbacks.objects.filter(~Q(operation_user='Mixer2'), plan_classes_uid=i['plan_classes_uid'], actual_trains__gte=i['begin_trains'], actual_trains__lte=i['end_trains']).values_list('id', flat=True)
                    id_list.extend(list(s_ids))
                filter_kwargs['id__in'] = set(id_list)
            else:
                if trace_material:
                    filter_kwargs['product_no__icontains'] = trace_material
                if st:
                    filter_kwargs['factory_date__gte'] = st
                if et:
                    filter_kwargs['factory_date__lte'] = et
                if classes:
                    filter_kwargs['classes'] = classes
                if equip_no:
                    filter_kwargs['equip_no'] = equip_no
                    if equip_no == 'Z04':
                        filter_kwargs['operation_user'] = 'Mixer1'
                if sc:
                    filter_kwargs['actual_trains__gte'] = sc
                if ec:
                    filter_kwargs['actual_trains__lte'] = ec
            records = TrainsFeedbacks.objects.filter(**filter_kwargs).order_by('-factory_date', 'equip_no', 'actual_trains')\
                .values('plan_classes_uid', 'actual_trains', 'equip_no', 'product_no', 'actual_weight', 'begin_time', 'end_time', 'factory_date', 'classes')
            for i in records:
                plan_classes_uid, train = i['plan_classes_uid'], i['actual_trains']
                begin_time = i['begin_time'] if not i['begin_time'] else i['begin_time'].strftime('%Y-%m-%d %H:%M:%S')
                end_time = i['end_time'] if not i['end_time'] else i['end_time'].strftime('%Y-%m-%d %H:%M:%S')
                p_info = PalletFeedbacks.objects.filter(plan_classes_uid=plan_classes_uid, begin_trains__lte=train, end_trains__gte=train).last()
                lot_no, pallet_no, product_time = [None, None, None] if not p_info else [p_info.lot_no, p_info.pallet_no, None if not p_info.product_time else p_info.product_time.strftime('%Y-%m-%d %H:%M:%S')]
                p = ProductClassesPlan.objects.filter(plan_classes_uid=plan_classes_uid, delete_flag=False).last()
                if bra_code and (not lot_no or bra_code not in lot_no):
                    continue
                group = p.work_schedule_plan.group.global_name if p else ''
                i.update({'lot_no': lot_no, 'pallet_no': pallet_no, 'product_time': product_time, 'begin_time': begin_time, 'end_time': end_time, 'group': group})
                results.append(i)
        else:
            raise ValidationError('未知操作')
        if data.get('export'):
            if not results:
                raise ValidationError('无数据可导出')
            if trace_flag == '0':
                file_name, export_fields = '原材料追溯', {'商品名': 'scan_material_record', '厂商': 'supplier', '批次号': 'batch_no', '生产日期': 'product_time',
                                                     'ERP入库日期': 'erp_in_time', '质检条码': 'bra_code', '托盘号': 'pallet_no', '重量(kg)': 'standard_weight'}
            else:
                file_name, export_fields = '胶料追溯', {'机台': 'equip_no', '生产日期': 'factory_date', '班次': 'classes', '班组': 'group', '胶料编码': 'product_no',
                                                    '车次': 'actual_trains', '计划编号': 'plan_classes_uid', '追溯码': 'lot_no', '托盘号': 'pallet_no',
                                                    '重量(kg)': 'actual_weight', '密炼开始时间': 'begin_time', '密炼结束时间': 'end_time', '收皮时间': 'product_time'}
            return gen_template_response(export_fields, results, file_name, handle_str=True)
        # 分页
        page, page_size = data.get('page', 1), data.get('page_size', 10)
        try:
            begin = (int(page) - 1) * int(page_size)
            end = int(page) * int(page_size)
        except:
            raise ValidationError("page/page_size异常，请修正后重试")
        else:
            if end >= 10000:
                page_result, total_page = results[begin:], 1
            else:
                if begin not in range(0, 99999):
                    raise ValidationError("page/page_size值异常")
                if end not in range(0, 99999):
                    raise ValidationError("page/page_size值异常")
                page_result, total_page = results[begin: end], math.ceil(len(results) / int(page_size))
        return Response({'total_data': len(results), 'total_page': total_page, 'page_result': page_result})

    def post(self, request):
        data = self.request.data
        bra_code, trains, product_no, trace_flag, code_type = data.get('bra_code'), data.get('trains'), data.get('product_no'), data.get('trace_flag'), data.get('code_type')
        results = {}
        if trace_flag == 0:  # 正向追溯 1MB->2MB->FMB
            # 需要追溯的条码信息
            codes = self.get_xl_codes(bra_code) if code_type == '料罐' else [bra_code]
            res = self.trace_up(codes)
            results.update(res)
        else:  # 反向追溯 FMB->2MB-1MB
            p = PalletFeedbacks.objects.filter(lot_no=bra_code).last()
            if not p:
                raise ValidationError('未找到条码对应的收皮信息')
            l_detail = LoadMaterialLog.objects.using('SFJ').filter(status=1, feed_log__plan_classes_uid=p.plan_classes_uid, feed_log__trains=trains).order_by(
                '-scan_material_type', 'bra_code', '-stage', '-material_name', 'feed_log__trains')
            if l_detail:
                p_list = p.product_no.split('-')
                s_stage = None if not p_list else (p_list[1] if len(p_list) > 2 else p_list[0])
                results.update({s_stage: [{product_no: self.supplement_info(l_detail.values('scan_material_type', 'scan_material', 'bra_code', 'feed_log__trains', 'material_name')), 'behind': ''}]})
                others = l_detail.filter(~Q(Q(bra_code__startswith='AAJZ20') | Q(bra_code__startswith='WMS')), scan_material_type='胶皮').order_by('-stage')
                if others:
                    res = self.trace_down(others, behind=s_stage)
                    results.update(res)
        if data.get('export'):
            if not results:
                raise ValidationError('无可导出数据')
            try:
                response = self.export_data(results, trace_flag)
            except:
                raise ValidationError('导出异常')
            return response
        return Response(results)

    def trace_up(self, codes, add_before=False):
        res, temp, next_barcode, rubber_index, get_record, before_info, pass_code = {}, {}, {}, {}, {}, {}, []
        code_list = codes.keys() if isinstance(codes, dict) else codes
        code_details = LoadMaterialLog.objects.using('SFJ').filter(status=1, bra_code__in=code_list).values_list('feed_log', flat=True)
        l_detail = LoadMaterialLog.objects.using('SFJ').filter(status=1, feed_log__in=code_details).order_by('-scan_material_type', 'bra_code', 'stage', '-material_name', 'feed_log__trains')
        if l_detail:
            for index, i in enumerate(l_detail):
                product_no, plan_classes_uid, trains, stage, bra_code, scan_material_type, scan_material = i.feed_log.product_no, i.feed_log.plan_classes_uid, \
                                                                                                           i.feed_log.trains, i.stage, i.bra_code, \
                                                                                                           i.scan_material_type, i.scan_material
                before = ''
                if add_before:
                    stage_info = codes.get(bra_code)
                    if stage_info:
                        before = f"{stage_info[1]}-{stage_info[0]}"
                        if before in before_info and before_info[before].get(plan_classes_uid) != trains:
                            continue
                        before_info[before] = {plan_classes_uid: trains}
                        pass_code.append(f'{plan_classes_uid}-{trains}')
                    else:
                        if f'{plan_classes_uid}-{trains}' not in pass_code:
                            continue
                # 是否完成收皮
                get_flag = get_record.get(f'{plan_classes_uid}-{trains}')  # 同计划、同车次是否收皮
                if get_flag:
                    if get_flag == '无':
                        continue
                    p = get_flag
                else:
                    p = PalletFeedbacks.objects.filter(plan_classes_uid=plan_classes_uid, begin_trains__lte=trains, end_trains__gte=trains).last()
                    if not p:
                        get_record[f'{plan_classes_uid}-{trains}'] = '无'
                        continue
                    else:  # 保留当前车, 其他车为无
                        get_record[f'{plan_classes_uid}-{trains}'] = p
                if p.lot_no not in next_barcode:
                    next_barcode[p.lot_no] = [index + 1, stage]
                # 某条数据的详情
                _k = f"{bra_code}_{scan_material}"
                if _k not in temp:
                    _i = {'scan_material_type': scan_material_type, 'scan_material': scan_material, 'bra_code': bra_code, 'feed_log__trains': trains,
                          'material_name': i.material_name}
                    s_info = self.supplement_info([_i])[0]
                    temp[_k] = s_info
                else:
                    s_info = copy.deepcopy(temp[_k])
                    s_info['feed_log__trains'] = trains
                if stage in res:
                    rubber_i = rubber_index.get(f'{stage}-{product_no}-{trains}')
                    if rubber_i is None:
                        res[stage].append({product_no: [s_info], 'before': before})
                        rubber_index[f'{stage}-{product_no}-{trains}'] = len(res[stage]) - 1
                    else:
                        res[stage][rubber_i][product_no].append(s_info)
                else:
                    res = {stage: [{product_no: [s_info], 'before': before}]}
                    rubber_index[f'{stage}-{product_no}-{trains}'] = 0
            if next_barcode:
                s = self.trace_up(next_barcode, add_before=True)
                res.update(s)
        return res

    def trace_down(self, others, behind):
        res = {}
        for index, o in enumerate(others):
            p = PalletFeedbacks.objects.filter(lot_no=o.bra_code).last()
            l_detail = LoadMaterialLog.objects.using('SFJ').filter(status=1, feed_log__plan_classes_uid=p.plan_classes_uid, feed_log__trains__gte=p.begin_trains,
                                                                   feed_log__trains__lte=p.end_trains).order_by('-scan_material_type', 'bra_code', '-stage', '-material_name', 'feed_log__trains')
            if l_detail:
                p_list = p.product_no.split('-')
                s_stage = None if not p_list else (p_list[1] if len(p_list) > 2 else p_list[0])
                s_info = {p.product_no: self.supplement_info(l_detail.values('scan_material_type', 'scan_material', 'bra_code', 'feed_log__trains', 'material_name', 'stage')), 'behind': f'{behind}-{index + 1}'}
                if s_stage in res:
                    res[s_stage].append(s_info)
                else:
                    res = {s_stage: [s_info]}
                others_before = l_detail.filter(~Q(Q(bra_code__startswith='AAJZ20') | Q(bra_code__startswith='WMS')), scan_material_type='胶皮')
                if others_before:
                    s = self.trace_down(others_before, behind=p.product_no.split('-')[1])
                    res.update(s)
        return res

    def supplement_info(self, query_set):
        """补充每条数据内容"""
        handle_info, temp = [], {}
        for i in query_set:
            key = f"{i['bra_code']}-{i['material_name']}"
            if temp.get(key):
                i.update(temp[key])
            else:
                b = BarCodeTraceDetail.objects.filter(bra_code=i['bra_code']).values('scan_material_record', 'material_name_record', 'product_time', 'trains',
                                                                                     'standard_weight', 'pallet_no', 'equip_no', 'group', 'classes',
                                                                                     'plan_classes_uid', 'begin_time', 'end_time', 'arrange_rubber_time')
                add_data_temp = b[0] if b else {'scan_material_record': None, 'material_name_record': None, 'product_time': None, 'standard_weight': None,
                                                'pallet_no': None, 'equip_no': None, 'group': None, 'classes': None, 'trains': None,
                                                'plan_classes_uid': None, 'begin_time': None, 'end_time': None, 'arrange_rubber_time': None}
                if i['bra_code'][0] in ['S', 'F']:  # 补充小料详情
                    res = self.get_xl_info(i['bra_code'], i['material_name'])
                    add_data_temp.update(res)
                i.update(add_data_temp)
                temp[key] = add_data_temp
            handle_info.append(i)
        return handle_info

    def get_xl_info(self, xl_code, material_name):
        """获取料包原材料对应信息"""
        s_data, lb_detail = [], {}
        xl = WeightPackageLog.objects.filter(bra_code=xl_code).last()
        w = WeightBatchingLog.objects.filter(material_name=material_name.rstrip('-C|-X'), batch_time__lte=xl.batch_time, status=1).order_by('batch_time').last()
        if w:
            detail = BarCodeTraceDetail.objects.filter(bra_code=w.bra_code, code_type='料罐').values('supplier', 'batch_no', 'erp_in_time', 'product_time', 'standard_weight')
            if detail:
                s = detail[0]
                s['erp_in_time'] = s.get('erp_in_time') if not s.get('erp_in_time') else s.get('erp_in_time').strftime('%Y-%m-%d %H:%M:%S')
                s['product_time'] = s.get('product_time') if not s.get('product_time') else s.get('product_time').strftime('%Y-%m-%d %H:%M:%S')
                lb_detail.update(s)
        if lb_detail:
            lb_detail['material_name'] = material_name.rstrip('-C|-X')
            s_data.append(lb_detail)
        return {'xl_detail': s_data}

    def get_xl_codes(self, code):
        """查询条码配置了哪些料包"""
        xl_codes = []
        db_config = [k for k, v in DATABASES.items() if 'YK_XL' in v['NAME'] or 'MWDS' in v['NAME']]
        for equip_no in db_config:
            w_model = JZReportWeight if equip_no in JZ_EQUIP_NO else ReportWeight
            f_code = WeightBatchingLog.objects.filter(bra_code=code, status=1, equip_no=equip_no).first()  # 第一次扫码
            if not f_code:
                continue
            st, tank_no, f_id, name = f_code.batch_time, f_code.tank_no, f_code.id, f_code.material_name
            # 下一次料罐不同条码扫码
            o_code = WeightBatchingLog.objects.filter(~Q(bra_code=code), id__gt=f_id, tank_no=tank_no, status=1, equip_no=equip_no).first()
            et = o_code.batch_time if o_code else datetime.datetime.now()
            # 使用该物料的配方
            res = w_model.objects.using(equip_no).filter(material=name, 时间__gte=st, 时间__lte=et).values('planid').annotate(fc=Min('车次'), lc=Max('车次'))
            if not res:
                continue
            # 依照时间段查询使用到物料的料包车次
            for i in res:
                code_list = WeightPackageLog.objects.filter(Q(begin_trains__gte=i['fc'], begin_trains__lte=i['lc']) |
                                                            Q(end_trains__gte=i['fc'], end_trains__lte=i['lc']),
                                                            plan_weight_uid=i['planid'], equip_no=equip_no).values_list('bra_code', flat=True)
                if code_list:
                    xl_codes.extend(list(code_list))
        return list(set(xl_codes))

    def export_data(self, data, trace_flag):
        bio = BytesIO()
        writer = pd.ExcelWriter(bio, engine='xlsxwriter')  # 注意安装这个包 pip install xlsxwriter
        key = 'behind' if trace_flag == 1 else 'before'
        for stage in data:
            # 整理数据
            res = self.handle_data(data[stage], key)
            df = pd.DataFrame(res)
            df.to_excel(writer, sheet_name=stage, index=None, encoding='SIMPLIFIED CHINESE_CHINA.UTF8')
        writer.save()
        bio.seek(0)
        from django.http import FileResponse
        response = FileResponse(bio)
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename="mm.xlsx"'
        return response

    def handle_data(self, s_data, key):
        res = []
        for i in s_data:
            product_no, cont = list(i.keys())[0], i.pop(key)
            for j in i[product_no]:
                xl_detail = j.get('xl_detail')
                if xl_detail:
                    d = xl_detail[0]
                    xl_detail = f"供应商: {d['supplier']}, 批次号: {d['batch_no']}, ERP入库时间: {d['erp_in_time']}, 生产日期: {d['product_time']}," \
                                f"重量: {d['standard_weight']}, 物料名: {d['material_name']};"
                else:
                    xl_detail = ''
                _data = {'物料编码': product_no, '投入物料类别': j['scan_material_type'], 'scan_material': j['scan_material'], '机台': j['equip_no'],
                         '生产日期': j['product_time'] if not j['product_time'] else j['product_time'].strftime('%Y-%m-%d'), '班次': j['classes'],
                         '班组': j['group'], '车次': j['trains'], '追溯码': j['bra_code'], '托盘号': j['pallet_no'], '重量': j['standard_weight'],
                         '密炼/配料 开始时间': j['begin_time'], '密炼/配料 结束时间': j['end_time'], '收皮时间': j['arrange_rubber_time'],
                         '料包明细': xl_detail, '行关联': cont}
                res.append(_data)
        return res


@method_decorator([api_recorder], name="dispatch")
class MaterialOutBack(APIView):

    # 出库反馈
    @atomic
    def post(self, request):
        """WMS->MES:任务编号、物料信息ID、物料名称、PDM号（促进剂以外为空）、批号、条码、重量、重量单位、
        生产日期、使用期限、托盘RFID、工位（出库口）、MES->WMS:信息接收成功or失败"""
        # 任务编号
        return Response({"status": 1, "desc": "成功", "message": "反馈成功"})
        #
        # data = request.data
        # # data = {'order_no':'20201114131845',"pallet_no":'20102494',
        # #         'location':'二层前端','qty':'2','weight':'2.00',
        # #         'quality_status':'合格','lot_no':'122222',
        # #         'inout_num_type':'123456','fin_time':'2020-11-10 15:02:41'
        # #         }
        # data = dict(data)
        # data.pop("status", None)
        # order_no = data.get('order_no')
        # if order_no:
        #     temp = MaterialInventoryLog.objects.filter(order_no=order_no).aggregate(all_weight=Sum('weight'))
        #     all_weight = temp.get("all_qty")
        #     if all_weight:
        #         all_weight += float(data.get("qty"))
        #     else:
        #         all_weight = float(data.get("qty"))
        #     order = MaterialOutPlan.objects.filter(order_no=order_no).first()
        #     if order:
        #         need_weight = order.need_weight
        #     else:
        #         return Response({"status": 0, "desc": "失败", "message": "该订单非mes下发订单"})
        #     if int(all_weight) >= need_weight:  # 若加上当前反馈后出库数量已达到订单需求数量则改为(1:完成)
        #         order.status = 1
        #         order.finish_time = datetime.datetime.now()
        #         order.save()
        #     temp_data = {}
        #     temp_data['warehouse_no'] = order.warehouse_info.no
        #     temp_data['warehouse_name'] = order.warehouse_info.name
        #     temp_data['inout_reason'] = order.inventory_reason
        #     temp_data['unit'] = order.unit
        #     temp_data['initiator'] = order.created_user
        #     temp_data['material_no'] = order.material_no
        #     temp_data['start_time'] = order.created_date
        #     temp_data['order_type'] = order.order_type if order.order_type else "出库"
        #     temp_data['station'] = order.station
        #     equip_list = list(set(order.equip.all().values_list("equip_no", flat=True)))
        #     temp_data["dst_location"] = ",".join(equip_list)
        #     material = Material.objects.filter(material_no=order.material_no).first()
        #     material_inventory_dict = {
        #         "material": material,
        #         "container_no": data.get("pallet_no"),
        #         "site_id": 15,
        #         "qty": data.get("qty"),
        #         "unit": order.unit,
        #         "unit_weight": float(data.get("weight")) / float(data.get("qty")),
        #         "total_weight": data.get("weight"),
        #         "quality_status": data.get("quality_status"),
        #         "lot_no": data.get("lot_no"),
        #         "location": "预留",
        #         "warehouse_info": order.warehouse_info,
        #     }
        # else:
        #     raise ValidationError("订单号不能为空")
        # MaterialInventory.objects.create(**material_inventory_dict)
        # try:
        #     MaterialInventoryLog.objects.create(**data, **temp_data)
        # except Exception as e:
        #     logger.error(e)
        #     result = {"status": 0, "desc": "失败", "message": f"反馈异常{e}"}
        # else:
        #     result = {"status": 1, "desc": "成功", "message": "反馈成功"}
        #     if data.get("inventory_type"):  # 若加上当前反馈后出库数量已达到订单需求数量则改为(1:完成)
        #         order.status = 1
        #         order.finish_time = datetime.datetime.now()
        #         order.save()
        # return Response(result)


# 出库大屏
# 分为混炼胶和终炼胶出库大屏
# 混炼胶出库大屏一共份三个接口
@method_decorator([api_recorder], name="dispatch")
class DeliveryPlanNow(APIView):
    """混炼胶 当前在出库口的胶料信息"""

    def get(self, request):
        dp_last_obj = DeliveryPlan.objects.filter(status=2).all().last()
        if dp_last_obj:
            try:
                location_name = dp_last_obj.dispatch.all().filter(
                    order_no=dp_last_obj.order_no).last().dispatch_location.name
            except:
                location_name = None
            try:
                if IS_BZ_USING:
                    mix_gum_out_obj = MixGumOutInventoryLog.objects.using('bz').filter(
                        order_no=dp_last_obj.order_no).last()
                else:
                    mix_gum_out_obj = MixGumOutInventoryLog.objects.filter(order_no=dp_last_obj.order_no).last()
            except Exception as e:
                raise ValidationError(f'连接北自数据库超时: {e}')
            if mix_gum_out_obj:
                lot_no = mix_gum_out_obj.lot_no
            else:
                lot_no = None
            result = {'order_no': dp_last_obj.order_no,
                      'material_no': dp_last_obj.material_no,
                      'location_name': location_name,
                      'lot_no': lot_no}

        else:
            result = None
        return Response({"result": result})


@method_decorator([api_recorder], name="dispatch")
class DeliveryPlanToday(APIView):
    """混炼胶  今日的总出库量"""

    def get(self, request):
        # 计划数量
        delivery_plan_qty = DeliveryPlan.objects.filter(finish_time__date=datetime.datetime.today()).values(
            'material_no').annotate(plan_qty=Sum('need_qty'))
        # 计划出库的order_no列表
        delivery_plan_set = DeliveryPlan.objects.filter(finish_time__date=datetime.datetime.today())
        delivery_plan_order_no_list = list(delivery_plan_set.values_list('order_no', flat=True))
        # 计划出库的material_no列表
        delivery_plan_material_no_list = list(delivery_plan_set.values_list('material_no', flat=True))
        try:

            if IS_BZ_USING:
                # 出库数量
                mix_gum_out_qty = MixGumOutInventoryLog.objects.using('bz').filter(
                    order_no__in=delivery_plan_order_no_list).values(
                    'material_no').annotate(out_qty=Sum('qty'))
                # 库存余量
                bz_inventory_qty = BzFinalMixingRubberInventory.objects.using('bz').filter(
                    material_no__in=delivery_plan_material_no_list).values(
                    'material_no').annotate(inventory_qty=Sum('qty'))
            else:
                mix_gum_out_qty = MixGumOutInventoryLog.objects.filter(order_no__in=delivery_plan_order_no_list).values(
                    'material_no').annotate(out_qty=Sum('qty'))

                bz_inventory_qty = BzFinalMixingRubberInventory.objects.filter(
                    material_no__in=delivery_plan_material_no_list).values(
                    'material_no').annotate(inventory_qty=Sum('qty'))
        except Exception as e:
            raise ValidationError(f'连接北自数据库超时: {e}')
        for delivery_plan in delivery_plan_qty:
            delivery_plan['out_qty'] = None
            delivery_plan['inventory_qty'] = None
            for mix_gum_out in mix_gum_out_qty:
                if delivery_plan['material_no'] == mix_gum_out['material_no']:
                    delivery_plan['out_qty'] = mix_gum_out['out_qty']
            for bz_inventory in bz_inventory_qty:
                if delivery_plan['material_no'] == bz_inventory['material_no']:
                    delivery_plan['inventory_qty'] = bz_inventory['inventory_qty']
        return Response({'result': delivery_plan_qty})


@method_decorator([api_recorder], name="dispatch")
class MixGumOutInventoryLogAPIView(APIView):
    """混炼胶  倒叙显示最近几条出库信息"""

    def get(self, request):
        try:
            if IS_BZ_USING:
                mix_gum_out_data = MixGumOutInventoryLog.objects.using('bz').filter(
                    start_time__date=datetime.datetime.today()).order_by(
                    '-start_time').values(
                    'order_no',
                    'start_time',
                    'location', 'pallet_no',
                    'lot_no', 'material_no',
                    'qty', 'weight',
                    'quality_status')

            else:
                mix_gum_out_data = MixGumOutInventoryLog.objects.filter(
                    start_time__date=datetime.datetime.today()).order_by('-start_time').values(
                    'order_no',
                    'start_time',
                    'location', 'pallet_no',
                    'lot_no', 'material_no',
                    'qty', 'weight',
                    'quality_status')

            for mix_gum_out_obj in mix_gum_out_data:
                dp_last_obj = DeliveryPlan.objects.filter(order_no=mix_gum_out_obj['order_no']).all().last()
                location_name = None
                if dp_last_obj:
                    try:
                        location_name = dp_last_obj.dispatch.all().filter(
                            order_no=dp_last_obj.order_no).last().dispatch_location.name
                    except:
                        location_name = None
                mix_gum_out_obj['location_name'] = location_name
                mix_gum_out_obj['start_time'] = mix_gum_out_obj['start_time'].strftime('%Y-%m-%d %H:%M:%S')
        except:
            raise ValidationError('连接北自数据库超时')
        return Response({'result': mix_gum_out_data})


# 终炼胶出库大屏一共份三个接口
@method_decorator([api_recorder], name="dispatch")
class DeliveryPlanFinalNow(APIView):
    """终炼胶 当前在出库口的胶料信息"""

    def get(self, request):
        dp_last_obj = DeliveryPlanFinal.objects.filter(status=2).all().last()
        if dp_last_obj:
            try:
                location_name = dp_last_obj.dispatch.all().filter(
                    order_no=dp_last_obj.order_no).last().dispatch_location.name
            except:
                location_name = None
            try:
                if IS_BZ_USING:
                    final_gum_out_obj = FinalGumOutInventoryLog.objects.using('lb').filter(
                        order_no=dp_last_obj.order_no).last()
                else:
                    final_gum_out_obj = FinalGumOutInventoryLog.objects.filter(order_no=dp_last_obj.order_no).last()
            except Exception as e:
                raise ValidationError(f'连接北自数据库超时: {e}')
            if final_gum_out_obj:
                lot_no = final_gum_out_obj.lot_no
            else:
                lot_no = None
            result = {'order_no': dp_last_obj.order_no,
                      'material_no': dp_last_obj.material_no,
                      'location_name': location_name,
                      'lot_no': lot_no}

        else:
            result = None
        return Response({"result": result})


@method_decorator([api_recorder], name="dispatch")
class DeliveryPlanFinalToday(APIView):
    """终炼胶  今日的总出库量"""

    def get(self, request):
        # 计划数量
        delivery_plan_qty = DeliveryPlanFinal.objects.filter(finish_time__date=datetime.datetime.today()).values(
            'material_no').annotate(plan_qty=Sum('need_qty'))
        # 计划出库的order_no列表
        deliver_plan_set = DeliveryPlanFinal.objects.filter(finish_time__date=datetime.datetime.today())
        delivery_plan_order_no_list = list(deliver_plan_set.values_list('order_no', flat=True))
        # 计划出库的material_no列表
        delivery_plan_material_no_list = list(deliver_plan_set.values_list('material_no', flat=True))
        try:
            if IS_BZ_USING:
                # 出库数量
                mix_gum_out_qty = FinalGumOutInventoryLog.objects.using('lb').filter(
                    order_no__in=delivery_plan_order_no_list).values(
                    'material_no').annotate(out_qty=Sum('qty'))
                # 库存余量
                bz_inventory_qty = BzFinalMixingRubberInventory.objects.using('lb').filter(
                    material_no__in=delivery_plan_material_no_list).values(
                    'material_no').annotate(inventory_qty=Sum('qty'))
            else:
                mix_gum_out_qty = FinalGumOutInventoryLog.objects.filter(
                    order_no__in=delivery_plan_order_no_list).values(
                    'material_no').annotate(out_qty=Sum('qty'))
                bz_inventory_qty = BzFinalMixingRubberInventory.objects.filter(
                    material_no__in=delivery_plan_material_no_list).values(
                    'material_no').annotate(inventory_qty=Sum('qty'))
            # print(delivery_plan_qty, mix_gum_out_qty, bz_inventory_qty)
        except:
            raise ValidationError('连接北自数据库超时')
        for delivery_plan in delivery_plan_qty:
            delivery_plan['out_qty'] = None
            delivery_plan['inventory_qty'] = None
            for mix_gum_out in mix_gum_out_qty:
                if delivery_plan['material_no'] == mix_gum_out['material_no']:
                    delivery_plan['out_qty'] = mix_gum_out['out_qty']
            for bz_inventory in bz_inventory_qty:
                if delivery_plan['material_no'] == bz_inventory['material_no']:
                    delivery_plan['inventory_qty'] = bz_inventory['inventory_qty']
        return Response({'result': delivery_plan_qty})


@method_decorator([api_recorder], name="dispatch")
class FinalGumOutInventoryLogAPIView(APIView):
    """终炼胶  倒叙显示最近几条出库信息"""

    def get(self, request):
        try:
            if IS_BZ_USING:
                final_gum_out_data = FinalGumOutInventoryLog.objects.using('lb').filter(
                    start_time__date=datetime.datetime.today()).order_by(
                    '-start_time').values(
                    'order_no',
                    'start_time',
                    'location', 'pallet_no',
                    'lot_no', 'material_no',
                    'qty', 'weight',
                    'quality_status')
            else:
                final_gum_out_data = FinalGumOutInventoryLog.objects.filter(
                    start_time__date=datetime.datetime.today()).order_by('-start_time').values(
                    'order_no',
                    'start_time',
                    'location', 'pallet_no',
                    'lot_no', 'material_no',
                    'qty', 'weight',
                    'quality_status')
            for mix_gum_out_obj in final_gum_out_data:
                dp_last_obj = DeliveryPlanFinal.objects.filter(order_no=mix_gum_out_obj['order_no']).all().last()
                location_name = None
                if dp_last_obj:
                    try:
                        location_name = dp_last_obj.dispatch.all().filter(
                            order_no=dp_last_obj.order_no).last().dispatch_location.name
                    except:
                        location_name = None
                mix_gum_out_obj['location_name'] = location_name
                mix_gum_out_obj['start_time'] = mix_gum_out_obj['start_time'].strftime('%Y-%m-%d %H:%M:%S')
        except Exception as e:
            raise ValidationError(f'连接北自数据库超时:{e}')
        return Response({'result': final_gum_out_data})


@method_decorator([api_recorder], name="dispatch")
class InventoryStaticsView(APIView):
    # permission_classes = (IsAuthenticated, PermissionClass({'view': 'view_product_stock_detail'}))

    # def single_mix_inventory(self, product_type, model=BzFinalMixingRubberInventory):
    #     temp_set = model.objects.filter(material_no__icontains=product_type)
    #     data = {}
    #     for section in self.sections:
    #         data.update(**{section: temp_set.filter(material_no__icontains=section).aggregate(weight=Sum('total_weight')/1000)})
    #     return data
    #
    # def single_edge_inventory(self, product_type, model=MaterialInventory, filter_key="material"):
    #     temp_set = model.objects.filter(material__material_no__icontains=product_type)
    #     data = {}
    #     for section in self.sections:
    #         data.update(**{
    #             section: temp_set.filter(material__material_no__icontains=section).aggregate(weight=Sum('total_weight') / 1000)})
    #     return data
    def my_sum(self, x, y):
        if not x:
            x = 0
        if not y:
            y = 0
        return x + y

    def my_cut(self, x, y):
        if not x:
            x = 0
        if not y:
            y = 0
        return x - y

    def single(self, model, filter_key="material__material_no__icontains", db="default"):
        temp_set = model.objects.using(db).filter(**{filter_key: self.product_type,
                                                     }).values(filter_key.split('__icontains')[0]).annotate(
            qty=Sum('qty'), weight=Sum('total_weight')).values(filter_key.split('__icontains')[0], 'qty', 'weight')

        return temp_set

    def get_sections(self, s_time, e_time):
        main_titles = []
        edge_titles = []
        product_set = set(
            BzFinalMixingRubberInventory.objects.filter(material_no__icontains=self.product_type,
                                                        in_storage_time__gte=s_time,
                                                        in_storage_time__lte=e_time
                                                        ).using('bz').values(
                'material_no').annotate().values_list('material_no', flat=True))

        for x in product_set:
            try:
                t = x.split('-')[1]
            except:
                pass
            else:
                main_titles.append(t)
        edge_set = set(MaterialInventory.objects.filter(material__material_no=self.product_type,
                                                        created_date__gte=s_time,
                                                        created_date__lte=e_time
                                                        ).values(
            'material__material_no').annotate().values_list('material__material_no', flat=True))

        for x in edge_set:
            try:
                t = x.split('-')[1]
            except:
                pass
            else:
                edge_titles.append(t)
        return list(main_titles), list(edge_titles)

    def get(self, request):
        product_type = request.query_params.get("name")
        s_time = request.query_params.get("s_time")
        e_time = request.query_params.get("e_time")
        page = request.query_params.get("page", 1)
        if not s_time and not e_time:
            s_time, e_time = '1111-11-11', '9999-11-11'

        self.product_type = product_type
        main_titles, edge_titles = self.get_sections(s_time, e_time)
        # st = (int(page) - 1) * 10
        # et = int(page) * 10

        a = MaterialInventory.objects.using('default').filter(material__material_no__icontains=self.product_type,
                                                              created_date__gte=s_time,
                                                              created_date__lte=e_time
                                                              ).values('material__material_no').annotate(
            qty=Sum('qty'), weight=Sum('total_weight')).values('material__material_no', 'qty', 'weight').order_by('material')
        aa = []
        if len(a) > 0:
            for i in a:
                aa.append({'material_no': i['material__material_no'], 'qty': i['qty'], 'weight': i['weight']})

        bz = BzFinalMixingRubberInventory.objects.using('bz').filter(material_no__icontains=self.product_type,
                                                                     in_storage_time__gte=s_time,
                                                                     in_storage_time__lte=e_time
                                                                     ).values('material_no').annotate(
            qty=Sum('qty'), weight=Sum('total_weight')).values('material_no', 'qty', 'weight').order_by('material_no')

        lb = BzFinalMixingRubberInventoryLB.objects.using('lb').filter(material_no__icontains=self.product_type,
                                                                       store_name='炼胶库',
                                                                       in_storage_time__gte=s_time,
                                                                       in_storage_time__lte=e_time
                                                                       ).values('material_no').annotate(
            qty=Sum('qty'), weight=Sum('total_weight')).values('material_no', 'qty', 'weight').order_by('material_no')

        edge = list(aa)  # 车间
        subject = list(bz) + list(lb)  # 立库

        results = {}

        for i in subject:
            try:
                res = {
                    i['material_no'].split('-')[2]: {
                        'subject': {i['material_no'].split('-')[1]: {'qty': i['qty'], 'weight': i['weight']}},
                        'edge': {},
                        'error': 0,
                        'fm_all': 0,
                        'ufm_all': 0  # 不加硫
                    }
                }

                if results.get(i['material_no'].split('-')[2]):
                    if results[i['material_no'].split('-')[2]]['subject'].get(i['material_no'].split('-')[1]):
                        results[i['material_no'].split('-')[2]]['subject'][i['material_no'].split('-')[1]]['qty'] += i[
                            'qty']
                        results[i['material_no'].split('-')[2]]['subject'][i['material_no'].split('-')[1]]['weight'] += \
                        i['weight']
                    else:
                        results[i['material_no'].split('-')[2]]['subject'].update(
                            {i['material_no'].split('-')[1]: {'qty': i['qty'], 'weight': i['weight']}})
                else:
                    results.update(res)
            except:
                pass

        for i in edge:
            try:
                res = {i['material_no'].split('-')[2]: {
                    'subject': {},
                    'edge': {i['material_no'].split('-')[1]: {'qty': i['qty'], 'weight': i['weight']}},
                    'error': 0,
                    'fm_all': 0,
                    'ufm_all': 0  # 不加硫
                }}

                if results.get(i['material_no'].split('-')[2]):
                    if results[i['material_no'].split('-')[2]]['subject'].get(i['material_no'].split('-')[1]):
                        results[i['material_no'].split('-')[2]]['subject'][i['material_no'].split('-')[1]]['qty'] += i['qty']
                        results[i['material_no'].split('-')[2]]['subject'][i['material_no'].split('-')[1]]['weight'] += i['weight']
                    else:
                        results[i['material_no'].split('-')[2]]['subject'].update(
                            {i['material_no'].split('-')[1]: {'qty': i['qty'], 'weight': i['weight']}})
                else:
                    results.update(res)
            except:
                pass

        for i in results:
            if "RFM" in main_titles and "FM" in main_titles:  # ['1MB', 'HMB']
                fm1_weight = results[i]['subject'].get("FM", {}).get("weight")
                rfm1_weight = results[i]['subject'].get("RFM", {}).get("weight")
                fm1_qty = results[i]['subject'].get("FM", {}).get("qty")
                rfm1_qty = results[i]['subject'].get("RFM", {}).get("qty")
                results[i]['subject']["FM"]["weight"] = self.my_cut(fm1_weight, rfm1_weight)
                results[i]['subject']["FM"]["qty"] = self.my_cut(fm1_qty, rfm1_qty)
            if "RFM" in main_titles and "FM" in main_titles:
                fm2_weight = results[i]['edge'].get("FM", {}).get("weight")
                rfm2_weight = results[i]['edge'].get("RFM", {}).get("weight")
                fm2_qty = results[i]['edge'].get("FM", {}).get("qty")
                rfm2_qty = results[i]['edge'].get("RFM", {}).get("qty")
                results[i]['edge']["FM"]["weight"] = self.my_cut(fm2_weight, rfm2_weight)
                results[i]['edge']["FM"]["qty"] = self.my_cut(fm2_qty, rfm2_qty)

        # 不合格加硫计算/ 加硫总量计算
        s = ["FM", 'RE', 'RFM']
        for station in s:
            edge_error = MaterialInventory.objects.filter(material__material_no__icontains=self.product_type).filter(
                material__material_no__icontains=f'-{station}').values('material__material_no',
                                                                       'quality_status').annotate(
                weight=Sum("total_weight")).values('material__material_no', 'weight', 'quality_status')
            if len(edge_error) > 0:
                for i in edge_error:
                    try:
                        if results.get(i['material__material_no'].split('-')[2]) and i['quality_status'] == '三等品':
                            results[i['material__material_no'].split('-')[2]]['error'] += i['weight']
                        if results.get(i['material__material_no'].split('-')[2]):
                            results[i['material__material_no'].split('-')[2]]['fm_all'] += i['weight']
                    except:
                        pass

            inventory_error = BzFinalMixingRubberInventory.objects.using('bz').filter(
                in_storage_time__gte=s_time,
                in_storage_time__lte=e_time,
                material_no__icontains=self.product_type).filter(material_no__icontains=f'-{station}',
                                                                 ).values('material_no', 'quality_level'). \
                annotate(weight=Sum("total_weight")).values('material_no', 'weight', 'quality_level')
            if len(inventory_error) > 0:
                for i in inventory_error:
                    try:
                        if results.get(i['material_no'].split('-')[2]) and i['quality_level'] == '三等品':
                            results[i['material_no'].split('-')[2]]['error'] += i['weight']
                        if results.get(i['material_no'].split('-')[2]):
                            results[i['material_no'].split('-')[2]]['fm_all'] += i['weight']
                    except:
                        pass

            lb_error = BzFinalMixingRubberInventoryLB.objects.using('lb').filter(
                in_storage_time__gte=s_time,
                in_storage_time__lte=e_time,
                material_no__icontains=self.product_type).filter(material_no__icontains=f'-{station}',
                                                                 ).values('material_no', 'quality_level'). \
                annotate(weight=Sum("total_weight")).values('material_no', 'weight', 'quality_level')
            if len(lb_error) > 0:
                for i in lb_error:
                    try:
                        if results.get(i['material_no'].split('-')[2]) and i['quality_level'] == '三等品':
                            results[i['material_no'].split('-')[2]]['error'] += i['weight']
                        if results.get(i['material_no'].split('-')[2]):
                            results[i['material_no'].split('-')[2]]['fm_all'] += i['weight']
                    except:
                        pass

        # 无硫总量计算
        ws = ["CMB", 'HMB', 'NF', 'RMB', '1MB', '2MB', '3MB']
        for station in ws:
            product_mi = MaterialInventory.objects.filter(material__material_no__icontains=self.product_type,
                                                          created_date__gte=s_time,
                                                          created_date__lte=e_time
                                                          ).filter(
                material__material_no__icontains=station).values('material__material_no'). \
                annotate(weight=Sum("total_weight")).values('material__material_no', 'weight')
            if len(product_mi) > 0:
                for i in product_mi:
                    try:
                        if results.get(i['material__material_no'].split('-')[2]):
                            results[i['material__material_no'].split('-')[2]]['ufm_all'] += i['weight']
                    except:
                        pass

            product_bz = BzFinalMixingRubberInventory.objects.using('bz').filter(
                material_no__icontains=self.product_type,
                in_storage_time__gte=s_time,
                in_storage_time__lte=e_time,
                ).filter(
                material_no__icontains=station).values('material_no').annotate(weight=Sum("total_weight")).values(
                'material_no', 'weight')
            if len(product_bz) > 0:
                for i in product_bz:
                    try:
                        if results.get(i['material_no'].split('-')[2]):
                            results[i['material_no'].split('-')[2]]['ufm_all'] += i['weight']
                    except:
                        pass

            product_lb = BzFinalMixingRubberInventoryLB.objects.using('lb').filter(
                material_no__icontains=self.product_type,
                in_storage_time__gte=s_time,
                in_storage_time__lte=e_time,
                ).filter(
                material_no__icontains=station).values('material_no').annotate(weight=Sum("total_weight")).values(
                'material_no', 'weight')
            if len(product_lb) > 0:
                for i in product_lb:
                    try:
                        if results.get(i['material_no'].split('-')[2]):
                            results[i['material_no'].split('-')[2]]['ufm_all'] += i['weight']
                    except:
                        pass

        for i in results:
            lst = ["CMB", 'HMB', 'NF', 'RMB', '1MB', '2MB', '3MB', "FM", 'RE', 'RFM']
            for j in lst:
                try:
                    results[i]['subject'][j]['weight'] = round(results[i]['subject'][j]['weight'] / 1000, 3) if \
                    results[i]['subject'].get(j) else None
                except:
                    pass
                try:
                    results[i]['edge'][j]['weight'] = round(results[i]['edge'][j]['weight'] / 1000, 3) if results[i][
                        'edge'].get(j) else None
                except:
                    pass
            results[i]['error'] = round(results[i]['error'] / 1000, 3)
            results[i]['fm_all'] = round(results[i]['fm_all'] / 1000, 3)
            results[i]['ufm_all'] = round(results[i]['ufm_all'] / 1000, 3)

        return Response({'results': results, 'count': len(results)})


@method_decorator([api_recorder], name="dispatch")
class ProductDetailsView(APIView):
    permission_classes = (IsAuthenticated, PermissionClass({'view': 'view_workshop_stock_detail'}))

    def get(self, request):
        mix_set = BzFinalMixingRubberInventory.objects.using('bz').all()
        final_set = BzFinalMixingRubberInventory.objects.using('lb').filter(store_name='炼胶库').all()
        mix_data = mix_set.values("material_no", 'quality_level').annotate(qty=Sum('qty'), weight=Sum('total_weight')).values(
            "material_no", 'qty', 'weight', 'quality_level')
        final_data = final_set.values("material_no", 'quality_level').annotate(qty=Sum('qty'), weight=Sum('total_weight')).values(
            "material_no", 'qty', 'weight', 'quality_level')
        total_inventory_data = list(mix_data) + list(final_data)
        factory_date = get_current_factory_date().get('factory_date', datetime.datetime.now().date())
        area_data = ProductStockDailySummary.objects.filter(factory_date=factory_date).values('product_no', 'area_weight', 'stage')
        stock_data_dict = {}
        for x in total_inventory_data:
            m_split_data = x['material_no'].strip().split('-')
            stage = m_split_data[1]
            product_no = m_split_data[2]
            weight = x['weight'] / 1000
            qty = x['qty']
            quality_level = x['quality_level']
            if stage == 'FM':
                if quality_level == '一等品':
                    st = '合格'
                elif quality_level == '三等品':
                    st = '合格'
                else:
                    st = '待检测'
                stage = '{}({})'.format(stage, st)
            if product_no not in stock_data_dict:
                stock_data_dict[product_no] = {stage: {'weight': weight, 'qty': qty}}
            else:
                if stage not in stock_data_dict[product_no]:
                    stock_data_dict[product_no][stage] = {'weight': weight, 'qty': qty}
                else:
                    stock_data_dict[product_no][stage]['weight'] += weight
                    stock_data_dict[product_no][stage]['qty'] += qty
        area_data_dict = {}
        for item in area_data:
            product_no = item['product_no']
            weight = item['area_weight'] / 1000
            stage = item['stage']
            if stage in ('CMB', 'HMB'):
                stage = 'C/HMB'
            if product_no not in area_data_dict:
                area_data_dict[product_no] = {stage: {'weight': weight, 'qty': ''}}
            else:
                area_data_dict[product_no][stage] = {'weight': weight, 'qty': ''}
        common_product_nos = set(area_data_dict.keys()) & set(stock_data_dict.keys())
        l_product_nos = set(area_data_dict.keys()) - set(stock_data_dict.keys())
        r_product_nos = set(stock_data_dict.keys()) - set(area_data_dict.keys())
        ret = []
        for i in common_product_nos:
            ret.append({'product_no': i, 'area_data': area_data_dict[i], 'stock_data': stock_data_dict[i]})
        for i in l_product_nos:
            ret.append({'product_no': i, 'area_data': area_data_dict[i], 'stock_data': {}})
        for i in r_product_nos:
            ret.append({'product_no': i, 'area_data': {}, 'stock_data': stock_data_dict[i]})
        ret = sorted(ret, key=lambda x: x['product_no'])
        return Response({"results": ret})


"""原材料库出库接口"""


class WmsStorageSummaryView(APIView):
    """
        原材料库存统计列表（按物料编码、品质状态、单位、批次号分组统计）
        参数：?material_name=物料名称&material_no=物料编码&zc_material_code=中策物料编码&batch_no=批次号&pdm_no=PDM号&st=入库开始时间&et=入库结束时间&quality_status=# 品质状态 1：合格 3：不合格
    """
    DATABASE_CONF = WMS_CONF
    permission_classes = (IsAuthenticated, )

    def get(self, request):
        factory = self.request.query_params.get('factory')  # 厂家
        material_name = self.request.query_params.get('material_name')  # 物料名称
        material_no = self.request.query_params.get('material_no')  # 物料编码
        zc_material_code = self.request.query_params.get('zc_material_code')  # 中策物料编码
        batch_no = self.request.query_params.get('batch_no')  # 批次号
        pdm_no = self.request.query_params.get('pdm_no')  # PDM号
        inventory_st = self.request.query_params.get('st')  # 入库开始时间
        inventory_et = self.request.query_params.get('et')  # 入库结束时间
        quality_status = self.request.query_params.get('quality_status')  # 品质状态 1：合格  3：不合格
        page = self.request.query_params.get('page', 1)
        page_size = self.request.query_params.get('page_size', 15)
        st = (int(page) - 1) * int(page_size)
        et = int(page) * int(page_size)
        extra_where_str = inventory_where_str = ""
        if material_name:
            extra_where_str += "where temp.MaterialName like '%{}%'".format(material_name)
        if factory:
            if extra_where_str:
                extra_where_str += " and temp.MaterialName like '%{}%'".format(factory)
            else:
                extra_where_str += "where temp.MaterialName like '%{}%'".format(factory)
        if material_no:
            if extra_where_str:
                extra_where_str += " and temp.MaterialCode like '%{}%'".format(material_no)
            else:
                extra_where_str += "where temp.MaterialCode like '%{}%'".format(material_no)
        if zc_material_code:
            if extra_where_str:
                extra_where_str += " and m.ZCMaterialCode='{}'".format(zc_material_code)
            else:
                extra_where_str += "where m.ZCMaterialCode='{}'".format(zc_material_code)
        if batch_no:
            if extra_where_str:
                extra_where_str += " and temp.BatchNo='{}'".format(batch_no)
            else:
                extra_where_str += "where temp.BatchNo='{}'".format(batch_no)
        if quality_status:
            if extra_where_str:
                extra_where_str += " and temp.StockDetailState='{}'".format(quality_status)
            else:
                extra_where_str += "where temp.StockDetailState='{}'".format(quality_status)
        if pdm_no:
            if extra_where_str:
                extra_where_str += " and m.Pdm='{}'".format(pdm_no)
            else:
                extra_where_str += "where m.Pdm='{}'".format(pdm_no)
        if inventory_st:
            if inventory_where_str:
                inventory_where_str += " and a.CreaterTime>='{}'".format(inventory_st)
            else:
                inventory_where_str += "where a.CreaterTime>='{}'".format(inventory_st)
        if inventory_et:
            if inventory_where_str:
                inventory_where_str += " and a.CreaterTime<='{}'".format(inventory_et)
            else:
                inventory_where_str += "where a.CreaterTime<='{}'".format(inventory_et)
        sql = """
                select
            temp.MaterialName,
            temp.MaterialCode,
            m.ZCMaterialCode,
            temp.StandardUnit,
            m.Pdm,
            temp.quantity,
            temp.WeightOfActual,
            temp.BatchNo,
            temp.StockDetailState,
            temp.creater_time
        from (
            select
                a.MaterialCode,
                a.BatchNo,
                a.StandardUnit,
                a.StockDetailState,
                a.MaterialName,
                SUM ( a.WeightOfActual ) AS WeightOfActual,
                SUM ( a.Quantity ) AS quantity,
                Min (a.CreaterTime) as creater_time
            from dbo.t_inventory_stock AS a
            {}
            group by
                 a.MaterialCode,
                 a.MaterialName,
                 a.BatchNo,
                 a.StandardUnit,
                 a.StockDetailState
            ) temp
        left join t_inventory_material m on m.MaterialCode=temp.MaterialCode 
        {}
        order by m.MaterialCode
        """.format(inventory_where_str, extra_where_str)
        sc = SqlClient(sql=sql, **self.DATABASE_CONF)
        temp = sc.all()
        l_data = list(WmsNucleinManagement.objects.filter(locked_status='已锁定').values_list('batch_no', flat=True))
        if self.request.query_params.get('l_flag'):
            temp = list(filter(lambda x: x[7] not in l_data, temp))
        count = len(temp)
        temp = temp[st:et]
        result = []
        for item in temp:
            result.append(
                {'material_name': item[0],
                 'material_no': item[1],
                 'zc_material_code': item[2],
                 'unit': item[3],
                 'pdm_no': item[4],
                 'quantity': item[5],
                 'weight': item[6],
                 'batch_no': item[7],
                 'quality_status': item[8],
                 'factory': re.findall(r'[(](.*?)[)]', item[0])[-1] if re.findall(r'[(](.*?)[)]', item[0]) else '',
                 'creater_time': item[9].strftime('%Y-%m-%d %H:%M:%S') if isinstance(item[9], datetime.datetime) else item[9]
                 })
        sc.close()
        return Response({'results': result, "count": count})


@method_decorator([api_recorder], name="dispatch")
class WmsStorageView(ListAPIView):
    queryset = WmsInventoryStock.objects.order_by('in_storage_time')
    serializer_class = WmsInventoryStockSerializer
    permission_classes = (IsAuthenticated,)
    DATABASE_CONF = 'wms'
    FILE_NAME = '原材料库位明细'
    EXPORT_FIELDS_DICT = {"物料名称": "material_name", "物料编码": "material_no", "质检条码": "lot_no",
                          "批次号": "batch_no", "是否进烘房": "is_entering", "供应商": "supplier_name",
                          "托盘号": "container_no", "库位地址": "location", "单位": "unit",
                          "单位重量": "unit_weight", "总重量": "total_weight",
                          "核酸管控": "in_charged_tag", "品质状态": "quality_status",
                          '件数': 'sl', '唛头重量': 'zl'}

    def list(self, request, *args, **kwargs):
        filter_kwargs = {}
        # 模糊查询字段
        container_no = self.request.query_params.get('pallet_no')
        material_name = self.request.query_params.get('material_name')
        material_no = self.request.query_params.get('material_no')
        material_nos = self.request.query_params.get('material_nos')
        supplier_name = self.request.query_params.get('supplier_name')
        l_batch_no = self.request.query_params.get('l_batch_no')
        tunnel = self.request.query_params.get('tunnel')
        # 等于查询
        e_material_no = self.request.query_params.get('e_material_no')
        e_material_name = self.request.query_params.get('e_material_name')
        unit = self.request.query_params.get('unit')
        batch_no = self.request.query_params.get('batch_no')
        is_entering = self.request.query_params.get('is_entering')
        in_charged_tag = self.request.query_params.get('in_charged_tag')
        st = self.request.query_params.get('st')
        et = self.request.query_params.get('et')
        quality_status = self.request.query_params.get('quality_status')
        mooney_level = self.request.query_params.get('mooney_level')
        export = self.request.query_params.get('export')  # 1：当前页面  2：所有
        if material_no:
            filter_kwargs['material_no__icontains'] = material_no
        if material_nos:
            filter_kwargs['material_no__in'] = material_nos.split(',')
        if material_name:
            filter_kwargs['material_name__icontains'] = material_name
        if container_no:
            filter_kwargs['container_no__icontains'] = container_no
        if supplier_name:
            filter_kwargs['supplier_name__icontains'] = supplier_name
        if l_batch_no:
            filter_kwargs['batch_no__icontains'] = l_batch_no
        if e_material_no:
            filter_kwargs['material_no'] = e_material_no
        if e_material_name:
            filter_kwargs['material_name'] = e_material_name
        if unit:
            filter_kwargs['unit'] = unit
        if batch_no:
            filter_kwargs['batch_no'] = batch_no
        if quality_status:
            filter_kwargs['quality_status'] = quality_status
        if st:
            filter_kwargs['in_storage_time__gte'] = st
        if et:
            filter_kwargs['in_storage_time__lte'] = et
        if tunnel:
            filter_kwargs['location__startswith'] = 'ZCM-{}'.format(tunnel)
        queryset = WmsInventoryStock.objects.using(self.DATABASE_CONF).filter(**filter_kwargs).order_by('in_storage_time')
        if is_entering:
            if is_entering == 'Y':
                queryset = queryset.filter(container_no__startswith=5)
            elif is_entering == 'N':
                queryset = queryset.exclude(container_no__startswith=5)
        if in_charged_tag:
            if in_charged_tag in ('已锁定', '已解锁'):
                batch_nos = list(WmsNucleinManagement.objects.filter(
                    locked_status=in_charged_tag).values_list('batch_no', flat=True))
                queryset = queryset.filter(batch_no__in=batch_nos)
            else:
                batch_nos = list(WmsNucleinManagement.objects.values_list('batch_no', flat=True))
                queryset = queryset.exclude(batch_no__in=batch_nos)
        stock_batch_nos = set(queryset.values_list('batch_no', flat=True))
        context = {
            'request': self.request,
            'format': self.format_kwarg,
            'view': self,
            'ncm_data': dict(WmsNucleinManagement.objects.filter(batch_no__in=stock_batch_nos).values_list('batch_no', 'locked_status'))
        }
        if mooney_level:
            wms_mooney_level_material_nos = set(WMSMooneyLevel.objects.filter(
                h_upper_limit_value__isnull=False).values_list('material_no', flat=True))
            stock_material_nos = set(queryset.values_list('material_no', flat=True))
            stock_level_material_nos = wms_mooney_level_material_nos & stock_material_nos
            examined_stock_batch_nos = set(MaterialSingleTypeExamineResult.objects.filter(
                type__name__icontains='门尼',
                material_examine_result__material__batch__in=stock_batch_nos
            ).values_list('material_examine_result__material__batch', flat=True))
            queryset = queryset.filter(material_no__in=stock_level_material_nos,
                                       batch_no__in=examined_stock_batch_nos)
            ret = list(filter(lambda x: x['mn_level'] == mooney_level, WmsInventoryStockSerializer(queryset, many=True, context=context).data))
            page = self.paginate_queryset(ret)
            # serializer = self.get_serializer(page, many=True)
            resp_data = self.get_paginated_response(page).data
            if export:
                if export == '1':
                    data = page
                else:
                    data = ret
                return gen_template_response(self.EXPORT_FIELDS_DICT, data, self.FILE_NAME)
            resp_data['total_weight'] = round(sum(float(i['total_weight']) for i in ret), 2)
            resp_data['total_trains'] = round(sum(float(i['qty']) for i in ret), 2)
            return Response(resp_data)

        page = self.paginate_queryset(queryset)
        serializer = WmsInventoryStockSerializer(page, many=True, context=context)
        if export:
            if export == '1':
                data = serializer.data
            else:
                data = WmsInventoryStockSerializer(queryset, many=True, context=context).data
            return gen_template_response(self.EXPORT_FIELDS_DICT, data, self.FILE_NAME)
        data = self.get_paginated_response(serializer.data).data
        sum_data = queryset.aggregate(total_weight=Sum('total_weight'),
                                      total_trains=Sum('qty'))
        data['total_weight'] = sum_data['total_weight']
        data['total_trains'] = sum_data['total_trains']
        return Response(data)


@method_decorator([api_recorder], name="dispatch")
class WmsInventoryStockView(APIView):
    """WMS库存货位信息，参数：material_name=原材料名称&material_no=原材料编号&quality_status=品质状态1合格3不合格&entrance_name=出库口名称"""
    DATABASE_CONF = WMS_CONF
    permission_classes = (IsAuthenticated, )
    DB = 'WMS'

    def get(self, request, *args, **kwargs):
        material_name = self.request.query_params.get('material_name')
        material_no = self.request.query_params.get('material_no')
        quality_status = self.request.query_params.get('quality_status')
        entrance_name = self.request.query_params.get('entrance_name')
        position = self.request.query_params.get('position')
        is_entering = self.request.query_params.get('is_entering')
        batch_no = self.request.query_params.get('batch_no')
        page = self.request.query_params.get('page', 1)
        page_size = self.request.query_params.get('page_size', 15)
        mooney_level = self.request.query_params.get('mooney_level')
        pallet_no = self.request.query_params.get('pallet_no')
        tunnel = self.request.query_params.get('tunnel')
        st = (int(page) - 1) * int(page_size)
        et = int(page) * int(page_size)
        extra_where_str = ""
        if not entrance_name:
            raise ValidationError('请选择出库口！')
        if material_name:
            extra_where_str += " and c.Name like '%{}%'".format(material_name)
        if material_no:
            extra_where_str += " and c.MaterialCode like '%{}%'".format(material_no)
        if quality_status:
            extra_where_str += " and a.StockDetailState={}".format(quality_status)
        if batch_no:
            extra_where_str += " and a.BatchNo like '%{}%'".format(batch_no)
        if pallet_no:
            extra_where_str += " and a.LadenToolNumber ='{}'".format(pallet_no)
        if tunnel:
            if self.DB == 'WMS':
                extra_where_str += " and a.SpaceId like 'ZCM-{}%'".format(tunnel)
            else:
                extra_where_str += " and a.SpaceId like 'ZCB-{}%'".format(tunnel)

        sql = """SELECT
                 a.StockDetailState,
                 c.MaterialCode,
                 c.Name AS MaterialName,
                 a.BatchNo,
                 a.SpaceId,
                 a.Sn,
                 a.StandardUnit,
                 a.CreaterTime,
                 a.LadenToolNumber
                FROM
                 dbo.t_inventory_stock AS a
                 INNER JOIN t_inventory_space b ON b.Id = a.StorageSpaceEntityId
                 INNER JOIN t_inventory_material c ON c.MaterialCode= a.MaterialCode
                 INNER JOIN t_inventory_tunnel d ON d.TunnelCode= a.TunnelId 
                WHERE
                 NOT EXISTS ( 
                     SELECT 
                            tp.TrackingNumber 
                     FROM t_inventory_space_plan tp 
                     WHERE tp.TrackingNumber = a.TrackingNumber ) 
                 AND d.State= 1 
                 AND b.SpaceState= 1 
                 AND a.TunnelId IN ( 
                     SELECT 
                            ab.TunnelCode 
                     FROM t_inventory_entrance_tunnel ab INNER JOIN t_inventory_entrance ac ON ac.Id= ab.EntranceEntityId 
                     WHERE ac.name= '{}' ) {} order by a.CreaterTime""".format(entrance_name, extra_where_str)
        sc = SqlClient(sql=sql, **self.DATABASE_CONF)
        temp = sc.all()
        if position == '内':
            temp = list(filter(lambda x: x[4][6] in ('1', '2'), temp))
        elif position == '外':
            temp = list(filter(lambda x: x[4][6] in ('3', '4'), temp))
        if is_entering == 'Y':
            temp = list(filter(lambda x: x[8].startswith('5'), temp))
        elif is_entering == 'N':
            temp = list(filter(lambda x: not x[8].startswith('5'), temp))
        count = len(temp)
        result = []
        if not mooney_level:
            temp = temp[st:et]
        stock_batch_nos = set([i[3] for i in temp])
        material_nos = set([i[1] for i in temp])

        # 门尼等级信息
        wms_mooney_levels = WMSMooneyLevel.objects.filter(
            h_upper_limit_value__isnull=False,
            material_no__in=material_nos).values('material_no', 'h_upper_limit_value',
                                                 'h_lower_limit_value', 'm_upper_limit_value',
                                                 'm_lower_limit_value', 'l_upper_limit_value','l_lower_limit_value')
        wms_mooney_level_dict = {i['material_no']: i for i in wms_mooney_levels}

        # 物料检测信息
        examine_data = MaterialSingleTypeExamineResult.objects.filter(
            type__name__icontains='门尼',
            material_examine_result__material__batch__in=stock_batch_nos,
            material_examine_result__material__wlxxid__in=material_nos
        ).values('material_examine_result__material__batch',
                 'material_examine_result__material__wlxxid',
                 'value')
        batch_value_dict = {}
        for i in examine_data:
            k = '{}+{}'.format(i['material_examine_result__material__batch'],
                               i['material_examine_result__material__wlxxid'])
            batch_value_dict[k] = i['value']

        for item in temp:
            batch = item[3].strip()
            material_code = item[1].strip()
            mn_level = ''
            mn_value = ''
            if self.DB == 'WMS':
                ml_test_value = batch_value_dict.get('{}+{}'.format(batch, material_code))
                if ml_test_value:
                    mn_value = ml_test_value
                    level_data = wms_mooney_level_dict.get(material_code)
                    if level_data:
                        h_lower_limit_value = level_data['h_lower_limit_value'] if level_data['h_lower_limit_value'] else 0
                        h_upper_limit_value = level_data['h_upper_limit_value'] if level_data['h_upper_limit_value'] else 0
                        m_lower_limit_value = level_data['m_lower_limit_value'] if level_data['m_lower_limit_value'] else 0
                        m_upper_limit_value = level_data['m_upper_limit_value'] if level_data['m_upper_limit_value'] else 0
                        l_lower_limit_value = level_data['l_lower_limit_value'] if level_data['l_lower_limit_value'] else 0
                        l_upper_limit_value = level_data['l_upper_limit_value'] if level_data['l_upper_limit_value'] else 0
                        if h_lower_limit_value <= ml_test_value <= h_upper_limit_value:
                            mn_level = '高门尼'
                        elif m_lower_limit_value <= ml_test_value <= m_upper_limit_value:
                            mn_level = '标准门尼'
                        elif l_lower_limit_value <= ml_test_value <= l_upper_limit_value:
                            mn_level = '低门尼'
            result.append(
                {'StockDetailState': item[0],
                 'MaterialCode': item[1],
                 'MaterialName': item[2],
                 'BatchNo': item[3],
                 'SpaceId': item[4],
                 'Sn': item[5],
                 'unit': item[6],
                 'inventory_time': item[7],
                 'position': '内' if item[4][6] in ('1', '2') else '外',
                 'RFID': item[8],
                 'mn_level': mn_level,
                 'mn_value': mn_value
                 })
        if mooney_level:
            result = list(filter(lambda x: x['mn_level'] == mooney_level, result))
            count = len(result)
            result = result[st:et]
        sc.close()
        return Response({'results': result, "count": count})


@method_decorator([api_recorder], name="dispatch")
class WmsInStockView(APIView):
    """根据当前货物外伸位地址获取内伸位数据, 参数：entrance_name=出库口名称&space_id=货位地址"""
    DATABASE_CONF = WMS_CONF
    permission_classes = (IsAuthenticated, )

    def get(self, request):
        out_space_id = self.request.query_params.get('space_id')
        entrance_name = self.request.query_params.get('entrance_name')
        if not all([out_space_id, entrance_name]):
            raise ValidationError('参数缺失！')
        out_space_id_list = out_space_id.split('-')
        if out_space_id_list[2] == '3':
            out_space_id_list[2] = '1'
        elif out_space_id_list[2] == '4':
            out_space_id_list[2] = '2'
        else:
            return Response([])
        in_space_id = '-'.join(out_space_id_list)
        sql = """
            SELECT
                 a.StockDetailState,
                 c.MaterialCode,
                 c.Name AS MaterialName,
                 a.BatchNo,
                 a.SpaceId,
                 a.Sn,
                 a.StandardUnit,
                 a.CreaterTime
            FROM 
                 dbo.t_inventory_stock AS a
             INNER JOIN t_inventory_space b ON b.Id = a.StorageSpaceEntityId
             INNER JOIN t_inventory_material c ON c.MaterialCode= a.MaterialCode
             INNER JOIN t_inventory_tunnel d ON d.TunnelCode= a.TunnelId 
            WHERE
             NOT EXISTS ( 
                 SELECT 
                        tp.TrackingNumber 
                 FROM t_inventory_space_plan tp 
                 WHERE tp.TrackingNumber = a.TrackingNumber ) 
             AND d.State= 1 
             AND b.SpaceState= 1 
             AND a.TunnelId IN ( 
                 SELECT 
                        ab.TunnelCode 
                 FROM t_inventory_entrance_tunnel ab INNER JOIN t_inventory_entrance ac ON ac.Id= ab.EntranceEntityId 
                 WHERE ac.name= '{}')
             and a.SpaceId in ('{}', '{}');""".format(
            entrance_name, in_space_id, out_space_id)
        sc = SqlClient(sql=sql, **self.DATABASE_CONF)
        temp = sc.all()
        if len(temp) <= 1:
            return Response([])
        result = []
        for item in temp:
            result.append(
                {'StockDetailState': item[0],
                 'MaterialCode': item[1],
                 'MaterialName': item[2],
                 'BatchNo': item[3],
                 'SpaceId': item[4],
                 'Sn': item[5],
                 'unit': item[6],
                 'inventory_time': item[7],
                 'position': '内' if item[4][6] in ('1', '2') else '外'
                 })
        sc.close()
        return Response(result)


@method_decorator([api_recorder], name="dispatch")
class WMSRelease(APIView):
    permission_classes = (IsAuthenticated, )
    REQUEST_URL = WMS_URL

    def post(self, request):
        operation_type = self.request.data.get('operation_type')  # 1:放行 2: 不放行
        tracking_nums = self.request.data.get('tracking_nums')
        if not all([operation_type, tracking_nums]):
            raise ValidationError('参数不足！')
        if not isinstance(tracking_nums, list):
            raise ValidationError('参数错误！')
        batch_nos = list(WmsInventoryStock.objects.using('wms').filter(lot_no__in=tracking_nums).values_list('batch_no', flat=True))
        if WmsNucleinManagement.objects.filter(
                locked_status='已锁定',
                batch_no__in=batch_nos).exists():
            raise ValidationError('该批次物料已锁定核酸管控，无法处理！')
        data = {
            "TestingType": 1,
            "AllCheckDetailList": []
        }
        release_log_list = []
        for tracking_num in tracking_nums:
            if not tracking_num:
                continue
            check_result = 1
            if operation_type == '不放行':
                check_result = 2
            data['AllCheckDetailList'].append({
                "TrackingNumber": tracking_num,
                "CheckResult": check_result
            })
            release_log_list.append(WMSReleaseLog(**{'tracking_num': tracking_num,
                                                     'operation_type': '放行' if check_result == 1 else '不放行',
                                                     'created_user': self.request.user}))
        headers = {"Content-Type": "application/json ;charset=utf-8"}
        try:
            r = requests.post(self.REQUEST_URL + '/MESApi/UpdateTestingResult', json=data, headers=headers,
                              timeout=5)
            r = r.json()
        except Exception as e:
            raise ValidationError('服务错误！')
        resp_status = r.get('state')
        if not resp_status == 1:
            raise ValidationError('请求失败！{}'.format(r.get('msg')))
        WMSReleaseLog.objects.bulk_create(release_log_list)
        return Response('更新成功！')


@method_decorator([api_recorder], name="dispatch")
class WMSExceptHandleView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        material_code = self.request.query_params.get('material_code', None)
        lot_no = self.request.query_params.get('lot_no', None)
        batch_no = self.request.query_params.get('batch_no', None)
        if batch_no:
            queryset = []
            nums = WMSExceptHandle.objects.filter(batch_no=batch_no).values_list('num', flat=True)
            for num in set(nums):
                queryset.append(WMSExceptHandle.objects.filter(batch_no=batch_no, num=num).first())
        else:
            queryset = WMSExceptHandle.objects.filter(material_code=material_code,lot_no=lot_no).order_by('id')
        if queryset:
            serializer = WMSExceptHandleSerializer(instance=queryset, many=True)
            data = serializer.data
        else:
            data = []
        return Response({'results': data})

    def post(self, request):
        data = self.request.data
        batch_no = data.get('batch_no')
        lot_no = data.pop('lot_no', None)
        lst = []
        obj = WMSExceptHandle.objects.filter(batch_no=batch_no).last()
        num = 1
        if obj:
            num = obj.num + 1
        for item in lot_no:
            lst.append(WMSExceptHandle(**data, lot_no=item, created_user=self.request.user, num=num))
        WMSExceptHandle.objects.bulk_create(lst)
        return Response('保存成功')


@method_decorator([api_recorder], name="dispatch")
class WMSExpireListView(APIView):
    permission_classes = (IsAuthenticated,)
    DATABASE_CONF = WMS_CONF

    def get(self, request):
        expire_days = self.request.query_params.get('expire_days', 30)
        page = self.request.query_params.get('page', 1)
        page_size = self.request.query_params.get('page_size', 15)
        st = (int(page) - 1) * int(page_size)
        et = int(page) * int(page_size)
        sql = """select
       m.MaterialCode,
       m.Name,
       sum(a.WeightOfActual) as weight,
       count(a.Quantity) as quality,
       a.StockDetailState,
       m.StandardUnit
from t_inventory_stock a
inner join t_inventory_material m on m.MaterialCode=a.MaterialCode
where m.IsValidity=1 and m.Validity - datediff(day ,a.CreaterTime, getdate()) <={}
group by m.MaterialCode,
         m.Name,
         m.StandardUnit,
         a.StockDetailState
order by m.MaterialCode;""".format(expire_days)
        sc = SqlClient(sql=sql, **self.DATABASE_CONF)
        temp = sc.all()
        count = len(temp)
        result = []
        data = temp[st:et]
        total_weight = sum([i[2] for i in temp])
        total_quantity = sum([i[3] for i in temp])
        for item in data:
            result.append(
                {'MaterialCode': item[0],
                 'MaterialName': item[1],
                 'WeightOfActual': item[2],
                 'quantity': item[3],
                 'quality_status': item[4],
                 'unit': item[5]
                 })
        sc.close()
        return Response({'results': result, "count": count, 'total_weight': total_weight, 'total_quantity': total_quantity})


@method_decorator([api_recorder], name="dispatch")
class WMSExpireDetailView(APIView):
    permission_classes = (IsAuthenticated,)
    DATABASE_CONF = WMS_CONF
    FILE_NAME = '库位明细'

    def export_xls(self, result):
        response = HttpResponse(content_type='application/vnd.ms-excel')
        filename = self.FILE_NAME
        response['Content-Disposition'] = u'attachment;filename= ' + filename.encode('gbk').decode(
            'ISO-8859-1') + '.xls'
        # 创建一个文件对象
        wb = xlwt.Workbook(encoding='utf8')
        # 创建一个sheet对象
        sheet = wb.add_sheet('出入库信息', cell_overwrite_ok=True)
        style = xlwt.XFStyle()
        style.alignment.wrap = 1
        columns = ['序号', '物料名称', '物料编码', '质检条码', '托盘号', '库存位', '库存数',
                   '单位', '单位重量', '总重量', '品质状态', '入库时间', '有效期至', '剩余有效天数']
        for col_num in range(len(columns)):
            sheet.write(0, col_num, columns[col_num])
            # 写入数据
        data_row = 1
        for i in result:
            sheet.write(data_row, 0, result.index(i) + 1)
            sheet.write(data_row, 1, i[0])
            sheet.write(data_row, 2, i[1])
            sheet.write(data_row, 3, i[2])
            sheet.write(data_row, 4, i[3])
            sheet.write(data_row, 5, i[4])
            sheet.write(data_row, 6, i[5])
            sheet.write(data_row, 7, i[6])
            sheet.write(data_row, 8, i[7])
            sheet.write(data_row, 9, i[7])
            sheet.write(data_row, 10, i[8])
            sheet.write(data_row, 11, i[9])
            sheet.write(data_row, 12, i[10])
            sheet.write(data_row, 13, i[11])
            data_row = data_row + 1
        # 写出到IO
        output = BytesIO()
        wb.save(output)
        # 重新定位到开始
        output.seek(0)
        response.write(output.getvalue())
        return response

    def get(self, request):
        expire_days = self.request.query_params.get('expire_days', 30)
        quality_status = self.request.query_params.get('quality_status')
        material_code = self.request.query_params.get('material_code')
        export = self.request.query_params.get('export')
        page = self.request.query_params.get('page', 1)
        page_size = self.request.query_params.get('page_size', 15)
        st = (int(page) - 1) * int(page_size)
        et = int(page) * int(page_size)
        if not all([expire_days, quality_status, material_code]):
            raise ValidationError('参数不足！')
        sql = """select
       a.MaterialName,
       a.MaterialCode,
       a.TrackingNumber,
       a.LadenToolNumber,
       a.SpaceId,
       a.Quantity,
       a.StandardUnit,
       a.WeightOfActual,
       a.StockDetailState,
       a.CreaterTime,
       dateadd(dd,m.Validity,a.CreaterTime) as expire_time,
       m.Validity - datediff(day ,a.CreaterTime, getdate()) as left_days
from t_inventory_stock a
inner join t_inventory_material m on m.MaterialCode=a.MaterialCode
where m.IsValidity=1
  and m.Validity - datediff(day ,a.CreaterTime, getdate()) <= {}
  and m.MaterialCode='{}'
  and a.StockDetailState={}
order by left_days;""".format(expire_days, material_code, quality_status)
        sc = SqlClient(sql=sql, **self.DATABASE_CONF)
        temp = sc.all()
        if export == '2':
            return self.export_xls(list(temp))
        elif export == '1':
            return self.export_xls(list(temp[st:et]))

        count = len(temp)
        result = []
        data = temp[st:et]
        total_weight = sum([i[7] for i in temp])
        total_quantity = sum([i[5] for i in temp])
        for item in data:
            result.append(
                {
                 'material_name': item[0],
                 'material_no': item[1],
                 'lot_no': item[2],
                 'container_no': item[3],
                 'location': item[4],
                 'qty': item[5],
                 'unit': item[6],
                 'total_weight': item[7],
                 'quality_status': item[8],
                 'in_storage_time': item[9],
                 'expire_time': item[10],
                 'left_days': item[11],
                 })
        sc.close()
        return Response({'results': result, "count": count, 'total_weight': total_weight, 'total_quantity': total_quantity})


@method_decorator([api_recorder], name="dispatch")
class WmsInventoryWeightStockView(APIView):
    """WMS库存货位信息，参数：material_name=原材料名称&material_no=原材料编号&quality_status=品质状态1合格3不合格&entrance_name=出库口名称"""
    DATABASE_CONF = WMS_CONF
    permission_classes = (IsAuthenticated, )

    def get(self, request, *args, **kwargs):
        material_name = self.request.query_params.get('material_name')
        material_no = self.request.query_params.get('material_no')
        quality_status = self.request.query_params.get('quality_status')
        entrance_name = self.request.query_params.get('entrance_name')
        extra_where_str = ""
        if not entrance_name:
            raise ValidationError('请选择出库口！')
        if material_name:
            extra_where_str += "and c.Name like '%{}%'".format(material_name)
        if material_no:
            extra_where_str += "and c.MaterialCode like '%{}%'".format(material_no)
        if quality_status:
            extra_where_str += "and a.StockDetailState={}".format(quality_status)

        sql = """SELECT
                 c.MaterialCode,
                 c.Name AS MaterialName,
                 SUM ( a.WeightOfActual ) AS WeightOfActual,
                 SUM ( a.Quantity ) AS quantity,
                 Min ( a.WeightOfActual ) AS min_quantity,
                 a.StockDetailState
                FROM
                 dbo.t_inventory_stock AS a
                 INNER JOIN t_inventory_space b ON b.Id = a.StorageSpaceEntityId
                 INNER JOIN t_inventory_material c ON c.MaterialCode= a.MaterialCode
                 INNER JOIN t_inventory_tunnel d ON d.TunnelCode= a.TunnelId 
                WHERE
                 NOT EXISTS ( SELECT tp.TrackingNumber FROM t_inventory_space_plan tp WHERE tp.TrackingNumber = a.TrackingNumber ) 
                 AND d.State= 1 
                 AND b.SpaceState= 1 
                 AND a.TunnelId IN (
                     SELECT
                            ab.TunnelCode
                     FROM t_inventory_entrance_tunnel ab
                         INNER JOIN t_inventory_entrance ac ON ac.Id= ab.EntranceEntityId
                     WHERE ac.name= '{}' )
                 {}
                GROUP BY
                 c.MaterialCode,
                 c.Name,
                 a.StockDetailState
                 order by c.MaterialCode;""".format(entrance_name, extra_where_str)
        sc = SqlClient(sql=sql, **self.DATABASE_CONF)
        temp = sc.all()
        count = len(temp)
        result = []
        for item in temp:
            if item[3] <= 1:
                avg_weight = round(item[2] / item[3], 2)
            else:
                avg_weight = round((item[2] - item[4]) / (item[3] - 1), 2)
            result.append(
                {'MaterialCode': item[0],
                 'MaterialName': item[1],
                 'WeightOfActual': item[2],
                 'quantity': item[3],
                 'avg_weight': avg_weight,
                 'quality_status': item[5]
                 })
        sc.close()
        return Response({'results': result, "count": count})


@method_decorator([api_recorder], name="dispatch")
class InventoryEntranceView(APIView):
    """获取所有出库口名称"""
    DATABASE_CONF = WMS_CONF
    permission_classes = (IsAuthenticated, )

    def get(self, request):
        sql = 'select name, EntranceCode from t_inventory_entrance where Type=2;'
        sc = SqlClient(sql=sql, **self.DATABASE_CONF)
        temp = sc.all()
        result = []
        for item in temp:
            result.append(
                {'name': item[0],
                 'code': item[1],
                 })
        sc.close()
        return Response(result)


@method_decorator([api_recorder], name="dispatch")
class WMSMaterialGroupNameView(APIView):
    """获取所有原材料库物料组名称"""
    DATABASE_CONF = WMS_CONF
    permission_classes = (IsAuthenticated, )

    def get(self, request):
        sql = 'select Name from t_inventory_material_group;'
        sc = SqlClient(sql=sql, **self.DATABASE_CONF)
        temp = sc.all()
        result = []
        for item in temp:
            result.append(
                {'name': item[0]})
        sc.close()
        return Response(result)


@method_decorator([api_recorder], name="dispatch")
class WMSTunnelView(APIView):
    """获取所有原材料库巷道名称"""
    DATABASE_CONF = WMS_CONF
    permission_classes = (IsAuthenticated, )

    def get(self, request):
        sql = 'select TunnelName, TunnelCode from t_inventory_tunnel order by TunnelCode;'
        sc = SqlClient(sql=sql, **self.DATABASE_CONF)
        temp = sc.all()
        result = []
        for item in temp:
            result.append(
                {'name': item[0],
                 'code': item[1]})
        sc.close()
        return Response(result)


@method_decorator([api_recorder], name="dispatch")
class WMSMaterialsView(APIView):
    """获取所有原材料名称列表"""
    DATABASE_CONF = WMS_CONF
    permission_classes = (IsAuthenticated, )

    def get(self, request):
        sql = 'select Name, MaterialCode from t_inventory_material order by Name;'
        sc = SqlClient(sql=sql, **self.DATABASE_CONF)
        temp = sc.all()
        result = []
        for item in temp:
            result.append(
                {'name': item[0],
                 'code': item[1]})
        sc.close()
        return Response(result)


@method_decorator([api_recorder], name="dispatch")
class WmsInventoryMaterialAttribute(APIView):
    permission_classes = (IsAuthenticated, PermissionClass({'view': 'view_material_attr',
                                                            'add': ["add_material_attr", "change_material_attr"]}))

    def get(self, request):
        material_name = self.request.query_params.get('material_name')
        material_no = self.request.query_params.get('material_no')
        page = self.request.query_params.get('page', 1)
        page_size = self.request.query_params.get('page_size', 15)
        filter_kwargs = {}
        only_storage_flag = self.request.query_params.get('only_storage_flag')  # 仅显示未设定有效期的物料
        if material_no:
            filter_kwargs['material_no__icontains'] = material_no
        if material_name:
            filter_kwargs['material_name__icontains'] = material_name
        if only_storage_flag:
            filter_kwargs['is_validity'] = 0
        query_set = WmsInventoryMaterial.objects.using('wms').filter(
            **filter_kwargs).values('id', 'material_no', 'material_name', 'period_of_validity')
        st = (int(page) - 1) * int(page_size)
        et = int(page) * int(page_size)
        count = len(query_set)
        data = query_set[st:et]
        return Response({'results': data, "count": count})

    def post(self, request):
        material_ids = self.request.data.get('materials')
        period_of_validity = self.request.data.get('period_of_validity')
        WmsInventoryMaterial.objects.using('wms').filter(id__in=material_ids).update(
            is_validity=1, period_of_validity=period_of_validity)
        return Response('ok')


@method_decorator([api_recorder], name="dispatch")
class WMSInventoryView(APIView):
    """原材料库存信息，material_name=原材料名称&material_no=原材料编号&material_group_name=物料组名称&tunnel_name=巷道名称&page=页数&page_size=每页数量"""
    DATABASE_CONF = WMS_CONF
    FILE_NAME = '原材料库存统计'
    permission_classes = (IsAuthenticated, )

    def export_xls(self, result):
        response = HttpResponse(content_type='application/vnd.ms-excel')
        filename = self.FILE_NAME
        response['Content-Disposition'] = u'attachment;filename= ' + filename.encode('gbk').decode(
            'ISO-8859-1') + '.xls'
        # 创建一个文件对象
        wb = xlwt.Workbook(encoding='utf8')
        # 创建一个sheet对象
        sheet = wb.add_sheet('出入库信息', cell_overwrite_ok=True)
        style = xlwt.XFStyle()
        style.alignment.wrap = 1
        columns = ['序号', '物料名称', '物料编码', '中策物料编码', '批次号', '单位', 'PDM',
                   '物料组', '巷道', '可用数量', '重量']
        for col_num in range(len(columns)):
            sheet.write(0, col_num, columns[col_num])
            # 写入数据
        data_row = 1
        for i in result:
            sheet.write(data_row, 0, result.index(i) + 1)
            sheet.write(data_row, 1, i[0])
            sheet.write(data_row, 2, i[1])
            sheet.write(data_row, 3, i[2])
            sheet.write(data_row, 4, i[9])
            sheet.write(data_row, 5, i[3])
            sheet.write(data_row, 6, i[4])
            sheet.write(data_row, 7, i[5])
            sheet.write(data_row, 8, i[6])
            sheet.write(data_row, 9, i[7])
            sheet.write(data_row, 10, i[8])
            data_row = data_row + 1
        # 写出到IO
        output = BytesIO()
        wb.save(output)
        # 重新定位到开始
        output.seek(0)
        response.write(output.getvalue())
        return response

    def get(self, request):
        material_name = self.request.query_params.get('material_name')
        material_no = self.request.query_params.get('material_no')
        material_group_name = self.request.query_params.get('material_group_name')
        tunnel_name = self.request.query_params.get('tunnel_name')
        page = self.request.query_params.get('page', 1)
        page_size = self.request.query_params.get('page_size', 15)
        export = self.request.query_params.get('export')
        st = (int(page) - 1) * int(page_size)
        et = int(page) * int(page_size)
        extra_where_str = ""
        if material_name:
            extra_where_str += "where temp.MaterialName like '%{}%'".format(material_name)
        if material_no:
            if extra_where_str:
                extra_where_str += " and temp.MaterialCode like '%{}%'".format(material_no)
            else:
                extra_where_str += "where temp.MaterialCode like '%{}%'".format(material_no)
        if material_group_name:
            if extra_where_str:
                extra_where_str += " and m.MaterialGroupName='{}'".format(material_group_name)
            else:
                extra_where_str += "where m.MaterialGroupName='{}'".format(material_group_name)
        if tunnel_name:
            if extra_where_str:
                extra_where_str += " and temp.TunnelName='{}'".format(tunnel_name)
            else:
                extra_where_str += "where temp.TunnelName='{}'".format(tunnel_name)
        sql = """
                select
            temp.MaterialName,
            temp.MaterialCode,
            m.ZCMaterialCode,
            temp.StandardUnit,
            m.Pdm,
            m.MaterialGroupName,
            temp.TunnelName,
            temp.quantity,
            temp.WeightOfActual,
            temp.BatchNo
        from (
            select
                a.MaterialCode,
                a.MaterialName,
                a.BatchNo,
                d.TunnelName,
                a.StandardUnit,
                SUM ( a.WeightOfActual ) AS WeightOfActual,
                SUM ( a.Quantity ) AS quantity
            from dbo.t_inventory_stock AS a
            INNER JOIN t_inventory_tunnel d ON d.TunnelCode= a.TunnelId
            group by
                 a.MaterialCode,
                 a.MaterialName,
                 d.TunnelName,
                 a.BatchNo,
                 a.StandardUnit
            ) temp
        left join t_inventory_material m on m.MaterialCode=temp.MaterialCode {}""".format(extra_where_str)
        sc = SqlClient(sql=sql, **self.DATABASE_CONF)
        temp = sc.all()

        if export == '2':
            return self.export_xls(list(temp))
        elif export == '1':
            return self.export_xls(list(temp[st:et]))

        count = len(temp)
        total_quantity = total_weight = 0
        for i in temp:
            total_quantity += i[7]
            total_weight += i[8]
        temp = temp[st:et]
        result = []
        for item in temp:
            result.append(
                {'name': item[0],
                 'code': item[1],
                 'zc_material_code': item[2],
                 'unit': item[3],
                 'pdm': item[4],
                 'group_name': item[5],
                 'tunnel_name': item[6],
                 'quantity': item[7],
                 'weight': item[8],
                 'batch_no': item[9]
                 })
        sc.close()
        return Response(
            {'results': result, "count": count, 'total_quantity': total_quantity, 'total_weight': total_weight})


class WmsNucleinManagementView(ModelViewSet):
    queryset = WmsNucleinManagement.objects.order_by('-id')
    serializer_class = WmsNucleinManagementSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend,)
    filter_class = WmsNucleinManagementFilter

    @atomic()
    def create(self, request, *args, **kwargs):
        data = self.request.data
        if not isinstance(data, list):
            raise ValidationError('参数错误')
        s = self.serializer_class(data=data, many=True, context={'request': request})
        s.is_valid(raise_exception=True)
        s.save()
        if not settings.DEBUG:
            data_list = [{
                    "BatchNo": w['batch_no'],
                    "MaterialCode": w['material_no'],
                    "CheckResult": 2
                } for w in data]
            update_wms_quality_result(data_list)
        return Response('ok')


@method_decorator([api_recorder], name="dispatch")
class THStorageSummaryView(WmsStorageSummaryView):
    """
        炭黑库存统计列表（按物料编码、品质状态、单位、批次号分组统计）
        参数：?material_name=物料名称&material_no=物料编码&zc_material_code=中策物料编码&batch_no=批次号&pdm_no=PDM号&st=入库开始时间&et=入库结束时间&quality_status=# 品质状态 1：合格 3：不合格
    """
    DATABASE_CONF = TH_CONF


@method_decorator([api_recorder], name="dispatch")
class THStorageView(WmsStorageView):
    DATABASE_CONF = 'cb'
    FILE_NAME = '炭黑库位明细'


@method_decorator([api_recorder], name="dispatch")
class THInventoryStockView(WmsInventoryStockView):
    """炭黑库存货位信息，参数：material_name=原材料名称&material_no=原材料编号&quality_status=品质状态1合格3不合格&entrance_name=出库口名称"""
    DATABASE_CONF = TH_CONF
    DB = 'CB'


@method_decorator([api_recorder], name="dispatch")
class THInStockView(WmsInStockView):
    """炭黑库根据当前货物外伸位地址获取内伸位数据, 参数：material_no=原材料编号&entrance_name=出库口名称&space_id=货位地址"""
    DATABASE_CONF = TH_CONF


@method_decorator([api_recorder], name="dispatch")
class THInventoryWeightStockView(WmsInventoryWeightStockView):
    """炭黑库存货位信息，参数：material_name=原材料名称&material_no=原材料编号&quality_status=品质状态1合格3不合格&entrance_name=出库口名称"""
    DATABASE_CONF = TH_CONF


@method_decorator([api_recorder], name="dispatch")
class THInventoryEntranceView(InventoryEntranceView):
    """获取所有炭黑出库口名称"""
    DATABASE_CONF = TH_CONF


@method_decorator([api_recorder], name="dispatch")
class THMaterialGroupNameView(WMSMaterialGroupNameView):
    """获取炭黑库所有物料组名称"""
    DATABASE_CONF = TH_CONF


@method_decorator([api_recorder], name="dispatch")
class THTunnelView(WMSTunnelView):
    """获取炭黑库所有巷道名称"""
    DATABASE_CONF = TH_CONF


@method_decorator([api_recorder], name="dispatch")
class THMaterialsView(WMSMaterialsView):
    """获取所有原材料名称列表"""
    DATABASE_CONF = TH_CONF


@method_decorator([api_recorder], name="dispatch")
class THInventoryView(WMSInventoryView):
    """炭黑库存信息"""
    DATABASE_CONF = TH_CONF
    FILE_NAME = '炭黑库存统计'


@method_decorator([api_recorder], name="dispatch")
class THRelease(WMSRelease):
    REQUEST_URL = TH_URL


@method_decorator([api_recorder], name="dispatch")
class THExpireListView(WMSExpireListView):
    DATABASE_CONF = TH_CONF


@method_decorator([api_recorder], name="dispatch")
class THExpireDetailView(WMSExpireDetailView):
    DATABASE_CONF = TH_CONF


@method_decorator([api_recorder], name="dispatch")
class DepotModelViewSet(ModelViewSet):
    """线边库库区"""
    queryset = Depot.objects.filter(is_use=True)
    serializer_class = DepotModelSerializer
    permission_classes = [IsAuthenticated, ]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        if self.request.query_params.get('all'):
            data = queryset.values('id', 'depot_name')
            return Response({'results': data})
        return super().list(self, request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        s = DepotPallt.objects.filter(depot_site__depot=instance, pallet_status=1).first()  # True不能删
        if not s:
            instance.is_use = 0
            DepotSite.objects.filter(depot=instance).update(is_use=0)
            instance.save()
        else:
            raise ValidationError('该库区下存在物料,不能删除!')
        return Response(status=status.HTTP_204_NO_CONTENT)


@method_decorator([api_recorder], name="dispatch")
class DepotSiteModelViewSet(ModelViewSet):
    """线边库库位"""
    queryset = DepotSite.objects.filter(is_use=True)
    serializer_class = DepotSiteModelSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = [DjangoFilterBackend]
    filter_class = DepotSiteDataFilter

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        if self.request.query_params.get('all'):
            data = queryset.values('id', 'depot_site_name', 'description', 'depot', 'depot__depot_name')
            return Response({'results': data})
        elif request.query_params.get('depot_site'):
            data = DepotSite.objects.filter(is_use=True).values('id', 'depot_site_name', 'depot')
            return Response({'results': data})
        return super().list(self, request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        s = DepotPallt.objects.filter(depot_site=instance, pallet_status=1).first()  # True不能删
        if not s:
            instance.is_use = 0
            instance.save()
        else:
            raise ValidationError('该库位下存在物料,不能删除!')
        return Response(status=status.HTTP_204_NO_CONTENT)


@method_decorator([api_recorder], name="dispatch")
class DepotPalltModelViewSet(ModelViewSet):
    """线边库库存查询"""
    queryset = DepotPallt.objects.filter(pallet_status=1).order_by('-enter_time')
    serializer_class = DepotPalltModelSerializer
    permission_classes = [IsAuthenticated, ]
    filter_backends = [DjangoFilterBackend]
    filter_class = DepotDataFilter

    def list(self, request, *args, **kwargs):
        results = PalletFeedbacks.objects.filter(palletfeedbacks__pallet_status=1).values('product_no').annotate(
            num=Count('product_no'),
            trains=Sum(F('end_trains') - F('begin_trains') + 1),
            actual_weight=Sum('actual_weight')
        )
        return Response({'results': results})


@method_decorator([api_recorder], name="dispatch")
class DepotPalltInfoModelViewSet(ModelViewSet):
    """库存查询详情"""
    queryset = DepotPallt.objects.filter(pallet_status=1)
    serializer_class = DepotPalltInfoModelSerializer
    permission_classes = [IsAuthenticated, ]
    filter_backends = [DjangoFilterBackend]
    filter_class = DepotDataFilter

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


@method_decorator([api_recorder], name='dispatch')
class PalletTestResultView(APIView):
    """查询某拖收皮数据的检测结果，参数:lot_no=xxx"""

    def get(self, request):
        lot_no = self.request.query_params.get('lot_no')
        if not lot_no:
            raise ValidationError('参数缺失')
        # {
        #     '门尼': ['ML(1+4)'],
        #     '流变': ['MH', 'ML', 'TC10'],
        #     '比重': ['比重值']
        # }
        # [
        #     {
        #         'trains': 1,
        #         'level': 1,  # 等级
        #         'test_data': {
        #                     '门尼': {
        #                         'ML(1+4)': 66,
        #
        #                     },
        #                     '流变': {
        #                         'MH': 55,
        #                         'ML': 99,
        #                         'TC10': 12,
        #                     }
        #                 }
        #     },
        #     {
        #         'trains': 2,
        #         'level': 1,
        #         'test_data': {
        #             '门尼': {
        #                 'ML(1+4)': 66,
        #
        #             },
        #         }
        #     }
        # ]
        ret = []
        mdr_obj = MaterialDealResult.objects.filter(lot_no=lot_no).exclude(status='复测').last()
        if mdr_obj:
            serializers = MaterialDealResultListSerializer(instance=mdr_obj)
            deal_result = serializers.data
        else:
            return Response([])
        table_head = deal_result['mtr_list']['table_head']
        mtr_list = deal_result['mtr_list']
        mtr_list.pop('table_head', None)
        test_result = deal_result['test_result']
        for item in mtr_list['trains']:
            data = {}
            data['trains'] = item['train']
            data['test_data'] = {}
            for j in item['content']:
                data['status'] = j.get('status')
                test_indicator_name = j['test_indicator_name']
                data_point_name = j['data_point_name']
                value = j['value']
                if test_indicator_name in data['test_data']:
                    data['test_data'][test_indicator_name][data_point_name] = value
                else:
                    data['test_data'][test_indicator_name] = {data_point_name: value}
            ret.append(data)

        return Response({'table_head': table_head, 'results': ret, 'test_result': test_result})


@method_decorator([api_recorder], name="dispatch")
class PalletDataModelViewSet(ModelViewSet):
    """线边库出入库管理"""
    queryset = PalletFeedbacks.objects.exclude(palletfeedbacks__pallet_status=2).order_by('-product_time')
    serializer_class = PalletDataModelSerializer
    permission_classes = [IsAuthenticated, ]
    filter_backends = [DjangoFilterBackend]
    filter_class = PalletDataFilter

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            for i in serializer.data:
                s = ProductClassesPlan.objects.filter(plan_classes_uid=i['plan_classes_uid']).values(
                    'work_schedule_plan__group__global_name').first()
                i.update({'group': s['work_schedule_plan__group__global_name']})
            if request.query_params.get('group'):
                group = request.query_params.get('group')
                data = [i for i in serializer.data if i['group'].startswith(group)]
                return self.get_paginated_response(data)
            elif request.query_params.get('all'):
                data = PalletFeedbacks.objects.filter(delete_flag=False).values('product_no').distinct()
                return Response({'results': data})
            else:
                return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        pallet_id = request.data.get('id')
        pallet_status = request.data.get('status')
        enter_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        depot_site = request.data.get('depot_site')
        depot_pallet_id = request.data.get('depot_pallet_id')
        depot_site_obj = DepotSite.objects.filter(id=depot_site).first()
        pallet_data_obj = PalletFeedbacks.objects.get(pk=pallet_id)

        if pallet_status == 1:  # 入库
            data_obj = DepotPallt.objects.create(pallet_data=pallet_data_obj, depot_site=depot_site_obj,
                                                 enter_time=enter_time,
                                                 pallet_status=pallet_status)
            data = PalletFeedbacks.objects.filter(palletfeedbacks=data_obj).first()
        elif pallet_status == 2:  # 出库
            DepotPallt.objects.filter(id=depot_pallet_id).update(pallet_status=2, outer_time=datetime.datetime.now())
            data_obj = DepotPallt.objects.filter(id=depot_pallet_id).first()
            data = PalletFeedbacks.objects.filter(palletfeedbacks=data_obj).first()
        serializer = PalletDataModelSerializer(instance=data)
        return Response({"result": serializer.data})


@method_decorator([api_recorder], name="dispatch")
class DepotResumeModelViewSet(ModelViewSet):
    """线边库出入库履历"""
    queryset = DepotPallt.objects.all().order_by('-enter_time')
    serializer_class = DepotResumeModelSerializer
    permission_classes = [IsAuthenticated, ]
    filter_backends = [DjangoFilterBackend]
    filter_class = DepotResumeFilter

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            for i in serializer.data:
                s = ProductClassesPlan.objects.filter(plan_classes_uid=i['plan_classes_uid']).values(
                    'work_schedule_plan__group__global_name').first()
                i.update({'group': s['work_schedule_plan__group__global_name']})

            if request.query_params.get('group'):
                group = request.query_params.get('group')
                data = [i for i in serializer.data if i['group'].startswith(group)]
                return self.get_paginated_response(data)

            elif request.query_params.get('all'):
                data = DepotPallt.objects.values('pallet_data__product_no').annotate(
                    num=Count('pallet_data__product_no'))
                return Response({'results': data})
            else:
                return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


@method_decorator([api_recorder], name="dispatch")
class SulfurDepotModelViewSet(ModelViewSet):
    """硫磺库库区"""
    queryset = SulfurDepot.objects.filter(is_use=True)
    serializer_class = SulfurDepotModelSerializer
    permission_classes = (IsAuthenticated,)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        if self.request.query_params.get('all'):
            data = queryset.values('id', 'depot_name')
            return Response({'results': data})
        return super().list(self, request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        s = Sulfur.objects.filter(depot_site__depot=instance, sulfur_status=1).first()
        if not s:
            instance.is_use = 0
            SulfurDepotSite.objects.filter(depot=instance).update(is_use=0)
            instance.save()
        else:
            raise ValidationError('该库区下存在物料,不能删除!')
        return Response(status=status.HTTP_204_NO_CONTENT)


@method_decorator([api_recorder], name="dispatch")
class SulfurDepotSiteModelViewSet(ModelViewSet):
    """硫磺库库位"""
    queryset = SulfurDepotSite.objects.filter(is_use=True)
    serializer_class = SulfurDepotSiteModelSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = [DjangoFilterBackend]
    filter_class = SulfurDepotSiteFilter

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        if self.request.query_params.get('all'):
            data = queryset.values('id', 'depot_site_name', 'depot', 'depot__depot_name', 'description')
            return Response({'results': data})
        elif request.query_params.get('depot_site'):
            data = SulfurDepotSite.objects.filter(is_use=True).values('id', 'depot_site_name', 'depot')
            return Response({'results': data})
        return super().list(self, request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        s = Sulfur.objects.filter(depot_site=instance, sulfur_status=1).first()
        if not s:
            instance.is_use = 0
            instance.save()
        else:
            raise ValidationError('该库区下存在物料,不能删除!')
        return Response(status=status.HTTP_204_NO_CONTENT)


@method_decorator([api_recorder], name="dispatch")
class SulfurDataModelViewSet(ModelViewSet):
    """硫磺库出入库管理"""
    queryset = Sulfur.objects.filter(sulfur_status=1).order_by('-enter_time')
    serializer_class = SulfurDataModelSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = [DjangoFilterBackend]
    filter_class = SulfurDataFilter

    def list(self, request, *args, **kwargs):
        name = self.request.query_params.get('_name')
        product_no = self.request.query_params.get('_product_no')
        provider = self.request.query_params.get('_provider')
        if name:
            queryset = Sulfur.objects.filter(name__icontains=name).values('name').distinct()
        elif product_no:
            queryset = Sulfur.objects.filter(product_no__icontains=product_no).values('product_no').distinct()
        elif provider:
            queryset = Sulfur.objects.filter(provider__icontains=provider).values('provider').distinct()
        else:
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        return Response(queryset)

    # 硫磺人工入库
    def create(self, request, *args, **kwargs):
        if request.data.get('sulfur_status') == 1:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            try:
                depot_site_obj = SulfurDepotSite.objects.get(pk=request.data.get('depot_site'))
            except:
                raise ValidationError('该库位不存在')

            enter_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            data = Sulfur.objects.filter(depot_site=depot_site_obj, lot_no=serializer.data.get('lot_no'),
                                         name=serializer.data.get('name'),
                                         product_no=serializer.data.get('product_no'),
                                         provider=serializer.data.get('provider'),
                                         ).first()
            weight = float(serializer.data.get('weight'))
            num = int(serializer.data.get('num'))
            if data:
                data.num += num
                data.weight += decimal.Decimal(weight * num)
                data.enter_time = enter_time
                data.save()
            else:
                serializer.data.update({'weight': weight * num})
                data = Sulfur.objects.create(**serializer.data, depot_site=depot_site_obj, enter_time=enter_time)

            serializer = SulfurDataModelSerializer(instance=data)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        elif request.data.get('sulfur_status') == 2:
            num = request.data.get('num')
            try:
                num = int(num)
            except:
                raise ValidationError('您输入的数量有误')
            obj = Sulfur.objects.filter(id=request.data.get('id')).first()
            if num > obj.num:
                raise ValidationError(f"库存数量为{obj.num}！")
            outer_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            obj.sulfur_status = 1 if num < obj.num else 2
            obj.num -= num
            obj.outer_time = outer_time
            obj.save()
            return Response({'results': '出库成功'})


@method_decorator([api_recorder], name="dispatch")
class DepotSulfurModelViewSet(ModelViewSet):
    """硫磺库库存查询"""
    queryset = Sulfur.objects.filter(sulfur_status=1)
    serializer_class = DepotSulfurModelSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = [DjangoFilterBackend]
    filter_class = DepotSulfurFilter

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        lst = []
        for i in serializer.data:
            lst.append(
                {'name': i['name'], 'product_no': i['product_no'], 'provider': i['provider'], 'lot_no': i['lot_no'],
                 'num': i['num']})
        c = {i['name']: {} for i in lst}
        for i in lst:
            if not c[i['name']]:
                c[i['name']].update(i)
            else:
                c[i['name']]['num'] += i['num']
        return Response({'results': c.values()})


@method_decorator([api_recorder], name="dispatch")
class DepotSulfurInfoModelViewSet(ModelViewSet):
    """硫磺库库存查询详情"""
    queryset = Sulfur.objects.filter(sulfur_status=1)
    serializer_class = DepotSulfurInfoModelSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = [DjangoFilterBackend]
    filter_class = DepotSulfurFilter

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


@method_decorator([api_recorder], name="dispatch")
class SulfurResumeModelViewSet(ModelViewSet):
    """硫磺库出入库履历"""
    queryset = Sulfur.objects.all().order_by('-enter_time')
    serializer_class = SulfurResumeModelSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = [DjangoFilterBackend]
    filter_class = SulfurResumeFilter


@method_decorator([api_recorder], name="dispatch")
class BzMixingRubberInventory(ListAPIView):
    """
        北自混炼胶库存列表，参数：?material_no=物料编码&container_no=托盘号&lot_no=收皮条码&location=库存位
                            &tunnel=巷道&quality_status=品质状态&lot_existed=收皮条码有无（1：有，0：无）
                            &station=出库口名称&st=入库开始时间&et=入库结束时间
    """
    serializer_class = BzMixingRubberInventorySearchSerializer
    permission_classes = (IsAuthenticated,)
    queryset = BzFinalMixingRubberInventory.objects.all()

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        product_validity_data = dict(MaterialAttribute.objects.filter(
            period_of_validity__isnull=False
        ).values_list('material__material_no', 'period_of_validity'))
        locked_lot_data = dict(
            ProductInventoryLocked.objects.filter(is_locked=True).values_list('lot_no', 'locked_status'))
        return {
            'request': self.request,
            'format': self.format_kwarg,
            'view': self,
            'product_validity_data': product_validity_data,
            'locked_lot_data': locked_lot_data
        }

    def export_xls(self, result):
        response = HttpResponse(content_type='application/vnd.ms-excel')
        filename = '库位明细'
        response['Content-Disposition'] = u'attachment;filename= ' + filename.encode('gbk').decode(
            'ISO-8859-1') + '.xls'
        # 创建一个文件对象
        wb = xlwt.Workbook(encoding='utf8')
        # 创建一个sheet对象
        sheet = wb.add_sheet('库存信息', cell_overwrite_ok=True)

        style = xlwt.XFStyle()
        style.alignment.wrap = 1
        columns = ['No', '胶料类型', '胶料编码', '质检条码', '托盘号', '库存位', '车数',
                   '总重量', '品质状态', '入库时间', '机台号', '车号', '货位状态']
        for col_num in range(len(columns)):
            sheet.write(0, col_num, columns[col_num])
            # 写入数据
        data_row = 1
        for i in result:
            sheet.write(data_row, 0, data_row)
            sheet.write(data_row, 1, i['material_type'])
            sheet.write(data_row, 2, i['material_no'])
            sheet.write(data_row, 3, i['lot_no'])
            sheet.write(data_row, 4, i['container_no'])
            sheet.write(data_row, 5, i['location'])
            sheet.write(data_row, 6, i['qty'])
            sheet.write(data_row, 7, i['total_weight'])
            sheet.write(data_row, 8, i['quality_status'])
            sheet.write(data_row, 9, i['in_storage_time'])
            sheet.write(data_row, 10, i['equip_no'])
            sheet.write(data_row, 11, i['memo'])
            sheet.write(data_row, 12, i['location_status'])
            data_row = data_row + 1
        # 写出到IO
        output = BytesIO()
        wb.save(output)
        # 重新定位到开始
        output.seek(0)
        response.write(output.getvalue())
        return response

    def list(self, request, *args, **kwargs):
        material_no = self.request.query_params.get('material_no')  # 物料编码
        container_no = self.request.query_params.get('container_no')  # 托盘号
        lot_no = self.request.query_params.get('lot_no')  # 收皮条码
        location = self.request.query_params.get('location')  # 库存位
        tunnel = self.request.query_params.get('tunnel')  # 巷道
        quality_status = self.request.query_params.get('quality_status')  # 品质状态
        lot_existed = self.request.query_params.get('lot_existed')  # 收皮条码有无（1：有，0：无）
        station = self.request.query_params.get('station')  # 出库口名称
        location_status = self.request.query_params.get('location_status')  # 货位状态
        st = self.request.query_params.get('st')  # 入库开始时间
        et = self.request.query_params.get('et')  # 入库结束时间
        equip_no = self.request.query_params.get('equip_no')  # 机台
        export = self.request.query_params.get('export')  # 1：当前页面  2：所有
        outbound_order_id = self.request.query_params.get('outbound_order_id')  # 指定托盘和指定生产信息出库时使用
        begin_trains = self.request.query_params.get('begin_trains')  # 开始车次
        end_trains = self.request.query_params.get('end_trains')  # 结束车次
        yx_state = self.request.query_params.get('yx_state')  # 有效状态
        queryset = BzFinalMixingRubberInventory.objects.using('bz').all().order_by('in_storage_time')
        if material_no:
            queryset = queryset.filter(material_no=material_no)
        if container_no:
            queryset = queryset.filter(container_no__icontains=container_no)
        if location:
            queryset = queryset.filter(location__icontains=location)
        if tunnel:
            queryset = queryset.filter(location__istartswith=tunnel)
        if lot_no:
            queryset = queryset.filter(lot_no__icontains=lot_no)
        if quality_status:
            queryset = queryset.filter(quality_level=quality_status)
        if location_status:
            queryset = queryset.filter(location_status=location_status)
        if st:
            queryset = queryset.filter(in_storage_time__gte=st)
        if et:
            queryset = queryset.filter(in_storage_time__lte=et)
        if equip_no:
            queryset = queryset.filter(bill_id__iendswith=equip_no)
        if lot_existed:
            if lot_existed == '1':
                queryset = queryset.exclude(lot_no__isnull=True)
            else:
                queryset = queryset.filter(lot_no__isnull=True)

        # 指定托盘和指定生产信息出库查询
        if outbound_order_id:
            try:
                order = OutBoundDeliveryOrder.objects.get(id=outbound_order_id)
            except Exception:
                raise ValidationError('参数错误！')
            if order.order_type == 2:  # 指定生产信息出库
                pallet_data = PalletFeedbacks.objects.filter(
                    factory_date=order.factory_date,
                    equip_no=order.equip_no,
                    classes=order.classes,
                    product_no=order.product_no).values('lot_no', 'begin_trains', 'end_trains')
                common_pallet = list(filter(lambda x: max(x['begin_trains'], order.begin_trains)
                                                      <= min(x['end_trains'], order.end_trains),
                                            pallet_data))
                lot_nos = [i['lot_no'] for i in common_pallet]
                queryset = queryset.filter(lot_no__in=lot_nos, material_no=order.product_no)
            elif order.order_type == 3:  # 指定托盘出库
                queryset = queryset.filter(container_no=order.pallet_no)
        if station:
            if station == '一层前端':
                queryset = queryset.filter(Q(location__startswith='3') | Q(location__startswith='4'))
                # queryset = queryset.extra(where=["substring(货位地址, 0, 2) in (3, 4)"])
            elif station == '二层前端':
                queryset = queryset.filter(Q(location__startswith='1') | Q(location__startswith='2'))
                # queryset = queryset.extra(where=["substring(货位地址, 0, 2) in (1, 2)"])
            elif station == '一层后端':
                raise ValidationError('该出库口不可用！')
        if all([begin_trains, end_trains]):
            b_e_range = [int(begin_trains), int(end_trains)]
        elif begin_trains:
            b_e_range = [int(begin_trains), 99999]
        elif end_trains:
            b_e_range = [0, int(end_trains)]
        else:
            b_e_range = []
        ret = self.get_serializer(queryset, many=True).data
        if b_e_range:
            ret = list(filter(lambda x: max(x['begin_end_trains'][0], b_e_range[0]) <= min(x['begin_end_trains'][1], b_e_range[1]), ret))
        if yx_state:
            ret = list(filter(lambda x: x['yx_state']==yx_state, ret))

        page = self.paginate_queryset(ret)
        # serializer = self.get_serializer(page, many=True)
        resp_data = self.get_paginated_response(page).data

        if export:
            if export == '1':
                return self.export_xls(page)
            elif export == '2':
                return self.export_xls(ret)
        resp_data['total_weight'] = round(sum(float(i['total_weight']) for i in ret), 2)
        resp_data['total_trains'] = round(sum(float(i['qty']) for i in ret), 1)
        return Response(resp_data)


@method_decorator([api_recorder], name="dispatch")
class BzMixingRubberInventorySummary(APIView):
    """根据出库口获取混炼胶库存统计列表。参数：quality_status=品质状态&station=出库口名称&location_status=货位状态&lot_existed="""
    permission_classes = (IsAuthenticated, )

    def get(self, request):
        params = request.query_params
        quality_status = params.get("quality_status")
        station = params.get("station")
        location_status = params.get("location_status")
        lot_existed = params.get("lot_existed")
        queryset = BzFinalMixingRubberInventory.objects.using('bz').all()
        if location_status:
            queryset = queryset.filter(location_status=location_status)
        if station:
            if station == '一层前端':
                queryset = queryset.filter(Q(location__startswith='3') | Q(location__startswith='4'))
                # queryset = queryset.extra(where=["substring(货位地址, 0, 2) in (3, 4)"])
            elif station == '二层前端':
                queryset = queryset.filter(Q(location__startswith='1') | Q(location__startswith='2'))
                # queryset = queryset.extra(where=["substring(货位地址, 0, 2) in (1, 2)"])
            elif station == '一层后端':
                return Response([])
        if quality_status:
            queryset = queryset.filter(quality_level=quality_status)
        if lot_existed:
            if lot_existed == '1':
                queryset = queryset.filter(lot_no__isnull=False)
            else:
                queryset = queryset.filter(lot_no__isnull=True)
        try:
            ret = queryset.values('material_no').annotate(all_qty=Sum('qty'),
                                                          all_weight=Sum('total_weight')
                                                          ).values('material_no', 'all_qty', 'all_weight')
        except Exception as e:
            raise ValidationError(f"混炼胶库连接失败:{e}")
        return Response(ret)


@method_decorator([api_recorder], name="dispatch")
class BzMixingRubberInventorySearch(ListAPIView):
    """根据出库口、搜索指定数量的混炼胶库存信息.参数：?material_no=物料编码&quality_status=品质状态&station=出库口名称&need_qty=出库数量"""
    queryset = BzFinalMixingRubberInventory.objects.all()
    serializer_class = BzMixingRubberInventorySearchSerializer
    permission_classes = (IsAuthenticated,)

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        product_validity_data = dict(MaterialAttribute.objects.filter(
            period_of_validity__isnull=False
        ).values_list('material__material_no', 'period_of_validity'))
        locked_lot_data = dict(
            ProductInventoryLocked.objects.filter(is_locked=True).values_list('lot_no', 'locked_status'))
        return {
            'request': self.request,
            'format': self.format_kwarg,
            'view': self,
            'product_validity_data': product_validity_data,
            'locked_lot_data': locked_lot_data
        }

    def list(self, request, *args, **kwargs):
        material_no = self.request.query_params.get('material_no')  # 物料编码
        quality_status = self.request.query_params.get('quality_status')  # 品质状态
        station = self.request.query_params.get('station')  # 出库口名称
        need_qty = self.request.query_params.get('need_qty')  # 出库数量
        tunnel = self.request.query_params.get('tunnel')  # 巷道
        st = self.request.query_params.get('st')  # 入库开始时间
        et = self.request.query_params.get('et')  # 入库结束时间
        equip_no = self.request.query_params.get('equip_no')  # 机台
        outbound_order_id = self.request.query_params.get('outbound_order_id')  # 指定托盘和指定生产信息出库时使用
        begin_trains = self.request.query_params.get('begin_trains')  # 开始车次
        end_trains = self.request.query_params.get('end_trains')  # 结束车次
        if not need_qty:
            raise ValidationError('请输入正确的需求数量！')
        try:
            need_qty = int(need_qty)
        except Exception:
            raise ValidationError('参数错误！')
        queryset = BzFinalMixingRubberInventory.objects.using('bz').filter(
            location_status="有货货位").order_by('in_storage_time')
        if material_no:
            queryset = queryset.filter(material_no=material_no,)
        if station == '一层前端':
            queryset = queryset.filter(Q(location__startswith='3') | Q(location__startswith='4'))
            # queryset = queryset.extra(where=["substring(货位地址, 0, 2) in (3, 4)"])
        elif station == '二层前端':
            queryset = queryset.filter(Q(location__startswith='1') | Q(location__startswith='2'))
            # queryset = queryset.extra(where=["substring(货位地址, 0, 2) in (1, 2)"])
        elif station == '一层后端':
            raise ValidationError('该出库口不可用！')
        if quality_status:
            queryset = queryset.filter(quality_level=quality_status)
        if st:
            queryset = queryset.filter(in_storage_time__gte=st)
        if et:
            queryset = queryset.filter(in_storage_time__lte=et)
        if tunnel:
            queryset = queryset.filter(location__istartswith=tunnel)
        if equip_no:
            queryset = queryset.filter(bill_id__iendswith=equip_no)

        # 指定托盘和指定生产信息出库查询
        if outbound_order_id:
            try:
                order = OutBoundDeliveryOrder.objects.get(id=outbound_order_id)
            except Exception:
                raise ValidationError('参数错误！')
            if order.order_type == 2:  # 指定生产信息出库
                pallet_data = PalletFeedbacks.objects.filter(
                    factory_date=order.factory_date,
                    equip_no=order.equip_no,
                    classes=order.classes,
                    product_no=order.product_no).values('lot_no', 'begin_trains', 'end_trains')
                common_pallet = list(filter(lambda x: max(x['begin_trains'], order.begin_trains)
                                                      <= min(x['end_trains'], order.end_trains),
                                            pallet_data))
                lot_nos = [i['lot_no'] for i in common_pallet]
                queryset = queryset.filter(lot_no__in=lot_nos, material_no=order.product_no)
            elif order.order_type == 3:  # 指定托盘出库
                queryset = queryset.filter(container_no=order.pallet_no)
        storage_quantity = 0
        ret = []
        if all([begin_trains, end_trains]):
            b_e_range = [int(begin_trains), int(end_trains)]
        elif begin_trains:
            b_e_range = [int(begin_trains), 99999]
        elif end_trains:
            b_e_range = [0, int(end_trains)]
        else:
            b_e_range = []
        serializer_data = list(self.get_serializer(queryset, many=True).data)
        if b_e_range:
            serializer_data = list(filter(
                lambda x: max(x['begin_end_trains'][0], b_e_range[0]) <= min(x['begin_end_trains'][1], b_e_range[1]),
                serializer_data))

        for item in serializer_data:
            qty = round(float(item['qty']), 1)
            storage_quantity += qty
            ret.append(item)
            if storage_quantity >= need_qty:
                break
        return Response({'data': ret, 'total_trains': storage_quantity})


@method_decorator([api_recorder], name="dispatch")
class BzFinalRubberInventory(ListAPIView):
    """
        终炼胶、帘布库存列表
    """
    serializer_class = BzFinalRubberInventorySearchSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend,)
    queryset = BzFinalMixingRubberInventoryLB.objects.all()

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        product_validity_data = dict(MaterialAttribute.objects.filter(
            period_of_validity__isnull=False
        ).values_list('material__material_no', 'period_of_validity'))
        locked_lot_data = dict(
            ProductInventoryLocked.objects.filter(is_locked=True).values_list('lot_no', 'locked_status'))
        return {
            'request': self.request,
            'format': self.format_kwarg,
            'view': self,
            'product_validity_data': product_validity_data,
            'locked_lot_data': locked_lot_data
        }

    def export_xls(self, result):
        response = HttpResponse(content_type='application/vnd.ms-excel')
        filename = '库位明细'
        response['Content-Disposition'] = u'attachment;filename= ' + filename.encode('gbk').decode(
            'ISO-8859-1') + '.xls'
        # 创建一个文件对象
        wb = xlwt.Workbook(encoding='utf8')
        # 创建一个sheet对象
        sheet = wb.add_sheet('库存信息', cell_overwrite_ok=True)

        style = xlwt.XFStyle()
        style.alignment.wrap = 1
        columns = ['No', '胶料类型', '胶料编码', '质检条码', '托盘号', '库存位', '车数',
                   '总重量', '品质状态', '入库时间', '机台号', '车号', '货位状态']
        for col_num in range(len(columns)):
            sheet.write(0, col_num, columns[col_num])
            # 写入数据
        data_row = 1
        for i in result:
            sheet.write(data_row, 0, data_row)
            sheet.write(data_row, 1, i['material_type'])
            sheet.write(data_row, 2, i['material_no'])
            sheet.write(data_row, 3, i['lot_no'])
            sheet.write(data_row, 4, i['container_no'])
            sheet.write(data_row, 5, i['location'])
            sheet.write(data_row, 6, i['qty'])
            sheet.write(data_row, 7, i['total_weight'])
            sheet.write(data_row, 8, i['quality_status'])
            sheet.write(data_row, 9, i['in_storage_time'])
            sheet.write(data_row, 10, i['equip_no'])
            sheet.write(data_row, 11, i['memo'])
            sheet.write(data_row, 12, i['location_status'])
            data_row = data_row + 1
        # 写出到IO
        output = BytesIO()
        wb.save(output)
        # 重新定位到开始
        output.seek(0)
        response.write(output.getvalue())
        return response

    def list(self, request, *args, **kwargs):
        filter_kwargs = {}
        store_name = self.request.query_params.get('store_name', '炼胶库')  # 仓库
        quality_status = self.request.query_params.get('quality_status', None)
        lot_existed = self.request.query_params.get('lot_existed')
        container_no = self.request.query_params.get('container_no')
        material_no = self.request.query_params.get('material_no')
        order_no = self.request.query_params.get('order_no')
        location = self.request.query_params.get('location')
        tunnel = self.request.query_params.get('tunnel')
        lot_no = self.request.query_params.get('lot_no')
        location_status = self.request.query_params.get('location_status')  # 货位状态
        st = self.request.query_params.get('st')  # 入库开始时间
        et = self.request.query_params.get('et')  # 入库结束时间
        export = self.request.query_params.get('export')  # 1：当前页面  2：所有
        equip_no = self.request.query_params.get('equip_no')  # 机台
        outbound_order_id = self.request.query_params.get('outbound_order_id')  # 指定托盘和指定生产信息出库时使用
        begin_trains = self.request.query_params.get('begin_trains')  # 开始车次
        end_trains = self.request.query_params.get('end_trains')  # 结束车次
        yx_state = self.request.query_params.get('yx_state')  # 有效状态
        if store_name:
            if store_name == '终炼胶库':
                store_name = "炼胶库"
            filter_kwargs['store_name'] = store_name
        if quality_status:
            filter_kwargs['quality_level'] = quality_status
        if lot_existed:
            if lot_existed == '1':
                filter_kwargs['lot_no__isnull'] = False
            else:
                filter_kwargs['lot_no__isnull'] = True
        if container_no:
            filter_kwargs['container_no__icontains'] = container_no
        if material_no:
            filter_kwargs['material_no'] = material_no
        if order_no:
            filter_kwargs['bill_id__icontains'] = container_no
        if location:
            filter_kwargs['location__icontains'] = location
        if tunnel:
            filter_kwargs['location__istartswith'] = tunnel
        if lot_no:
            filter_kwargs['lot_no__icontains'] = lot_no
        if location_status:
            filter_kwargs['location_status'] = location_status
        if st:
            filter_kwargs['in_storage_time__gte'] = st
        if et:
            filter_kwargs['in_storage_time__lte'] = et
        if equip_no:
            filter_kwargs['bill_id__iendswith'] = equip_no
        # 指定托盘和指定生产信息出库查询
        if outbound_order_id:
            try:
                order = OutBoundDeliveryOrder.objects.get(id=outbound_order_id)
            except Exception:
                raise ValidationError('参数错误！')
            if order.order_type == 2:  # 指定生产信息出库
                pallet_data = PalletFeedbacks.objects.filter(
                    factory_date=order.factory_date,
                    equip_no=order.equip_no,
                    classes=order.classes,
                    product_no=order.product_no).values('lot_no', 'begin_trains', 'end_trains')
                common_pallet = list(filter(lambda x: max(x['begin_trains'], order.begin_trains)
                                                      <= min(x['end_trains'], order.end_trains),
                                            pallet_data))
                lot_nos = [i['lot_no'] for i in common_pallet]
                filter_kwargs['lot_no__in'] = lot_nos
                filter_kwargs['material_no'] = order.product_no
            elif order.order_type == 3:  # 指定托盘出库
                filter_kwargs['container_no'] = order.pallet_no
        queryset = BzFinalMixingRubberInventoryLB.objects.using('lb').filter(**filter_kwargs).order_by(
            'in_storage_time')

        if all([begin_trains, end_trains]):
            b_e_range = [int(begin_trains), int(end_trains)]
        elif begin_trains:
            b_e_range = [int(begin_trains), 99999]
        elif end_trains:
            b_e_range = [0, int(end_trains)]
        else:
            b_e_range = []
        if store_name == '炼胶库':
            ret = self.get_serializer(queryset, many=True).data
        else:
            ret = BzFinalMixingRubberLBInventorySerializer(queryset, many=True).data

        if b_e_range:
            ret = list(filter(
                lambda x: max(x['begin_end_trains'][0], b_e_range[0]) <= min(x['begin_end_trains'][1], b_e_range[1]),
                ret))
        if yx_state:
            ret = list(filter(lambda x: x['yx_state']==yx_state, ret))

        page = self.paginate_queryset(ret)
        # serializer = self.get_serializer(page, many=True)
        resp_data = self.get_paginated_response(page).data

        if export:
            if export == '1':
                return self.export_xls(page)
            elif export == '2':
                return self.export_xls(ret)
        resp_data['total_weight'] = round(sum(float(i['total_weight']) for i in ret), 2)
        resp_data['total_trains'] = round(sum(float(i['qty']) for i in ret), 1)
        return Response(resp_data)


@method_decorator([api_recorder], name="dispatch")
class BzFinalRubberInventorySummary(APIView):
    """终炼胶库存、帘布库库存统计列表。参数：quality_status=品质状态&location_status=货位状态&store_name=炼胶库/帘布库&lot_existed=有无收皮条码"""
    permission_classes = (IsAuthenticated, )

    def get(self, request):
        params = request.query_params
        quality_status = params.get("quality_status")
        location_status = params.get("location_status")
        store_name = params.get("store_name", '炼胶库')
        lot_existed = params.get("lot_existed")
        queryset = BzFinalMixingRubberInventoryLB.objects.using('lb').all()
        if location_status:
            queryset = queryset.filter(location_status="有货货位")
        if quality_status:
            queryset = queryset.filter(quality_level=quality_status)
        if store_name:
            if store_name == '终炼胶库':
                store_name = "炼胶库"
            queryset = queryset.filter(store_name=store_name)
        if lot_existed:
            if lot_existed == '1':
                queryset = queryset.filter(lot_no__isnull=False)
            else:
                queryset = queryset.filter(lot_no__isnull=True)
        try:
            ret = queryset.values('material_no').annotate(all_qty=Sum('qty'),
                                                          all_weight=Sum('total_weight')
                                                          ).values('material_no', 'all_qty', 'all_weight')
        except Exception as e:
            raise ValidationError(f"混炼胶库连接失败:{e}")
        return Response(ret)


@method_decorator([api_recorder], name="dispatch")
class BzFinalRubberInventorySearch(ListAPIView):
    """根据出库口、搜索指定数量的终炼胶库存信息.参数：?material_no=物料编码&quality_status=品质状态&need_qty=出库数量"""
    queryset = BzFinalMixingRubberInventoryLB.objects.all()
    serializer_class = BzFinalRubberInventorySearchSerializer
    permission_classes = (IsAuthenticated,)

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        product_validity_data = dict(MaterialAttribute.objects.filter(
            period_of_validity__isnull=False
        ).values_list('material__material_no', 'period_of_validity'))
        locked_lot_data = dict(
            ProductInventoryLocked.objects.filter(is_locked=True).values_list('lot_no', 'locked_status'))
        return {
            'request': self.request,
            'format': self.format_kwarg,
            'view': self,
            'product_validity_data': product_validity_data,
            'locked_lot_data': locked_lot_data
        }

    def list(self, request, *args, **kwargs):
        material_no = self.request.query_params.get('material_no')  # 物料编码
        quality_status = self.request.query_params.get('quality_status')  # 品质状态
        need_qty = self.request.query_params.get('need_qty')  # 出库数量
        tunnel = self.request.query_params.get('tunnel')  # 巷道
        st = self.request.query_params.get('st')  # 入库开始时间
        et = self.request.query_params.get('et')  # 入库结束时间
        equip_no = self.request.query_params.get('equip_no')  # 机台
        outbound_order_id = self.request.query_params.get('outbound_order_id')  # 指定托盘和指定生产信息出库时使用
        begin_trains = self.request.query_params.get('begin_trains')  # 开始车次
        end_trains = self.request.query_params.get('end_trains')  # 结束车次
        if not need_qty:
            raise ValidationError('请输入正确的需求数量！')
        try:
            need_qty = int(need_qty)
        except Exception:
            raise ValidationError('参数错误！')
        queryset = BzFinalMixingRubberInventoryLB.objects.using('lb').filter(
            store_name="炼胶库",
            location_status="有货货位").order_by('in_storage_time')
        if material_no:
            queryset = queryset.filter(material_no=material_no,)
        if quality_status:
            queryset = queryset.filter(quality_level=quality_status)
        if st:
            queryset = queryset.filter(in_storage_time__gte=st)
        if et:
            queryset = queryset.filter(in_storage_time__lte=et)
        if tunnel:
            queryset = queryset.filter(location__istartswith=tunnel)
        if equip_no:
            queryset = queryset.filter(bill_id__iendswith=equip_no)

        # 指定托盘和指定生产信息出库查询
        if outbound_order_id:
            try:
                order = OutBoundDeliveryOrder.objects.get(id=outbound_order_id)
            except Exception:
                raise ValidationError('参数错误！')
            if order.order_type == 2:  # 指定生产信息出库
                pallet_data = PalletFeedbacks.objects.filter(
                    factory_date=order.factory_date,
                    equip_no=order.equip_no,
                    classes=order.classes,
                    product_no=order.product_no).values('lot_no', 'begin_trains', 'end_trains')
                common_pallet = list(filter(lambda x: max(x['begin_trains'], order.begin_trains)
                                                      <= min(x['end_trains'], order.end_trains),
                                            pallet_data))
                lot_nos = [i['lot_no'] for i in common_pallet]
                queryset = queryset.filter(lot_no__in=lot_nos, material_no=order.product_no)
            elif order.order_type == 3:  # 指定托盘出库
                queryset = queryset.filter(container_no=order.pallet_no)
        storage_quantity = 0
        ret = []
        if all([begin_trains, end_trains]):
            b_e_range = [int(begin_trains), int(end_trains)]
        elif begin_trains:
            b_e_range = [int(begin_trains), 99999]
        elif end_trains:
            b_e_range = [0, int(end_trains)]
        else:
            b_e_range = []
        serializer_data = list(self.get_serializer(queryset, many=True).data)
        if b_e_range:
            serializer_data = list(filter(lambda x: max(x['begin_end_trains'][0], b_e_range[0]) <= min(x['begin_end_trains'][1], b_e_range[1]), serializer_data))

        for item in serializer_data:
            qty = round(float(item['qty']), 1)
            storage_quantity += qty
            ret.append(item)
            if storage_quantity >= need_qty:
                break
        return Response({'data': ret, 'total_trains': storage_quantity})


@method_decorator([api_recorder], name="dispatch")
class OutBoundTasksListView(ListAPIView):
    """
        根据出库口过滤混炼、终炼出库任务列表，参数：warehouse_name=混炼胶库/终炼胶库&station_id=出库口id
    """
    serializer_class = OutBoundTasksSerializer
    # permission_classes = (IsAuthenticated, )  # 出库看板使用，不需要登录
    authentication_classes = ()

    def get_queryset(self):
        warehouse_name = self.request.query_params.get('warehouse_name')  # 库存名称
        station_id = self.request.query_params.get('station_id')  # 出库口名称
        try:
            station = Station.objects.get(id=station_id).name
        except Exception:
            raise ValidationError('参数错误')
        return OutBoundDeliveryOrderDetail.objects.filter(outbound_delivery_order__warehouse=warehouse_name,
                                                          outbound_delivery_order__station=station,
                                                          status=3
                                                          ).order_by('-finish_time')


@method_decorator([api_recorder], name="dispatch")
class InOutBoundSummaryView(APIView):
    """混炼终炼出库口出入库统计，参数：warehouse_name=混炼胶库/终炼胶库&station_id=出库口id"""
    # permission_classes = (IsAuthenticated, )  # 出库看板使用，不需要登录
    authentication_classes = ()

    def get(self, request):
        warehouse_name = self.request.query_params.get('warehouse_name')  # 库存名称
        station_id = self.request.query_params.get('station_id')  # 出库口名称
        try:
            station = Station.objects.get(id=station_id).name
        except Exception:
            raise ValidationError('参数错误')
        now = datetime.datetime.now()
        current_work_schedule_plan = WorkSchedulePlan.objects.filter(
            start_time__lte=now,
            end_time__gte=now,
            plan_schedule__work_schedule__work_procedure__global_name='密炼'
        ).first()
        if current_work_schedule_plan:
            date_now = str(current_work_schedule_plan.plan_schedule.day_time)
        else:
            date_now = str(now.date())
        date_begin_time = date_now + ' 08:00:00'
        if warehouse_name == '混炼胶库':
            if station == '一层前端':
                ret = [
                    {'tunnel': '3巷',
                     'in_bound_count': MixGumInInventoryLog.objects.using('bz').filter(
                         start_time__gte=date_begin_time,
                         location__startswith='3'
                     ).exclude(Q(material_no__icontains='-RE') |
                               Q(material_no__icontains='-FM') |
                               Q(material_no__icontains='-RFM')
                               ).aggregate(count=Sum('qty'))['count'],
                     "out_bound_count": MixGumOutInventoryLog.objects.using('bz').filter(
                         start_time__gte=date_begin_time,
                         location__startswith='3'
                     ).exclude(Q(material_no__icontains='-RE') |
                               Q(material_no__icontains='-FM') |
                               Q(material_no__icontains='-RFM')
                               ).aggregate(count=Sum('qty'))['count']
                     },
                    {'tunnel': '4巷',
                     'in_bound_count': MixGumInInventoryLog.objects.using('bz').filter(
                         start_time__gte=date_begin_time,
                         location__startswith='4'
                     ).exclude(Q(material_no__icontains='-RE') |
                               Q(material_no__icontains='-FM') |
                               Q(material_no__icontains='-RFM')
                               ).aggregate(count=Sum('qty'))['count'],
                     "out_bound_count": MixGumOutInventoryLog.objects.using('bz').filter(
                         start_time__gte=date_begin_time,
                         location__startswith='4'
                     ).exclude(Q(material_no__icontains='-RE') |
                               Q(material_no__icontains='-FM') |
                               Q(material_no__icontains='-RFM')
                               ).aggregate(count=Sum('qty'))['count']
                     },
                ]
                # 出库
            elif station == '二层前端':
                ret = [
                    {'tunnel': '1巷',
                     'in_bound_count': MixGumInInventoryLog.objects.using('bz').filter(
                         start_time__gte=date_begin_time,
                         location__startswith='1'
                     ).exclude(Q(material_no__icontains='-RE') |
                               Q(material_no__icontains='-FM') |
                               Q(material_no__icontains='-RFM')
                               ).aggregate(count=Sum('qty'))['count'],
                     "out_bound_count": MixGumOutInventoryLog.objects.using('bz').filter(
                         start_time__gte=date_begin_time,
                         location__startswith='1'
                     ).exclude(Q(material_no__icontains='-RE') |
                               Q(material_no__icontains='-FM') |
                               Q(material_no__icontains='-RFM')
                               ).aggregate(count=Sum('qty'))['count']
                     },
                    {'tunnel': '2巷',
                     'in_bound_count': MixGumInInventoryLog.objects.using('bz').filter(
                         start_time__gte=date_begin_time,
                         location__startswith='2'
                     ).exclude(Q(material_no__icontains='-RE') |
                               Q(material_no__icontains='-FM') |
                               Q(material_no__icontains='-RFM')
                               ).aggregate(count=Sum('qty'))['count'],
                     "out_bound_count": MixGumOutInventoryLog.objects.using('bz').filter(
                         start_time__gte=date_begin_time,
                         location__startswith='2'
                     ).exclude(Q(material_no__icontains='-RE') |
                               Q(material_no__icontains='-FM') |
                               Q(material_no__icontains='-RFM')
                               ).aggregate(count=Sum('qty'))['count']
                     },
                ]
            elif station == '二层后端':
                ret = [
                    {'tunnel': '1巷',
                     'in_bound_count': MixGumInInventoryLog.objects.using('bz').filter(
                         start_time__gte=date_begin_time,
                         location__startswith='1'
                     ).exclude(Q(material_no__icontains='-RE') |
                               Q(material_no__icontains='-FM') |
                               Q(material_no__icontains='-RFM')
                               ).aggregate(count=Sum('qty'))['count'],
                     "out_bound_count": MixGumOutInventoryLog.objects.using('bz').filter(
                         start_time__gte=date_begin_time,
                         location__startswith='1'
                     ).exclude(Q(material_no__icontains='-RE') |
                               Q(material_no__icontains='-FM') |
                               Q(material_no__icontains='-RFM')
                               ).aggregate(count=Sum('qty'))['count']
                     },
                    {'tunnel': '2巷',
                     'in_bound_count': MixGumInInventoryLog.objects.using('bz').filter(
                         start_time__gte=date_begin_time,
                         location__startswith='2'
                     ).exclude(Q(material_no__icontains='-RE') |
                               Q(material_no__icontains='-FM') |
                               Q(material_no__icontains='-RFM')
                               ).aggregate(count=Sum('qty'))['count'],
                     "out_bound_count": MixGumOutInventoryLog.objects.using('bz').filter(
                         start_time__gte=date_begin_time,
                         location__startswith='2'
                     ).exclude(Q(material_no__icontains='-RE') |
                               Q(material_no__icontains='-FM') |
                               Q(material_no__icontains='-RFM')
                               ).aggregate(count=Sum('qty'))['count']
                     },
                    {'tunnel': '3巷',
                     'in_bound_count': MixGumInInventoryLog.objects.using('bz').filter(
                         start_time__gte=date_begin_time,
                         location__startswith='3'
                     ).exclude(Q(material_no__icontains='-RE') |
                               Q(material_no__icontains='-FM') |
                               Q(material_no__icontains='-RFM')
                               ).aggregate(count=Sum('qty'))['count'],
                     "out_bound_count": MixGumOutInventoryLog.objects.using('bz').filter(
                         start_time__gte=date_begin_time,
                         location__startswith='3'
                     ).exclude(Q(material_no__icontains='-RE') |
                               Q(material_no__icontains='-FM') |
                               Q(material_no__icontains='-RFM')
                               ).aggregate(count=Sum('qty'))['count']
                     },
                    {'tunnel': '4巷',
                     'in_bound_count': MixGumInInventoryLog.objects.using('bz').filter(
                         start_time__gte=date_begin_time,
                         location__startswith='4'
                     ).exclude(Q(material_no__icontains='-RE') |
                               Q(material_no__icontains='-FM') |
                               Q(material_no__icontains='-RFM')
                               ).aggregate(count=Sum('qty'))['count'],
                     "out_bound_count": MixGumOutInventoryLog.objects.using('bz').filter(
                         start_time__gte=date_begin_time,
                         location__startswith='4'
                     ).exclude(Q(material_no__icontains='-RE') |
                               Q(material_no__icontains='-FM') |
                               Q(material_no__icontains='-RFM')
                               ).aggregate(count=Sum('qty'))['count']
                     },
                ]
            else:
                ret = []
            # 混炼胶总入库车数
            total_inbound_count = MixGumInInventoryLog.objects.using('bz').filter(
                start_time__gte=date_begin_time).exclude(Q(material_no__icontains='-RE') |
                                                         Q(material_no__icontains='-FM') |
                                                         Q(material_no__icontains='-RFM')
                                                         ).aggregate(count=Sum('qty'))['count']
            # 混炼胶总出库数量
            total_outbound_count = MixGumOutInventoryLog.objects.using('bz').filter(
                start_time__gte=date_begin_time).exclude(Q(material_no__icontains='-RE') |
                                                         Q(material_no__icontains='-FM') |
                                                         Q(material_no__icontains='-RFM')
                                                         ).aggregate(count=Sum('qty'))['count']
            # 混炼胶总生产车次
            production_count = TrainsFeedbacks.objects.filter(
                factory_date=date_now).exclude(
                Q(product_no__icontains='-RE') |
                Q(product_no__icontains='-FM') |
                Q(product_no__icontains='-RFM')).count()
        else:
            ret = [
                {'tunnel': '1巷',
                 'in_bound_count': FinalGumInInventoryLog.objects.using('lb').filter(
                     start_time__gte=date_begin_time,
                     location__startswith='1').aggregate(count=Sum('qty'))['count'],
                 "out_bound_count": FinalGumOutInventoryLog.objects.using('lb').filter(
                     start_time__gte=date_begin_time, location__startswith='1').aggregate(count=Sum('qty'))['count']
                 },
                {'tunnel': '2巷',
                 'in_bound_count': FinalGumInInventoryLog.objects.using('lb').filter(
                     start_time__gte=date_begin_time,
                     location__startswith='2').aggregate(count=Sum('qty'))['count'],
                 "out_bound_count": FinalGumOutInventoryLog.objects.using('lb').filter(
                     start_time__gte=date_begin_time, location__startswith='2').aggregate(count=Sum('qty'))['count']
                 },
                {'tunnel': '3巷',
                 'in_bound_count': FinalGumInInventoryLog.objects.using('lb').filter(
                     start_time__gte=date_begin_time,
                     location__startswith='3').aggregate(count=Sum('qty'))['count'],
                 "out_bound_count": FinalGumOutInventoryLog.objects.using('lb').filter(
                     start_time__gte=date_begin_time, location__startswith='3').aggregate(count=Sum('qty'))['count']
                 },
                {'tunnel': '4巷',
                 'in_bound_count': FinalGumInInventoryLog.objects.using('lb').filter(
                     start_time__gte=date_begin_time,
                     location__startswith='4').aggregate(count=Sum('qty'))['count'],
                 "out_bound_count": FinalGumOutInventoryLog.objects.using('lb').filter(
                     start_time__gte=date_begin_time, location__startswith='4').aggregate(count=Sum('qty'))['count']
                 },
            ]
            # 终炼库区终炼胶入库总车数
            final_inbound_count = FinalGumInInventoryLog.objects.using('lb').filter(
                start_time__gte=date_begin_time).filter(Q(location__startswith='1') |
                                                        Q(location__startswith='2') |
                                                        Q(location__startswith='3') |
                                                        Q(location__startswith='4')
                                                        ).aggregate(count=Sum('qty'))['count']
            # 混炼库区终炼胶入库总车数
            mixin_inbound_count = MixGumInInventoryLog.objects.using('bz').filter(
                start_time__gte=date_begin_time).filter(Q(material_no__icontains='-RE') |
                                                        Q(material_no__icontains='-FM') |
                                                        Q(material_no__icontains='-RFM')
                                                        ).aggregate(count=Sum('qty'))['count']
            # 终炼总入库车数
            if not final_inbound_count:
                final_inbound_count = 0
            if not mixin_inbound_count:
                mixin_inbound_count = 0
            total_inbound_count = final_inbound_count + mixin_inbound_count

            # 终炼库区终炼胶出库总车数
            final_outbound_count = FinalGumOutInventoryLog.objects.using('lb').filter(
                start_time__gte=date_begin_time).filter(Q(location__startswith='1') |
                                                        Q(location__startswith='2') |
                                                        Q(location__startswith='3') |
                                                        Q(location__startswith='4')
                                                        ).aggregate(count=Sum('qty'))['count']
            # 混炼库区终炼胶出库总车数
            mixin_outbound_count = MixGumOutInventoryLog.objects.using('bz').filter(
                start_time__gte=date_begin_time).filter(Q(material_no__icontains='-RE') |
                                                        Q(material_no__icontains='-FM') |
                                                        Q(material_no__icontains='-RFM')
                                                        ).aggregate(count=Sum('qty'))['count']
            # 终炼总出库车数
            if not final_outbound_count:
                final_outbound_count = 0
            if not mixin_outbound_count:
                mixin_outbound_count = 0
            total_outbound_count = final_outbound_count + mixin_outbound_count
            # 终炼总车次
            production_count = TrainsFeedbacks.objects.filter(
                factory_date=date_now).filter(
                Q(product_no__icontains='-RE') |
                Q(product_no__icontains='-FM') |
                Q(product_no__icontains='-RFM')).count()
        return Response({"data": ret,
                         "total_inbound_count": total_inbound_count,
                         "total_outbound_count": total_outbound_count,
                         "production_count": production_count
                         })


@method_decorator([api_recorder], name="dispatch")
class LIBRARYINVENTORYView(APIView):
    permission_classes = (IsAuthenticated, )

    def get_result(self, model, db, store_name, warehouse_name, location_status, product_validity_dict, **kwargs):
        now_time = datetime.datetime.now()
        # 各胶料封闭货位数据
        fb = model.objects.using(db).filter(**kwargs).filter(location_status='封闭货位').values('material_no').annotate(
            qty=Sum('qty'),
            total_weight=Sum('total_weight')
            ).values('material_no', 'qty', 'total_weight')
        # 胶料品质状态数据
        query_set = model.objects.using(db).filter(store_name=store_name).filter(**kwargs)
        if location_status:
            if location_status == 'Y':
                query_set = query_set.filter(location_status='封闭货位')
            else:
                query_set = query_set.exclude(location_status='封闭货位')
                fb = []
        result = query_set.values('material_no', 'quality_level').annotate(qty=Sum('qty'),
                                                                           total_weight=Sum('total_weight'),
                                                                           min_inventory_time=Min('in_storage_time')
                                                                           ).values(
            'material_no', 'quality_level', 'qty', 'total_weight', 'min_inventory_time').order_by('material_no')
        locked_lot_nos = list(ProductInventoryLocked.objects.filter(is_locked=True).values_list('lot_no', flat=True))
        stock_locked_data = dict(
            query_set.filter(
                lot_no__in=locked_lot_nos
            ).values('material_no').annotate(qty=Sum('qty')).values_list('material_no', 'qty'))
        res = {}
        for i in result:
            material_no = i['material_no'].strip()
            quality_level = i['quality_level'].strip()
            validity_days = product_validity_dict.get(material_no, 0)
            expire_flag = False
            yj_flag = False
            if validity_days:
                if (now_time - i['min_inventory_time']).total_seconds() / 60 / 60 / 24 > validity_days:
                    expire_flag = True
                if validity_days - (now_time - i['min_inventory_time']).total_seconds() / 60 / 60 / 24 <= 3:
                    yj_flag = True
            dj_flag = False
            if quality_level == '待检品':
                if (now_time - i['min_inventory_time']).total_seconds() / 60 / 60 / 24 > 3:
                    dj_flag = True
            if material_no not in res:
                try:
                    stage = material_no.split('-')[1]
                except Exception:
                    stage = material_no
                res[material_no] = {
                    'material_no': material_no,
                    'warehouse_name': warehouse_name,
                    'location': kwargs.get('location__startswith'),
                    'stage': stage,
                    'all_qty': i['qty'],
                    'total_weight': i['total_weight'],
                    'locked_trains': stock_locked_data.get(i['material_no'], 0),
                    i['quality_level']: {'qty': i['qty'], 'total_weight': i['total_weight'], 'expire_flag': expire_flag, 'dj_flag': dj_flag, 'yj_flag': yj_flag},
                    'expire_flag': expire_flag,
                    'dj_flag': dj_flag,
                    'yj_flag': yj_flag,
                }
            else:
                res[material_no][quality_level] = {
                    'qty': i['qty'],
                    'total_weight': i['total_weight'],
                    'expire_flag': expire_flag,
                    'dj_flag': dj_flag,
                    'yj_flag': yj_flag,
                }
                if not res[material_no]['dj_flag']:
                    res[material_no]['dj_flag'] = dj_flag
                if not res[material_no]['expire_flag']:
                    res[material_no]['expire_flag'] = expire_flag
                if not res[material_no]['yj_flag']:
                    res[material_no]['yj_flag'] = yj_flag
                res[material_no]['all_qty'] += i['qty']
                res[material_no]['total_weight'] += i['total_weight']
            res[material_no]['active_qty'] = res[material_no]['all_qty']

        for i in fb:
            material_no = i['material_no']
            if res.get(material_no):
                res[material_no].update({'封闭': {'qty': i['qty'], 'total_weight': i['total_weight']}})
                res[material_no]['active_qty'] -= res[material_no]['封闭']['qty']

        return list(res.values())

    def export_xls(self, result):
        response = HttpResponse(content_type='application/vnd.ms-excel')
        filename = '库内库存明细'
        response['Content-Disposition'] = u'attachment;filename= ' + filename.encode('gbk').decode(
            'ISO-8859-1') + '.xls'
        # 创建一个文件对象
        wb = xlwt.Workbook(encoding='utf8')
        # 创建一个sheet对象
        sheet = wb.add_sheet('库存信息', cell_overwrite_ok=True)
        style = xlwt.XFStyle()
        style.alignment.wrap = 1

        columns = ['No', '胶料类型', '物料编码', '物料名称', '库区', '巷道', '一等品库存数(车)', '重量(kg)', '三等品库存数(车)', '重量(kg)',
                   '待检品库存数(车)', '重量(kg)', '总库存数(车)', '总重量(kg)', '封闭库存数(车)', '重量(kg)', '有效库存数']
        # 写入文件标题
        for col_num in range(len(columns)):
            sheet.write(0, col_num, columns[col_num])
            # 写入数据
        data_row = 1
        for i in result:
            try:
                product_no_split_list = i['material_no'].split('-')
                if product_no_split_list[1] in ('RE', 'FM', 'RFM'):
                    product_no = product_no_split_list[2]
                else:
                    product_no = '-'.join(product_no_split_list[1:3])
            except Exception:
                product_no = i['material_no']
            sheet.write(data_row, 0, result.index(i) + 1)
            sheet.write(data_row, 1, i['stage'])
            sheet.write(data_row, 2, product_no)
            sheet.write(data_row, 3, product_no)
            sheet.write(data_row, 4, i['warehouse_name'])
            sheet.write(data_row, 5, i['location'])
            sheet.write(data_row, 6, i['一等品']['qty'] if i.get('一等品') else None)
            sheet.write(data_row, 7, i['一等品']['total_weight'] if i.get('一等品') else None)
            sheet.write(data_row, 8, i['三等品']['qty'] if i.get('三等品') else None)
            sheet.write(data_row, 9, i['三等品']['total_weight'] if i.get('三等品') else None)
            sheet.write(data_row, 10, i['待检品']['qty'] if i.get('待检品') else None)
            sheet.write(data_row, 11, i['待检品']['total_weight'] if i.get('待检品') else None)
            sheet.write(data_row, 12, i['all_qty'])
            sheet.write(data_row, 13, i['total_weight'])
            sheet.write(data_row, 14, i['封闭']['qty'] if i.get('封闭') else None)
            sheet.write(data_row, 15, i['封闭']['total_weight'] if i.get('封闭') else None)
            sheet.write(data_row, 16, i['active_qty'])
            data_row = data_row + 1
        # 写出到IO
        output = BytesIO()
        wb.save(output)
        # 重新定位到开始
        output.seek(0)
        response.write(output.getvalue())
        return response

    def get(self, request, *args, **kwargs):
        params = request.query_params
        page = params.get("page", 1)
        page_size = params.get("page_size", 10)
        warehouse_name = params.get("warehouse_name", '')  # 库区
        stage = params.get("stage", '')  # 段次
        material_no = params.get("material_no", '')  # 物料编码
        location = params.get('location', '')  # 巷道
        location_status = params.get('location_status', '')  # 有无封闭货位
        quality_level = params.get('quality_level')
        equip_no = params.get('equip_no')
        export = params.get("export", None)
        locked_status = params.get("locked_status")
        ordering_field = params.get("ordering_field")
        order_by = params.get("order_by")

        product_validity_dict = dict(MaterialAttribute.objects.filter(
            period_of_validity__isnull=False
        ).values_list('material__material_no', 'period_of_validity'))

        try:
            st = (int(page) - 1) * int(page_size)
            et = int(page) * int(page_size)
        except:
            raise ValidationError("page/page_size异常，请修正后重试")
        # else:
        #     if st not in range(0, 99999):
        #         raise ValidationError("page/page_size值异常")
        #     if et not in range(0, 99999):
        #         raise ValidationError("page/page_size值异常")

        filter_kwargs = {}
        if material_no:
            filter_kwargs['material_no__icontains'] = material_no
        if stage:
            filter_kwargs['material_no__contains'] = f'-{stage}'
        if location:
            filter_kwargs['location__startswith'] = location
        if quality_level:
            filter_kwargs['quality_level'] = quality_level
        if equip_no:
            filter_kwargs['bill_id__iendswith'] = equip_no
        if locked_status:
            if locked_status == '1':
                locked_lot_nos = list(
                    ProductInventoryLocked.objects.filter(is_locked=True, locked_status=1).values_list('lot_no',
                                                                                                       flat=True))
                filter_kwargs['lot_no__in'] = locked_lot_nos
            elif locked_status == '2':
                locked_lot_nos = list(
                    ProductInventoryLocked.objects.filter(is_locked=True, locked_status=2).values_list('lot_no',
                                                                                                       flat=True))
                filter_kwargs['lot_no__in'] = locked_lot_nos
        if warehouse_name == '混炼胶库':
            model = BzFinalMixingRubberInventory
            store_name = '立体库'
            temp = self.get_result(model, 'bz', store_name, warehouse_name, location_status, product_validity_dict, **filter_kwargs)

        elif warehouse_name == '终炼胶库':
            model = BzFinalMixingRubberInventoryLB
            store_name = '炼胶库'
            temp = self.get_result(model, 'lb', store_name, warehouse_name, location_status, product_validity_dict, **filter_kwargs)

        else:
            model1 = BzFinalMixingRubberInventory
            store_name1 = '立体库'
            warehouse_name1 = '混炼胶库'
            temp1 = self.get_result(model1, 'bz', store_name1, warehouse_name1, location_status, product_validity_dict, **filter_kwargs)
            model2 = BzFinalMixingRubberInventoryLB
            store_name2 = '炼胶库'
            warehouse_name2 = '终炼胶库'
            temp2 = self.get_result(model2, 'lb', store_name2, warehouse_name2, location_status, product_validity_dict, **filter_kwargs)
            temp = list(temp1) + list(temp2)
        if ordering_field and order_by:
            if ordering_field == 'locked_trains':
                temp = sorted(temp, key=lambda x: x.get('locked_trains', 0), reverse=True if order_by == 'descending' else False)
            elif ordering_field == '1_qty':
                temp = sorted(temp, key=lambda x: x.get('一等品', {}).get('qty', 0), reverse=True if order_by == 'descending' else False)
            elif ordering_field == '3_qty':
                temp = sorted(temp, key=lambda x: x.get('三等品', {}).get('qty', 0), reverse=True if order_by == 'descending' else False)
            elif ordering_field == '2_qty':
                temp = sorted(temp, key=lambda x: x.get('待检品', {}).get('qty', 0), reverse=True if order_by == 'descending' else False)
            elif ordering_field == '1_weight':
                temp = sorted(temp, key=lambda x: x.get('一等品', {}).get('total_weight', 0), reverse=True if order_by == 'descending' else False)
            elif ordering_field == '3_weight':
                temp = sorted(temp, key=lambda x: x.get('三等品', {}).get('total_weight', 0), reverse=True if order_by == 'descending' else False)
            elif ordering_field == '2_weight':
                temp = sorted(temp, key=lambda x: x.get('待检品', {}).get('total_weight', 0), reverse=True if order_by == 'descending' else False)
        else:
            temp = sorted(temp, key=itemgetter('expire_flag', 'yj_flag', 'dj_flag', 'material_no'), reverse=True)  # 按多个字段排序
        weight_1 = qty_1 = weight_3 = qty_3 = weight_dj = qty_dj = weight_fb = qty_fb = total_locked_qty = 0

        for i in temp:
            weight_1 += i['一等品']['total_weight'] if i.get('一等品') else 0
            qty_1 += i['一等品']['qty'] if i.get('一等品') else 0
            weight_3 += i['三等品']['total_weight'] if i.get('三等品') else 0
            qty_3 += i['三等品']['qty'] if i.get('三等品') else 0
            weight_dj += i['待检品']['total_weight'] if i.get('待检品') else 0
            qty_dj += i['待检品']['qty'] if i.get('待检品') else 0
            weight_fb += i['封闭']['total_weight'] if i.get('封闭') else 0
            qty_fb += i['封闭']['qty'] if i.get('封闭') else 0
            total_locked_qty += 0 if not i['locked_trains'] else i['locked_trains']

        total_qty = qty_1 + qty_3 + qty_dj
        total_weight = weight_1 + weight_3 + weight_dj
        count = len(temp)
        if export == 'all':
            result = temp
        else:
            result = temp[st:et]
        if export:
            return self.export_xls(result)

        if warehouse_name == '终炼胶库':
            total_goods_num = 1952
            used_goods_num = BzFinalMixingRubberInventoryLB.objects.using('lb').filter(store_name='炼胶库').count()
        elif warehouse_name == '混炼胶库':
            total_goods_num = 1428
            used_goods_num = BzFinalMixingRubberInventory.objects.using('bz').all().count()
        else:
            total_goods_num = 1428 + 1952
            used_goods_num = BzFinalMixingRubberInventoryLB.objects.using('lb').filter(store_name='炼胶库').count() \
                             + BzFinalMixingRubberInventory.objects.using('bz').all().count()

        return Response({'results': result,
                         "total_count": total_qty,
                         "total_weight": total_weight,
                         'weight_1': weight_1,
                         'qty_1': qty_1,
                         'weight_3': weight_3,
                         'qty_3': qty_3,
                         'weight_dj': weight_dj,
                         'qty_dj': qty_dj,
                         'weight_fb': weight_fb,
                         'qty_fb': qty_fb,
                         'count': count,
                         'total_goods_num': total_goods_num,
                         'used_goods_num': used_goods_num,
                         'empty_goods_num': total_goods_num - used_goods_num,
                         'total_locked_qty': total_locked_qty
                         })


@method_decorator([api_recorder], name="dispatch")
class OutBoundDeliveryOrderViewSet(ModelViewSet):
    queryset = OutBoundDeliveryOrder.objects.exclude(status=4).order_by("-id")
    filter_backends = (DjangoFilterBackend,)
    filter_class = OutBoundDeliveryOrderFilter
    permission_classes = (IsAuthenticated, )

    def list(self, request, *args, **kwargs):
        task_no = self.request.query_params.get('task_no')
        lot_no = self.request.query_params.get('lot_no')
        pallet_no = self.request.query_params.get('pallet_no')
        queryset = self.filter_queryset(self.get_queryset())
        if task_no:
            order_ids = OutBoundDeliveryOrderDetail.objects.filter(
                order_no=task_no).values_list('outbound_delivery_order_id', flat=True)
            if not order_ids:
                return Response({})
            queryset = queryset.filter(id__in=order_ids)
        if pallet_no:
            order_ids = OutBoundDeliveryOrderDetail.objects.filter(
                pallet_no=pallet_no).values_list('outbound_delivery_order_id', flat=True)
            if not order_ids:
                return Response({})
            queryset = queryset.filter(id__in=order_ids)
        if lot_no:
            order_ids = OutBoundDeliveryOrderDetail.objects.filter(
                lot_no=lot_no).values_list('outbound_delivery_order_id', flat=True)
            if not order_ids:
                return Response({})
            queryset = queryset.filter(id__in=order_ids)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_serializer_class(self):
        if self.action in ('update', 'partial_update'):
            return OutBoundDeliveryOrderUpdateSerializer
        else:
            return OutBoundDeliveryOrderSerializer

    @action(methods=['get'], detail=False, permission_classes=[], url_path='export',
            url_name='export')
    def export(self, request):
        order_ids = self.request.query_params.get('order_ids', '')
        order_id_list = order_ids.split(',')
        try:
            orders = OutBoundDeliveryOrder.objects.filter(id__in=order_id_list)
        except Exception:
            raise ValidationError('参数错误')
        ws = xlwt.Workbook(encoding='utf-8')
        for order in orders:
            # 创建工作薄
            w = ws.add_sheet("{}".format(order.order_no))
            w.write(0, 0, "订单子编号")
            w.write(0, 1, "胶料编码")
            w.write(0, 2, "lot_no")
            w.write(0, 3, "托盘号")
            w.write(0, 4, "车次")
            w.write(0, 5, "库位编号")
            w.write(0, 6, "出库时间")
            w.write(0, 7, "状态")
            # 写入数据
            excel_row = 1
            for obj in order.outbound_delivery_details.all():
                w.write(excel_row, 0, obj.order_no)
                w.write(excel_row, 1, order.product_no)
                w.write(excel_row, 2, obj.lot_no)
                w.write(excel_row, 3, obj.pallet_no)
                w.write(excel_row, 4, obj.memo)
                w.write(excel_row, 5, obj.location)
                w.write(excel_row, 6, obj.finish_time)
                w.write(excel_row, 7, obj.get_status_display())
                excel_row += 1
        response = HttpResponse(content_type='application/vnd.ms-excel')
        filename = '备品备件信息导入模板'
        response['Content-Disposition'] = 'attachment;filename= ' + filename.encode('gbk').decode('ISO-8859-1') + '.xls'
        output = BytesIO()
        ws.save(output)
        # 重新定位到开始
        output.seek(0)
        response.write(output.getvalue())
        return response


@method_decorator([api_recorder], name="dispatch")
class OutboundStock(APIView):
    permission_classes = (IsAuthenticated, PermissionClass({'add': 'outbound_product_inventory'}))

    def post(self, request):
        data = self.request.data
        warehouse = data.get('warehouse')
        quality_status = data.get('quality_status')
        product_no = data.get('product_no')
        station = data.get('station')
        stock_data = data.get('stock_data')

        last_order = OutBoundDeliveryOrder.objects.filter(
            created_date__date=datetime.datetime.now().date()
        ).order_by('created_date').last()
        if last_order:
            last_ordering = str(int(last_order.order_no[12:])+1)
            if len(last_ordering) <= 5:
                ordering = last_ordering.zfill(5)
            else:
                ordering = last_ordering.zfill(len(last_ordering))
        else:
            ordering = '00001'
        order_no = 'MES{}{}{}'.format('Z' if warehouse == '终炼胶库' else 'H',
                                      datetime.datetime.now().date().strftime('%Y%m%d'),
                                      ordering)
        instance = OutBoundDeliveryOrder.objects.create(
            warehouse=warehouse,
            order_no=order_no,
            order_qty=9999,
            station=station,
            quality_status=quality_status,
            product_no=product_no,
            created_user=self.request.user
        )

        detail_ids = []
        items = []
        for item in stock_data:
            item['sub_no'] = '00001'
            item['outbound_delivery_order'] = instance.id
            s = OutBoundDeliveryOrderDetailSerializer(data=item, context={'request': request})
            s.is_valid(raise_exception=True)
            detail = s.save()
            detail_ids.append(detail.id)
            dict1 = {'WORKID': detail.order_no,
                     'MID': instance.product_no,
                     'PICI': "1",
                     'RFID': detail.pallet_no,
                     'STATIONID': instance.station,
                     'SENDDATE': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            if instance.warehouse == '终炼胶库':
                dict1['STOREDEF_ID'] = 1
            items.append(dict1)
        username = self.request.user.username
        json_data = {
            'msgId': instance.order_no,
            'OUTTYPE': '快检出库',
            "msgConut": str(len(items)),
            "SENDUSER": self.request.user.username,
            "items": items
        }
        if not DEBUG:
            json_data = json.dumps(json_data, ensure_ascii=False)
            if instance.warehouse == '混炼胶库':
                sender = OUTWORKUploader(end_type="指定出库")
            else:
                sender = OUTWORKUploaderLB(end_type="指定出库")
            result = sender.request(instance.order_no, '指定出库', str(len(items)), username, json_data)
            if result is not None:
                try:
                    items = result['items']
                    msg = items[0]['msg']
                except:
                    msg = result[0]['msg']
                if "TRUE" in msg:  # 成功
                    OutBoundDeliveryOrderDetail.objects.filter(id__in=detail_ids).update(status=2)
                else:  # 失败
                    OutBoundDeliveryOrderDetail.objects.filter(id__in=detail_ids).update(status=5)
                    raise ValidationError('出库失败：{}'.format(msg))
        return Response('ok')


@method_decorator([api_recorder], name="dispatch")
class OutBoundDeliveryOrderDetailViewSet(ModelViewSet):
    queryset = OutBoundDeliveryOrderDetail.objects.all().order_by('-id')
    serializer_class = OutBoundDeliveryOrderDetailSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_class = OutBoundDeliveryOrderDetailFilter
    permission_classes = (IsAuthenticated, )

    def get_serializer_class(self):
        if self.action == 'create':
            return OutBoundDeliveryOrderDetailSerializer
        return OutBoundDeliveryOrderDetailListSerializer

    def get_queryset(self):
        queryset = self.queryset
        statuses = self.request.query_params.get('status')
        if statuses:
            try:
                queryset = queryset.filter(status__in=statuses.split(','))
            except Exception:
                raise ValidationError('参数错误')
        return queryset

    def create(self, request, *args, **kwargs):
        data = self.request.data
        if not isinstance(data, list):
            raise ValidationError('参数错误！')
        if not data:
            raise ValidationError('请选择货物出库！')
        try:
            instance = OutBoundDeliveryOrder.objects.get(id=data[0]['outbound_delivery_order'])
        except Exception:
            raise ValidationError('出库单据号不存在')

        last_order_detail = instance.outbound_delivery_details.order_by('id').last()
        if not last_order_detail:
            sub_no = '00001'
        else:
            if last_order_detail.sub_no:
                last_sub_no = str(int(last_order_detail.sub_no) + 1)
                if len(last_sub_no) <= 5:
                    sub_no = last_sub_no.zfill(5)
                else:
                    sub_no = last_sub_no.zfill(len(last_sub_no))
            else:
                sub_no = '00001'

        detail_ids = []
        items = []
        for item in data:
            item['sub_no'] = sub_no
            s = self.serializer_class(data=item, context={'request': request})
            s.is_valid(raise_exception=True)
            detail = s.save()
            detail_ids.append(detail.id)
            dict1 = {'WORKID': detail.order_no,
                     'MID': instance.product_no,
                     'PICI': "1",
                     'RFID': detail.pallet_no,
                     'STATIONID': instance.station,
                     'SENDDATE': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            if instance.warehouse == '终炼胶库':
                dict1['STOREDEF_ID'] = 1
            items.append(dict1)
        username = self.request.user.username
        json_data = {
            'msgId': instance.order_no,
            'OUTTYPE': '快检出库',
            "msgConut": str(len(items)),
            "SENDUSER": self.request.user.username,
            "items": items
        }
        if not DEBUG:
            json_data = json.dumps(json_data, ensure_ascii=False)
            if instance.warehouse == '混炼胶库':
                sender = OUTWORKUploader(end_type="指定出库")
            else:
                sender = OUTWORKUploaderLB(end_type="指定出库")
            result = sender.request(instance.order_no, '指定出库', str(len(items)), username, json_data)
            # {'msgId': 'MESZ2022070500045', 'OUTTYPE': '快检出库', 'msgConut': 1, 'SENDUSER': 'MES',
            #  'items': [{'workId': 'CHDZ2022070500371', 'msg': 'TRUE#CHDZ2022070500371任务下发成功', 'flag': '01'}]}
            logger.info('出库单据号：{},北自反馈信息：{}'.format(instance.order_no, result))
            if result is not None:
                try:
                    items = result.get('items', [])
                except Exception:
                    raise ValidationError('出库失败，北自系统错误！')
                for item in items:
                    try:
                        msg = item['msg']
                        work_id = item['workId']
                        if "TRUE" in msg:  # 成功
                            state = 2
                        else:
                            state = 5
                    except Exception:
                        continue
                    OutBoundDeliveryOrderDetail.objects.filter(order_no=work_id).update(status=state)
            else:
                OutBoundDeliveryOrderDetail.objects.filter(id__in=detail_ids).update(status=2)
        return Response('ok')

    @action(methods=['post'], detail=False, permission_classes=[IsAuthenticated], url_path='cancel-task',
            url_name='cancel-task')
    def cancel_task(self, request):
        warehouse_name = self.request.data.get('warehouse_name')
        task_ids = self.request.data.get('task_ids')
        if warehouse_name == '混炼胶库':
            db = 'bz'
        else:
            db = 'lb'
        query_set = OutBoundDeliveryOrderDetail.objects.filter(id__in=task_ids, status=2)
        data = query_set.values('order_no', 'pallet_no')
        for item in data:
            CancelTask.objects.using(db).create(**item)
        query_set.update(status=4)
        return Response('ok')


@method_decorator([api_recorder], name="dispatch")
class OutBoundHistory(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        last_out_bound_order = OutBoundDeliveryOrder.objects.filter(
            created_user=self.request.user).order_by('id').last()
        if last_out_bound_order:
            data = {
                'warehouse': last_out_bound_order.warehouse,
                'station': last_out_bound_order.station,
                'order_qty': last_out_bound_order.order_qty,
                'quality_status': last_out_bound_order.quality_status
            }
        else:
            data = {}
        return Response(data)


@method_decorator([api_recorder], name="dispatch")
class WmsInventoryMaterialViewSet(GenericAPIView):
    DB = 'wms'
    queryset = WmsInventoryMaterial.objects.all()
    serializer_class = WmsInventoryMaterialSerializer
    permission_classes = (IsAuthenticated, )

    def get(self, request, *args, **kwargs):
        queryset = WmsInventoryMaterial.objects.using(self.DB).all()
        material_no = self.request.query_params.get('material_no')
        material_name = self.request.query_params.get('material_name')
        unset_flag = self.request.query_params.get('unset_flag')
        if material_no:
            queryset = queryset.filter(material_no__icontains=material_no)
        if material_name:
            queryset = queryset.filter(material_name__icontains=material_name)
        if unset_flag:
            mt_codes = list(WMSMaterialSafetySettings.objects.values_list('wms_material_code', flat=True))
            queryset = queryset.exclude(material_no__in=mt_codes)
        page = self.paginate_queryset(queryset)
        serializer = WmsInventoryMaterialSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def post(self, request):
        material_nos = self.request.data.get('material_nos')
        avg_consuming_weight = self.request.data.get('avg_consuming_weight')
        avg_setting_weight = self.request.data.get('avg_setting_weight')
        warning_days = self.request.data.get('warning_days')
        if avg_consuming_weight:
            defaults = {'avg_consuming_weight': avg_consuming_weight,
                        'type': 1,
                        'created_user': self.request.user}
        elif avg_setting_weight:
            defaults = {'avg_setting_weight': avg_setting_weight,
                        'type': 2,
                        'created_user': self.request.user}
        else:
            defaults = {'warning_days': warning_days,
                        'created_user': self.request.user}
        for material_no in material_nos:
            obj, _ = WMSMaterialSafetySettings.objects.update_or_create(defaults=defaults, wms_material_code=material_no)
            obj.save()
        return Response('设置成功！')


@method_decorator([api_recorder], name="dispatch")
class WMSStockSummaryView(APIView):
    DATABASE_CONF = WMS_CONF
    permission_classes = (IsAuthenticated, )

    def export_xls(self, result):
        response = HttpResponse(content_type='application/vnd.ms-excel')
        filename = '库存统计'
        response['Content-Disposition'] = u'attachment;filename= ' + filename.encode('gbk').decode(
            'ISO-8859-1') + '.xls'
        # 创建一个文件对象
        wb = xlwt.Workbook(encoding='utf8')
        # 创建一个sheet对象
        sheet = wb.add_sheet('库存信息', cell_overwrite_ok=True)

        style = xlwt.XFStyle()
        style.alignment.wrap = 1

        columns = ['No', '物料名称', '物料编码', '中策物料编码', '数单位量', 'PDM', '物料组',
                   '有效库存数量', '有效库存重量（kg）',
                   '合格品数量', '合格品重量（kg）',
                   '待检品数量', '待检品重量（kg）',
                   '不合格品数量', '不合格品重量（kg）',
                   '总数量', '总重量（kg）', '总件数', '总唛头重量（kg）', ]
        for col_num in range(len(columns)):
            sheet.write(1, col_num, columns[col_num])
            # 写入数据
        data_row = 2
        for i in result:
            sheet.write(data_row, 0, result.index(i) + 1)
            sheet.write(data_row, 1, i['name'])
            sheet.write(data_row, 2, i['code'])
            sheet.write(data_row, 3, i['zc_material_code'])
            sheet.write(data_row, 4, i['unit'])
            sheet.write(data_row, 5, i['pdm'])
            sheet.write(data_row, 6, i['group_name'])
            sheet.write(data_row, 7, i['quantity_1']+i['quantity_5'])
            sheet.write(data_row, 8, i['weight_1']+i['weight_5'])
            sheet.write(data_row, 9, i['quantity_1'])
            sheet.write(data_row, 10, i['weight_1'])
            sheet.write(data_row, 11, i['quantity_5'])
            sheet.write(data_row, 12, i['weight_5'])
            sheet.write(data_row, 13, i['quantity_3'])
            sheet.write(data_row, 14, i['weight_3'])
            sheet.write(data_row, 15, i['total_quantity'])
            sheet.write(data_row, 16, i['total_weight'])
            sheet.write(data_row, 17, i['total_sl'])
            sheet.write(data_row, 18, i['total_zl'])
            data_row = data_row + 1
        # 写出到IO
        output = BytesIO()
        wb.save(output)
        # 重新定位到开始
        output.seek(0)
        response.write(output.getvalue())
        return response

    def get(self, request):
        material_name = self.request.query_params.get('material_name')
        material_no = self.request.query_params.get('material_no')
        material_group_name = self.request.query_params.get('material_group_name')
        lower_only_flag = self.request.query_params.get('lower_only_flag')
        export = self.request.query_params.get('export')
        page = self.request.query_params.get('page', 1)
        page_size = self.request.query_params.get('page_size', 15)
        st = (int(page) - 1) * int(page_size)
        et = int(page) * int(page_size)
        extra_where_str = ""
        if material_name:
            extra_where_str += "where temp.MaterialName like '%{}%'".format(material_name)
        if material_no:
            if extra_where_str:
                extra_where_str += " and temp.MaterialCode like '%{}%'".format(material_no)
            else:
                extra_where_str += "where temp.MaterialCode like '%{}%'".format(material_no)
        if material_group_name:
            if extra_where_str:
                extra_where_str += " and m.MaterialGroupName='{}'".format(material_group_name)
            else:
                extra_where_str += "where m.MaterialGroupName='{}'".format(material_group_name)

        sql = """
                select
            temp.MaterialName,
            temp.MaterialCode,
            m.ZCMaterialCode,
            m.StandardUnit,
            m.Pdm,
            m.MaterialGroupName,
            temp.quantity,
            temp.WeightOfActual,
            temp.StockDetailState,
            temp.sl,
            temp.zl
        from (
            select
                a.MaterialCode,
                a.MaterialName,
                a.StockDetailState,
                SUM(a.WeightOfActual) AS WeightOfActual,
                SUM(a.Quantity ) AS quantity,
                SUM(a.SL ) AS sl,
                SUM(a.ZL ) AS zl
            from t_inventory_stock AS a
            group by
                 a.MaterialCode,
                 a.MaterialName,
                 a.StockDetailState
            ) temp
        left join t_inventory_material m on m.MaterialCode=temp.MaterialCode {}""".format(extra_where_str)
        sc = SqlClient(sql=sql, **self.DATABASE_CONF)
        temp = sc.all()

        safety_data = dict(WMSMaterialSafetySettings.objects.values_list(
            F('wms_material_code'), F('warning_weight')))

        data_dict = {}

        for item in temp:
            quality_status = item[8]
            if quality_status == 2:
                quality_status = 5
            if item[1] not in data_dict:
                data = {'name': item[0], 'code': item[1], 'zc_material_code': item[2], 'unit': item[3], 'pdm': item[4],
                        'group_name': item[5], 'total_quantity': item[6], 'total_weight': item[7], 'total_sl': item[9],
                        'total_zl': item[10], 'quantity_1': 0, 'weight_1': 0, 'quantity_3': 0, 'weight_3': 0,
                        'quantity_4': 0, 'weight_4': 0, 'quantity_5': 0, 'weight_5': 0,
                        'quantity_{}'.format(quality_status): item[6], 'weight_{}'.format(quality_status): item[7]}
                data_dict[item[1]] = data
            else:
                data_dict[item[1]]['total_quantity'] += item[6]
                data_dict[item[1]]['total_weight'] += item[7]
                data_dict[item[1]]['total_sl'] += item[9]
                data_dict[item[1]]['total_zl'] += item[10]
                data_dict[item[1]]['quantity_{}'.format(quality_status)] = item[6]
                data_dict[item[1]]['weight_{}'.format(quality_status)] = item[7]
        result = []
        for item in data_dict.values():
            weighting = safety_data.get(item['code'].strip())
            if weighting:
                if weighting < item['weight_1'] + item['weight_5']:
                    item['flag'] = 'H'
                else:
                    item['flag'] = 'L'
            else:
                item['flag'] = None
            result.append(item)
        sc.close()
        if lower_only_flag:
            result = list(filter(lambda x: x['flag'] == 'L', result))
        total_quantity = sum([item['total_quantity'] for item in result])
        total_weight = sum([item['total_weight'] for item in result])
        total_sl = sum([item['total_sl'] for item in result])
        total_zl = sum([item['total_zl'] for item in result])
        total_quantity1 = sum([item['quantity_1'] for item in result])
        total_weight1 = sum([item['weight_1'] for item in result])
        total_quantity3 = sum([item['quantity_3'] for item in result])
        total_weight3 = sum([item['weight_3'] for item in result])
        total_quantity5 = sum([item['quantity_5'] for item in result])
        total_weight5 = sum([item['weight_5'] for item in result])
        count = len(result)
        ret = result[st:et]
        if export:
            if export == '1':
                data = ret
            else:
                data = result
            return self.export_xls(data)
        return Response(
            {'results': ret, "count": count,
             'total_quantity': total_quantity, 'total_weight': total_weight, 'total_sl': total_sl, 'total_zl': total_zl,
             'total_quantity1': total_quantity1, 'total_weight1': total_weight1,
             'total_quantity3': total_quantity3, 'total_weight3': total_weight3,
             'total_quantity5': total_quantity5, 'total_weight5': total_weight5
             })


@method_decorator([api_recorder], name="dispatch")
class THInventoryMaterialViewSet(WmsInventoryMaterialViewSet):
    DB = 'cb'


@method_decorator([api_recorder], name="dispatch")
class THStockSummaryView(WMSStockSummaryView):
    DATABASE_CONF = TH_CONF


@method_decorator([api_recorder], name="dispatch")
class WMSOutTaskView(ListAPIView):
    serializer_class = MaterialOutHistoryOtherSerializer
    permission_classes = (IsAuthenticated,)
    DB = 'wms'
    EXPORT_FIELDS_DICT = {'出库单据号': 'order_no',
                          '单据类型': 'task_type_name',
                          '创建时间': 'start_time',
                          '状态': 'task_status_name',
                          '数量': 'qty',
                          '创建人': 'initiator'
                          }
    db_model = MaterialOutHistoryOther

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        return {
            'request': self.request,
            'format': self.format_kwarg,
            'view': self,
            'db': self.DB
        }

    def get_queryset(self):
        query_set = self.db_model.objects.using(self.DB).order_by('-id')
        order_no = self.request.query_params.get('order_no')
        task_status = self.request.query_params.get('task_status')
        material_no = self.request.query_params.get('material_no')
        material_name = self.request.query_params.get('material_name')
        st = self.request.query_params.get('st')
        et = self.request.query_params.get('et')
        filter_kwargs = {}
        if order_no:
            filter_kwargs['order_no__icontains'] = order_no
        if task_status:
            filter_kwargs['task_status'] = task_status
        if material_no:
            task_ids = MaterialOutHistory.objects.using(self.DB).filter(material_no=material_no).values_list('task_id', flat=True)
            filter_kwargs['id__in'] = task_ids
        if material_name:
            task_ids = MaterialOutHistory.objects.using(self.DB).filter(material_name=material_name).values_list('task_id', flat=True)
            filter_kwargs['id__in'] = task_ids
        if st:
            filter_kwargs['start_time__gte'] = st
        if et:
            filter_kwargs['start_time__lte'] = et
        return query_set.filter(**filter_kwargs)

    def list(self, request, *args, **kwargs):
        export = self.request.query_params.get('export')
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if export:
            et = self.request.query_params.get('et')
            st = self.request.query_params.get('st')
            if not all([st, et]):
                raise ValidationError('请选择导出的时间范围！')
            diff = datetime.datetime.strptime(et, '%Y-%m-%d %H:%M:%S') - datetime.datetime.strptime(st, '%Y-%m-%d %H:%M:%S')
            if diff.days > 31:
                raise ValidationError('导出数据的日期跨度不得超过一个月！')
            data = self.get_serializer(queryset, many=True).data
            return gen_template_response(self.EXPORT_FIELDS_DICT, data, '出库单据')
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


@method_decorator([api_recorder], name="dispatch")
class THOutTaskView(WMSOutTaskView):
    DB = 'cb'
    serializer_class = THOutHistoryOtherSerializer
    db_model = THOutHistoryOther


@method_decorator([api_recorder], name="dispatch")
class WMSOutTaskDetailView(ListAPIView):
    serializer_class = MaterialOutHistorySerializer
    permission_classes = (IsAuthenticated,)
    DB = 'wms'
    FILE_NAME = '出库任务'
    EXPORT_FIELDS_DICT = {'出库单据号': 'task_order_no',
                          '下架任务号': 'order_no',
                          '巷道编号': 'tunnel',
                          '追踪码': 'lot_no',
                          '识别卡ID': 'pallet_no',
                          '库位码': 'location',
                          '物料名称': 'material_name',
                          '物料编码': 'material_no',
                          '批次号': 'batch_no',
                          '创建时间': 'created_time',
                          '状态': 'status',
                          '创建人': 'initiator',
                          '数量': 'qty',
                          '重量': 'weight',
                          '出库站台': 'entrance_name',
                          }
    db_model = MaterialOutHistory

    def get_queryset(self):
        task = self.request.query_params.get('task')
        task_order_no = self.request.query_params.get('task_order_no')
        task_status = self.request.query_params.get('task_status')
        lot_no = self.request.query_params.get('lot_no')
        material_no = self.request.query_params.get('material_no')
        tunnel = self.request.query_params.get('tunnel')
        location = self.request.query_params.get('location')
        pallet_no = self.request.query_params.get('pallet_no')
        entrance_name = self.request.query_params.get('entrance_name')
        st = self.request.query_params.get('st')
        et = self.request.query_params.get('et')
        filter_kwargs = {}
        if task:
            filter_kwargs['task_id'] = task
        if task_order_no:
            filter_kwargs['task__order_no'] = task_order_no
        if task_status:
            filter_kwargs['task_status'] = task_status
        if lot_no:
            filter_kwargs['lot_no__icontains'] = lot_no
        if material_no:
            filter_kwargs['material_no__icontains'] = material_no
        if tunnel:
            filter_kwargs['location__icontains'] = '-{}'.format(tunnel)
        if location:
            filter_kwargs['location__icontains'] = location
        if pallet_no:
            filter_kwargs['pallet_no__icontains'] = pallet_no
        if st:
            filter_kwargs['task__start_time__gte'] = st
        if et:
            filter_kwargs['task__start_time__lte'] = et
        if entrance_name:
            entrance_data = dict(MaterialEntrance.objects.using(self.DB).values_list('name', 'code'))
            filter_kwargs['entrance'] = entrance_data.get(entrance_name)
        return self.db_model.objects.using(self.DB).filter(**filter_kwargs).order_by('-task')

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        entrance_data = dict(MaterialEntrance.objects.using(self.DB).values_list('code', 'name'))
        return {
            'request': self.request,
            'format': self.format_kwarg,
            'view': self,
            'entrance_data': entrance_data,
            'db': self.DB
        }

    def list(self, request, *args, **kwargs):
        export = self.request.query_params.get('export')
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if export:
            et = self.request.query_params.get('et')
            st = self.request.query_params.get('st')
            if not all([st, et]):
                raise ValidationError('请选择导出的时间范围！')
            diff = datetime.datetime.strptime(et, '%Y-%m-%d %H:%M:%S') - datetime.datetime.strptime(st, '%Y-%m-%d %H:%M:%S')
            if diff.days > 31:
                raise ValidationError('导出数据的日期跨度不得超过一个月！')
            data = self.get_serializer(queryset, many=True).data
            return gen_template_response(self.EXPORT_FIELDS_DICT, data, self.FILE_NAME)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


@method_decorator([api_recorder], name="dispatch")
class THOutTaskDetailView(WMSOutTaskDetailView):
    DB = 'cb'
    serializer_class = THOutHistorySerializer
    db_model = THOutHistory


@method_decorator([api_recorder], name="dispatch")
class WmsOutboundOrderView(APIView):
    permission_classes = (IsAuthenticated, )
    URL = WMS_URL
    ORDER_TYPE = 1

    def post(self, request):
        outbound_type = self.request.data.get('outbound_type')  # 1 指定库位出库 2：指定重量出库
        entrance_code = self.request.data.get('entrance_code')  # 出库口
        outbound_data = self.request.data.get('outbound_data')
        if outbound_type not in (1, 2):
            raise ValidationError('bad request！')
        if not entrance_code:
            raise ValidationError('请选择出库口！')
        if not isinstance(outbound_data, list):
            raise ValidationError('data error!')
        task_num = 'MES{}'.format(datetime.datetime.now().strftime('%Y%m%d%H%M%S%f'))
        details = []
        if outbound_type == 1:
            url = '{}/MESApi/AllocateSpaceDelivery'.format(self.URL)
            for idx, item in enumerate(outbound_data):
                task_no = task_num + str(idx+1)
                details.append(
                    {
                        "TaskDetailNumber": task_no,
                        "MaterialCode": item.get('MaterialCode'),
                        "MaterialName": item.get('MaterialName'),
                        "SpaceCode": item.get('SpaceCode'),
                        "Quantity": 1
                    }
                )
                if self.ORDER_TYPE == 1:
                    quality_status_map = {1: "合格品", 2: "抽检中", 3: "不合格品", 4: "过期", 5: "待检"}
                    em = ExamineMaterial.objects.filter(wlxxid=item['MaterialCode'],
                                                        batch=item['BatchNo']).first()
                    if em:
                        mes_test_result = '合格' if em.qualified else '不合格'
                    else:
                        mes_test_result = '未检测'
                    mtr = MaterialInspectionRegistration.objects.filter(material_no=item['MaterialCode'],
                                                                        batch=item['BatchNo']).first()
                    if mtr:
                        zc_test_result = mtr.quality_status
                    else:
                        zc_test_result = '未知'
                    hs = WmsNucleinManagement.objects.filter(batch_no=item['BatchNo'],
                                                             material_no=item['MaterialCode']).first()
                    if hs:
                        hs_status = hs.locked_status
                    else:
                        hs_status = '未管控'
                    try:
                        WMSOutboundHistory.objects.create(
                            task_no=task_no,
                            quality_status=quality_status_map.get(item['StockDetailState']),
                            mes_test_result=mes_test_result,
                            zc_test_result=zc_test_result,
                            hs_status=hs_status,
                            mooney_value=None if not item.get('mn_value') else item['mn_value'],
                            mooney_level=item.get('mn_level')
                        )
                    except Exception:
                        raise
            data = {
                "TaskNumber": task_num,
                "EntranceCode": entrance_code,
                "AllocationInventoryDetails": details
            }
        else:
            url = '{}/MESApi/AllocateWeightDelivery'.format(self.URL)
            for idx, item in enumerate(outbound_data):
                details.append({
                        "MaterialCode": item.get('MaterialCode'),
                        "StockDetailState": item.get('StockDetailState'),
                        "MaterialName": item.get('MaterialName'),
                        "WeightOfActual": item.get('WeightOfActual')
                    }
                )
            data = {
                "TaskNumber": task_num,
                "EntranceCode": entrance_code,
                "AllocationInventoryDetails": details
            }
        # headers = {"UserId": 75, "tenantNumber": 1}
        MaterialOutboundOrder.objects.create(order_no=task_num,
                                             created_username=self.request.user.username,
                                             order_type=self.ORDER_TYPE)
        try:
            res = requests.post(url, json=data, timeout=10)
        except Exception as e:
            raise ValidationError('请求出库失败，请联系管理员！')
        try:
            resp = json.loads(res.content)
        except Exception:
            resp = {}
        resp_status = resp.get('state')
        if resp_status != 1:
            raise ValidationError('出库失败：{}'.format(resp.get('msg')))
        return Response('成功')


@method_decorator([api_recorder], name="dispatch")
class THOutboundOrderView(WmsOutboundOrderView):
    URL = TH_URL
    ORDER_TYPE = 2


@method_decorator([api_recorder], name="dispatch")
class WwsCancelTaskView(APIView):
    URL = WMS_URL
    permission_classes = (IsAuthenticated, )

    def post(self, request):
        task_num = self.request.data.get('task_num')
        if not task_num:
            raise ValidationError('请输入出库单号！')
        data = [{"TaskNumber": task_num}]
        url = self.URL + '/MESApi/CancelTask'
        try:
            res = requests.post(url, json=data, timeout=5)
        except Exception as e:
            raise ValidationError('请求取消出库失败，请联系管理员！')
        try:
            resp = json.loads(res.content)
        except Exception:
            resp = {}
        # {'state': 1, 'datas': '调用MES-取消出库任务接口成功', 'msg': '调用MES-取消出库任务接口成功'}
        resp_status = resp.get('state')
        if resp_status != 1:
            raise ValidationError('取消失败：{}'.format(resp.get('msg')))
        return Response('ok')


@method_decorator([api_recorder], name="dispatch")
class THCancelTaskView(WwsCancelTaskView):
    URL = TH_URL


@method_decorator([api_recorder], name="dispatch")
class HFStockView(APIView):
    DATABASE_CONF = HF_CONF
    permission_classes = (IsAuthenticated, PermissionClass({'view': 'view_material_hf_summary'}))

    def get(self, request):
        st = self.request.query_params.get('st')
        et = self.request.query_params.get('et')
        material_no = self.request.query_params.get('material_no')
        material_name = self.request.query_params.get('material_name')
        extra_where_str = ""
        extra_where_str2 = "where OastInTime is not null"
        extra_where_str3 = "where OastOutTime is not null"
        if material_name:
            extra_where_str += "where ProductName like N'%{}%'".format(material_name)
        if material_no:
            if extra_where_str:
                extra_where_str += " and ProductNo like '%{}%'".format(material_no)
            else:
                extra_where_str += "where ProductNo like '%{}%'".format(material_no)
        if st:
            if extra_where_str:
                extra_where_str += " and TaskStartTime >= '{}'".format(st)
            else:
                extra_where_str += "where TaskStartTime >= '{}'".format(st)
            extra_where_str2 += " and OastInTime >= '{}'".format(st)
            extra_where_str3 += " and OastOutTime >= '{}'".format(st)
        if et:
            if extra_where_str:
                extra_where_str += " and TaskStartTime <= '{}'".format(et)
            else:
                extra_where_str += "where TaskStartTime <= '{}'".format(et)
            extra_where_str2 += " and OastInTime <= '{}'".format(et)
            extra_where_str3 += " and OastOutTime <= '{}'".format(et)
        sql = """select
                   ProductNo,
                   ProductName,
                   TaskState,
                   count(*)
            from dsp_OastTask
            {}
            group by ProductNo, ProductName, TaskState;""".format(extra_where_str)
        sc = SqlClient(sql=sql, **self.DATABASE_CONF)
        temp = sc.all()
        result = {}
        for item in temp:
            material_no = item[0]
            qty = item[3]
            task_state = item[2]
            if material_no not in result:
                underway_qty = waiting_qty = baking_qty = finished_qty = indoor_qty = outbound_qty = 0
                if task_state == 1:  # 入库中
                    underway_qty += qty
                elif task_state == 2:  # 烘烤运行中
                    baking_qty += qty
                    indoor_qty += qty
                elif task_state == 3:  # 出库中
                    outbound_qty += qty
                #     indoor_qty += qty
                elif task_state == 4:  # 等待烘烤
                    waiting_qty += qty
                    indoor_qty += qty
                elif task_state == 5:  # 等待出库
                    finished_qty += qty
                    indoor_qty += qty
                elif task_state == 6:  # 已出库
                    outbound_qty += qty
                result[item[0]] = {'material_no': item[0],
                                   'material_name': item[1],
                                   'underway_qty': underway_qty,
                                   'waiting_qty': waiting_qty,
                                   'baking_qty': baking_qty,
                                   'finished_qty': finished_qty,
                                   'indoor_qty': indoor_qty,
                                   'outbound_qty': outbound_qty}
            else:
                if task_state == 1:  # 入库中
                    result[item[0]]['underway_qty'] += qty
                elif task_state == 2:  # 烘烤运行中
                    result[item[0]]['baking_qty'] += qty
                    result[item[0]]['indoor_qty'] += qty
                elif task_state == 3:  # 出库中
                    result[item[0]]['outbound_qty'] += qty
                #     result[item[0]]['indoor_qty'] += qty
                elif task_state == 4:  # 等待烘烤
                    result[item[0]]['waiting_qty'] += qty
                    result[item[0]]['indoor_qty'] += qty
                elif task_state == 5:  # 等待出库
                    result[item[0]]['finished_qty'] += qty
                    result[item[0]]['indoor_qty'] += qty
                elif task_state == 6:  # 已出库
                    result[item[0]]['outbound_qty'] += qty
        sc.close()
        material_nos = list(result.keys())

        r_sql = """select
                   ProductNo,
                   count(*)
            from dsp_OastTask
            {}
            group by ProductNo;""".format(extra_where_str2)
        sc = SqlClient(sql=r_sql, **self.DATABASE_CONF)
        temp2 = sc.all()
        temp2_data = {i[0]: i[1] for i in temp2}

        c_sql = """select
                   ProductNo,
                   count(*)
            from dsp_OastTask
            {}
            group by ProductNo;""".format(extra_where_str3)
        sc = SqlClient(sql=c_sql, **self.DATABASE_CONF)
        temp2 = sc.all()
        temp3_data = {i[0]: i[1] for i in temp2}

        # 补充立体库库内库存数量
        stock_data = dict(WmsInventoryStock.objects.using('wms').filter(
            material_no__in=material_nos,
            container_no__startswith='5'
        ).values('material_no').annotate(c=Count('material_no')).values_list('material_no', 'c'))
        for key, value in result.items():
            value['stock_qty'] = stock_data.get(key)
            value['in_qty'] = temp2_data.get(key)
            value['out_qty'] = temp3_data.get(key)
        return Response(result.values())


@method_decorator([api_recorder], name="dispatch")
class HFStockDetailView(APIView):
    DATABASE_CONF = HF_CONF
    permission_classes = (IsAuthenticated, PermissionClass({'view': 'view_material_hf_summary'}))

    def get(self, request):
        st = self.request.query_params.get('st')  # 开始时间
        et = self.request.query_params.get('et')  # 结束时间
        material_no = self.request.query_params.get('material_no')  # 物料编码
        data_type = self.request.query_params.get('data_type')  # 3：输送途中 4：正在烘  5：已经烘完 6：烘房小计 7：已出库 8:等待烘烤
        page = int(self.request.query_params.get('page', 1))
        page_size = int(self.request.query_params.get('page_size', 10))
        if not data_type:
            raise ValidationError('参数缺失！')
        extra_where_str = ""
        if material_no:
            extra_where_str += "where ProductNo = '{}'".format(material_no)
        if data_type == '1':
            if extra_where_str:
                extra_where_str += ' and OastInTime is not null'
            else:
                extra_where_str += 'where OastInTime is not null'
        if data_type == '2':
            if extra_where_str:
                extra_where_str += ' and OastOutTime is not null'
            else:
                extra_where_str += 'where OastOutTime is not null'
        if data_type == '3':  # 输送途中
            if extra_where_str:
                extra_where_str += ' and TaskState=1'
            else:
                extra_where_str += 'where TaskState=1'
        if data_type == '4':  # 正在烘
            if extra_where_str:
                extra_where_str += ' and TaskState=2'
            else:
                extra_where_str += 'where TaskState=2'
        if data_type == '5':  # 已经烘完
            if extra_where_str:
                extra_where_str += ' and TaskState=5'
            else:
                extra_where_str += 'where TaskState=5'
        if data_type == '6':  # 烘房小计
            if extra_where_str:
                extra_where_str += ' and TaskState in (2, 4, 5)'
            else:
                extra_where_str += 'where TaskState in (2, 4, 5)'
        if data_type == '7':  # 已出库
            if extra_where_str:
                extra_where_str += ' and TaskState in (3, 6)'
            else:
                extra_where_str += 'where TaskState in (3, 6)'
        if data_type == '8':  # 等待烘烤
            if extra_where_str:
                extra_where_str += ' and TaskState=4'
            else:
                extra_where_str += 'where TaskState=4'
        if st:
            if data_type == '1':  # 入箱托数
                if extra_where_str:
                    extra_where_str += " and OastInTime >= '{}'".format(st)
                else:
                    extra_where_str += "where OastInTime >= '{}'".format(st)
            elif data_type == '2':  # 出箱托数
                if extra_where_str:
                    extra_where_str += " and OastOutTime >= '{}'".format(st)
                else:
                    extra_where_str += "where OastOutTime >= '{}'".format(st)
            else:
                if extra_where_str:
                    extra_where_str += " and TaskStartTime >= '{}'".format(st)
                else:
                    extra_where_str += "where TaskStartTime >= '{}'".format(st)
        if et:
            if data_type == '1':  # 入箱托数
                if extra_where_str:
                    extra_where_str += " and OastInTime <= '{}'".format(et)
                else:
                    extra_where_str += "where OastInTime <= '{}'".format(et)
            elif data_type == '2':  # 出箱托数
                if extra_where_str:
                    extra_where_str += " and OastOutTime <= '{}'".format(et)
                else:
                    extra_where_str += "where OastOutTime <= '{}'".format(et)
            else:
                if extra_where_str:
                    extra_where_str += " and TaskStartTime <= '{}'".format(et)
                else:
                    extra_where_str += "where TaskStartTime <= '{}'".format(et)

        sql = """select
                OastNo,
                TaskState,
                ProductName,
                ProductNo,
                RFID,
                OastInTime,
                OastOutTime,
                OastStartTime,
                OastEntTime
            from dsp_OastTask {} order by OastNo OFFSET {} ROWS FETCH FIRST {} ROWS ONLY
            """.format(extra_where_str, (page-1)*page_size, page_size)
        sc = SqlClient(sql=sql, **self.DATABASE_CONF)
        temp = sc.all()
        result = []

        count_sql = 'select count(*) from dsp_OastTask {}'.format(extra_where_str)
        sc = SqlClient(sql=count_sql, **self.DATABASE_CONF)
        temp2 = sc.all()
        count = temp2[0][0]
        # 查询历史设定
        hf_set = HfBakeMaterialSet.objects.filter(delete_flag=False).values('material_name')\
            .annotate(max_temp=Max('temperature_set'), max_time=Max('bake_time', output_field=FloatField()))
        handle_hf_set = {i['material_name']: [i['max_temp'], i['max_time']] for i in hf_set}
        for item in temp:
            # 温度、时长设定值获取
            temperature_set, bake_time_set = handle_hf_set.get(item[2]) if handle_hf_set.get(item[2]) else ['', '']
            # 时长计算
            baking_begin = '' if not item[7] else item[7].strftime('%Y-%m-%d %H:%M:%S')
            baking_end = '' if not item[8] else item[8].strftime('%Y-%m-%d %H:%M:%S')
            if not baking_begin:
                baking_time = ''
            else:
                if not baking_end:
                    baking_time = round((datetime.datetime.now() - item[7]).total_seconds() / 3600, 2)
                else:
                    baking_time = round((item[8] - item[7]).total_seconds() / 3600, 2)
            result.append(
                {
                    'oven_no': item[0],
                    'status': item[1],
                    'material_name': item[2],
                    'material_no': item[3],
                    'pallet_no': item[4],
                    'baking_start_time': '' if not item[5] else item[5].strftime('%Y-%m-%d %H:%M:%S'),
                    'baking_end_time': '' if not item[6] else item[6].strftime('%Y-%m-%d %H:%M:%S'),
                    'baking_begin': baking_begin,
                    'baking_end': baking_end,
                    'baking_time': baking_time,
                    'temperature_set': temperature_set,
                    'bake_time_set': bake_time_set
                }
            )
        sc.close()
        return Response({'result': result, 'count': count})


@method_decorator([api_recorder], name="dispatch")
class HFInventoryLogView(APIView):
    # 权限共用烘房统计信息查询
    DATABASE_CONF = HF_CONF
    permission_classes = (IsAuthenticated, PermissionClass({'view': 'view_material_hf_summary'}))

    def export_xls(self, result):
        response = HttpResponse(content_type='application/vnd.ms-excel')
        filename = '物料出入库履历'
        response['Content-Disposition'] = u'attachment;filename= ' + filename.encode('gbk').decode(
            'ISO-8859-1') + '.xls'
        # 创建一个文件对象
        wb = xlwt.Workbook(encoding='utf8')
        # 创建一个sheet对象
        sheet = wb.add_sheet('出入库信息', cell_overwrite_ok=True)
        style = xlwt.XFStyle()
        style.alignment.wrap = 1

        columns = ['No', '类别', '烘箱编号', '状态', '物料名称', '物料编码', '批次号', '托盘号',
                   '入/出 烘房时间', '质检条码', '供应商', '单位', '单位重量(kg)', '件数']
        # 写入文件标题
        for col_num in range(len(columns)):
            sheet.write(0, col_num, columns[col_num])
            # 写入数据
        data_row = 1
        for i in result:
            sheet.write(data_row, 0, result.index(i) + 1)
            sheet.write(data_row, 1, i['order_type'])
            sheet.write(data_row, 2, i['oven_no'])
            sheet.write(data_row, 3, i['status'])
            sheet.write(data_row, 4, i['material_name'])
            sheet.write(data_row, 5, i['material_no'])
            sheet.write(data_row, 6, i['batch_no'])
            sheet.write(data_row, 7, i['pallet_no'])
            sheet.write(data_row, 8, i['baking_start_time'] if i['order_type'] == '入烘房' else i['baking_end_time'])
            sheet.write(data_row, 9, i['lot_no'])
            sheet.write(data_row, 10, i['supplier'])
            sheet.write(data_row, 11, i['unit'])
            sheet.write(data_row, 12, i['weight'])
            sheet.write(data_row, 13, i['piece_count'])
            data_row = data_row + 1
        # 写出到IO
        output = BytesIO()
        wb.save(output)
        # 重新定位到开始
        output.seek(0)
        response.write(output.getvalue())
        return response

    def get(self, request):
        st = self.request.query_params.get('st')  # 开始时间
        et = self.request.query_params.get('et')  # 结束时间
        material_no = self.request.query_params.get('material_no')  # 物料编码
        material_name = self.request.query_params.get('material_name')  # 物料名称
        pallet_no = self.request.query_params.get('pallet_no')  # 托盘号
        lot_no = self.request.query_params.get('lot_no')  # 条码
        page = int(self.request.query_params.get('page', 1))
        page_size = int(self.request.query_params.get('page_size', 10))
        inventory_type = self.request.query_params.get('inventory_type', '入烘房')
        export = self.request.query_params.get('export')
        if inventory_type == '入烘房':
            extra_where_str = 'where OastInTime is not null'
            if st:
                extra_where_str += " and OastInTime >= '{}'".format(st)
            if et:
                extra_where_str += " and OastInTime <= '{}'".format(et)
        else:
            extra_where_str = 'where OastOutTime is not null'
            if st:
                extra_where_str += " and OastOutTime >= '{}'".format(st)
            if et:
                extra_where_str += " and OastOutTime <= '{}'".format(et)
        if material_name:
            extra_where_str += " and ProductName like N'%{}%'".format(material_name.strip())
        if material_no:
            extra_where_str += " and ProductNo like '%{}%'".format(material_no.strip())
        if pallet_no:
            extra_where_str += " and RFID = '{}'".format(pallet_no.strip())
        if lot_no:
            last_out_log = MaterialOutHistory.objects.using('wms').filter(lot_no=lot_no.strip()).order_by('id').last()
            if not last_out_log:
                return Response({})
            extra_where_str += " and MissionID = '{}'".format(last_out_log.order_no.strip())
        if not export:
            limit_str = 'OFFSET {} ROWS FETCH FIRST {} ROWS ONLY'.format((page-1)*page_size, page_size)
        else:
            limit_str = ''
        sql = """select
                OastNo,
                TaskState,
                ProductName,
                ProductNo,
                RFID,
                OastInTime,
                OastOutTime,
                MissionID
            from dsp_OastTask {} order by OastInTime DESC {}
            """.format(extra_where_str, limit_str)
        sc = SqlClient(sql=sql, **self.DATABASE_CONF)
        temp = sc.all()
        result = []
        out_task = MaterialOutHistory.objects.using('wms').filter(
            order_no__in=[item[7] for item in temp]).values(
            'batch_no', 'supplier', 'unit', 'lot_no', 'piece_count', 'weight', 'order_no')
        out_task_dict = {item['order_no']: item for item in out_task}
        status_dict = {1: '入库中', 2: '烘烤运行中', 3: '出库中', 4: '等待烘烤', 5: '等待出库', 6: '已出库'}
        for item in temp:
            data = {'order_type': '出烘房' if inventory_type == '出库' else '入烘房',
                    'oven_no': item[0],
                    'status': status_dict.get(item[1]),
                    'material_name': item[2],
                    'material_no': item[3],
                    'pallet_no': item[4],
                    'baking_start_time': '' if not item[5] else item[5].strftime('%Y-%m-%d %H:%M:%S'),
                    'baking_end_time': '' if not item[6] else item[6].strftime('%Y-%m-%d %H:%M:%S'),
                    'batch_no': '',
                    'supplier': '',
                    'unit': '',
                    'lot_no': '',
                    'piece_count': '',
                    'weight': '',
                    'order_no': ''
                }
            if out_task:
                data.update(out_task_dict.get(item[7], {}))
            result.append(data)
        if export:
            return self.export_xls(result)
        count_sql = 'select count(*) from dsp_OastTask {}'.format(extra_where_str)
        sc = SqlClient(sql=count_sql, **self.DATABASE_CONF)
        temp2 = sc.all()
        count = temp2[0][0]
        sc.close()
        return Response({'result': result, 'count': count})


@method_decorator([api_recorder], name="dispatch")
class HFRealStatusView(APIView):
    permission_classes = (IsAuthenticated, PermissionClass({'view': 'view_material_hf_real_data',
                                                            'add': 'outbound_material_hf_real_data'}))
    DATABASE_CONF = HF_CONF

    def get(self, request):
        data_type = self.request.query_params.get('type')
        page = int(self.request.query_params.get('page', 1))
        page_size = int(self.request.query_params.get('page_size', 10))
        response_data = {}
        try:
            if data_type == '0':  # 烘箱状态
                hf = HFSystem()
                hf_info = hf.get_hf_info()
                # 非运行中不展示开始时间和时长
                for i in hf_info:
                    if i['OastState'] != 2:
                        i.update({'OastStartTime': '', 'OastServiceTime': ''})
                response_data['results'] = hf_info
            elif data_type == '1':  # 任务列表
                TaskState = self.request.query_params.get('TaskState')
                ProductName = self.request.query_params.get('ProductName')
                RFID = self.request.query_params.get('RFID')
                OastNo = self.request.query_params.get('OastNo')
                RoadWay = self.request.query_params.get('RoadWay')
                extra_where_str = 'where TaskState != 6'
                if TaskState:
                    extra_where_str += " and TaskState = {}".format(TaskState)
                if ProductName:
                    extra_where_str += " and ProductName like N'%{}%'".format(ProductName)
                if RFID:
                    extra_where_str += " and RFID like '%{}%'".format(RFID)
                if OastNo:
                    extra_where_str += " and OastNo = {}".format(OastNo)
                if RoadWay:
                    extra_where_str += " and RoadWay = {}".format(RoadWay)
                sql = """select F_Id, TaskState, ProductName, RFID, TaskStartTime, OastInTime, OastOutTime, 
                                 OastStartTime, OastEntTime, TaskEntTime, RoadWay, OastNo from dsp_OastTask {} 
                                 order by -F_Id """.format(extra_where_str)
                sc = SqlClient(sql=sql, **self.DATABASE_CONF)
                res = sc.all()
                all_pages = math.ceil(len(res) / page_size)
                data = res[(page - 1) * page_size: page * page_size] if all_pages > page else res[
                                                                                              (page - 1) * page_size:]
                hf_info = []
                for i in data:
                    run_time = None
                    if i[7]:
                        now_date = datetime.datetime.now()
                        end_time = now_date if not i[8] else i[8]
                        diff_time = end_time - i[7]
                        h_time, m_time = divmod(int(diff_time.total_seconds()) // 60, 60)
                        run_time = f'{h_time}小时{m_time}分钟'
                    hf_info.append({'F_Id': i[0],
                                    'TaskState': i[1],
                                    'ProductName': i[2],
                                    'RFID': i[3],
                                    'OastNo': i[11],
                                    'TaskStartTime': '' if not i[4] else i[4].strftime("%Y-%m-%d %H:%M:%S"),
                                    'OastInTime': '' if not i[5] else i[5].strftime("%Y-%m-%d %H:%M:%S"),
                                    'OastOutTime': '' if not i[6] else i[6].strftime("%Y-%m-%d %H:%M:%S"),
                                    'RoadWay': i[10],
                                    'TaskEntTime': '' if not i[9] else i[9].strftime("%Y-%m-%d %H:%M:%S"),
                                    'Runtime': run_time})
                response_data.update({'all_pages': all_pages, 'total_data': len(res), 'results': hf_info})
            else:  # 待入箱列表
                sql = f"""select F_Id, ProductName, RFID, TaskStartTime, RoadWay from dsp_OastTask where OastNo = 0
                          order by -F_id"""
                sc = SqlClient(sql=sql, **self.DATABASE_CONF)
                res = sc.all()
                all_pages = math.ceil(len(res) / page_size)
                data = res[(page - 1) * page_size: page * page_size] if all_pages > page else res[
                                                                                              (page - 1) * page_size:]
                hf_info = []
                for i in data:
                    hf_info.append(
                        {'F_Id': i[0],
                         'ProductName': i[1],
                         'RFID': i[2],
                         'TaskStartTime': '' if not i[3] else i[3].strftime("%Y-%m-%d %H:%M:%S"),
                         'RoadWay': i[4]})
                response_data.update({'all_pages': all_pages, 'total_data': len(res), 'results': hf_info})
        except Exception as e:
            raise ValidationError(e.args[0])
        return Response(response_data)

    @atomic
    def post(self, request):
        """烘箱手动出库 OastNo: '1' """
        data = self.request.data
        try:
            hf = HFSystem()
            res = hf.manual_out_hf(data)
            # 更新履历
            hf_log = HfBakeLog.objects.filter(oast_no=data['OastNo'], actual_temperature__isnull=True, actual_bake_time__isnull=True).last()
            hf_log.actual_temperature = res.get('ShiJiT')
            hf_log.actual_bake_time = res.get('ShiJiTime')
            hf_log.last_updated_date = datetime.datetime.now()
            hf_log.save()
        except Exception as e:
            raise ValidationError(e.args[0])
        else:
            return Response(res)


@method_decorator([api_recorder], name="dispatch")
class HFForceHandleView(APIView):

    @atomic
    def post(self, request):
        data = self.request.data
        user_name = self.request.user.username
        opera_type = data.pop('opera_type', 3)
        client = data.pop('client', False)
        try:
            hf = HFSystem()
            if opera_type == 1:  # 强制出料
                data['OastType'] = 'E'
                res = hf.force_bake(data)
            elif opera_type == 2:  # 强制烘烤
                # 查询设定值
                OastMatiles = data.pop('OastMatiles')
                material_list = set([i.get('ProductName') for i in OastMatiles])
                bake_set_target = HfBakeMaterialSet.objects.filter(material_name__in=material_list, delete_flag=False)
                if not bake_set_target:
                    if client:
                        return response(success=False, message='未找到物料设置的标准温度与时长')
                    else:
                        raise ValidationError('未找到物料设置的标准温度与时长')
                bake_set = bake_set_target.aggregate(standard_temp=Max('temperature_set'), standard_bake_time=Max('bake_time', output_field=FloatField()))
                standard_temp, standard_bake_time = bake_set.get('standard_temp'), bake_set.get('standard_bake_time')
                data.update({'OastType': 'S', 'Temperature': standard_temp, 'Duration': standard_bake_time})
                if client:
                    data['client'] = client
                res = hf.force_bake(data)
                # 增加履历
                HfBakeLog.objects.create(**{'oast_no': data.get('OastNo'), 'material_name': ','.join(material_list),
                                            'temperature_set': bake_set['standard_temp'], 'opera_username': user_name if user_name else 'wcs',
                                            'bake_time': bake_set['standard_bake_time']})
            else:
                raise ValidationError('未知操作: 只支持强制出料与强制烘烤')
        except Exception as e:
            if client:
                return response(success=False, message=e.args[0])
            else:
                raise ValidationError(e.args[0])
        else:
            if client:
                return response(success=True, message='请求成功')
            else:
                return Response({"results": f"强制{'出料' if opera_type == 1 else '烘烤'}操作成功"})


@method_decorator([api_recorder], name="dispatch")
class HFConfigSetView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        """获取原材料烘烤温度以及时长设置"""
        query_set = HfBakeMaterialSet.objects.filter(delete_flag=False).order_by('created_date')
        return Response({'results': list(query_set.values())})

    @atomic
    def post(self, request):
        data = self.request.data.get('set_data')
        delete_data = self.request.data.get('delete_data')
        user_name = self.request.user.username
        repeat_material_name = []
        # 删除物料
        if delete_data:
            HfBakeMaterialSet.objects.filter(id=delete_data).update(**{'delete_flag': True})
            return Response('删除设置成功')
        for s_data in data:
            rid, material_name, temperature_set, bake_time = s_data.get('id'),  s_data.get('material_name'), \
                                                             s_data.get('temperature_set'),  s_data.get('bake_time')
            if material_name in repeat_material_name:
                raise ValidationError(f'参数异常: {material_name}重复')
            if not all([material_name, temperature_set, bake_time]):
                raise ValidationError(f'参数异常: 物料名称、烘烤温度、烘烤时长不可为空')
            if temperature_set < 0 or temperature_set > 100 or bake_time < 0 or bake_time > 200:
                raise ValidationError(f'检查{material_name}设置[烘烤温度[0-100], 烘烤时长[0-200]')
            common_data = {'material_name': material_name, 'bake_time': bake_time, 'temperature_set': temperature_set,
                           'opera_username': user_name}
            if rid:  # 存在id则为修改
                common_data.update({'last_updated_date': datetime.datetime.now()})
                HfBakeMaterialSet.objects.filter(id=rid).update(**common_data)
            else:
                if not HfBakeMaterialSet.objects.filter(material_name=material_name, delete_flag=False).exists():
                    HfBakeMaterialSet.objects.create(**common_data)
                else:
                    raise ValidationError(f'{material_name}已经存在')
            repeat_material_name.append(material_name)
        return Response('设置成功')


@method_decorator([api_recorder], name="dispatch")
class ProductExpireListView(APIView):
    permission_classes = (IsAuthenticated, PermissionClass({'view': 'view_product_expire_query'}))

    def get(self, request):
        expire_days = self.request.query_params.get('expire_days')
        if not expire_days:
            expire_days = 0
        expire_days = int(expire_days)
        warehouse_name = self.request.query_params.get('warehouse_name')
        stage = self.request.query_params.get('stage')
        quality_level = self.request.query_params.get('quality_level')
        page = self.request.query_params.get('page', 1)
        page_size = self.request.query_params.get('page_size', 15)
        st = (int(page) - 1) * int(page_size)
        et = int(page) * int(page_size)
        filter_kwargs = {}
        now_time = datetime.datetime.now()
        if stage:
            filter_kwargs['material_no__icontains'] = '-{}'.format(stage)
        if quality_level:
            filter_kwargs['quality_level'] = quality_level
        if warehouse_name == '混炼胶库':
            product_data = BzFinalMixingRubberInventory.objects.using('bz').filter(**filter_kwargs).values(
                'material_no', 'in_storage_time', 'qty', 'total_weight', 'quality_level', 'store_name')
        elif warehouse_name == '终炼胶库':
            product_data = BzFinalMixingRubberInventoryLB.objects.using('lb').filter(store_name='炼胶库').filter(**filter_kwargs).values(
                'material_no', 'in_storage_time', 'qty', 'total_weight', 'quality_level', 'store_name')
        else:
            m_data = list(BzFinalMixingRubberInventory.objects.using('bz').filter(**filter_kwargs).values(
                'material_no', 'in_storage_time', 'qty', 'total_weight', 'quality_level', 'store_name'))
            f_data = list(BzFinalMixingRubberInventoryLB.objects.using('lb').filter(store_name='炼胶库').filter(**filter_kwargs).values(
                'material_no', 'in_storage_time', 'qty', 'total_weight', 'quality_level', 'store_name'))
            product_data = m_data + f_data

        product_validity_dict = dict(MaterialAttribute.objects.filter(
            period_of_validity__isnull=False
        ).values_list('material__material_no', 'period_of_validity'))
        ret = {}
        for m in product_data:
            material_no = m['material_no'].strip()
            quality_level = m['quality_level'].strip()
            store_name = '混炼胶库' if m['store_name'] == '立体库' else '终炼胶库'
            key = material_no + '-' + quality_level + store_name
            period_of_validity = product_validity_dict.get(material_no, 0)
            if period_of_validity:
                already_inventory_days = (now_time - m['in_storage_time']).total_seconds() / 60 / 60 / 24
                if period_of_validity - already_inventory_days <= expire_days:
                    expire_flag = False
                    yj_flag = False
                    if already_inventory_days > period_of_validity:
                        expire_flag = True
                    if period_of_validity - already_inventory_days <= 3:
                        yj_flag = True
                    dj_flag = False
                    if quality_level == '待检品':
                        if already_inventory_days > 3:
                            dj_flag = True
                    if key in ret:
                        if not ret[key]['expire_flag']:
                            ret[key]['expire_flag'] = expire_flag
                        if not ret[key]['dj_flag']:
                            ret[key]['dj_flag'] = dj_flag
                        if not ret[key]['yj_flag']:
                            ret[key]['yj_flag'] = yj_flag
                        ret[key]['qty'] += m['qty']
                        ret[key]['total_weight'] += m['total_weight']
                    else:
                        ret[key] = {'material_no': material_no,
                                    'qty': m['qty'],
                                    'total_weight': m['total_weight'],
                                    'quality_status': quality_level,
                                    'warehouse_name': store_name,
                                    'period_of_validity': period_of_validity,
                                    'expire_flag': expire_flag,
                                    'dj_flag': dj_flag,
                                    'yj_flag': yj_flag,
                                    }
        temp = list(ret.values())
        count = len(temp)
        data = temp[st:et]
        total_weight = sum([i['qty'] for i in temp])
        total_quantity = sum([i['total_weight'] for i in temp])
        return Response({'results': data, "count": count, 'total_weight': total_weight, 'total_quantity': total_quantity})


@method_decorator([api_recorder], name="dispatch")
class ProductExpireDetailView(APIView):
    permission_classes = (IsAuthenticated, PermissionClass({'view': 'view_product_expire_query'}))
    EXPORT_FIELDS_DICT = {'库区': 'store_name',
                            '胶料名称': 'material_no',
                            '追踪码': 'lot_no',
                            '托盘号': 'container_no',
                            '库存位': 'location',
                            '机台': 'equip_no',
                            '车次': 'memo',
                            '重量（kg）': 'total_weight',
                            '品质状态': 'quality_level',
                            '入库时间': 'in_storage_time',
                            '有效期至': 'expire_time',
                            '剩余有效天数': 'left_days'}
    FILE_NAME = '库位明细'

    def get(self, request):
        expire_days = self.request.query_params.get('expire_days')
        if not expire_days:
            expire_days = 0
        expire_days = int(expire_days)
        warehouse_name = self.request.query_params.get('warehouse_name')
        material_no = self.request.query_params.get('material_no')
        quality_status = self.request.query_params.get('quality_status')
        export = self.request.query_params.get('export')
        page = self.request.query_params.get('page', 1)
        page_size = self.request.query_params.get('page_size', 15)
        st = (int(page) - 1) * int(page_size)
        et = int(page) * int(page_size)
        filter_kwargs = {}
        if material_no:
            filter_kwargs['material_no'] = material_no
        if quality_status:
            filter_kwargs['quality_level'] = quality_status
        if warehouse_name == '混炼胶库':
            product_data = BzFinalMixingRubberInventory.objects.using('bz').filter(**filter_kwargs).values()
        elif warehouse_name == '终炼胶库':
            product_data = BzFinalMixingRubberInventoryLB.objects.using('lb').filter(store_name='炼胶库').filter(
                **filter_kwargs).values()
        else:
            m_data = list(BzFinalMixingRubberInventory.objects.using('bz').filter(**filter_kwargs).values())
            f_data = list(BzFinalMixingRubberInventoryLB.objects.using('lb').filter(store_name='炼胶库').filter(**filter_kwargs).values())
            product_data = m_data + f_data

        product_validity_dict = dict(MaterialAttribute.objects.filter(
            period_of_validity__isnull=False
        ).values_list('material__material_no', 'period_of_validity'))
        temp = []
        now_time = datetime.datetime.now()
        for m in product_data:
            material_no = m['material_no'].strip()
            period_of_validity = product_validity_dict.get(material_no)
            in_storage_time = m['in_storage_time']
            if period_of_validity:
                if (period_of_validity * 24 * 60 * 60 - (
                        now_time - m['in_storage_time']).total_seconds()) <= expire_days * 24 * 60 * 60:
                    expire_date = in_storage_time + datetime.timedelta(days=period_of_validity)
                    m['expire_time'] = expire_date.strftime("%Y-%m-%d %H:%M:%S")
                    m['in_storage_time'] = in_storage_time.strftime("%Y-%m-%d %H:%M:%S")
                    m['left_days'] = expire_date.__sub__(now_time).days
                    store_name = '混炼胶库' if m['store_name'] == '立体库' else '终炼胶库'
                    m['store_name'] = store_name
                    m['equip_no'] = m['bill_id'][-3:]
                    temp.append(m)
        if export:
            return gen_template_response(self.EXPORT_FIELDS_DICT, temp, self.FILE_NAME)
        count = len(temp)
        data = temp[st:et]
        for i in data:
            if i['lot_no']:
                deal_result = MaterialDealResult.objects.filter(
                    lot_no=i['lot_no']).first()
                if deal_result:
                    if deal_result.deal_user:
                        i['deal_suggestion'] = deal_result.deal_suggestion
                    else:
                        i['deal_suggestion'] = 'PASS' if deal_result.test_result == 'PASS' else None
        total_weight = sum([i['total_weight'] for i in temp])
        total_quantity = sum([i['qty'] for i in temp])
        return Response(
            {'results': data, "count": count, 'total_weight': total_weight, 'total_quantity': total_quantity})

#
# @method_decorator([api_recorder], name="dispatch")
# class ProductInOutHistoryView(APIView):
#     permission_classes = (IsAuthenticated, PermissionClass({'view': 'view_in_out_history'}))
#     EXPORT_FIELDS_DICT = {'胶料名称': 'product_no',
#                           '机台号': 'equip_no',
#                           '车次': 'memo',
#                           '重量(kg)': 'weight',
#                           '托盘号': 'pallet_no',
#                           '巷道': 'location',
#                           '质检条码': 'lot_no',
#                           '入库单号': 'inbound_order_no',
#                           '入库发起时间': 'inbound_time',
#                           '出库单号': 'outbound_order_no',
#                           '出库发起时间': 'outbound_time',
#                           '出库发起人': 'outbound_user',
#                           }
#     FILE_NAME = '出入库履历'
#
#     def get(self, request):
#         warehouse_name = self.request.query_params.get('warehouse_name')
#         in_st = self.request.query_params.get('in_st')
#         in_et = self.request.query_params.get('in_et')
#         out_st = self.request.query_params.get('out_st')
#         out_et = self.request.query_params.get('out_et')
#         tunnel = self.request.query_params.get('tunnel')
#         product_no = self.request.query_params.get('product_no')
#         order_no = self.request.query_params.get('order_no')
#         pallet_no = self.request.query_params.get('pallet_no')
#         lot_no = self.request.query_params.get('lot_no')
#         equip_no = self.request.query_params.get('equip_no')
#         page = int(self.request.query_params.get('page', 1))
#         page_size = int(self.request.query_params.get('page_size', 10))
#         export = self.request.query_params.get('export')
#         if not warehouse_name:
#             raise ValidationError('请选择库区！')
#         if export:
#             if not all([out_st, out_et]):
#                 raise ValidationError('请选择出库时间范围不超过一周进行导出！')
#             st = datetime.datetime.strptime(out_st, "%Y-%m-%d %H:%M:%S")
#             et = datetime.datetime.strptime(out_et, "%Y-%m-%d %H:%M:%S")
#             if (et - st).total_seconds() / 60 / 60 / 24 > 7:
#                 raise ValidationError('出库时间范围不得超过一周！')
#         if warehouse_name == '混炼胶库':
#             database_conf = {'host': DATABASES['bz']['HOST'],
#                              'user': DATABASES['bz']['USER'],
#                              'password': DATABASES['bz']['PASSWORD'],
#                              'database': DATABASES['bz']['NAME']}
#         else:
#             database_conf = {'host': DATABASES['lb']['HOST'],
#                              'user': DATABASES['lb']['USER'],
#                              'password': DATABASES['lb']['PASSWORD'],
#                              'database': DATABASES['lb']['NAME']}
#         extra_where_str = ""
#         pagination_str = "OFFSET {} ROWS FETCH FIRST {} ROWS ONLY".format((page-1)*page_size, page_size)
#         if in_st:
#             extra_where_str += "where a.LTIME>='{}'".format(in_st)
#         if in_et:
#             if extra_where_str:
#                 extra_where_str += " and a.LTIME<='{}'".format(in_et)
#             else:
#                 extra_where_str += "where a.LTIME<='{}'".format(in_et)
#         if out_st:
#             if extra_where_str:
#                 extra_where_str += " and b.DEALTIME>='{}'".format(out_st)
#             else:
#                 extra_where_str += "where b.DEALTIME>='{}'".format(out_st)
#         if out_et:
#             if extra_where_str:
#                 extra_where_str += " and b.DEALTIME<='{}'".format(out_et)
#             else:
#                 extra_where_str += "where b.DEALTIME<='{}'".format(out_et)
#         if tunnel:
#             if extra_where_str:
#                 extra_where_str += " and a.CID like '{}%'".format(tunnel)
#             else:
#                 extra_where_str += "where a.CID like '{}%'".format(tunnel)
#         if product_no:
#             if extra_where_str:
#                 extra_where_str += " and a.MATNAME = '{}'".format(product_no)
#             else:
#                 extra_where_str += "where a.MATNAME = '{}'".format(product_no)
#         if order_no:
#             if extra_where_str:
#                 extra_where_str += " and a.BILLID like '%{}%' or b.BILLID like '%{}%'".format(order_no, order_no)
#             else:
#                 extra_where_str += "where a.BILLID like '%{}%' or b.BILLID like '%{}%'".format(order_no, order_no)
#         if pallet_no:
#             if extra_where_str:
#                 extra_where_str += " and a.PALLETID like '%{}%'".format(pallet_no)
#             else:
#                 extra_where_str += "where a.PALLETID like '%{}%'".format(pallet_no)
#         if lot_no:
#             if extra_where_str:
#                 extra_where_str += " and a.LotNo like '%{}%'".format(lot_no)
#             else:
#                 extra_where_str += "where a.LotNo like '%{}%'".format(lot_no)
#         if equip_no:
#             if extra_where_str:
#                 extra_where_str += " and a.LotNo like '%{}%'".format(equip_no)
#             else:
#                 extra_where_str += "where a.LotNo like '%{}%'".format(equip_no)
#         if export:
#             pagination_str = ""
#         sql = """select
#        a.LotNo,
#        a.BILLID,
#        a.LTIME,
#        b.BILLID,
#        b.OutUser,
#        b.DEALTIME,
#        a.CID,
#        a.PALLETID,
#        a.MATNAME,
#        a.NUM,
#        a.SWEIGHT,
#        b.Lot_no,
#        b.CID,
#        b.PALLETID,
#        b.MID,
#        b.CarNum,
#        b.Weight
# from v_ASRS_LOG_IN_OPREATE_MESVIEW a
# left join v_ASRS_TO_MES_RE_MESVIEW b on a.LotNo=b.Lot_no and a.PALLETID=b.PALLETID and a.MATNAME=b.MID
# {} order by a.LTIME desc {}""".format(extra_where_str, pagination_str)
#         sc = SqlClient(sql=sql, **database_conf)
#         temp = sc.all()
#         result = []
#         count_sql = """select
#         count(*)
#         from v_ASRS_LOG_IN_OPREATE_MESVIEW a
#         left join v_ASRS_TO_MES_RE_MESVIEW b on a.LotNo=b.Lot_no and a.PALLETID=b.PALLETID and a.MATNAME=b.MID {}
#         """.format(extra_where_str)
#         sc = SqlClient(sql=count_sql, **database_conf)
#         temp2 = sc.all()
#         count = temp2[0][0]
#         outbound_order_nos = [i[3] for i in temp]
#         outbound_order_dict = dict(OutBoundDeliveryOrderDetail.objects.filter(
#             order_no__in=outbound_order_nos).values_list('order_no', 'created_user__username'))
#         lot_nos = [i[0] for i in temp]
#         lot_nos_data = PalletFeedbacks.objects.filter(lot_no__in=lot_nos).values('lot_no', 'begin_trains', 'end_trains')
#         lot_nos_dict = {i['lot_no']: '{}-{}'.format(i['begin_trains'], i['end_trains']) for i in lot_nos_data}
#         for item in temp:
#             try:
#                 lot_no = item[0].strip() if item[0] else item[11].strip()
#                 equip = lot_no[4:7]
#             except Exception:
#                 equip = ""
#                 lot_no = ""
#             result.append(
#                 {
#                     'lot_no': lot_no,
#                     'inbound_order_no': item[1],
#                     'inbound_time': '' if not item[2] else item[2].strftime('%Y-%m-%d %H:%M:%S'),
#                     'outbound_order_no': item[3],
#                     'outbound_user': outbound_order_dict.get(item[3], ''),
#                     'outbound_time': '' if not item[5] else item[5].strftime('%Y-%m-%d %H:%M:%S'),
#                     'location': item[6] if item[6] else item[12],
#                     'pallet_no': item[7] if item[7] else item[13],
#                     'product_no': item[8] if item[8] else item[14],
#                     'qty': item[9] if item[9] else item[15],
#                     'weight': item[10] if item[10] else item[16],
#                     'equip_no': equip if equip.startswith('Z') else '',
#                     'memo': lot_nos_dict.get(lot_no, '')
#                 }
#             )
#         sc.close()
#         if export:
#             return gen_template_response(self.EXPORT_FIELDS_DICT, result, self.FILE_NAME)
#         return Response({'result': result, 'count': count})


@method_decorator([api_recorder], name="dispatch")
class ProductInOutHistoryView(ListAPIView):
    permission_classes = (IsAuthenticated, PermissionClass({'view': 'view_in_out_history'}))
    EXPORT_FIELDS_DICT = {'胶料名称': 'product_no',
                          '机台号': 'equip_no',
                          '车次': 'memo',
                          '重量(kg)': 'weight',
                          '托盘号': 'pallet_no',
                          '巷道': 'location',
                          '质检条码': 'lot_no',
                          '入库单号': 'inbound_order_no',
                          '入库发起时间': 'inbound_time',
                          '出库单号': 'outbound_order_no',
                          '出库发起时间': 'outbound_time',
                          '出库发起人': 'outbound_user',
                          }
    FILE_NAME = '出入库履历'
    queryset = InventoryLog.objects.all()
    serializer_class = ProductInOutHistorySerializer

    def list(self, request, *args, **kwargs):
        warehouse_name = self.request.query_params.get('warehouse_name')
        in_st = self.request.query_params.get('in_st')
        in_et = self.request.query_params.get('in_et')
        out_st = self.request.query_params.get('out_st')
        out_et = self.request.query_params.get('out_et')
        tunnel = self.request.query_params.get('tunnel')
        product_no = self.request.query_params.get('product_no')
        task_no = self.request.query_params.get('task_no')
        order_no = self.request.query_params.get('order_no')
        pallet_no = self.request.query_params.get('pallet_no')
        lot_no = self.request.query_params.get('lot_no')
        equip_no = self.request.query_params.get('equip_no')
        export = self.request.query_params.get('export')
        if not warehouse_name:
            raise ValidationError('请选择库区！')
        if warehouse_name == '混炼胶库':
            if task_no or order_no:
                query_set = MixGumOutInventoryLog.objects.using('bz').order_by('-start_time')
                inout_type = 'out'
            elif not in_st and not in_et and not out_st and not out_et:
                query_set = MixGumInInventoryLog.objects.using('bz').order_by('-start_time')
                inout_type = 'in'
            elif all([in_st, in_et, out_st, out_et]):
                query_set = MixGumInInventoryLog.objects.using('bz').order_by('-start_time')
                inout_type = 'in'
            elif all([in_st, in_et]):
                query_set = MixGumInInventoryLog.objects.using('bz').order_by('-start_time')
                inout_type = 'in'
            elif all([out_st, out_et]):
                query_set = MixGumOutInventoryLog.objects.using('bz').order_by('-start_time')
                inout_type = 'out'
            else:
                raise ValidationError('参数错误')
        else:
            if task_no or order_no:
                query_set = FinalGumOutInventoryLog.objects.using('lb').filter(Q(location__startswith=1) |
                                                                               Q(location__startswith=2) |
                                                                               Q(location__startswith=3) |
                                                                               Q(location__startswith=4)
                                                                               ).order_by('-start_time')
                inout_type = 'out'
            elif not in_st and not in_et and not out_st and not out_et:
                query_set = FinalGumInInventoryLog.objects.using('lb').filter(Q(location__startswith=1) |
                                                                              Q(location__startswith=2) |
                                                                              Q(location__startswith=3) |
                                                                              Q(location__startswith=4)
                                                                              ).order_by('-start_time')
                inout_type = 'in'
            elif all([in_st, in_et, out_st, out_et]):
                query_set = FinalGumInInventoryLog.objects.using('lb').filter(Q(location__startswith=1) |
                                                                              Q(location__startswith=2) |
                                                                              Q(location__startswith=3) |
                                                                              Q(location__startswith=4)
                                                                              ).order_by('-start_time')
                inout_type = 'in'
            elif all([in_st, in_et]):
                query_set = FinalGumInInventoryLog.objects.using('lb').filter(Q(location__startswith=1) |
                                                                              Q(location__startswith=2) |
                                                                              Q(location__startswith=3) |
                                                                              Q(location__startswith=4)
                                                                              ).order_by('-start_time')
                inout_type = 'in'
            elif all([out_st, out_et]):
                query_set = FinalGumOutInventoryLog.objects.using('lb').filter(Q(location__startswith=1) |
                                                                               Q(location__startswith=2) |
                                                                               Q(location__startswith=3) |
                                                                               Q(location__startswith=4)
                                                                               ).order_by('-start_time')
                inout_type = 'out'
            else:
                raise ValidationError('参数错误')
        filter_dict = {}
        if tunnel:
            filter_dict.update(location__startswith=tunnel)
        if product_no:
            filter_dict.update(material_no=product_no)
        if task_no:
            filter_dict.update(order_no=task_no)
        if in_st and in_et:
            filter_dict.update(start_time__gte=in_st)
            filter_dict.update(start_time__lte=in_et)
        elif out_st and out_et:
            filter_dict.update(start_time__gte=out_st)
            filter_dict.update(start_time__lte=out_et)
        if order_no:
            order = OutBoundDeliveryOrder.objects.filter(order_no=order_no).first()
            if not order:
                return Response({})
            task_nos = list(order.outbound_delivery_details.values_list('order_no', flat=True))
            if not task_nos:
                return Response({})
            filter_dict.update(order_no__in=task_nos)
        if lot_no:
            filter_dict.update(lot_no=lot_no)
        if pallet_no:
            filter_dict.update(pallet_no=pallet_no)
        if equip_no:
            filter_dict.update(order_no__endswith=equip_no)
        queryset = query_set.filter(**filter_dict)
        if export:
            if not all([out_st, out_et]):
                raise ValidationError('请选择出库时间范围不超过一周进行导出！')
            st = datetime.datetime.strptime(out_st, "%Y-%m-%d %H:%M:%S")
            et = datetime.datetime.strptime(out_et, "%Y-%m-%d %H:%M:%S")
            if (et - st).total_seconds() / 60 / 60 / 24 > 7:
                raise ValidationError('出库时间范围不得超过一周！')
            data = ProductInOutHistorySerializer(queryset, many=True, context={'ware_house': warehouse_name, "inout_type": inout_type}).data
            return gen_template_response(self.EXPORT_FIELDS_DICT, data, self.FILE_NAME)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ProductInOutHistorySerializer(page, many=True, context={'ware_house': warehouse_name, "inout_type": inout_type})
            s_data = serializer.data
            lot_nos = [i['lot_no'] for i in s_data]
            locked_data = ProductInventoryLocked.objects.filter(
                lot_no__in=lot_nos).values('lot_no', 'gy_locked_user', 'kj_locked_user',
                                           'gy_locked_reason', 'kj_locked_reason',
                                           'gy_unlocked_user', 'kj_unlocked_user')
            locked_dict = {i['lot_no']: i for i in locked_data}
            for item in s_data:
                locked_dict_data = locked_dict.get(item['lot_no'])
                if locked_dict_data:
                    item['locked_user'] = locked_dict_data['gy_locked_user'] or locked_dict_data['kj_locked_user']
                    item['locked_reason'] = locked_dict_data['gy_locked_reason'] or locked_dict_data['kj_locked_reason']
                    item['unlocked_user'] = locked_dict_data['gy_unlocked_user'] or locked_dict_data['kj_unlocked_user']
            return self.get_paginated_response(serializer.data)

        serializer = ProductInOutHistorySerializer(queryset, many=True, context={'ware_house': warehouse_name, "inout_type": inout_type})
        return Response(serializer.data)


@method_decorator([api_recorder], name="dispatch")
class OutboundProductInfo(APIView):

    def get(self, request):
        warehouse = self.request.query_params.get('warehouse')
        factory_date = self.request.query_params.get('factory_date')
        classes = self.request.query_params.get('classes')
        equip_no = self.request.query_params.get('equip_no')
        if not all([factory_date, classes, equip_no, warehouse]):
            raise ValidationError('必填参数缺失！')
        lot_nos = list(PalletFeedbacks.objects.filter(
            factory_date=factory_date,
            classes=classes,
            equip_no=equip_no).values_list('lot_no', flat=True))
        if warehouse == '混炼胶库':
            stock_lot_nos = list(
                BzFinalMixingRubberInventory.objects.using('bz').filter(
                    lot_no__in=lot_nos).values_list('lot_no', flat=True))
        else:
            stock_lot_nos = list(
                BzFinalMixingRubberInventoryLB.objects.using('lb').filter(lot_no__in=lot_nos).values_list('lot_no', flat=True))

        pallet_info = list(PalletFeedbacks.objects.filter(lot_no__in=stock_lot_nos).values('product_no').annotate(max_trains=Max('end_trains'),
                                                          min_trains=Min('begin_trains')))
        return Response(pallet_info)


@method_decorator([api_recorder], name="dispatch")
class WMSMnLevelSearchView(APIView):

    def get(self, request):
        task_no = self.request.query_params.get('task_no')
        hs = WMSOutboundHistory.objects.filter(task_no=task_no).values()
        if hs:
            return Response(hs[0])
        else:
            return Response({})

    def post(self, request):
        order_nos = self.request.data.get('order_nos')  # 下架任务号列表
        if not isinstance(order_nos, list):
            return Response({'message': "参数错误！", "success:": False, "data": []})
        out_history = list(WMSOutboundHistory.objects.filter(
            task_no__in=order_nos).values('task_no', 'mooney_level', 'mooney_value'))
        out_history_dict = {item['task_no']: item for item in out_history}
        out_log = MaterialOutHistory.objects.using('wms').filter(
            order_no__in=order_nos).values('order_no', 'material_name', 'lot_no')
        out_log_dict = {i['order_no']: i for i in out_log}
        ret = []
        for order_no in order_nos:
            ot = out_log_dict.get(order_no)
            if ot:
                material_name = ot['material_name']
                tracking_num = ot['lot_no']
            else:
                material_name = ""
                tracking_num = ""
            out_history_data = out_history_dict.get(order_no)
            if not out_history_data:
                mn_level = "无等级"
            else:
                level = out_history_data['mooney_level']
                value = out_history_data['mooney_value']
                if level:
                    mn_level = level
                else:
                    if value:
                        mn_level = "未设置等级标准"
                    else:
                        mn_level = "门尼未检测"
            ret.append(
                {"order_no": order_no,
                 "material_name": material_name,
                 "tracking_num": tracking_num,
                 "mn_level": mn_level
                 }
            )
        return Response({'message': "OK", "success:": True, "data": ret})


@method_decorator([api_recorder], name="dispatch")
class ProductInventoryLockedView(APIView):

    @atomic()
    def post(self, request):
        data = self.request.data
        operation_type = data.get('operation_type')  # 1:工艺 2:快检
        locked_type = data.get('locked_type')  # 1:锁定 2:解锁
        lot_nos = data.get('lot_nos')
        reason = data.get('reason')
        for lot_no in lot_nos:
            instance, _ = ProductInventoryLocked.objects.get_or_create(lot_no=lot_no)
            if locked_type == 1:  # 锁定
                if operation_type == 1:  # 工艺
                    locked_status = 1
                    if instance.locked_status == 2:
                        locked_status = 3
                    instance.gy_locked_user = self.request.user.username
                    instance.gy_locked_reason = reason
                    instance.locked_status = locked_status
                    instance.is_locked = True
                else:  # 快检
                    locked_status = 2
                    if instance.locked_status == 1:
                        locked_status = 3
                    instance.kj_locked_user = self.request.user.username
                    instance.kj_locked_reason = reason
                    instance.locked_status = locked_status
                    instance.is_locked = True
            else:
                locked_status = 0
                is_locked = False
                if operation_type == 1:  # 工艺
                    if instance.locked_status in (2, 3):
                        locked_status = 2
                        is_locked = True
                    instance.gy_unlocked_user = self.request.user.username
                    instance.gy_unlocked_reason = reason
                    instance.locked_status = locked_status
                    instance.is_locked = is_locked
                else:  # 快检
                    if instance.locked_status in (1, 3):
                        locked_status = 1
                        is_locked = True
                    instance.kj_unlocked_user = self.request.user.username
                    instance.kj_unlocked_reason = reason
                    instance.locked_status = locked_status
                    instance.is_locked = is_locked
            instance.save()
        return Response('ok')

    def get(self, request):
        material_no = self.request.query_params.get('material_no')
        warehouse_name = self.request.query_params.get('warehouse_name')
        locked_status = self.request.query_params.get('locked_status')
        queryset = ProductInventoryLocked.objects.filter(is_locked=True)
        tunnel = self.request.query_params.get('tunnel')  # 巷道
        quality_status = self.request.query_params.get('quality_status')
        equip_no = self.request.query_params.get('equip_no')  # 机台
        if locked_status:
            if locked_status == '1':  # 工艺锁定
                queryset = queryset.filter(locked_status__in=(1, 3))
            elif locked_status == '2':  # 快检锁定
                queryset = queryset.filter(locked_status__in=(2, 3))
        locked_lot_nos = list(queryset.values_list('lot_no', flat=True))
        if warehouse_name == '混炼胶库':
            stock_query_set = BzFinalMixingRubberInventory.objects.using('bz').filter(
                material_no=material_no, lot_no__in=locked_lot_nos)
        else:
            stock_query_set = BzFinalMixingRubberInventoryLB.objects.using('lb').filter(
                                store_name='炼胶库',
                                material_no=material_no,
                                lot_no__in=locked_lot_nos)
        if equip_no:
            stock_query_set = stock_query_set.filter(bill_id__iendswith=equip_no)
        if tunnel:
            stock_query_set = stock_query_set.filter(location__istartswith=tunnel)
        if quality_status:
            stock_query_set = stock_query_set.filter(quality_level=quality_status)
        s = BzFinalMixingRubberInventorySerializer(stock_query_set, many=True)
        locked_data = queryset.values('lot_no', 'locked_status', 'gy_locked_user', 'kj_locked_user', 'gy_locked_reason', 'kj_locked_reason')
        locked_dict = {i['lot_no']: i for i in locked_data}
        s_data = s.data
        for item in s_data:
            locked_dict_data = locked_dict.get(item['lot_no'])
            locked_status = locked_dict_data['locked_status']
            item['locked_status'] = locked_status
            if locked_status == 1:
                item['locked_user'] = locked_dict_data['gy_locked_user']
                item['locked_reason'] = locked_dict_data['gy_locked_reason']
            else:
                item['locked_user'] = locked_dict_data['kj_locked_user']
                item['locked_reason'] = locked_dict_data['kj_locked_reason']
        return Response(s.data)


@method_decorator([api_recorder], name="dispatch")
class BZInventoryWorkingTasksView(APIView):

    def get(self, request):
        warehouse = self.request.query_params.get('warehouse')
        product_no = self.request.query_params.get('product_no')
        station = self.request.query_params.get('station')
        tunnel = self.request.query_params.get('tunnel')
        filter_kwargs = {'status': 2}
        if warehouse:
            filter_kwargs['outbound_delivery_order__warehouse'] = warehouse
        if product_no:
            filter_kwargs['outbound_delivery_order__product_no'] = product_no
        if station:
            filter_kwargs['outbound_delivery_order__station'] = station
        if tunnel:
            filter_kwargs['location__startswith'] = tunnel
        qs = OutBoundDeliveryOrderDetail.objects.filter(**filter_kwargs).order_by('id', 'location')
        s_data = OutBoundDeliveryOrderDetailListSerializer(qs, many=True).data
        tunnel_task_num_dict = {}
        for i in s_data:
            tunnel = i['location'][0]
            if tunnel_task_num_dict.get(tunnel, 0) == 2:
                i['task_status'] = '等待'
                continue
            i['task_status'] = '进行中'
            tunnel_task_num_dict[tunnel] = tunnel_task_num_dict.get(tunnel, 0) + 1
        return Response(s_data)


@method_decorator([api_recorder], name="dispatch")
class EmptyTrayOutboundDeliveryView(APIView):

    def get(self, request):
        gc = GlobalCode.objects.filter(global_type__type_name='炭黑空托盘出库模式').order_by('id').first()
        if not gc:
            return Response({'out_type': ''})
        total_qty = WmsInventoryStock.objects.using('cb').filter(material_name='空托盘').count()
        return Response({'out_type': gc.global_name, 'total_qty': total_qty})

    def post(self, request):
        req_data = self.request.data
        out_type = req_data.get('out_type')
        out_num = req_data.get('out_num', 0)
        gc = GlobalCode.objects.filter(global_type__type_name='炭黑空托盘出库模式').order_by('id').first()
        if not gc:
            raise ValidationError('请配置炭黑空托盘出库模式公共代码！')
        if out_type == '手动':
            req_data = {"ktpType": 0, "ktpNum": out_num}
        else:
            req_data = {'ktpType': 1, 'ktpNum': out_num}
        if DEBUG:
            headers = {"Content-Type": "text/xml; charset=utf-8",
                       "SOAPAction": "http://tempuri.org/IStockService/IssueKtpTypeAndNum"}
            data = """<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:tem="http://tempuri.org/">
            <soapenv:Header/>
            <soapenv:Body>
            <tem:IssueKtpTypeAndNum>
             <tem:JsonGet>{}</tem:JsonGet>
            </tem:IssueKtpTypeAndNum>
            </soapenv:Body>
            </soapenv:Envelope>""".format(json.dumps(req_data))
            url = 'http://10.4.24.33:3000/StockService?wsdl'
            try:
                ret = requests.post(url, data=data.encode('utf-8'), headers=headers, timeout=5)
            except Exception:
                raise ValidationError('接口调用失败，请联系管理员！')
            try:
                resp_xml = ret.text
                json_data = xmltodict.parse(resp_xml)
                status_data = json.loads(json_data.get('s:Envelope').get('s:Body').get('IssueKtpTypeAndNumResponse').get('IssueKtpTypeAndNumResult'))
                if status_data.get('Result') != '0':
                    raise ValidationError('操作失败：{}'.format(status_data.get('Message')))
            except Exception:
                pass
        gc.global_name = out_type
        gc.save()
        return Response('ok')