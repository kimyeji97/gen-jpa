#!/usr/bin/python
# -*- coding: utf-8 -*-

import common as common
import config as config


# entity & entity ID Core 생성
def make_java_entity_core(_column_info, _package_path_info, table, fields, model_gen_package, is_entity_id=False):
    class_name = table.table_entity_core_name if not is_entity_id else table.primary_keys_java_type

    source_prefix = [
        common.make_import_code(_package_path_info.base_entity_package)
        , common.make_import_code(_package_path_info.jakarta_persistence_all)
        , common.make_import_code(_package_path_info.lombok_data)
        , common.make_import_code(_package_path_info.lombok_extend_hashcode)
        , common.make_import_code(_package_path_info.jpa_auditing)
        , '' if not table.is_multiple_key() else common.make_import_code('{}.{}'.format(_package_path_info.core_entity_id_package, table.primary_keys_java_type))
    ] if not is_entity_id else [
        common.make_import_code(_package_path_info.lombok_data)
        , common.make_import_code(_package_path_info.lombok_all_args_const)
        , common.make_import_code(_package_path_info.lombok_no_args_const)
        , common.make_import_code(_package_path_info.serializable)
    ]

    source = [
        "@IdClass({}.class)".format(table.primary_keys_java_type)
    ] if (not is_entity_id) and table.is_multiple_key() else []

    if not is_entity_id:
        source += [
            "@Data"
            , "@MappedSuperclass"  # 부모 엔티티를 따르기 위함
            , "@EqualsAndHashCode(callSuper = true)"
            , "@EntityListeners(value = { AuditingEntityListener.class })"  # 엔티티 영속성 탐지
            , "public class {} extends BaseDomain".format(class_name)
            , "{"
        ]
    else:
        source += [
            "@Data"
            , "@NoArgsConstructor"
            , "@AllArgsConstructor"
            , "public class {} implements Serializable".format(class_name)
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

            # annotation 추가
            # 1. @Id + @GeneratedValue
            if field.is_pk:
                source.append("    @Id")
                if field.is_auto_increment() and not table.is_multiple_key:
                    source.append("    @GeneratedValue(strategy = GenerationType.IDENTITY)")
            elif field.is_auto_increment():
                source.append("    @GeneratedValue(strategy = GenerationType.AUTO)")

            # 2. @Column
            column_values = [
                "name = \"" + field.name+"\""
            ]
            if _column_info.include_update_dt_columns(field.name) or field.is_pk:
                column_values.append("updatable = false")
            if not field.nullable:
                column_values.append("nullable = false")
            if field.is_unique:
                column_values.append("unique = true")

            if len(column_values) > 0:
                source.append("    @Column({})".format(", ".join(column_values)))

            # 3. @JsonProperty 추가
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

            # 4. @DateTimeFormat + @JsonFormat
            # 날짜 Type 인 경우
            if _column_info.is_use_date_format and field.is_date():
                source_prefix.append(common.make_import_code(_package_path_info.date_time_format))
                source_prefix.append(common.make_import_code(_package_path_info.json_format))
                source.append('    @DateTimeFormat(pattern="' + _column_info.date_format_pattern + '")')
                source.append('    @JsonFormat(shape = JsonFormat.Shape.STRING, pattern = "' + _column_info.date_format_pattern + '")')
            # 날짜 시간 Type 인 경우
            if _column_info.is_use_time_format is True and (field.is_datetime() or field.is_datetime3() or field.is_time()):
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

            # 5. @Convert
            if field.is_enum:
                source.append("    @Convert(converter = {}.Converter.class)".format(field.java_type))

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
    source.insert(0, config.__FILE_ANNOTATION__.format(table.table_name))

    source_prefix = sorted(list(set(source_prefix)))
    source_prefix.insert(0, common.make_package_code(model_gen_package))
    source_prefix.insert(1, "")
    source_prefix.append("")
    source_prefix.append("")

    return "\n".join(map(str, source_prefix + source))


# Entity 생성
def make_java_entity_ex(_column_info, _package_path_info, table, fields, repository_package, model_package):
    core_class_name = table.table_entity_core_name
    class_name = table.table_entity_name

    source_prefix = [
        common.make_import_code(_package_path_info.core_entity_package + "." + core_class_name)
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
        , '@Table(name = "{}")'.format(table.table_name)
        , "@EqualsAndHashCode(callSuper = false)"
        , "public class {} extends {}".format(class_name, core_class_name)
        , "{"
        , "}"
    ]

    source.insert(0, config.__FILE_ANNOTATION__.format(table.table_name))

    source_prefix = sorted(list(set(source_prefix)))
    source_prefix.insert(0, common.make_package_code(model_package))
    source_prefix.insert(1, "")
    source_prefix.append("")

    source_prefix.append("")
    return "\n".join(map(str, source_prefix + source))
