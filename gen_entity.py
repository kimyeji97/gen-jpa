#!/usr/bin/python
# -*- coding: utf-8 -*-

import common as common

_column_info = None
_package_path_info = None


def make_java_domain_core(_c_info, _p_info, table, fields, model_gen_package, is_entity_id=False):
    global _column_info
    global _package_path_info
    _column_info = _c_info
    _package_path_info = _p_info

    table_class_name = common.to_class_name(table.table_name) + 'Core'

    # 중복 제어해야함
    source_prefix = [
        common.make_import_code(_package_path_info.base_domain_package)
        , common.make_import_code(_package_path_info.jakarta_persistence_all)
        , common.make_import_code(_package_path_info.lombok_data)
        , common.make_import_code(_package_path_info.lombok_extend_hashcode)
        , common.make_import_code(_package_path_info.jpa_auditing)
    ] if not is_entity_id else [
        common.make_import_code(_package_path_info.lombok_data)
        , common.make_import_code(_package_path_info.lombok_all_args_const)
        , common.make_import_code(_package_path_info.lombok_no_args_const)
        , common.make_import_code(_package_path_info.serializable)
    ]

    source = [
        "@IdClass({}ID.class)".format(table_class_name)
    ] if (not is_entity_id) and table.is_multiple_key() else []

    if not is_entity_id:
        source += [
            "@Data"
            , "@MappedSuperclass"  # 부모 엔티티를 따르기 위함
            , "@EqualsAndHashCode(callSuper = true)"
            , "@EntityListeners(value = { AuditingEntityListener.class })"  # 엔티티 영속성 탐지
            , "public class {} extends BaseDomain".format(table_class_name)
            , "{"
        ]
    else:
        source += [
            "@Data"
            , "@NoArgsConstructor"
            , "@AllArgsConstructor"
            , "public class {}ID implements Serializable".format(table_class_name)
            , "{"
        ]

    write_only_source = []

    # 매개변수 추가
    for field in fields:

        # BaseDomain에 존재하는 컬럼이면 -> skip
        if field.name in _column_info.base_domain_columns:
            continue

        if is_entity_id and not field.is_pk:
            continue

        # Class Type import문 추가
        if field.java_type_package is not None:
            source_prefix.append(common.make_import_code(field.java_type_package))

        if not is_entity_id:

            # jpa annotation 추가
            column_values = []
            if field.is_pk:
                source.append("    @Id")
                if field.is_auto_increment() and not table.is_multiple_key:
                    source.append("    @GeneratedValue(strategy = GenerationType.IDENTITY)")
            elif field.is_auto_increment():
                source.append("    @GeneratedValue(strategy = GenerationType.AUTO)")

            if _column_info.include_update_dt_columns(field.name) or field.is_pk:
                column_values.append("updatable = false")
            if not field.nullable:
                column_values.append("nullable = false")
            if field.is_unique:
                column_values.append("unique = true")

            if len(column_values) > 0:
                source.append("    @Column({})".format(", ".join(column_values)))

            # JsonProperty 추가
            if field.jackson_prop is not None:
                source_prefix.append(common.make_import_code(_package_path_info.json_property))

                prop_str_list = []
                # value 옵션 추가
                if 'value' in field.jackson_prop:
                    prop_str_list.append('value = "{}"'.format(field.jackson_prop['value']))
                # access 옵션 추가
                if 'access' in field.jackson_prop:
                    prop_str_list.append('access = {}'.format(field.jackson_prop['access']))

                if len(prop_str_list) > 0:
                    source.append('    @JsonProperty({})'.format(','.join(prop_str_list)))

            # 날짜 Type 인 경우
            if _column_info.is_use_date_format and field.is_date():
                source_prefix.append(common.make_import_code(_package_path_info.date_time_format))
                source_prefix.append(common.make_import_code(_package_path_info.json_format))
                source.append('    @DateTimeFormat(pattern="' + _column_info.date_format_pattern + '")')
                source.append('    @JsonFormat(shape = JsonFormat.Shape.STRING, pattern = "' + _column_info.date_format_pattern + '")')
            # 날짜 시간 Type 인 경우
            if (_column_info.is_use_time_format is True):
                source_prefix.append(common.make_import_code(_package_path_info.date_time_format))
                source_prefix.append(common.make_import_code(_package_path_info.json_format))
                if field.is_datetime3():
                    source.append('    @DateTimeFormat(pattern="' + _column_info.date_time3_format_pattern + '")')
                    source.append('    @JsonFormat(shape = JsonFormat.Shape.STRING, pattern = "' + _column_info.date_time3_format_pattern + '")')
                elif field.is_datetime():
                    source.append('    @DateTimeFormat(pattern="' + _column_info.date_time_format_pattern + '")')
                    source.append('    @JsonFormat(shape = JsonFormat.Shape.STRING, pattern = "' + _column_info.date_time_format_pattern + '")')
                elif field.is_time():
                    source.append('    @JsonFormat(shape = JsonFormat.Shape.STRING, pattern = "' + _column_info.time_format_pattern + '")')

        # Field 추가
        source.append("    private {} {};".format(field.java_type, field.java_field_name))

        # 검색용 Field 추가 (WRITE_ONLY)
        if not is_entity_id:
            if field.is_date() or field.is_datetime() or field.is_datetime3() or field.is_time():
                source_prefix.append(common.make_import_code(_package_path_info.json_property))
                source_prefix.append(common.make_import_code(_package_path_info.json_format))
                source_prefix.append(common.make_import_code(_package_path_info.jakarta_persistence_transient))

                write_only_source.append("""
    /*
     * 내부 사용
     */""")
                write_only_source.append("    @Transient")
                write_only_source.append('    @JsonProperty(access = JsonProperty.Access.WRITE_ONLY)')
                write_only_source.append(
                    "    private {} {}{};".format(field.java_type, field.java_field_name, _column_info.period_search_start_postfix))
                write_only_source.append("    @Transient")
                write_only_source.append('    @JsonProperty(access = JsonProperty.Access.WRITE_ONLY)')
                write_only_source.append(
                    "    private {} {}{};".format(field.java_type, field.java_field_name, _column_info.period_search_end_postfix))

    source += write_only_source

    source.append("}")

    source_prefix = list(set(source_prefix))
    source_prefix.insert(0, common.make_package_code(model_gen_package))
    source_prefix.insert(1, "")
    source_prefix.append("")
    source_prefix.append("")
    return "\n".join(map(str, source_prefix + source))


# Model 생성
def make_java_domain_ex(_c_info, _p_info, table, fields, mapper_package, model_package):
    global _column_info
    global _package_path_info
    _column_info = _c_info
    _package_path_info = _p_info

    tname = table.table_name
    core_table_class_name = common.to_class_name(tname) + 'Core'
    table_class_name = common.to_class_name(tname)

    source_prefix = [
        common.make_import_code(_package_path_info.core_domain_package + "." + core_table_class_name)
        , common.make_import_code(_package_path_info.jakarta_persistence_entity)
        , common.make_import_code(_package_path_info.jakarta_persistence_table)
        , common.make_import_code(_package_path_info.lombok_builder)
        , common.make_import_code(_package_path_info.lombok_data)
        , common.make_import_code(_package_path_info.lombok_extend_hashcode)
        , common.make_import_code(_package_path_info.lombok_no_args_const)
    ]

    source = [
        '@Data'
        , '@Builder'
        , '@Entity'
        , '@NoArgsConstructor'
        , '@Table(name = "{}")'.format(tname)
        , "@EqualsAndHashCode(callSuper = false)"
        , "public class {} extends {}".format(table_class_name, core_table_class_name)
        , "{"
        , "}"
    ]

    source_prefix = list(set(source_prefix))
    source_prefix.insert(0, common.make_package_code(model_package))
    source_prefix.insert(1, "")
    source_prefix.append("")
    source_prefix.append("")
    return "\n".join(map(str, source_prefix + source))
