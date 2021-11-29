import json
import logging
import random
import re
from datetime import datetime, timedelta
from decimal import Decimal

import requests
from django.db.models import Q, Sum, Max, F
from django.db.transaction import atomic
from django.db.utils import ConnectionDoesNotExist
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from basics.models import PlanSchedule, GlobalCode, WorkSchedulePlan
from inventory.models import MaterialOutHistory, MixGumOutInventoryLog, DepotPallt
from mes import settings
from mes.base_serializer import BaseModelSerializer
from mes.conf import COMMON_READ_ONLY_FIELDS
from plan.models import ProductClassesPlan, BatchingClassesPlan, BatchingClassesEquipPlan
from production.models import PalletFeedbacks
from recipe.models import ERPMESMaterialRelation, WeighCntType, ProductBatching
from terminal.models import EquipOperationLog, WeightBatchingLog, FeedingLog, WeightTankStatus, \
    WeightPackageLog, FeedingMaterialLog, LoadMaterialLog, MaterialInfo, Bin, Plan, RecipePre, ReportBasic, \
    ReportWeight, LoadTankMaterialLog, PackageExpire, RecipeMaterial, CarbonTankFeedWeightSet, \
    FeedingOperationLog, CarbonTankFeedingPrompt, PowderTankSetting, OilTankSetting, ReplaceMaterial, ReturnRubber, \
    ToleranceRule, WeightPackageManual, WeightPackageManualDetails, WeightPackageSingle
from terminal.utils import TankStatusSync, CLSystem, material_out_barcode

logger = logging.getLogger('send_log')


def generate_bra_code(equip_no, factory_date, classes):
    # 后端生成，工厂编码E101 + 称量机台号 + 小料计划的工厂日期8位 + 班次1 - 3 + 四位随机数。
    # 重复打印条码规则不变，重新生成会比较麻烦，根据修改的工厂时间班次来生成，序列号改成字母。从A~Z
    random_str = ['z', 'y', 'x', 'w', 'v', 'u', 't', 's', 'r',
                  'q', 'p', 'o', 'n', 'm', 'l', 'k', 'j', 'i',
                  'h', 'g', 'f', 'e', 'd', 'c', 'b', 'a',
                  '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    classes_dict = {'早班': '1', '中班': '2', '夜班': '3'}
    return 'E101{}{}{}{}'.format(equip_no, ''.join(str(factory_date).split('-')),
                                 classes_dict[classes],
                                 ''.join(random.sample(random_str, 4)))


class LoadMaterialLogSerializer(BaseModelSerializer):
    product_no = serializers.ReadOnlyField(source='feed_log.product_no')
    created_date = serializers.DateTimeField(source='feed_log.feed_begin_time')
    trains = serializers.ReadOnlyField(source='feed_log.trains')

    class Meta:
        model = LoadMaterialLog
        fields = '__all__'


class LoadMaterialLogUpdateSerializer(BaseModelSerializer):
    adjust_left_weight = serializers.DecimalField(write_only=True, decimal_places=2, max_digits=8)

    class Meta:
        model = LoadTankMaterialLog
        fields = ['adjust_left_weight']


class LoadMaterialLogCreateSerializer(BaseModelSerializer):
    bra_code = serializers.CharField(write_only=True)

    def validate(self, attrs):
        # 条码来源有三种，wms子系统、收皮条码，称量打包条码
        bra_code = attrs['bra_code']
        plan_classes_uid = attrs['plan_classes_uid']
        # 计划号中存在条码
        is_used = LoadTankMaterialLog.objects.filter(plan_classes_uid=plan_classes_uid, bra_code=bra_code)
        if is_used:
            raise serializers.ValidationError('同一计划中不可多次扫同一条码')
        # 查原材料出库履历查到原材料物料编码
        if settings.DEBUG:
            res = None
        else:
            try:
                res = material_out_barcode(bra_code)
            except Exception as e:
                raise serializers.ValidationError(e)
        pallet_feedback = PalletFeedbacks.objects.filter(lot_no=bra_code).first()
        # 隐藏细料硫磺
        weight_package = WeightPackageLog.objects.filter(bra_code=bra_code).first()
        # 非胶皮/不加硫
        rubber, add_s = False, False
        material_no = material_name = None
        total_weight = 0
        unit = 'KG'
        classes_plan = ProductClassesPlan.objects.filter(plan_classes_uid=plan_classes_uid).first()
        if not classes_plan:
            raise serializers.ValidationError('该计划不存在')
        # 获取配方信息
        material_name_weight = classes_plan.product_batching.get_product_batch
        if not material_name_weight:
            raise serializers.ValidationError(f'mes中未找到该机型配方:{classes_plan.product_batching.stage_product_batch_no}')
        detail_infos = {i['material__material_name']: i['actual_weight'] for i in material_name_weight}
        materials = detail_infos.keys()
        if res:
            attrs['scan_material'] = res.get('WLMC')
            material_name_set = set(ERPMESMaterialRelation.objects.filter(
                zc_material__wlxxid=res['WLXXID'],
                use_flag=True
            ).values_list('material__material_name', flat=True))
            if not material_name_set:
                raise serializers.ValidationError('该物料未与MES原材料建立绑定关系！')
            comm_material = list(material_name_set & materials)
            if comm_material:
                material_name = comm_material[0]
                material_no = comm_material[0]
                total_weight = res.get('ZL')
                unit = res.get('BZDW')
        if pallet_feedback:
            rubber = True
            if re.findall('FM|RFM|RE', pallet_feedback.product_no):
                add_s = True
            material_no = pallet_feedback.product_no
            material_name = pallet_feedback.product_no
            total_weight = pallet_feedback.actual_weight
            unit = unit
            attrs['scan_material'] = material_name
            DepotPallt.objects.filter(pallet_data__lot_no=bra_code).update(outer_time=datetime.now(), pallet_status=2)
        if len(bra_code) > 12 and bra_code[12] in ['H', 'Z']:
            start_time = f'20{bra_code[:2]}-{bra_code[2:4]}-{bra_code[4:6]} {bra_code[6:8]}:{bra_code[8:10]}:{bra_code[10:12]}'
            end_time = str(datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S') + timedelta(seconds=1))
            location = f'{bra_code[13]}-{bra_code[14]}-{bra_code[15: len(bra_code) - 1]}-{bra_code[-1]}'
            db_name = 'bz' if bra_code[12] == 'H' else 'lb'
            instance = MixGumOutInventoryLog.objects.using(db_name).filter(location=location, start_time__gte=start_time,
                                                                           start_time__lte=end_time).last()
            if not instance:
                raise serializers.ValidationError(f'条码解析异常{bra_code}')
            rubber = True
            if db_name == 'lb':
                add_s = True
            material_no = instance.material_no
            material_name = instance.material_no
            total_weight = instance.weight
            unit = unit
            attrs['scan_material'] = material_name
        # 隐藏细料硫磺
        if weight_package:
            material_no = weight_package.material_no
            material_name = weight_package.material_name
            total_weight = weight_package.package_count
            unit = '包'
            attrs['scan_material'] = material_name
        if not material_name:
            raise serializers.ValidationError('未找到该条形码信息！')
        attrs['equip_no'] = classes_plan.equip.equip_no
        attrs['material_name'] = material_name
        attrs['material_no'] = material_no
        attrs['tank_data'] = {'msg': '', 'bra_code': bra_code, 'init_weight': total_weight, 'scan_time': datetime.now(),
                              'useup_time': datetime.strptime('1970-01-01 00:00:00', '%Y-%m-%d %H:%M:%S'), 'unit': unit,
                              'material_no': material_no, 'material_name': material_name, 'real_weight': total_weight,
                              'scan_material': attrs.pop('scan_material', ''), 'plan_classes_uid': plan_classes_uid}
        material_error_msg = ''
        # 是否走进物料在配方里的判断
        flag = True
        # 物料是否走入在配方中的判断
        material_in_flag = True
        # 添加到工艺放行表中的数据
        replace_material_data = {"plan_classes_uid": plan_classes_uid, "equip_no": weight_package.equip_no,
                                 "product_no": classes_plan.product_batching.stage_product_batch_no,
                                 "real_material": material_name, "bra_code": bra_code, "status": "未处理",
                                 "created_user": self.context['request'].user, 'material_no': material_no,
                                 "last_updated_date": datetime.now(), 'material_type': '料包' if weight_package else '胶块'}
        # 细料
        if weight_package:
            material_in_flag = False
            if weight_package.dev_type != classes_plan.product_batching.dev_type.category_name:
                raise serializers.ValidationError('投料与生产机型不一致, 无法投料')
            elif re.split(r'\(|\（|\[', weight_package.product_no)[0] != classes_plan.product_batching.stage_product_batch_no:
                material_error_msg = '配方名不一致, 请工艺确认'
                ReplaceMaterial.objects.create(**replace_material_data)
            elif weight_package.plan_weight != detail_infos.get([i for i in materials if re.findall('-细料|-硫磺', i)][0]):
                material_error_msg = '料包重量与配方不一致, 请工艺确认'
                ReplaceMaterial.objects.create(**replace_material_data)
            elif weight_package.expire_days != 0 and datetime.now().replace(microsecond=False) - weight_package.batch_time > timedelta(days=weight_package.expire_days):
                material_error_msg = '料包已过期, 请工艺确认'
                ReplaceMaterial.objects.create(**replace_material_data)
            else:
                # 条件都匹配, 转换名称记入料框表
                flag = True
                material_no = material_name = classes_plan.product_batching.weight_cnt_types.first().name
        # 判断物料是否在配方中
        if material_in_flag and material_name not in materials:
            flag, attrs['status'] = False, 2
            # 胶皮
            if rubber:
                # 查看群控配方是否含有掺料和待处理料
                product_recipe = classes_plan.product_batching.batching_details.filter(delete_flag=False, type=1)
                query_set = product_recipe.filter(Q(Q(material__material_name__icontains='掺料') |
                                                  Q(material__material_name__icontains='待处理料'))).first()
                if query_set:
                    material_name = f'掺料-{material_name}'
                    # 炼胶类型判断: 混炼/终炼
                    if 'FM' in classes_plan.product_batching.stage_product_batch_no:
                        # 待处理料不需要做加硫磺前后判断
                        if '掺料' in query_set.material.material_name:
                            # 加硫磺前后(上面限定了胶皮,这里不会出现小料硫磺xxx-硫磺)
                            s_id = product_recipe.filter(Q(material__material_name__icontains='硫磺')).first()
                            if s_id.id < query_set.id:
                                # 硫磺在前, 只能投加硫料
                                if add_s:
                                    material_error_msg = f'物料:{material_name} 扫码成功'
                                else:
                                    material_error_msg = '加硫磺前只能投入无硫料'
                            else:
                                if add_s:
                                    material_error_msg = '加硫磺后只能投入加硫料'
                                else:
                                    material_error_msg = f'物料:{material_name} 扫码成功'
                        else:
                            material_error_msg = f'物料:{material_name} 扫码成功'
                    else:
                        # 加硫禁止投料
                        if add_s:
                            material_error_msg = '无硫混炼不可投入加硫料'
                        else:
                            material_error_msg = f'物料:{material_name} 扫码成功'
                else:
                    material_error_msg = '配方中无掺料, 所投物料不在配方中'
            # 胶块/细料
            else:
                # 查找物料替代表
                replace_record = ReplaceMaterial.objects.filter(plan_classes_uid=plan_classes_uid, status='已处理',
                                                                real_material=material_name, result=1).first()
                if replace_record and replace_record.result:
                    # 转换物料名
                    flag = True
                    material_no = material_name = replace_record.recipe_material
                else:
                    # 胶块
                    material_error_msg = '胶块不在配方中, 请工艺确认'
                    ReplaceMaterial.objects.create(**replace_material_data)
        if flag:
            # 配方中物料单车需要重量
            single_material_weight = detail_infos[material_name]
            # 获取计划号对应料框信息
            add_materials = LoadTankMaterialLog.objects.filter(plan_classes_uid=plan_classes_uid, useup_time__year='1970',
                                                               material_name=material_name)

            if not add_materials:
                # 上一条计划剩余量判定
                pre_material = LoadTankMaterialLog.objects.filter(bra_code=bra_code).first()
                # 料框表中无该条码信息
                if not pre_material:
                    attrs['tank_data'].update({'actual_weight': 0, 'adjust_left_weight': total_weight,
                                               'single_need': single_material_weight})
                    attrs['status'] = 1
                # 存在该条码信息(其他计划使用过)
                else:
                    # 未用完
                    if pre_material.adjust_left_weight != 0:
                        attrs['tank_data'].update({'actual_weight': pre_material.actual_weight,
                                                   'real_weight': pre_material.real_weight, 'pre_material': pre_material,
                                                   'adjust_left_weight': pre_material.adjust_left_weight,
                                                   'variety': pre_material.variety,
                                                   'single_need': single_material_weight})
                        attrs['status'] = 1
                    # 已用完(异常扫码)
                    else:
                        attrs['tank_data'].update({'msg': '该物料条码已无剩余量,请扫新条码'})
                        attrs['status'] = 2
            else:
                # 扫码物料不在已有物料中
                if material_name not in add_materials.values_list('material_name', flat=True):
                    attrs['tank_data'].update({'actual_weight': 0, 'adjust_left_weight': total_weight,
                                               'single_need': single_material_weight})
                    attrs['status'] = 1
                # 同物料扫码
                else:
                    left_weight = add_materials.aggregate(left_weight=Sum('real_weight'))['left_weight']
                    if left_weight > single_material_weight:
                        attrs['tank_data'].update({'msg': '同物料未使用完, 不能扫码'})
                        attrs['status'] = 2
                    else:
                        # 剩余物料 < 单车需要物料
                        # 上一条计划剩余量判定
                        pre_material = LoadTankMaterialLog.objects.filter(bra_code=bra_code).first()
                        # 料框表中无该条码信息
                        if not pre_material:
                            attrs['tank_data'].update({'actual_weight': 0, 'adjust_left_weight': total_weight,
                                                       'single_need': single_material_weight})
                            attrs['status'] = 1
                        # 存在该条码信息(其他计划使用过)
                        else:
                            # 未用完
                            if pre_material.adjust_left_weight != 0:
                                attrs['tank_data'].update({'actual_weight': pre_material.actual_weight,
                                                           'real_weight': pre_material.real_weight,
                                                           'pre_material': pre_material,
                                                           'variety': pre_material.variety,
                                                           'adjust_left_weight': pre_material.adjust_left_weight,
                                                           'single_need': single_material_weight})
                                attrs['status'] = 1
                            # 已用完(异常扫码)
                            else:
                                attrs['tank_data'].update({'msg': '该物料条码已无剩余量,请扫新条码'})
                                attrs['status'] = 2
        try:
            resp = requests.post(url=settings.AUXILIARY_URL + 'api/v1/production/current_weigh/', data=attrs, timeout=5)
        except Exception as e:
            logger.error('群控服务器错误！')
            raise serializers.ValidationError(e.args[0])
        if material_error_msg:
            raise serializers.ValidationError(material_error_msg)
        msg = attrs['tank_data'].pop('msg')
        if msg:
            raise serializers.ValidationError(msg)
        return attrs

    def create(self, validated_data):
        tank_data = validated_data.get('tank_data')
        plan_classes_uid = validated_data.get('plan_classes_uid')
        trains = validated_data.get('trains')
        pre_material = tank_data.pop('pre_material', '')
        # 上一计划的条码物料归零(同计划中同物料的先一物料扣重时归0)
        if pre_material:
            pre_material.actual_weight = pre_material.init_weight
            pre_material.adjust_left_weight = 0
            pre_material.real_weight = 0
            pre_material.useup_time = datetime.now()
            pre_material.save()
        instance = LoadTankMaterialLog.objects.create(**tank_data)
        # 判断补充进料后是否能进上辅机
        fml = FeedingMaterialLog.objects.using('SFJ').filter(plan_classes_uid=plan_classes_uid, trains=int(trains)).last()
        if fml and fml.add_feed_result == 1:
            # 请求进料判断接口
            try:
                resp = requests.post(url=settings.AUXILIARY_URL + 'api/v1/production/handle_feed/', timeout=5,
                                     data=validated_data)
                content = json.loads(resp.content.decode())
                if content['success']:
                    logger.info('扫码补料后调用接口成功')
                else:
                    logger.error('扫码补料后调用接口时不可进料')
            except:
                logger.error('扫码补料后调用接口时群控服务器错误！')
        return instance

    class Meta:
        model = FeedingMaterialLog
        fields = ('plan_classes_uid', 'bra_code', 'batch_classes', 'batch_group', 'trains')


class ReplaceMaterialSerializer(BaseModelSerializer):

    class Meta:
        model = ReplaceMaterial
        fields = '__all__'


class ReturnRubberSerializer(BaseModelSerializer):
    print_username = serializers.ReadOnlyField(source='last_updated_user.username', help_text='打印员')

    def create(self, validated_data):
        now_date = datetime.now().replace(microsecond=0)
        classes_dict = {'早班': '1', '中班': '2', '夜班': '3'}
        # 获取班次班组
        batch_class = '早班' if '08:00:00' < str(now_date)[-8:] < '20:00:00' else '夜班'
        record = WorkSchedulePlan.objects.filter(plan_schedule__day_time=str(now_date)[:10], classes__global_name=batch_class,
                                                 plan_schedule__work_schedule__work_procedure__global_name='密炼').first()
        batch_group = record.group.global_name
        # 生成条码
        prefix_code = f"AAJ1Z20{now_date.date().strftime('%Y%m%d')}{classes_dict[batch_class]}"
        max_code = ReturnRubber.objects.filter(bra_code__startswith=prefix_code).aggregate(max_code=Max('bra_code'))['max_code']
        bra_code = prefix_code + ("%04d" % (int(max_code[-4:]) + 1) if max_code else '0001')
        validated_data.update({'batch_class': batch_class, 'batch_group': batch_group, 'bra_code': bra_code,
                               'created_user': self.context['request'].user})
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data.update({'status': 1, 'last_updated_user': self.context['request'].user,
                               'last_updated_date': datetime.now()})
        return super().update(instance, validated_data)

    class Meta:
        model = ReturnRubber
        fields = '__all__'
        read_only_fields = ['bra_code', 'batch_group', 'batch_class']


class ToleranceRuleSerializer(BaseModelSerializer):
    distinguish_name = serializers.ReadOnlyField(source='distinguish.keyword_name')
    project_name = serializers.ReadOnlyField(source='project.keyword_name')

    def validate(self, attrs):
        standard_error = attrs.get('standard_error')
        small_handle = attrs.get('small_handle')
        small_num = attrs.get('small_num')
        big_num = attrs.get('big_num')
        if standard_error < 0:
            raise serializers.ValidationError('容许差值应为正数')
        if small_handle:
            if small_num < 0 or big_num < 0 or small_num > big_num:
                raise serializers.ValidationError('两侧数字未填全或左侧数字大于右侧数字')
        return attrs

    def to_representation(self, instance):
        res = super().to_representation(instance)
        res['handle_standard_error'] = f'{instance.handle.keyword_name}{str(instance.standard_error)}{instance.unit}'
        return res

    class Meta:
        model = ToleranceRule
        fields = '__all__'


class EquipOperationLogSerializer(BaseModelSerializer):
    class Meta:
        model = EquipOperationLog
        fields = '__all__'
        read_only_fields = COMMON_READ_ONLY_FIELDS


class BatchingClassesEquipPlanSerializer(BaseModelSerializer):
    dev_type_name = serializers.CharField(source='batching_class_plan.weigh_cnt_type'
                                                 '.product_batching.dev_type.category_name', read_only=True)
    product_no = serializers.CharField(source='batching_class_plan.weigh_cnt_type.'
                                              'product_batching.stage_product_batch_no',
                                       read_only=True)
    product_factory_date = serializers.CharField(source='batching_class_plan.work_schedule_plan.plan_schedule.day_time',
                                                 read_only=True)
    plan_trains = serializers.IntegerField(source='packages', read_only=True)
    classes = serializers.CharField(source='batching_class_plan.work_schedule_plan.classes.global_name', read_only=True)
    finished_trains = serializers.SerializerMethodField(read_only=True)
    plan_batching_uid = serializers.ReadOnlyField(source='batching_class_plan.plan_batching_uid')
    name = serializers.ReadOnlyField(source='batching_class_plan.weigh_cnt_type.name')

    @staticmethod
    def get_finished_trains(obj):
        finished_trains = WeightPackageLog.objects.filter(plan_batching_uid=obj.batching_class_plan.plan_batching_uid
                                                          ).aggregate(trains=Max('package_fufil'))['trains']
        return finished_trains if finished_trains else 0

    class Meta:
        model = BatchingClassesEquipPlan
        fields = '__all__'


class WeightBatchingLogSerializer(BaseModelSerializer):
    created_username = serializers.CharField(source='created_user.username')

    class Meta:
        model = WeightBatchingLog
        fields = ('id', 'tank_no', 'material_no', 'material_name', 'bra_code', 'created_date', 'status', 'scan_material',
                  'created_username')


class WeightBatchingLogCreateSerializer(BaseModelSerializer):

    def validate(self, attr):
        equip_no = attr['equip_no']
        dev_type = attr['dev_type']
        bra_code = attr['bra_code']
        batch_classes = attr['batch_classes']
        batch_group = attr['batch_group']
        location_no = attr['location_no']
        # 查原材料出库履历查到原材料物料编码
        try:
            res = material_out_barcode(bra_code)
        except Exception as e:
            if settings.DEBUG:
                res = None
            else:
                raise serializers.ValidationError(e)
        material_name = material_no = ''
        attr['scan_material'] = res.get('WLMC')
        material_name_set = set(ERPMESMaterialRelation.objects.filter(
            zc_material__wlxxid=res['WLXXID'],
            use_flag=True
        ).values_list('material__material_name', flat=True))
        if not material_name_set:
            raise serializers.ValidationError('该物料未与MES原材料建立绑定关系！')
        # 机台计划配方的所有物料名
        try:
            date_now = datetime.now().date()
            date_before = date_now - timedelta(days=1)
            date_now_planid = ''.join(str(date_now).split('-'))[2:]
            date_before_planid = ''.join(str(date_before).split('-'))[2:]
            all_recipe = Plan.objects.using(equip_no).filter(
                Q(planid__startswith=date_now_planid) | Q(planid__startswith=date_before_planid),
                state__in=['运行中', '等待']).all().values_list('recipe', flat=True)
        except:
            raise serializers.ValidationError('称量机台{}错误'.format(equip_no))
        if not all_recipe:
            raise serializers.ValidationError('机台{}无进行中或已完成的配料计划'.format(equip_no))
        materials = set(RecipeMaterial.objects.using(equip_no).filter(recipe_name__in=set(all_recipe))
                        .values_list('name', flat=True))
        comm_material = list(material_name_set & materials)
        if comm_material:
            material_name = comm_material[0]
            material_no = comm_material[0]
        # else:
        #     raise serializers.ValidationError('所扫物料不在机台{}所有配料计划配方中'.format(equip_no))
        attr['batch_time'] = datetime.now()
        # 扫码物料不在当日计划配方对应原材料中
        if not material_name:
            attr['status'] = 2
            attr['tank_no'] = ''
            attr['failed_reason'] = '不在称量计划内, 无法开门'
        else:
            # 从称量系统同步料罐状态到mes表中
            try:
                tank_status_sync = TankStatusSync(equip_no=equip_no)
                tank_status_sync.sync()
            except:
                raise serializers.ValidationError('mes同步称量系统{}料罐状态失败'.format(equip_no))
            # 扫码物料与所有料罐不一致
            feed_info = WeightTankStatus.objects.filter(equip_no=equip_no, use_flag=True, material_name=material_name)
            if not feed_info:
                attr['status'] = 2
                attr['tank_no'] = ''
                attr['failed_reason'] = '没有对应的料罐, 无法开门'
            else:
                single_tank = feed_info.first()
                if single_tank.status == 2:
                    attr['status'] = 2
                    attr['tank_no'] = ''
                    attr['failed_reason'] = '料罐处于高位, 无法开门'
                else:
                    attr['tank_no'] = single_tank.tank_no
        attr['material_name'] = material_name
        attr['material_no'] = material_no
        attr['created_user'] = self.context['request'].user
        return attr

    class Meta:
        model = WeightBatchingLog
        fields = ('equip_no', 'bra_code', 'batch_classes', 'batch_group', 'dev_type', 'location_no')
        read_only_fields = COMMON_READ_ONLY_FIELDS


class FeedingLogSerializer(BaseModelSerializer):
    class Meta:
        model = FeedingLog
        fields = ('feeding_port', 'material_name', 'created_date')
        read_only_fields = ('created_date',)


class WeightTankStatusSerializer(BaseModelSerializer):
    tank_no = serializers.CharField(max_length=64, help_text='料罐编码',
                                    validators=[UniqueValidator(queryset=WeightTankStatus.objects.all(),
                                                                message='该料罐编号已存在！')])

    class Meta:
        model = WeightTankStatus
        fields = '__all__'
        read_only_fields = COMMON_READ_ONLY_FIELDS


class WeightPackageLogCreateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(write_only=True, help_text='行标')
    manual_infos = serializers.ListField(help_text="""人工配物料信息[{"manual_type": "manual_single", "manual_id":[1, 2, 3]},
                                                                   {"manual_type": "manual", "manual_id":[1, 2, 3]}]""", write_only=True, default=[])

    def validate(self, attrs):
        id = attrs.pop('id')
        record = attrs.get('record')
        print_begin_trains = attrs['print_begin_trains']
        package_count = attrs['package_count']
        plan_weight_uid = attrs['plan_weight_uid']
        product_no = attrs['product_no']
        equip_no = attrs['equip_no']
        package_fufil = attrs['package_fufil']
        batch_classes = attrs['batch_classes']
        dev_type = attrs['dev_type']
        print_flag = attrs.get('print_flag')
        print_count = attrs.get('print_count', 1)
        plan_weight = attrs['plan_weight']
        batch_group = attrs['batch_group']
        package_plan_count = attrs['package_plan_count']
        merge_flag = attrs.get('merge_flag', False)
        status = attrs['status']
        manual_infos = attrs.get('manual_infos')
        # 需要合包但没有扫入手工配料
        if merge_flag and not manual_infos:
            raise serializers.ValidationError('称量计划设置了合包, 请扫码加入人工配料')
        # 打印数量判断
        if print_count <= 0 or print_count > package_count or not isinstance(print_count, int):
            raise serializers.ValidationError('打印张数需小于等于配置数量')
        attrs['material_no'] = re.split(r'\(|\（|\[', product_no)[0]
        attrs['material_name'] = attrs['material_no']
        # 配料时间
        batch_time = ReportBasic.objects.using(equip_no).get(planid=plan_weight_uid, actno=print_begin_trains).starttime
        # 计算有效期
        single_expire_record = PackageExpire.objects.filter(product_no=product_no)
        if not single_expire_record:
            single_date = PackageExpire.objects.create(**{'product_no': product_no, 'product_name': product_no,
                                                          'update_user': 'system', 'update_date': datetime.now().date()})
        else:
            single_date = single_expire_record.first()
        days = single_date.package_fine_usefullife if equip_no.startswith('F') else single_date.package_sulfur_usefullife
        attrs.update({'bra_code': '', 'begin_trains': print_begin_trains, 'print_flag': 1, 'status': 'N',
                      'end_trains': print_begin_trains + package_count - 1, 'noprint_count': package_fufil - package_count,
                      'expire_days': days, 'batch_time': batch_time})
        # # 履历表中数据重新打印
        # last_print_record = WeightPackageLog.objects.filter(id=id)
        # if status == 'Y':
        #     last_print = last_print_record.first()
        #     # 修改了起始车次或者包数的重新打印, 新增一条记录到履历表中
        #     if print_begin_trains != last_print.print_begin_trains or package_count != last_print.package_count:
        #         # 其实车次配料时间
        #         attrs.update(data)
        #     else:
        #         last_print.print_flag = 1
        #         last_print.print_count = print_count
        #         attrs['obj'] = last_print
        # else:
        #     if last_print_record and print_flag == 1 and print_begin_trains == last_print_record.first().print_begin_trains\
        #             and package_count == last_print_record.first().package_count:
        #         raise serializers.ValidationError('已下发打印，等待打印机打印')
        #     # 生产计划中数据新增打印
        #     # 起始车次和数量的判断
        #     if print_begin_trains == 0 or print_begin_trains > package_fufil - 1:
        #         raise serializers.ValidationError('起始车次不在{}-{}的可选范围'.format(1, package_fufil - 1))
        #     if package_count > package_fufil - print_begin_trains + 1 or package_count <= 0:
        #         raise serializers.ValidationError('配置数量不在{}-{}的可选范围'.format(1, package_fufil - print_begin_trains + 1))
        #     attrs.update(data)
        # if 'obj' not in attrs:
        #     # 生成条码: 机台（3位）+年月日（8位）+班次（1位）+自增数（4位） 班次：1早班  2中班  3晚班
        #     # 履历表中无数据则初始为1, 否则获取最大数+1
        #     prefix = f"{equip_no}{''.join(batch_time[:10].split('-'))}"
        #     max_code = WeightPackageLog.objects.filter(bra_code__startswith=prefix).aggregate(max_code=Max('bra_code'))['max_code']
        #     incr_num = 1 if not max_code else int(max_code[-4:]) + 1
        #     map_list = {"早班": '1', "中班": '2', "夜班": '3'}
        #     train_batch_classes = map_list.get(batch_classes)
        #     bra_code = equip_no + ''.join(batch_time[:10].split('-')) + train_batch_classes + '%04d' % incr_num
        #     attrs.update({'bra_code': bra_code})
        # 生成条码: 机台（3位）+年月日（8位）+班次（1位）+自增数（4位） 班次：1早班  2中班  3晚班
        # 履历表中无数据则初始为1, 否则获取最大数+1
        prefix = f"{equip_no}{''.join(batch_time[:10].split('-'))}"
        max_code = WeightPackageLog.objects.filter(bra_code__startswith=prefix).aggregate(max_code=Max('bra_code'))[
            'max_code']
        incr_num = 1 if not max_code else int(max_code[-4:]) + 1
        map_list = {"早班": '1', "中班": '2', "夜班": '3'}
        train_batch_classes = map_list.get(batch_classes)
        bra_code = equip_no + ''.join(batch_time[:10].split('-')) + train_batch_classes + '%04d' % incr_num
        attrs.update({'bra_code': bra_code})
        return attrs

    # def create(self, validated_data):
    #     if 'obj' in validated_data:
    #         instance = validated_data['obj']
    #         instance.save()
    #     else:
    #         instance = WeightPackageLog.objects.create(**validated_data)
    #     return instance
    def create(self, validated_data):
        manual_infos = validated_data.pop('manual_infos')
        instance = WeightPackageLog.objects.create(**validated_data)
        # 机配物料关联人工配料
        for i in manual_infos:
            db_obj = WeightPackageSingle if 'single' in i['manual_type'] else WeightPackageManual
            db_obj.objects.filter(id__in=i['manual_id']).update(**{"weight_package_id": instance.id})
        return instance

    class Meta:
        model = WeightPackageLog
        fields = ['plan_weight_uid', 'product_no', 'plan_weight', 'dev_type', 'id', 'record', 'print_flag',
                  'package_count', 'print_begin_trains', 'noprint_count', 'package_fufil', 'package_plan_count',
                  'equip_no', 'batch_group', 'batch_classes', 'status', 'print_count', 'merge_flag', 'manual_infos']


class WeightPackageLogUpdateSerializer(serializers.ModelSerializer):
    print_flag = serializers.IntegerField(write_only=True)

    def validate(self, attrs):
        print_flag = attrs.get('print_flag')
        if not isinstance(print_flag, int):
            raise serializers.ValidationError('回传打印状态应为整数')
        attrs['status'] = 'Y'
        attrs['print_count'] = 1
        return attrs

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)

    class Meta:
        model = WeightPackageLog
        fields = ['print_flag']


class WeightPackageLogSerializer(BaseModelSerializer):
    # batch_time = serializers.DateTimeField(format='%Y-%m-%d', help_text='配料日期')

    class Meta:
        model = WeightPackageLog
        fields = ['id', 'plan_weight_uid', 'product_no', 'plan_weight', 'dev_type', 'batch_time', 'bra_code', 'record',
                  'package_count', 'print_begin_trains', 'noprint_count', 'package_fufil', 'package_plan_count',
                  'equip_no', 'print_flag', 'batch_group', 'status', 'begin_trains', 'end_trains', 'batch_classes']


class WeightPackageManualSerializer(BaseModelSerializer):
    dev_type_name = serializers.ReadOnlyField(source='dev_type.category_name', help_text='机型名称')
    manual_details = serializers.ListField(help_text='单配物料详情列表', write_only=True, default=[])

    def to_representation(self, instance):
        res = super().to_representation(instance)
        # 获取有效期
        expire_datetime = ''
        expire_record = PackageExpire.objects.filter(product_no=f"{instance.product_no}({instance.dev_type})").first()
        if expire_datetime:
            expire_day = expire_record.package_fine_usefullife if 'F' in instance.batching_equip else expire_record.package_sulfur_usefullife
            expire_datetime = expire_datetime if expire_day == 0 else str(instance.created_date + timedelta(days=expire_day))
        res.update({'manual_details': list(instance.package_details.all().annotate(batch_time=F('manual_details__created_date')).values('material_name', 'standard_weight', 'tolerance', 'batch_type', 'batch_time')), 'expire_datetime': expire_datetime})
        return res

    @atomic
    def create(self, validated_data):
        map_list = {"早班": '1', "中班": '2', "夜班": '3'}
        now_date = datetime.now().replace(microsecond=0)
        batching_equip = validated_data.get('batching_equip')
        manual_details = validated_data.pop('manual_details', [])
        # 班次, 班组
        batch_class = '早班' if '08:00:00' <= str(now_date)[-8:] < '20:00:00' else '夜班'
        record = WorkSchedulePlan.objects.filter(plan_schedule__day_time=str(now_date.date()),
                                                 classes__global_name=batch_class,
                                                 plan_schedule__work_schedule__work_procedure__global_name='密炼').first()
        batch_group = record.group.global_name
        # 条码
        prefix = f"M{batching_equip}{now_date.date().strftime('%Y%m%d')}{map_list.get(batch_class)}"
        max_code = WeightPackageManual.objects.filter(bra_code__startswith=prefix).aggregate(max_code=Max('bra_code'))['max_code']
        bra_code = prefix + ('%04d' % (int(max_code[-4:]) + 1) if max_code else '0001')
        total_weight = 0
        for item in manual_details:
            total_weight += item.get('standard_weight', 0)
        # 根据重量查询公差
        distinguish_name, project_name = ["细料称量", "整包细料重量"] if batching_equip.startswith('F') else ["硫磺称量", "整包硫磺重量"]
        rule = ToleranceRule.objects.filter(distinguish__keyword_name=distinguish_name, project__keyword_name=project_name,
                                            small_num__lt=total_weight, big_num__gte=total_weight).first()
        tolerance = f"{rule.handle.keyword_name}{rule.standard_error}{rule.unit}" if rule else ""
        single_weight = f"{str(total_weight)}{tolerance}"
        validated_data.update({'created_user': self.context['request'].user, 'batch_class': batch_class,
                               'batch_group': batch_group, 'bra_code': bra_code, 'single_weight': single_weight})
        instance = super().create(validated_data)
        # 添加单配物料详情
        for item in manual_details:
            item['manual_details_id'] = instance.id
            WeightPackageManualDetails.objects.create(**item)
        return instance

    def update(self, instance, validated_data):
        validated_data.update({'print_flag': True, 'last_updated_date': datetime.now(),
                               'last_updated_user': self.context['request'].user, 'print_datetime': datetime.now()})
        return super().update(instance, validated_data)

    class Meta:
        model = WeightPackageManual
        fields = '__all__'
        read_only_fields = ['bra_code', 'single_weight', 'batch_group', 'batch_class']


class WeightPackageSingleSerializer(BaseModelSerializer):
    dev_type_name = serializers.ReadOnlyField(source='dev_type.category_name', help_text='机型名称')

    def to_representation(self, instance):
        res = super().to_representation(instance)
        res['expire_datetime'] = str(instance.created_date + timedelta(days=instance.expire_day))
        return res

    @atomic
    def create(self, validated_data):
        map_list = {"早班": '1', "中班": '2', "夜班": '3'}
        now_date = datetime.now().replace(microsecond=0)
        material_name, single_weight = validated_data.get('material_name'), validated_data.get('single_weight')
        # 班次, 班组
        batch_class = '早班' if '08:00:00' <= str(now_date)[-8:] < '20:00:00' else '夜班'
        record = WorkSchedulePlan.objects.filter(plan_schedule__day_time=str(now_date.date()),
                                                 classes__global_name=batch_class,
                                                 plan_schedule__work_schedule__work_procedure__global_name='密炼').first()
        batch_group = record.group.global_name
        # 条码
        prefix = f"MC{now_date.date().strftime('%Y%m%d')}{map_list.get(batch_class)}"
        max_code = WeightPackageSingle.objects.filter(bra_code__startswith=prefix).aggregate(max_code=Max('bra_code'))['max_code']
        bra_code = prefix + ('%04d' % (int(max_code[-4:]) + 1) if max_code else '0001')
        # 单物料所有量程公差
        rule = ToleranceRule.objects.filter(distinguish__re_str__icontains=material_name).first()
        tolerance = f"{rule.handle.keyword_name}{rule.standard_error}{rule.unit}" if rule else ""
        single_weight = f"{single_weight}{tolerance}"
        validated_data.update({'created_user': self.context['request'].user, 'batch_class': batch_class,
                               'batch_group': batch_group, 'bra_code': bra_code, 'single_weight': single_weight})
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data.update({'print_flag': True, 'last_updated_date': datetime.now(),
                               'last_updated_user': self.context['request'].user, 'print_datetime': datetime.now()})
        return super().update(instance, validated_data)

    class Meta:
        model = WeightPackageSingle
        fields = '__all__'
        read_only_fields = ['bra_code', 'batch_group', 'batch_class']


class WeightPackagePlanSerializer(BaseModelSerializer):
    plan_weight_uid = serializers.ReadOnlyField(source='planid')
    product_no = serializers.ReadOnlyField(source='recipe')
    plan_weight = serializers.ReadOnlyField(default=0)
    batch_time = serializers.ReadOnlyField(default='')
    noprint_count = serializers.ReadOnlyField(source='actno')
    package_fufil = serializers.ReadOnlyField(source='actno')
    package_plan_count = serializers.ReadOnlyField(source='setno')
    dev_type = serializers.ReadOnlyField(default='')
    bra_code = serializers.ReadOnlyField(default='')
    record = serializers.ReadOnlyField(source='id')
    package_count = serializers.ReadOnlyField(default='')
    print_begin_trains = serializers.ReadOnlyField(default='')
    equip_no = serializers.ReadOnlyField(default='')
    print_flag = serializers.ReadOnlyField(default=0)
    batch_group = serializers.SerializerMethodField()
    status = serializers.ReadOnlyField(default='N')
    begin_trains = serializers.ReadOnlyField(default='')
    end_trains = serializers.ReadOnlyField(default='')
    batch_classes = serializers.ReadOnlyField(source='grouptime')

    def get_batch_group(self, obj):
        group = obj.grouptime if obj.grouptime != '中班' else ('早班' if '08:00:00' < obj.addtime[-8:] < '20:00:00' else '夜班')
        record = WorkSchedulePlan.objects.filter(plan_schedule__day_time=obj.date_time, classes__global_name=group,
                                                 plan_schedule__work_schedule__work_procedure__global_name='密炼').first()
        return record.group.global_name

    class Meta:
        model = Plan
        fields = ['id', 'plan_weight_uid', 'product_no', 'plan_weight', 'batch_time', 'noprint_count', 'package_fufil',
                  'print_flag', 'package_plan_count', 'dev_type', 'bra_code', 'record', 'package_count', 'status',
                  'print_begin_trains', 'equip_no', 'batch_group', 'begin_trains', 'end_trains', 'batch_classes']


class WeightPackageRetrieveLogSerializer(BaseModelSerializer):
    material_details = serializers.SerializerMethodField(read_only=True)

    @staticmethod
    def get_material_details(obj):
        return BatchingClassesPlan.objects.get(plan_batching_uid=obj.plan_batching_uid).weigh_cnt_type. \
            weight_details.filter(delete_flag=False).values('material__material_no',
                                                            'standard_weight',
                                                            'weigh_cnt_type__package_cnt')

    class Meta:
        model = WeightPackageLog
        fields = '__all__'


class WeightPackageUpdateLogSerializer(BaseModelSerializer):
    material_details = serializers.SerializerMethodField(read_only=True)

    @staticmethod
    def get_material_details(obj):
        return BatchingClassesPlan.objects.get(plan_batching_uid=obj.plan_batching_uid).weigh_cnt_type. \
            weight_details.filter(delete_flag=False).values('material__material_no',
                                                            'standard_weight',
                                                            'weigh_cnt_type__package_cnt')

    def update(self, instance, validated_data):
        instance.times += 1
        instance.save()
        return instance

    class Meta:
        model = WeightPackageLog
        fields = ('id', 'equip_no', 'plan_batching_uid', 'product_no', 'batch_classes', 'bra_code',
                  'batch_group', 'location_no', 'dev_type', 'begin_trains', 'end_trains', 'quantity',
                  'production_factory_date', 'production_classes', 'production_group', 'created_date',
                  'material_details')
        read_only_fields = ('equip_no', 'plan_batching_uid', 'product_no', 'batch_classes', 'bra_code',
                            'batch_group', 'location_no', 'dev_type', 'begin_trains', 'end_trains', 'quantity',
                            'production_factory_date', 'production_classes', 'production_group', 'created_date',
                            'material_details')


class WeightPackagePartialUpdateLogSerializer(BaseModelSerializer):

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        while 1:
            bra_code = generate_bra_code(instance.equip_no,
                                         instance.production_factory_date,
                                         instance.production_classes)
            if not WeightPackageLog.objects.filter(bra_code=bra_code).exists():
                break
        instance.bra_code = bra_code
        instance.save()
        return instance

    class Meta:
        model = WeightPackageLog
        fields = '__all__'
        read_only_fields = COMMON_READ_ONLY_FIELDS


class LoadMaterialLogListSerializer(serializers.ModelSerializer):
    mixing_finished = serializers.SerializerMethodField(help_text='混炼/终炼', read_only=True)
    product_no = serializers.ReadOnlyField(source='feed_log.product_no')
    created_date = serializers.DateTimeField(source='feed_log.feed_begin_time')
    trains = serializers.ReadOnlyField(source='feed_log.trains')
    production_factory_date = serializers.ReadOnlyField(source='feed_log.production_factory_date')
    production_classes = serializers.ReadOnlyField(source='feed_log.production_classes')
    equip_no = serializers.ReadOnlyField(source='feed_log.equip_no')
    created_username = serializers.ReadOnlyField(source='feed_log.created_username')

    def get_mixing_finished(self, obj):
        product_no = obj.feed_log.product_no
        if "FM" in product_no:
            return '终炼'
        else:
            return "混炼"

    class Meta:
        model = LoadMaterialLog
        fields = '__all__'


class WeightBatchingLogListSerializer(BaseModelSerializer):

    class Meta:
        model = WeightBatchingLog
        fields = '__all__'


"""
小料称量序列化器
"""


class MaterialInfoSerializer(serializers.ModelSerializer):
    equip_no = serializers.CharField(write_only=True, help_text='称量机台')

    def create(self, validated_data):
        equip_no = validated_data.pop('equip_no')
        validated_data['time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        try:
            instance = MaterialInfo.objects.using(equip_no).create(**validated_data)
        except ConnectionDoesNotExist:
            raise serializers.ValidationError('称量机台{}服务错误！'.format(equip_no))
        except Exception:
            raise
        return instance

    class Meta:
        model = MaterialInfo
        fields = '__all__'
        read_only_fields = ('time', 'remark')


class BinSerializer(serializers.ModelSerializer):

    class Meta:
        model = Bin
        fields = '__all__'


class PlanSerializer(serializers.ModelSerializer):
    equip_no = serializers.CharField(write_only=True, help_text='称量机台')

    def create(self, validated_data):
        equip_no = validated_data.pop('equip_no')
        last_group_plan = Plan.objects.using(equip_no).filter(date_time=validated_data['date_time'],
                                                              grouptime=validated_data['grouptime']
                                                              ).order_by('order_by').last()
        if last_group_plan:
            validated_data['order_by'] = last_group_plan.order_by + 1
        else:
            validated_data['order_by'] = 1
        validated_data['planid'] = datetime.now().strftime('%Y%m%d%H%M%S')[2:]
        validated_data['state'] = '等待'
        validated_data['actno'] = 0
        validated_data['addtime'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        try:
            instance = Plan.objects.using(equip_no).create(**validated_data)
        except ConnectionDoesNotExist:
            raise serializers.ValidationError('称量机台{}服务错误！'.format(equip_no))
        except Exception:
            raise
        ins = CLSystem(equip_no)
        ins.add_plan(instance.planid)
        return instance

    class Meta:
        model = Plan
        read_only_fields = ('planid', 'state', 'actno', 'order_by', 'addtime', 'starttime', 'stoptime', 'oper')
        fields = '__all__'


class PlanUpdateSerializer(serializers.ModelSerializer):
    action = serializers.IntegerField(help_text='动作 1：下达计划  2：计划重传  3：修改车次 4：计划停止', write_only=True)
    equip_no = serializers.CharField(write_only=True, help_text='称量机台')

    def update(self, instance, validated_data):
        action = validated_data['action']
        equip_no = validated_data['equip_no']
        ins = CLSystem(equip_no)
        if action == 1:
            ins.issue_plan(instance.planid, instance.recipe, instance.setno)
        elif action == 2:
            ins.reload_plan(instance.planid, instance.recipe)
        elif action == 3:
            setno = validated_data['setno']
            actno = instance.actno if instance.actno else 0
            if not setno:
                raise serializers.ValidationError('设定车次不可为空!')
            if setno <= actno:
                raise serializers.ValidationError('设定车次不能小于完成车次!')
            ins.update_trains(instance.planid, setno)
        elif action == 4:
            ins.stop(instance.planid)
        else:
            raise serializers.ValidationError('action参数错误！')
        return instance

    class Meta:
        model = Plan
        fields = ('id', 'setno', 'action', 'equip_no')


class RecipePreSerializer(serializers.ModelSerializer):

    class Meta:
        model = RecipePre
        fields = '__all__'


class ReportBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportBasic
        fields = '__all__'


class ReportWeightSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportWeight
        fields = '__all__'


class XLPlanCSerializer(serializers.ModelSerializer):
    dev_type = serializers.CharField(default='', help_text='生产机型')

    class Meta:
        model = Plan
        fields = ['id', 'recipe', 'setno', 'actno', 'state', 'dev_type', 'planid']


class XLPromptSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeightTankStatus
        fields = ['id', 'tank_no', 'material_name']


class PowderTankSettingSerializer(serializers.ModelSerializer):
    material_name = serializers.ReadOnlyField(source='material.material_name')

    class Meta:
        model = PowderTankSetting
        fields = ['id', 'equip_no', 'tank_no', 'material', 'bar_code', 'use_flag', 'material_name']


class OilTankSettingSerializer(serializers.ModelSerializer):
    material_name = serializers.ReadOnlyField(source='material.material_name')

    class Meta:
        model = OilTankSetting
        fields = ['id', 'tank_no', 'material', 'bar_code', 'use_flag', 'material_name']


class CarbonTankSetSerializer(serializers.ModelSerializer):

    class Meta:
        model = CarbonTankFeedWeightSet
        fields = '__all__'


class CarbonTankSetUpdateSerializer(serializers.ModelSerializer):

    def validate(self, attrs):
        attrs['update_user'] = self.context['request'].user.username
        attrs['update_datetime'] = datetime.now().date()
        return attrs

    class Meta:
        model = CarbonTankFeedWeightSet
        fields = ['tank_capacity_type', 'tank_capacity', 'feed_capacity_low', 'feed_capacity_mid']


class FeedingOperationLogSerializer(serializers.ModelSerializer):

    class Meta:
        model = FeedingOperationLog
        fields = '__all__'


class CarbonFeedingPromptSerializer(serializers.ModelSerializer):

    class Meta:
        model = CarbonTankFeedingPrompt
        fields = '__all__'


class CarbonFeedingPromptCreateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(allow_null=True)

    def create(self, validated_data):
        record_id = validated_data.pop('id')
        equip_id = validated_data.get('equip_id')
        tank_no = validated_data.get('tank_no')
        changed = validated_data.get('feed_change')
        # 没有id表示初次加载
        if record_id:
            # 更新旧罐号信息: 少变多按id删除数据, 多变少按罐号删除数据
            feed_change = CarbonTankFeedingPrompt.objects.filter(equip_id=equip_id, tank_no=tank_no).count()
            if changed >= feed_change:
                CarbonTankFeedingPrompt.objects.filter(id=record_id).delete()
            else:
                CarbonTankFeedingPrompt.objects.filter(equip_id=equip_id, tank_no=tank_no).delete()
        instance = CarbonTankFeedingPrompt.objects.create(**validated_data)
        return instance

    class Meta:
        model = CarbonTankFeedingPrompt
        fields = ['id', 'equip_id', 'tank_no', 'tank_capacity_type', 'tank_material_name', 'tank_level_status',
                  'feedcapacity_weight_set', 'feedport_code', 'feed_material_name', 'feed_status', 'feed_change',
                  'is_no_port_one', 'ex_warehouse_flag', 'wlxxid']
