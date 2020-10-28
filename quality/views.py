from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet, ModelViewSet, ReadOnlyModelViewSet

from basics.models import GlobalCode, GlobalCodeType
from basics.serializers import GlobalCodeSerializer
from mes.common_code import CommonDeleteMixin
from mes.paginations import SinglePageNumberPagination
from quality.filters import TestMethodFilter, DataPointFilter, \
    MaterialTestMethodFilter, MaterialDataPointIndicatorFilter, MaterialTestOrderFilter, MaterialDealResulFilter, \
    DealSuggestionFilter
from quality.models import TestIndicator, MaterialDataPointIndicator, TestMethod, MaterialTestOrder, \
    MaterialTestMethod, TestType, DataPoint, DealSuggestion, MaterialDealResult
from quality.serializers import MaterialDataPointIndicatorSerializer, \
    MaterialTestOrderSerializer, MaterialTestOrderListSerializer, \
    MaterialTestMethodSerializer, TestMethodSerializer, TestTypeSerializer, DataPointSerializer, \
    DealSuggestionSerializer, DealResultDealSerializer
from recipe.models import Material, ProductBatching


class TestIndicatorListView(ListAPIView):
    """试验指标列表"""
    queryset = TestIndicator.objects.all()

    def list(self, request, *args, **kwargs):
        data = TestIndicator.objects.values('id', 'name')
        return Response(data)


class TestTypeViewSet(ModelViewSet):
    """试验类型管理"""
    queryset = TestType.objects.filter(delete_flag=False)
    serializer_class = TestTypeSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('test_indicator', )

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        if self.request.query_params.get('all'):
            data = queryset.values('id', 'name')
            return Response({'results': data})
        return super().list(self, request, *args, **kwargs)


class DataPointViewSet(ModelViewSet):
    """试验类型数据点管理"""
    queryset = DataPoint.objects.filter(delete_flag=False)
    serializer_class = DataPointSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_class = DataPointFilter

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        if self.request.query_params.get('all'):
            data = queryset.values('id', 'name')
            return Response({'results': data})
        return super().list(self, request, *args, **kwargs)


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


# class MaterialTestIndicatorsTabView(ListAPIView):
#     """获取原材料及其试验类型表格数据，参数：?material_no=xxx"""
#     permission_classes = (IsAuthenticated, )
#     queryset = Material.objects.all()
#
#     def list(self, request, *args, **kwargs):
#         material_no = self.request.query_params.get('material_no')
#         material_data = MaterialTestMethod.objects.filter(delete_flag=False)
#         if material_no:
#             material_data = material_data.filter(material__material_no__icontains=material_no)
#         material_ids = set(material_data.values_list('material_id', flat=True))
#         materials = Material.objects.filter(id__in=material_ids)
#         page_materials = self.paginate_queryset(materials)
#         test_indicators = TestIndicator.objects.all()
#         ret = []
#         for material in page_materials:
#             material_data = {'material_id': material.id,
#                              'material_no': material.material_no,
#                              'material_name': material.material_name,
#                              'test_data_detail': {}
#                              }
#             for test_indicator in test_indicators:
#                 if MaterialDataPointIndicator.objects.filter(
#                         material_test_data_point__material_test_method__test_method__test_type__test_indicator=
#                         test_indicator,
#                         material_test_data_point__material_test_method__material=material).exists():
#                     material_data['test_data_detail'][test_indicator.id] = {'test_type_name': test_indicator.name,
#                                                                             'indicator_exists': True}
#                 else:
#                     material_data['test_data_detail'][test_indicator.id] = {'test_type_name': test_indicator.name,
#                                                                             'indicator_exists': False}
#             ret.append(material_data)
#         return self.get_paginated_response(ret)


# class MatIndicatorsTabView(APIView):
#     """根据原材料编号和试验方法获取判断标准表格数据， 参数：material_no=胶料编号&test_method_id=试验方法id"""
#     def get(self, request):
#         material_no = self.request.query_params.get('material_no', 'BS1485')
#         test_method_id = self.request.query_params.get('test_method_id', 7)
#         if not all([material_no, test_method_id]):
#             raise ValidationError('参数不足')
#         test_data = MaterialTestMethodDataPoint.objects.filter(
#             material_test_method__material__material_no=material_no,
#             material_test_method__test_method_id=test_method_id)
#         s = MaterialDataPointListSerializer(instance=test_data, many=True)
#         ret = {}
#         for item in s.data:
#             mat_indicators = item['mat_indicators']
#             for mat_indicator in mat_indicators:
#                 if item['name'] not in ret:
#                     ret[mat_indicator['result']] = {"level": mat_indicator['level'],
#                                                     "result": mat_indicator['result'],
#                                                     item['name']: {
#                                                          'id': mat_indicator['id'],
#                                                          "upper_limit": mat_indicator['upper_limit'],
#                                                          "lower_limit": mat_indicator['lower_limit']}
#                                                     }
#                 else:
#                     ret[mat_indicator['result']][item['name']] = {
#                         'id': mat_indicator['id'],
#                         "upper_limit": mat_indicator['upper_limit'],
#                         "lower_limit": mat_indicator['lower_limit']
#                         }
#         return Response(ret.values())


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
    permission_classes = (IsAuthenticated, )
    filter_class = MaterialTestOrderFilter

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


class MaterialTestMethodViewSet(ModelViewSet):
    """物料试验方法"""
    queryset = MaterialTestMethod.objects.filter(delete_flag=False)
    serializer_class = MaterialTestMethodSerializer
    filter_backends = (DjangoFilterBackend,)
    permission_classes = (IsAuthenticated,)
    filter_class = MaterialTestMethodFilter


class MaterialDataPointIndicatorViewSet(ModelViewSet):
    """物料数据点评判指标"""
    queryset = MaterialDataPointIndicator.objects.filter(delete_flag=False)
    serializer_class = MaterialDataPointIndicatorSerializer
    filter_backends = (DjangoFilterBackend,)
    permission_classes = (IsAuthenticated,)
    filter_class = MaterialDataPointIndicatorFilter
    pagination_class = None


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
    queryset = MaterialDealResult.objects.filter(delete_flag=False)
    serializer_class = DealResultDealSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_class =  MaterialDealResulFilter


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