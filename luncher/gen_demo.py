#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, os

sys.path.append(os.path.abspath("../"))

import gen_jpa as gen

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
      repository_path='/Users/yjkim/project_sources/web-platform-init/src/main/java/com/yjkim/web/platform/init/framework/core/gen/repository'
    , entity_path='/Users/yjkim/project_sources/web-platform-init/src/main/java/com/yjkim/web/platform/init/framework/core/gen/entity'
    , base_entity_package='com.yjkim.web.platform.init.framework.domain.BaseDomain'
    , enum_package='com.yjkim.web.platform.init.framework.data.PlatformCodes'
    , entity_package='com.yjkim.web.platform.init.framework.domain.entity'
    , repository_package='com.yjkim.web.platform.init.framework.repository'
    , core_entity_package='com.yjkim.web.platform.init.framework.gen.entity'
    , core_repository_package='com.yjkim.web.platform.init.framework.gen.repository'
)

_column_info = gen.ColumnInfo(
    is_remove_cd=False
    , is_remove_yn=False
    , is_use_date_format=True
    , is_use_time_format=True
    , base_domain_columns=['reg_dt', 'upd_dt']
    , insert_dt_columns=['reg_dt']
    , update_dt_columns=['upd_dt']
    , delete_columns=['is_deleted']
)



# gen.generate_mybatis(gen_targets,'테이블명', category, mapper_package, model_package, {
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
    mapper_base_pkg = _package_path_info.repository_package
    model_base_pkg = _package_path_info.entity_package
    #########################################


    category = 'demo'
    if len(category_targets) == 0 or category in category_targets:
        mapper_package = mapper_base_pkg + "." + category
        model_package = model_base_pkg + "." + category

        gen.generate_mybatis(gen_targets, 'tb_sample', category, mapper_package, model_package)



gen.set_base_info(_package_path_info, _column_info)

print("\r\n============================================")
print("Generate Start..!!")
print("---------------------------------------------")
generate_mybatis_files()
print("---------------------------------------------")
print("Generate Finish..!!")
print("============================================")
