#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, os

sys.path.append(os.path.abspath("../"))

import gen as gen

arguments = sys.argv
gen_targets = []
category_targets = []
print("CMD Arguments                      : ", arguments)

for gt in arguments[1:]:
    if gt.startswith("-C"):
        category_targets.append(gt[2:])
    else:
        gen_targets.append(gt)

print("Generator target file              : ", 'ALL' if len(gen_targets) == 0 else gen_targets)
print("Generator target category(package) : ", 'ALL' if len(category_targets) == 0 else category_targets)

dir_path = os.path.dirname(os.path.realpath(__file__))
_package_path_info = gen.PackagePathInfo(
    repository_path='/Users/yjkim/project_source/_mm/MetaMarket/src/main/java/com/techlabs/platform/metamarketing/framework/core/gen/repository'
    , entity_path='/Users/yjkim/project_source/_mm/MetaMarket/src/main/java/com/techlabs/platform/metamarketing/framework/core/gen/entity'
    , base_entity_package='com.techlabs.platform.metamarketing.framework.domain.BaseDomain'
    , enum_package='com.techlabs.platform.metamarketing.framework.core.data.PlatformCodes'
    , entity_package='com.techlabs.platform.metamarketing.framework.domain.entity'
    , repository_package='com.techlabs.platform.metamarketing.framework.domain.repository'
    , core_entity_package='com.techlabs.platform.metamarketing.framework.core.gen.entity'
    , core_repository_package='com.techlabs.platform.metamarketing.framework.core.gen.repository'
)

_column_info = gen.ColumnInfo(
    is_remove_cd=False
    , is_remove_yn=False
    , is_use_date_format=True
    , is_use_time_format=True
    , base_domain_columns=['insert_dt', 'update_dt']
    , insert_dt_columns=['insert_dt', 'register_dt']
    , update_dt_columns=['update_dt']
    , delete_columns=['is_del']
)



# gen.generate_mybatis(gen_targets,'테이블명', category, repository_package, entity_package, {
#     'pk': '시퀀스명'
#     , '필드명': {
#         'field_name': ''
#         , 'java_type': ''
#         , 'json_props': ''
#         , 'sequence_name': ''
#     }
# })
def generate_mybatis_files():
    #########################################
    repository_base_pkg = _package_path_info.repository_package
    entity_base_pkg = _package_path_info.entity_package
    #########################################


    category = 'test'
    if len(category_targets) == 0 or category in category_targets:
        repository_package = repository_base_pkg + "." + category
        entity_package = entity_base_pkg + "." + category

        gen.generate_mybatis(gen_targets, 'test_demo', category, repository_package, entity_package)

    category = 'report'
    if len(category_targets) == 0 or category in category_targets:
        repository_package = repository_base_pkg + "." + category
        entity_package = entity_base_pkg + "." + category

        gen.generate_mybatis(gen_targets, 'adgroup_report', category, repository_package, entity_package)


    category = 'ad'
    if len(category_targets) == 0 or category in category_targets:
        repository_package = repository_base_pkg + "." + category
        entity_package = entity_base_pkg + "." + category

        gen.generate_mybatis(gen_targets, 'ad_info', category, repository_package, entity_package)
        gen.generate_mybatis(gen_targets, 'adgroup_info', category, repository_package, entity_package)
        gen.generate_mybatis(gen_targets, 'campaign_info', category, repository_package, entity_package)


gen.set_base_info(_package_path_info, _column_info)

print("\r\n============================================")
print("Generate Start..!!")
print("---------------------------------------------")
generate_mybatis_files()
print("---------------------------------------------")
print("Generate Finish..!!")
print("============================================")
