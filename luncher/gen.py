#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import sys, os

sys.path.append(os.path.abspath("../"))

import gen_code_enum as gen_code
import gen_jpa as gen
import config

arguments = sys.argv
gen_targets = []
category_targets = []
system = arguments[1]

for gt in arguments[1:]:
    if gt == '-h' or gt == '--help':
        print(config.__HELP__)
        exit(0)
    if gt.startswith("-C"):
        category_targets.append(gt[2:])
    elif gt.startswith("-T"):
        gen_targets.append(gt[2:])

if system != 'admin' and system != 'batch' and system != 'app':
    print('Please enter the target system. (admin, batch, app)');
    exit(0)

print("Generator target file              : ", 'ALL' if len(gen_targets) == 0 else gen_targets)
print("Generator target category(package) : ", 'ALL' if len(category_targets) == 0 else category_targets)

src_path = '/Users/yjkim/project_source/_luckybite/luckybite_platform/'
_src_sub_path = {
    'core': 'platform-core/src/main/java/',
    'base': 'platform-base/' + system + '-base/src/main/java/',
}
_package_path_info = gen.PackagePathInfo(
    project_src_path=src_path + _src_sub_path['base']
    , core_enum_path=src_path + _src_sub_path['core'] + 'com/techlabs/platform/core/data'
    , core_convertor_path=src_path + _src_sub_path['core'] + 'com/techlabs/platform/core/gen/converter'
    , core_entity_path=src_path + _src_sub_path['core'] + 'com/techlabs/platform/core/gen/entity'
    , core_entity_id_path=src_path + _src_sub_path['core'] + 'com/techlabs/platform/core/gen/id'
    , core_repository_path=src_path + _src_sub_path['base'] + 'com/techlabs/' + system + '/base/gen/repository'
    , core_convertor_annotation_path=src_path + _src_sub_path['core'] + 'com/techlabs/platform/core/gen'
    , core_entity_package='com.techlabs.platform.core.gen.entity'
    , core_entity_id_package='com.techlabs.platform.core.gen.id'
    , core_repository_package='com.techlabs.' + system + '.base.gen.repository'
    , core_converter_package='com.techlabs.platform.core.gen.converter'
    , core_convertor_annotation_package='com.techlabs.platform.core.gen'
    , base_entity_package='com.techlabs.platform.core.domain.BaseDomain'
    , entity_package='com.techlabs.' + system + '.base.entity'
    , repository_package='com.techlabs.' + system + '.base.repository'
    , enum_package='com.techlabs.platform.core.data.PlatformCodes'
)
_column_info = gen.ColumnInfo(
    is_remove_cd=False
    , is_remove_yn=False
    , is_use_date_format=True
    , is_use_time_format=True
    , base_domain_columns=['reg_dt', 'reg_id', 'upd_dt', 'upd_id']
    , insert_dt_columns=['reg_dt']
    , update_dt_columns=['upd_dt']
    , delete_columns=['is_deleted']
)
_code_info = gen_code.CodeColumnName(
    code_column='cd_id',
    pcode_column='cd_pid',
    name_column='cd_nm',
    name_disp_column='cd_nm',
    enum_name_column='cd_value',
    value_1_column='lang_key',
    value_2_column='data_list',
)
_code_group_info = gen_code.CodeGroupColumnName(
    gcode_column='cd_id',
    gname_column='cd_nm',
    gname_disp_column='cd_nm',
    genum_name_column='cd_value',
    value_1_column='lang_key',
    value_2_column='data_list',
)
gen.set_base_info(_package_path_info, _column_info)
gen_code.set_base_info(_code_info, _code_group_info)


# gen.generate_mybatis(gen_targets,'테이블명', category, repository_package, entity_package, {
#     'pk': '시퀀스명'
#     , 'interface': 'package path'
#     , '필드명': {
#         'field_name': ''
#         , 'java_type': ''
#         , 'json_props': ''
#         , 'sequence_name': ''
#         , 'convert_type': ''
#     }
# })
def generate_jpa_files():
    #########################################
    repository_base_pkg = _package_path_info.repository_package
    entity_base_pkg = _package_path_info.entity_package
    dynamic_cd_field_attr = {
        'java_type': 'com.techlabs.platform.core.domain.DynamicCode'
        , 'convert_type': 'com.techlabs.platform.core.processor.converter.TargetDynamicCodeConverter'
    }
    worker_field_attr = {
        'java_type': 'com.techlabs.platform.core.domain.IWorker'
        , 'convert_type': 'com.techlabs.platform.core.processor.converter.TargetWorkerConverter'
    }
    #########################################

    category = 'bizapp'
    if len(category_targets) == 0 or category in category_targets:
        repository_package = repository_base_pkg + "." + category
        entity_package = entity_base_pkg + "." + category

        gen.generate_jpa_files(gen_targets, 'business', category, repository_package, entity_package,
                               {'biz_id': {'sequence_name': 'business_biz_id_seq'}})
        gen.generate_jpa_files(gen_targets, 'business_member', category, repository_package, entity_package, {
            'invite_id': worker_field_attr,
        })
        gen.generate_jpa_files(gen_targets, 'business_work_history', category, repository_package, entity_package,
                               {'history_id': {'sequence_name': 'business_work_history_history_id_seq'}})

        gen.generate_jpa_files(gen_targets, 'app', category, repository_package, entity_package, {
            'app_id': {'sequence_name': 'app_app_id_seq'},
            'category_cd': dynamic_cd_field_attr
        })
        gen.generate_jpa_files(gen_targets, 'app_menu', category, repository_package, entity_package)
        gen.generate_jpa_files(gen_targets, 'app_ui', category, repository_package, entity_package)
        gen.generate_jpa_files(gen_targets, 'app_member', category, repository_package, entity_package)
        gen.generate_jpa_files(gen_targets, 'app_event', category, repository_package, entity_package)
        gen.generate_jpa_files(gen_targets, 'app_contents_point', category, repository_package, entity_package)
        gen.generate_jpa_files(gen_targets, 'app_cs', category, repository_package, entity_package, {
            'cs_id': {'sequence_name': 'app_cs_cs_id_seq'},
            'cs_type_cd': dynamic_cd_field_attr,
            'answer_id': worker_field_attr,
        })
        gen.generate_jpa_files(gen_targets, 'app_ad', category, repository_package, entity_package)
        gen.generate_jpa_files(gen_targets, 'app_store', category, repository_package, entity_package)
        gen.generate_jpa_files(gen_targets, 'app_work_history', category, repository_package, entity_package,
                               {'history_id': {'sequence_name': 'app_work_history_history_id_seq'}})
        gen.generate_jpa_files(gen_targets, 'app_contract_history', category, repository_package, entity_package)
        gen.generate_jpa_files(gen_targets, 'app_term', category, repository_package, entity_package)
        gen.generate_jpa_files(gen_targets, 'app_term_version', category, repository_package, entity_package,
                               {'term_ver': {'sequence_name': "app_term_version_term_ver_seq"}})
        gen.generate_jpa_files(gen_targets, 'app_faq', category, repository_package, entity_package,
                               {'faq_id': {'sequence_name': 'app_faq_faq_id_seq'}})
        gen.generate_jpa_files(gen_targets, 'app_point_interlock_config', category, repository_package, entity_package)


        gen.generate_jpa_files(gen_targets, 'app_special_point', category, repository_package, entity_package,
                               {'special_id': {'sequence_name': 'app_special_point_special_id_seq'}})
        gen.generate_jpa_files(gen_targets, 'app_special_point_contents_result', category, repository_package, entity_package)
        gen.generate_jpa_files(gen_targets, 'app_special_point_freq_log', category, repository_package, entity_package,
                               {'log_id': {'sequence_name': 'app_special_point_freq_log_log_id_seq'}})

    category = 'user'
    if len(category_targets) == 0 or category in category_targets:
        repository_package = repository_base_pkg + "." + category
        entity_package = entity_base_pkg + "." + category

        gen.generate_jpa_files(gen_targets, 'app_user', category, repository_package, entity_package,
                               {'user_id': {'sequence_name': "app_user_user_id_seq"}})
        gen.generate_jpa_files(gen_targets, 'app_user_withdraw', category, repository_package, entity_package,
                               {'history_id': {'sequence_name': 'app_user_withdraw_history_id_seq'}})
        gen.generate_jpa_files(gen_targets, 'app_user_event_partcpnt', category, repository_package, entity_package,
                               {'partcpnt_id': {'sequence_name': "app_user_event_partcpnt_partcpnt_id_seq"}})
        gen.generate_jpa_files(gen_targets, 'app_user_contents_partcpnt', category, repository_package, entity_package,
                               {'partcpnt_id': {'sequence_name': "app_user_contents_partcpnt_partcpnt_id_seq"}})
        gen.generate_jpa_files(gen_targets, 'app_user_saju', category, repository_package, entity_package)
        gen.generate_jpa_files(gen_targets, 'app_user_term_agree', category, repository_package, entity_package)
        gen.generate_jpa_files(gen_targets, 'app_user_integ', category, repository_package, entity_package)


    category = 'contents'
    if len(category_targets) == 0 or category in category_targets:
        repository_package = repository_base_pkg + "." + category
        entity_package = entity_base_pkg + "." + category

        gen.generate_jpa_files(gen_targets, 'event', category, repository_package, entity_package,
                               {'event_id': {'sequence_name': 'event_event_id_seq'}})
        gen.generate_jpa_files(gen_targets, 'contents_view', category, repository_package, entity_package,
                               {'view_id': {'sequence_name': 'contents_view_view_id_seq'}})
        gen.generate_jpa_files(gen_targets, 'contents_view_group_ordr', category, repository_package, entity_package)
        gen.generate_jpa_files(gen_targets, 'contents_group', category, repository_package, entity_package,
                               {'group_id': {'sequence_name': 'contents_group_group_id_seq'}})
        gen.generate_jpa_files(gen_targets, 'contents_group_ordr', category, repository_package, entity_package)
        gen.generate_jpa_files(gen_targets, 'contents', category, repository_package, entity_package,
                               {'contents_id': {'sequence_name': 'contents_contents_id_seq'}})

        gen.generate_jpa_files(gen_targets, 'contents_fortune_cookie_result_set', category, repository_package, entity_package, {
            'interface': 'com.techlabs.platform.core.domain.IContentsResultSet',
            'result_id': {'sequence_name': 'contents_fortune_cookie_result_set_result_id_seq'}
        })
        gen.generate_jpa_files(gen_targets, 'contents_tarot_result_set', category, repository_package, entity_package, {
            'interface': 'com.techlabs.platform.core.domain.IContentsResultSet',
            'result_id': {'sequence_name': 'contents_tarot_result_set_result_id_seq'}
        })
        gen.generate_jpa_files(gen_targets, 'contents_sigh_box_result_set', category, repository_package, entity_package, {
            'interface': 'com.techlabs.platform.core.domain.IContentsResultSet',
            'result_id': {'sequence_name': 'contents_sigh_box_result_set_result_id_seq'}
        })

    category = 'point'
    if len(category_targets) == 0 or category in category_targets:
        repository_package = repository_base_pkg + "." + category
        entity_package = entity_base_pkg + "." + category

        gen.generate_jpa_files(gen_targets, 'point_history_raw', category, repository_package, entity_package)
        gen.generate_jpa_files(gen_targets, 'point_history_error_raw', category, repository_package, entity_package)

        gen.generate_jpa_files(gen_targets, 'point_manual', category, repository_package, entity_package,
                               {'manual_id': {'sequence_name': 'point_manual_manual_id_seq'}})
        gen.generate_jpa_files(gen_targets, 'point_manual_detail', category, repository_package, entity_package,
                               {'detail_id': {'sequence_name': 'point_manual_detail_detail_id_seq'}})
        gen.generate_jpa_files(gen_targets, 'point_history', category, repository_package, entity_package,{
            'worker_id': worker_field_attr
        })
        gen.generate_jpa_files(gen_targets, 'point_history_fail', category, repository_package, entity_package)
        gen.generate_jpa_files(gen_targets, 'point_daily_report', category, repository_package, entity_package)
        gen.generate_jpa_files(gen_targets, 'point_monthly_report', category, repository_package, entity_package)

    category = 'store'
    if len(category_targets) == 0 or category in category_targets:
        repository_package = repository_base_pkg + "." + category
        entity_package = entity_base_pkg + "." + category

        gen.generate_jpa_files(gen_targets, 'product', category, repository_package, entity_package, {
            'category_cd': dynamic_cd_field_attr
        })

    category = 'operation'
    if len(category_targets) == 0 or category in category_targets:
        repository_package = repository_base_pkg + "." + category
        entity_package = entity_base_pkg + "." + category


        gen.generate_jpa_files(gen_targets, 'fqa', category, repository_package, entity_package,
                               {'fqa_id': {'sequence_name': 'fqa_fqa_id_seq'}})
        gen.generate_jpa_files(gen_targets, 'term', category, repository_package, entity_package,
                               {'term_id': {'sequence_name': 'term_term_id_seq'}})
        gen.generate_jpa_files(gen_targets, 'term_tmpl', category, repository_package, entity_package,
                               {'term_tmpl_id': {'sequence_name': 'term_tmpl_term_tmpl_id_seq'}})
        gen.generate_jpa_files(gen_targets, 'company', category, repository_package, entity_package,
                               {'company_id': {'sequence_name': 'company_company_id_seq'}})
        gen.generate_jpa_files(gen_targets, 'oprtr', category, repository_package, entity_package,
                               {'oprtr_id': {'sequence_name': 'oprtr_oprtr_id_seq'}, 'approval_id': worker_field_attr})
        gen.generate_jpa_files(gen_targets, 'menu', category, repository_package, entity_package, {'menu_id': {'sequence_name': 'menu_menu_id_seq'}})
        gen.generate_jpa_files(gen_targets, 'menu_auth', category, repository_package, entity_package)
        gen.generate_jpa_files(gen_targets, 'auth', category, repository_package, entity_package)

        gen.generate_jpa_files(gen_targets, 'notice', category, repository_package, entity_package,
                               {'notice_id': {'sequence_name': 'notice_notice_id_seq'}})
        gen.generate_jpa_files(gen_targets, 'system_env', category, repository_package, entity_package)
        gen.generate_jpa_files(gen_targets, 'dynamic_code_item', category, repository_package, entity_package,
                               {'item_id': {'sequence_name': 'dynamic_code_item_item_id_seq'}})
        gen.generate_jpa_files(gen_targets, 'attach_file', category, repository_package, entity_package,
                               {'file_id': {'sequence_name': 'attach_file_file_id_seq'}})


if len(gen_targets) < 1 or config.__GEN_TARGET__[0] in gen_targets or config.__GEN_TARGET__[1] in gen_targets:
    print("\r\n============================================")
    print("Generate JPA Start..!!")
    print("---------------------------------------------")
    generate_jpa_files()
    print("---------------------------------------------")
    print("Generate JPA Finish..!!")
    print("============================================")

if len(category_targets) < 1 and (len(gen_targets) < 1 or config.__GEN_TARGET__[2] in gen_targets):
    print("\r\n============================================")
    print("Generate Code Start..!!")
    print("---------------------------------------------")
    gen_code.gen_code_enum(_package_path_info)
    gen_code.gen_code_handler(_package_path_info)
    print("---------------------------------------------")
    print("Generate Code Finish..!!")
    print("============================================")
