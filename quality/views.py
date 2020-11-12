import datetime

from django.db.models import Q
from django.db.transaction import atomic
from django.utils.decorators import method_decorator
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework.viewsets import GenericViewSet, ModelViewSet
from basics.models import GlobalCodeType
from basics.serializers import GlobalCodeSerializer
from mes.common_code import CommonDeleteMixin
from mes.paginations import SinglePageNumberPagination
from mes.derorators import api_recorder
from plan.models import ProductClassesPlan
from production.models import PalletFeedbacks
from quality.filters import TestMethodFilter, DataPointFilter, \
    MaterialTestMethodFilter, MaterialDataPointIndicatorFilter, MaterialTestOrderFilter, MaterialDealResulFilter, \
    DealSuggestionFilter, PalletFeedbacksTestFilter
from quality.models import TestIndicator, MaterialDataPointIndicator, TestMethod, MaterialTestOrder, \
    MaterialTestMethod, TestType, DataPoint, DealSuggestion, MaterialDealResult, LevelResult, MaterialTestResult, \
    LabelPrint
from quality.serializers import MaterialDataPointIndicatorSerializer, \
    MaterialTestOrderSerializer, MaterialTestOrderListSerializer, \
    MaterialTestMethodSerializer, TestMethodSerializer, TestTypeSerializer, DataPointSerializer, \
    DealSuggestionSerializer, DealResultDealSerializer, MaterialDealResultListSerializer, LevelResultSerializer, \
    TestIndicatorSerializer, LabelPrintSerializer
from recipe.models import Material, ProductBatching
import logging
from django.db.models import Max

logger = logging.getLogger('send_log')


@method_decorator([api_recorder], name="dispatch")
class TestIndicatorViewSet(ModelViewSet):
    """试验指标列表"""
    queryset = TestIndicator.objects.filter(delete_flag=False)
    serializer_class = TestIndicatorSerializer

    def list(self, request, *args, **kwargs):
        data = self.queryset.values('id', 'name')
        return Response(data)


@method_decorator([api_recorder], name="dispatch")
class TestTypeViewSet(ModelViewSet):
    """试验类型管理"""
    queryset = TestType.objects.filter(delete_flag=False)
    serializer_class = TestTypeSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('test_indicator',)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        if self.request.query_params.get('all'):
            data = queryset.values('id', 'name')
            return Response({'results': data})
        return super().list(self, request, *args, **kwargs)


@method_decorator([api_recorder], name="dispatch")
class DataPointViewSet(ModelViewSet):
    """试验类型数据点管理"""
    queryset = DataPoint.objects.filter(delete_flag=False)
    serializer_class = DataPointSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_class = DataPointFilter
    pagination_class = None

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        if self.request.query_params.get('all'):
            data = queryset.values('id', 'name', 'unit')
            return Response({'results': data})
        return super().list(self, request, *args, **kwargs)


@method_decorator([api_recorder], name="dispatch")
class TestMethodViewSet(ModelViewSet):
    """试验方法管理"""
    queryset = TestMethod.objects.filter(delete_flag=False)
    serializer_class = TestMethodSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_class = TestMethodFilter

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        if self.request.query_params.get('all'):
            data = queryset.values('id', 'name')
            return Response({'results': data})
        return super().list(self, request, *args, **kwargs)


@method_decorator([api_recorder], name="dispatch")
class TestIndicatorDataPointListView(ListAPIView):
    """获取试验指标及其所有的试验方法数据点"""
    queryset = TestIndicator.objects.filter(delete_flag=False)

    def list(self, request, *args, **kwargs):
        ret = []
        test_indicators = TestIndicator.objects.all()
        for test_indicator in test_indicators:
            data_names = set(DataPoint.objects.filter(
                test_type__test_indicator=test_indicator).values_list('name', flat=True))
            data = {'test_type_id': test_indicator.id,
                    'test_type_name': test_indicator.name,
                    'data_indicator_detail': [data_name for data_name in data_names]
                    }
            ret.append(data)
        return Response(ret)


class MaterialTestIndicatorMethods(APIView):
    """获取原材料指标试验方法"""

    def get(self, request):
        material_no = self.request.query_params.get('material_no')
        try:
            material = Material.objects.get(material_no=material_no)
        except Exception:
            raise ValidationError('该胶料不存在')
        ret = {}
        test_indicator_names = TestIndicator.objects.values_list('name', flat=True)
        test_methods = TestMethod.objects.all()
        for test_method in test_methods:
            indicator_name = test_method.test_type.test_indicator.name
            allowed = True
            data_points = None
            mat_test_method = MaterialTestMethod.objects.filter(
                material=material,
                test_method=test_method).first()
            if not mat_test_method:
                allowed = False
            else:
                if not MaterialDataPointIndicator.objects.filter(material_test_method=mat_test_method).exists():
                    allowed = False
                else:
                    data_points = mat_test_method.data_point.values('id', 'name', 'unit')
            if indicator_name not in ret:
                data = {
                    'test_indicator': indicator_name,
                    'methods': [
                        {'id': 1,
                         'name': test_method.name,
                         'allowed': allowed,
                         'data_points': data_points}
                    ]
                }
                ret[indicator_name] = data
            else:
                ret[indicator_name]['methods'].append(
                    {'id': 1, 'name': test_method.name, 'allowed': allowed, 'data_points': data_points})

        for item in test_indicator_names:
            if item not in ret:
                ret[item] = {'test_indicator': item, 'methods': []}
        return Response(ret.values())


@method_decorator([api_recorder], name="dispatch")
class MaterialTestOrderViewSet(mixins.CreateModelMixin,
                               mixins.ListModelMixin,
                               GenericViewSet):
    """
    list:
        列表展示
    create:
        手工录入数据
    """
    queryset = MaterialTestOrder.objects.filter(delete_flag=False)
    serializer_class = MaterialTestOrderSerializer
    filter_backends = (DjangoFilterBackend,)
    permission_classes = (IsAuthenticated,)
    filter_class = MaterialTestOrderFilter
    pagination_class = None

    def get_serializer_class(self):
        if self.action == 'create':
            return MaterialTestOrderSerializer
        else:
            return MaterialTestOrderListSerializer

    def create(self, request, *args, **kwargs):
        data = request.data
        if not isinstance(data, list):
            raise ValidationError('参数错误')
        for item in data:
            s = MaterialTestOrderSerializer(data=item, context={'request': request})
            if not s.is_valid():
                raise ValidationError(s.errors)
            s.save()
        return Response('新建成功')


@method_decorator([api_recorder], name="dispatch")
class MaterialTestMethodViewSet(ModelViewSet):
    """物料试验方法"""
    queryset = MaterialTestMethod.objects.filter(delete_flag=False)
    serializer_class = MaterialTestMethodSerializer
    filter_backends = (DjangoFilterBackend,)
    permission_classes = (IsAuthenticated,)
    filter_class = MaterialTestMethodFilter


@method_decorator([api_recorder], name="dispatch")
class MaterialDataPointIndicatorViewSet(ModelViewSet):
    """物料数据点评判指标"""
    queryset = MaterialDataPointIndicator.objects.filter(delete_flag=False)
    serializer_class = MaterialDataPointIndicatorSerializer
    filter_backends = (DjangoFilterBackend,)
    permission_classes = (IsAuthenticated,)
    filter_class = MaterialDataPointIndicatorFilter
    pagination_class = None


@method_decorator([api_recorder], name="dispatch")
class ProductBatchingMaterialListView(ListAPIView):
    """胶料原材料列表"""
    queryset = Material.objects.filter(delete_flag=False)

    def list(self, request, *args, **kwargs):
        batching_no = set(ProductBatching.objects.values_list('stage_product_batch_no', flat=True))
        material_data = self.queryset.filter(material_no__in=batching_no).values('id', 'material_no')
        return Response(material_data)


class DealSuggestionViewSet(CommonDeleteMixin, ModelViewSet):
    """处理意见
        list: 查询处理意见列表
        retrive: 查询处理意见详情
        post: 新增处理意见
        put: 修改处理意见
    """
    queryset = DealSuggestion.objects.filter(delete_flag=False)
    serializer_class = DealSuggestionSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_class = DealSuggestionFilter
    pagination_class = SinglePageNumberPagination


class MaterialDealResultViewSet(CommonDeleteMixin, ModelViewSet):
    """胶料处理结果
    list: 查询胶料处理结果列表
    post: 创建胶料处理结果
    put: 创建胶料处理结果
    """
    queryset = MaterialDealResult.objects.filter(~Q(deal_result="一等品")).filter(~Q(status="复测")).filter(delete_flag=False)
    serializer_class = DealResultDealSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_class = MaterialDealResulFilter


class MaterialDealStatusListView(APIView):
    """胶料状态列表"""

    def get(self, request):
        filter_set = MaterialDealResult.objects.filter(delete_flag=False).values("status").annotate()
        return Response(filter_set)


class DealTypeView(APIView):

    def post(self, request):
        data = request.data
        gct = GlobalCodeType.objects.filter(type_name="处理类型").first()
        if not gct:
            raise ValidationError("请先在基础信息管理下的公用代码管理内启用/创建'处理类型'")
        data.update(global_type=gct.id)
        serializer = GlobalCodeSerializer(data=data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "ok"}, status=status.HTTP_201_CREATED)


@method_decorator([api_recorder], name="dispatch")
class MaterialDealResultUpdateValidTime(APIView):
    # 快检信息综合管理修改有效时间
    @atomic()
    def post(self, request):
        id = self.request.data.get('id', None)
        valid_time = self.request.data.get('valid_time', None)
        if not id or not valid_time:
            raise ValidationError('id或有效时间必传')
        MaterialDealResult.objects.filter(id=id).update(valid_time=valid_time)
        return Response('修改成功')


@method_decorator([api_recorder], name="dispatch")
class PalletFeedbacksTestListView(ListAPIView):
    # 快检信息综合管里
    queryset = MaterialDealResult.objects.filter(delete_flag=False)
    serializer_class = MaterialDealResultListSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_class = PalletFeedbacksTestFilter

    def get_queryset(self):
        equip_no = self.request.query_params.get('equip_no', None)
        product_no = self.request.query_params.get('product_no', None)
        day_time = self.request.query_params.get('day_time', None)
        classes = self.request.query_params.get('classes', None)
        schedule_name = self.request.query_params.get('schedule_name', None)
        filter_dict = {'delete_flag': False}
        pfb_filter = {}
        pcp_filter = {}
        if day_time:
            pcp_filter['work_schedule_plan__plan_schedule__day_time'] = day_time
        if schedule_name:
            pcp_filter['work_schedule_plan__plan_schedule__work_schedule__schedule_name'] = schedule_name
        if pcp_filter:
            pcp_uid_list = ProductClassesPlan.objects.filter(**pcp_filter).values_list('plan_classes_uid', flat=True)
            pfb_filter['plan_classes_uid__in'] = list(pcp_uid_list)

        if equip_no:
            pfb_filter['equip_no'] = equip_no
        if product_no:
            pfb_filter['product_no__icontains'] = product_no
        if classes:
            pfb_filter['classes'] = classes
        if pfb_filter:
            pfb_product_list = PalletFeedbacks.objects.filter(**pfb_filter).values_list('lot_no', flat=True)
            filter_dict['lot_no__in'] = list(pfb_product_list)
        pfb_queryset = MaterialDealResult.objects.filter(**filter_dict).exclude(status='复测')
        return pfb_queryset


@method_decorator([api_recorder], name="dispatch")
class LevelResultViewSet(ModelViewSet):
    """等级和结果"""
    queryset = LevelResult.objects.filter(delete_flag=False)
    serializer_class = LevelResultSerializer
    filter_backends = (DjangoFilterBackend,)
    permission_classes = (IsAuthenticated,)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        mdp_set = MaterialDataPointIndicator.objects.filter(level=instance.level, result=instance.deal_result,
                                                            delete_flag=False)
        if mdp_set:
            raise ValidationError('该等级已被使用，不能删除')
        instance.delete_flag = True
        instance.last_updated_user = request.user
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        if self.request.query_params.get('all'):
            data = queryset.values('id', 'deal_result', 'level')
            return Response({'results': data})
        return super().list(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        deal_result = self.request.data.get('deal_result', None)
        level = self.request.data.get('level', None)
        if not deal_result or not level:
            raise ValidationError('等级和检测结果必传')
        lr_obj = LevelResult.objects.filter(deal_result=deal_result, level=level, delete_flag=False).first()
        if lr_obj:
            raise ValidationError('不可重复新建')
        lr_obj = LevelResult.objects.filter(deal_result=deal_result, level=level, delete_flag=True).first()
        if lr_obj:
            lr_obj.delete_flag = False
            lr_obj.save()
            return Response('新建成功')
        else:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


@method_decorator([api_recorder], name="dispatch")
class ProductDayStatistics(APIView):
    """胶料日合格率统计"""

    def get(self, request, *args, **kwargs):
        params = request.query_params
        # month_time = params.get('ym_time', datetime.datetime.now().month)
        # year_time = params.get('ym_time', datetime.datetime.now().year)
        month_time = params.get('ym_time', datetime.datetime.now()).month
        year_time = params.get('ym_time', datetime.datetime.now()).year
        pass_type = params.get('pass_type', '1')  # 1:综合合格率  2：一次合格率  3：流变合格率
        pass_dict = {'1': ['门尼', '比重', '硬度', '流变'], '2': ['门尼', '比重', '硬度'], '3': ['流变']}
        test_indicator_name_dict = pass_dict[pass_type]
        product_no_list = MaterialTestOrder.objects.filter(delete_flag=False,
                                                           production_factory_date__year=year_time,
                                                           production_factory_date__month=month_time).values(
            'product_no').annotate().distinct()
        ruturn_pass = []
        for product_no_dict in product_no_list:
            return_dict = {}
            return_dict['product_no'] = product_no_dict['product_no']
            for day_time in range(1, int(datetime.datetime.now().day) + 1):
                mto_set = MaterialTestOrder.objects.filter(delete_flag=False, production_factory_date__year=year_time,
                                                           production_factory_date__month=month_time,
                                                           production_factory_date__day=day_time,
                                                           **product_no_dict).all()
                if not mto_set:
                    continue
                mto_count = mto_set.count()
                pass_count = 0
                level_list = []

                for mto_obj in mto_set:
                    mrt_list = mto_obj.order_results.filter(
                        test_indicator_name__in=test_indicator_name_dict).all().values(
                        'data_point_name').annotate(max_test_time=Max('test_times'))
                    for mrt_dict in mrt_list:
                        mrt_dict_obj = MaterialTestResult.objects.filter(material_test_order=mto_obj,
                                                                         test_indicator_name__in=test_indicator_name_dict,
                                                                         data_point_name=mrt_dict['data_point_name'],
                                                                         test_times=mrt_dict['max_test_time']).last()
                        level_list.append(mrt_dict_obj)
                    if not level_list:
                        continue
                    max_mtr = level_list[0]
                    for mtr_obj in level_list:
                        if not mtr_obj.data_point_indicator:
                            continue
                        else:
                            if not max_mtr.data_point_indicator:
                                max_mtr = mtr_obj
                                continue
                            if mtr_obj.data_point_indicator.level > max_mtr.data_point_indicator.level:
                                max_mtr = mtr_obj
                    if not max_mtr.data_point_indicator:
                        continue
                    if max_mtr.data_point_indicator.result == '一等品':
                        pass_count += 1
                percent_of_pass = str((pass_count / mto_count) * 100) + '%'
                return_dict[f'{month_time}-{day_time}'] = percent_of_pass
            ruturn_pass.append(return_dict)
        return Response(ruturn_pass)


class LabelPrintViewSet(mixins.CreateModelMixin,
                        mixins.UpdateModelMixin,
                        GenericViewSet):
    """
    list: 获取一条打印标签
    create: 存储一条打印标签
    """
    queryset = LabelPrint.objects.all()
    serializer_class = LabelPrintSerializer
    permission_classes = ()
    authentication_classes = ()

    def list(self, request, *args, **kwargs):
        instance = self.get_queryset().filter(label_type=2, status=0).first()
        if instance:
            serializer = self.get_serializer(instance)
            data = serializer.data
        else:
            data = {}
        return Response(data)


class DealSuggestionView(APIView):
    """处理意见展示"""

    def get(self, request, *args, **kwargs):
        queryset = MaterialDealResult.objects.filter(delete_flag=False).values('deal_suggestion').annotate().distinct()
        return Response(queryset.values_list('deal_suggestion', flat=True))


class MaterialTestResultHistoryView(APIView):
    """试验结果数据展开列表， 参数：?test_order_id=检测单id"""
    def get(self, request):
        test_order_id = self.request.query_params.get('test_order_id')
        try:
            test_order = MaterialTestOrder.objects.get(id=test_order_id)
        except Exception:
            raise ValidationError('参数错误')
        data = MaterialTestResult.objects.filter(material_test_order=test_order).all()
        max_test_times = MaterialTestResult.objects.filter(material_test_order=test_order
                                                           ).aggregate(max_time=Max('test_times'))['max_time']
        ret = {i: {} for i in range(1, max_test_times+1)}

        for item in data:
            indicator_name = item.test_indicator_name
            data_point_name = item.data_point_name
            test_times = item.test_times
            value = item.value
            result = item.result
            mes_result = item.mes_result
            level = item.level
            machine_name = item.machine_name
            test_result = {
                'value': value,
                'result': result,
                'mes_result': mes_result,
                'machine_name': machine_name,
                'level': level,
                'test_times': test_times
            }
            if test_times in ret:
                if indicator_name not in ret[test_times]:
                    ret[test_times] = {indicator_name: {data_point_name: test_result}}
                else:
                    ret[test_times][indicator_name][data_point_name] = test_result
        return Response(ret)