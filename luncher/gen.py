#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, os

sys.path.append(os.path.abspath("../"))

import gen_code_enum as gen_code
import gen_jpa as gen
import config

arguments = sys.argv
gen_targets = []
category_targets = []
for gt in arguments[1:]:
    if gt == '-h' or gt == '--help':
        print(config.__HELP__)
        exit(0)
    if gt.startswith("-C"):
        category_targets.append(gt[2:])
    elif gt.startswith("-T"):
        gen_targets.append(gt[2:])

print("Generator target file              : ", 'ALL' if len(gen_targets) == 0 else gen_targets)
print("Generator target category(package) : ", 'ALL' if len(category_targets) == 0 else category_targets)

src_path = '/Users/yjkim/project_source/_mm/MetaMarket/src/main/java/'
_package_path_info = gen.PackagePathInfo(
    project_src_path=src_path
    , core_repository_path=src_path + 'com/techlabs/platform/metamarketing/framework/core/gen/repository'
    , core_entity_path=src_path + 'com/techlabs/platform/metamarketing/framework/core/gen/entity'
    , core_entity_id_path=src_path + 'com/techlabs/platform/metamarketing/framework/core/gen/id'
    , base_entity_package='com.techlabs.platform.metamarketing.framework.domain.BaseDomain'
    , enum_package='com.techlabs.platform.metamarketing.framework.core.data.PlatformCodes'
    , entity_package='com.techlabs.platform.metamarketing.framework.domain.entity'
    , repository_package='com.techlabs.platform.metamarketing.framework.repository'
    , core_entity_package='com.techlabs.platform.metamarketing.framework.core.gen.entity'
    , core_entity_id_package='com.techlabs.platform.metamarketing.framework.core.gen.id'
    , core_repository_package='com.techlabs.platform.metamarketing.framework.core.gen.repository'
    , core_converter_package='com.techlabs.platform.metamarketing.framework.core.gen.converter'
)
_column_info = gen.ColumnInfo(
    is_remove_cd=False
    , is_remove_yn=False
    , is_use_date_format=True
    , is_use_time_format=True
    , base_domain_columns=['insert_dt', 'update_dt']
    , insert_dt_columns=['insert_dt']
    , update_dt_columns=['update_dt']
    , delete_columns=['is_deleted']
)
gen.set_base_info(_package_path_info, _column_info)


# gen.generate_mybatis(gen_targets,'테이블명', category, repository_package, entity_package, {
#     'pk': '시퀀스명'
#     , '필드명': {
#         'field_name': ''
#         , 'java_type': ''
#         , 'json_props': ''
#         , 'sequence_name': ''
#     }
# })
def generate_jpa_files():
    #########################################
    repository_base_pkg = _package_path_info.repository_package
    entity_base_pkg = _package_path_info.entity_package
    #########################################

    category = 'test'
    if len(category_targets) == 0 or category in category_targets:
        repository_package = repository_base_pkg + "." + category
        entity_package = entity_base_pkg + "." + category

        gen.generate_jpa_files(gen_targets, 'test_demo', category, repository_package, entity_package)

    category = 'report'
    if len(category_targets) == 0 or category in category_targets:
        repository_package = repository_base_pkg + "." + category
        entity_package = entity_base_pkg + "." + category

        gen.generate_jpa_files(gen_targets, 'adgroup_report', category, repository_package, entity_package)

    category = 'ad'
    if len(category_targets) == 0 or category in category_targets:
        repository_package = repository_base_pkg + "." + category
        entity_package = entity_base_pkg + "." + category

        gen.generate_jpa_files(gen_targets, 'ad_info', category, repository_package, entity_package)
        gen.generate_jpa_files(gen_targets, 'adgroup_info', category, repository_package, entity_package)
        gen.generate_jpa_files(gen_targets, 'campaign_info', category, repository_package, entity_package)


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