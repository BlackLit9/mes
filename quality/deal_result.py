from quality.models import MaterialDealResult, MaterialTestOrder, MaterialTestResult, LevelResult
from production.models import PalletFeedbacks
from django.db.transaction import atomic
from django.db.models import Max


@atomic()
def synthesize_to_material_deal_result(mdr_lot_no):
    """等级综合判定"""
    mdr_dict = {}
    mdr_dict['lot_no'] = mdr_lot_no
    mto_set = MaterialTestOrder.objects.filter(lot_no=mdr_lot_no).all()
    level_list = []
    for mto_obj in mto_set:
        mrt_list = mto_obj.order_results.all().values('data_point_name').annotate(max_test_time=Max('test_times'))
        for mrt_dict in mrt_list:
            mrt_dict_obj = MaterialTestResult.objects.filter(material_test_order=mto_obj,
                                                             data_point_name=mrt_dict['data_point_name'],
                                                             test_times=mrt_dict['max_test_time']).last()
            level_list.append(mrt_dict_obj)
    max_mtr = level_list[0]
    # 找到检测次数最多的几条 每一条的等级进行比较选出做大的
    reason = ''
    exist_data_point_indicator = True
    for mtr_obj in level_list:
        if not mtr_obj.data_point_indicator:
            reason = reason + f'第{mtr_obj.material_test_order.actual_trains}车次{mtr_obj.data_point_name}指标{mtr_obj.value}数据错误！，\n'
            exist_data_point_indicator = False
        else:
            if mtr_obj.data_point_indicator.level > max_mtr.data_point_indicator.level:
                max_mtr = mtr_obj
            # 判断value值与指标上下限
            if mtr_obj.data_point_indicator.result == "合格":
                continue
            if mtr_obj.value < mtr_obj.data_point_indicator.lower_limit:
                reason = reason + f'第{mtr_obj.material_test_order.actual_trains}车次{mtr_obj.data_point_name}指标{mtr_obj.value}低于下限{mtr_obj.data_point_indicator.lower_limit}，\n'
            if mtr_obj.value > mtr_obj.data_point_indicator.upper_limit:
                reason = reason + f'第{mtr_obj.material_test_order.actual_trains}车次{mtr_obj.data_point_name}指标{mtr_obj.value}高于上限{mtr_obj.data_point_indicator.upper_limit}，\n'
            if mtr_obj.data_point_indicator.lower_limit <= mtr_obj.value <= mtr_obj.data_point_indicator.upper_limit:
                reason = reason + f'第{mtr_obj.material_test_order.actual_trains}车次{mtr_obj.data_point_name}指标{mtr_obj.value}在{mtr_obj.data_point_indicator.lower_limit}至{mtr_obj.data_point_indicator.upper_limit}区间内，\n'

    # 在生产模块里找开始生产时间
    pfb_obj = PalletFeedbacks.objects.filter(lot_no=mdr_lot_no).last()
    if exist_data_point_indicator:
        mdr_dict['level'] = max_mtr.data_point_indicator.level
        mdr_dict['deal_result'] = max_mtr.data_point_indicator.result
        mdr_dict['production_factory_date'] = pfb_obj.begin_time
    else:  # 数据不在上下限范围内，这个得前端做好约束
        lr_obj = LevelResult.objects.filter(delete_flag=False).all().order_by('level').last()
        mdr_dict['deal_result'] = lr_obj.deal_result  # 要确定合格和不合格对应的等级 已经是否只有合格和不合格这两种情况
        mdr_dict['level'] = lr_obj.level
        if pfb_obj:
            mdr_dict['production_factory_date'] = pfb_obj.begin_time
        else:
            mdr_dict['production_factory_date'] = '1212-12-12'

    mdr_dict['reason'] = reason
    mdr_dict['status'] = '待处理'

    iir_mdr_obj = MaterialDealResult.objects.filter(lot_no=mdr_lot_no).order_by('test_time').last()
    if iir_mdr_obj:
        mdr_dict['test_time'] = iir_mdr_obj.test_time + 1
        MaterialDealResult.objects.filter(lot_no=mdr_lot_no).update(status='复测')
        MaterialDealResult.objects.create(**mdr_dict)
    else:
        mdr_dict['test_time'] = 1
        MaterialDealResult.objects.create(**mdr_dict)
