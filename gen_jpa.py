#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, json
import datetime
import config as config
import common as common
import gen_entity as gen_model
import gen_repository as gen_repository
import mysql.connector as mysql
import psycopg2

from dataclasses import dataclass

tmpfolder = datetime.datetime.strftime(datetime.datetime.now(), "%Y%m%d.%H%M%S")


# @dataclass
class PackagePathInfo:
    date_time_format = 'org.springframework.format.annotation.DateTimeFormat'
    json_property = 'com.fasterxml.jackson.annotation.JsonProperty'
    json_format = 'com.fasterxml.jackson.annotation.JsonFormat'

    lombok_data = 'lombok.Data'
    lombok_builder = 'lombok.Builder'
    lombok_extend_hashcode = 'lombok.EqualsAndHashCode'
    lombok_all_args_const = 'lombok.AllArgsConstructor'
    lombok_no_args_const = 'lombok.NoArgsConstructor'
    lombok_toString = 'lombok.ToString'
    lombok_required_args_constructor = 'lombok.RequiredArgsConstructor'

    annotations_param = 'org.apache.ibatis.annotations.Param'

    jakarta_persistence_all = 'jakarta.persistence.*'
    jakarta_persistence_transient = 'jakarta.persistence.Transient'
    jakarta_persistence_entity = 'jakarta.persistence.Entity'
    jakarta_persistence_table = 'jakarta.persistence.Table'

    serializable = 'java.io.Serializable'

    jpa_auditing = 'org.springframework.data.jpa.domain.support.AuditingEntityListener'
    jpa_query_factory = 'com.querydsl.jpa.impl.JPAQueryFactory'


    def __init__(self, **kwargs):
        self.core_repository_path = kwargs['core_repository_path']
        self.core_entity_path = kwargs['core_entity_path']
        self.core_entity_id_path = kwargs['core_entity_id_path']
        self.base_entity_package = kwargs['base_entity_package']
        self.enum_package = kwargs['enum_package']
        self.entity_package = kwargs['entity_package']
        self.repository_package = kwargs['repository_package']
        self.core_entity_package = kwargs['core_entity_package']
        self.core_entity_id_package = kwargs['core_entity_id_package']
        self.core_repository_package = kwargs['core_repository_package']
        self.project_src_path = kwargs['project_src_path']
        self.core_converter_package = kwargs['core_converter_package']


# @dataclass
class ColumnInfo:
    period_search_start_postfix = 'Start'
    period_search_end_postfix = 'End'
    date_format_pattern = 'yyyy-MM-dd'
    date_time_format_pattern = 'yyyy-MM-dd HH:mm:ss'
    date_time3_format_pattern = 'yyyy-MM-dd HH:mm:ss.SSS'
    time_format_pattern = 'HH:mm:ss'
    insert_dt_columns = []
    update_dt_columns = []
    delete_columns = []

    def __init__(self, **kwargs):
        self.is_remove_cd = kwargs['is_remove_cd']
        self.is_remove_yn = kwargs['is_remove_yn']
        self.is_use_date_format = kwargs['is_use_date_format']
        self.is_use_time_format = kwargs['is_use_time_format']
        self.base_domain_columns = kwargs['base_domain_columns']
        self.insert_dt_columns = kwargs['insert_dt_columns']
        self.update_dt_columns = kwargs['update_dt_columns']
        self.delete_columns = kwargs['delete_columns']

    def set_date_format_pattern(self, pattern):
        self.date_format_pattern = pattern

    def set_date_time_format_pattern(self, pattern):
        self.date_time_format_pattern = pattern
        self.date_time3_format_pattern = pattern + '.SSS'

    def set_time_format_pattern(self, pattern):
        self.time_format_pattern = pattern

    def include_insert_dt_columns(self, column):
        if len(self.insert_dt_columns) < 1:
            return False
        return column in self.insert_dt_columns

    def include_update_dt_columns(self, column):
        if len(self.update_dt_columns) < 1:
            return False
        return column in self.update_dt_columns

    def include_delete_columns(self, column):
        if len(self.delete_columns) < 1:
            return False
        return column in self.delete_columns


_package_path_info: PackagePathInfo = None
_column_info: ColumnInfo = None


class Table:
    def __init__(self, tname, fields, **kwargs):
        self.table_name = tname
        self.fields = fields
        self.sequence = None  # kwargs['pk']
        self.kwargs = kwargs

        self.table_alias = self.get_table_alias(self.table_name)
        self.table_entity_name = common.to_class_name(self.table_name)
        self.table_entity_core_name = self.table_entity_name + 'Core'  # TableCore
        self.table_entity_id_core_name = self.table_entity_name + 'IdCore'  # TableIdCore
        self.table_repository_interface_name = self.table_entity_name + 'Repository'  # TableRepository
        self.table_qdsl_repository_interface_name = self.table_entity_name + 'QdslRepository'  # TableQdslRepository
        self.table_qdsl_repository_impl_name = self.table_qdsl_repository_interface_name + 'Impl'  # TableQdslRepositoryImpl
        self.table_qdsl_repository_core_interface_name = self.table_qdsl_repository_interface_name + 'Core'  # TableQdslRepositoryCore
        self.table_qdsl_repository_core_impl_name = self.table_qdsl_repository_core_interface_name + 'Impl'  # TableQdslRepositoryCoreImpl

        self.table_field_name = common.to_field_name(self.table_name)  # table
        self.table_qclass_name = 'Q' + self.table_entity_name  # QTable

        self.primary_keys = list(filter(lambda f: f.is_pk == True, fields))
        self.primary_keys_java_type = self._get_primary_keys_java_type()
        self.delete_column = list(filter(lambda f: _column_info.include_delete_columns(f.name), fields))

    def is_multiple_key(self):
        return len(self.primary_keys) > 1

    def has_column(self, column_name):
        for field in self.fields:
            if field.name.lower() == column_name:
                return True
        return False

    def get_table_alias(self, table_name):
        x = table_name.split("_")
        alias = ""
        for t in x:
            alias += t[0].upper()
        return alias

    def _get_primary_keys_java_type(self):
        if self.is_multiple_key():
            return self.table_entity_id_core_name
        else:
            if self.primary_keys[0] == None:
                return None
            else:
                return self.primary_keys[0].java_type


class FieldAttr:
    def __init__(self, **kwargs):
        self.fieldName = kwargs['field_name'] if 'field_name' in kwargs else None
        self.javaType = kwargs['java_type'] if 'java_type' in kwargs else None
        self.jsonProperties = kwargs['json_props'] if 'json_props' in kwargs else None
        # YJ 시퀀스 작업
        self.sequenceName = kwargs['sequence_name'] if 'sequence_name' in kwargs else None


class TableField:
    def __init__(self, **kwargs):
        self.field_attrs = kwargs['field_attrs']
        self.name = kwargs['field']
        self.is_pk = kwargs['key'] == 'PRI'
        self.is_unique = kwargs['key'] == 'UNI'
        self.nullable = kwargs['null'] != 'NO'
        self.type = kwargs['type']
        self.key = kwargs['key']
        self.extra = kwargs['extra']
        # python3 으로 업그레이드 하면서 default 조회값에 null이 아니라 None 이라는 문자열로 값이 들어감.
        if isinstance(kwargs['default'], str) and kwargs['default'] == 'None':
            self.default = None
        else:
            self.default = kwargs['default']
        self.java_type_package = None
        self.java_type = self._mk_java_type()
        self.java_field_name = self._mk_java_field_name()
        self.jackson_prop = self._mk_jackson_prop()
        self.null_check_string = self._mk_null_check_string("param")
        # YJ 시퀀스 작업
        self.sequence_name = self._mk_sequence_name()

        if self.default:
            if self.java_type == 'String':
                self.default = "'" + self.default + "'"

    def is_date(self):
        return self.type.startswith("date") and self.type.startswith("datetime") is not True

    def is_datetime(self):
        return self.type == 'datetime' or self.type == 'timestamp'

    def is_datetime3(self):
        return self.type.startswith("datetime(") or self.type.startswith("timestamp(")

    def is_time(self):
        return self.type == 'time'

    def is_auto_increment(self):
        return self.extra == 'auto_increment'

    def _mk_sequence_name(self):
        if self.name in self.field_attrs and self.field_attrs[self.name].sequenceName:
            return self.field_attrs[self.name].sequenceName
        else:
            return None

    def _mk_java_field_name(self):
        if self.name not in self.field_attrs:
            return common.to_field_name(self.name)
        else:
            attrs = self.field_attrs[self.name]
            if attrs.fieldName:
                return self.field_attrs.fieldName
            else:
                return common.to_field_name(self.name)

    def _mk_java_type(self):
        type_name = self.type.lower()
        name = self.name.lower()

        if name in self.field_attrs and self.field_attrs[name].javaType:
            tmpJavaType = self.field_attrs[name].javaType

            dot_pos = tmpJavaType.rfind('.')
            if dot_pos == -1:
                return tmpJavaType
            else:
                self.java_type_package = tmpJavaType
                return tmpJavaType[dot_pos + 1:]

        if type_name.startswith("timestamp") or type_name.startswith("datetime"):
            self.java_type_package = 'java.time.LocalDateTime'
            return 'LocalDateTime'
        elif type_name.startswith("date"):
            self.java_type_package = 'java.time.LocalDate'
            return 'LocalDate'
        elif type_name.startswith("bigint") or type_name.startswith('serial') or type_name.startswith('int8'):
            if self.name in config.FIELD_NAME_ENUM_TYPES:
                self.java_type_package = _column_info.enum_package + "." + config.FIELD_NAME_ENUM_TYPES[self.name]
                return config.FIELD_NAME_ENUM_TYPES[self.name]
            else:
                return 'Long'
        elif type_name.startswith("interval"):
            return 'String'
        elif type_name.startswith("int"):
            if self.name in config.FIELD_NAME_ENUM_TYPES:
                self.java_type_package = _column_info.enum_package + "." + config.FIELD_NAME_ENUM_TYPES[self.name]
                return config.FIELD_NAME_ENUM_TYPES[self.name]
            else:
                return 'Integer'
        elif type_name.startswith("float") or type_name.startswith("double"):
            return 'Double'
        elif type_name.startswith("decimal(") or type_name.startswith("numeric"):
            self.java_type_package = 'java.math.BigDecimal'
            return "BigDecimal"
            # return "Double"
        elif type_name.startswith("tinyint(1)") or type_name.startswith("bool"):
            return 'Boolean'
        elif type_name.startswith("bytea") or type_name.startswith("blob"):
            return 'byte[]'
        elif type_name.startswith("_varchar"):
            self.java_type_package = 'java.util.List'
            return 'List<String>'
        elif type_name.startswith("_int"):
            self.java_type_package = 'java.util.List'
            if self.name in config.FIELD_NAME_ENUM_TYPES:
                self.java_type_package = _column_info.enum_package + "." + config.FIELD_NAME_ENUM_TYPES[self.name]
                return "List<{}>".format(config.FIELD_NAME_ENUM_TYPES[self.name])
            else:
                return 'List<Integer>'
        else:
            if self.name in config.FIELD_NAME_ENUM_TYPES:
                self.java_type_package = _column_info.enum_package + "." + config.FIELD_NAME_ENUM_TYPES[self.name]
                return config.FIELD_NAME_ENUM_TYPES[self.name]
            else:
                return 'String'
            # return 'String'

    def _mk_null_check_string(self, value):
        getter = common.to_getter(value, self)
        if self.java_type == 'String':
            return ["!Objects.isNull({}) && !{}.isEmpty()".format(getter, getter)]
        elif self.is_date() or self.is_datetime() or self.is_datetime3() or self.is_time():
            return ["!Objects.isNull({})".format(getter),
                    "!Objects.isNull({}) && !Objects.isNull({})".format(
                        getter.replace("()", _column_info.period_search_start_postfix + "()"),
                        getter.replace("()", _column_info.period_search_end_postfix + "()")
                    )]
        else:
            return ["!Objects.isNull({})".format(getter)]

    def _mk_jackson_prop(self):
        json_props = {}
        json_prop_name = None

        if _column_info.is_remove_cd:
            if self.name.endswith('_CD') and self.java_type_package is not None:
                # return self.name[:-3].lower()
                json_prop_name = self.java_field_name[:-2]

        if _column_info.is_remove_yn:
            if self.name.endswith('_YN') and self.java_type == 'Boolean':
                # return self.name[:-3].lower()
                json_prop_name = self.java_field_name[:-2]

        # config value.
        if json_prop_name:
            json_props['value'] = json_prop_name

        if self.field_attrs and self.name in self.field_attrs and self.field_attrs[self.name].jsonProperties:
            jsonProperties = self.field_attrs[self.name].jsonProperties
            for prop_key in jsonProperties:
                json_props[prop_key] = jsonProperties[prop_key]

        if len(json_props) == 0:
            return None
        else:
            return json_props

    def print_info(self):
        print("{:30}\t{}\t{}\t{:12}\t{}".format(self.name, self.is_pk, self.nullable, self.type, self.java_type))


def set_base_info(p_info: PackagePathInfo, c_info: ColumnInfo):
    global _package_path_info
    global _column_info

    _package_path_info = p_info
    _column_info = c_info

    print("Column Info                        : ", json.dumps(_column_info.__dict__, indent=4))
    print("Package Path Info                  : ", json.dumps(_package_path_info.__dict__, indent=4))
    print("Result Dir                         : ", os.path.join(config.__TEMP_DIR__, 'mybatis-gen-' + tmpfolder))


def get_tables(connection_opts, con_schema):
    rows = []
    global gen_xml

    # postgresql
    if (connection_opts.engin == config.DB_ENGIN[0]):
        cnx = psycopg2.connect(**connection_opts)
        cursor = cnx.cursor()
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='" + con_schema + "'", False)

        fetchedCursor = cursor.fetchall()
        for row in fetchedCursor:
            rows.append(row[0])
        cursor.close()
        cnx.close()

    # mysql
    elif (connection_opts.engin == config.DB_ENGIN[1]):
        cnx = (mysql.connect(**connection_opts['options']))
        cursor = cnx.cursor()
        cursor.execute('show tables', False)

        fetchedCursor = cursor.fetchall()
        # col_names = map(common.to_lower, cursor.column_names)
        for row in fetchedCursor:
            # map_row = dict(zip(col_names, row))
            rows.append(row)
        cursor.close()
        cnx.close()
    return rows


def get_field_info(table_name, connection_opts, con_schema, field_attrs={}):
    rows = []

    global gen_xml

    # print('DB Connection Started.. (Get table schema info)')
    # print('DB Connection Options              : ', connection_opts)

    # Postgresql
    if connection_opts['engin'] == config.DB_ENGIN[0]:

        cnx = psycopg2.connect(**connection_opts['options'])
        cursor = cnx.cursor()
        # cursor.execute('desc %(table_name)s',{'table_name':table_name},False)
        sql = """SELECT 
       c.column_name AS Field
       , udt_name AS Type
       , is_nullable AS NULL
       , b.key AS KEY
       , C.column_default  AS DEFAULT
    FROM 
       information_schema.columns AS C
       LEFT JOIN (SELECT CC.COLUMN_NAME AS COLUMN_NAME,'PRI' AS KEY
          FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS       TC
              JOIN INFORMATION_SCHEMA.CONSTRAINT_COLUMN_USAGE CC
              ON (TC.TABLE_CATALOG = CC.TABLE_CATALOG AND TC.TABLE_SCHEMA = CC.TABLE_SCHEMA AND TC.TABLE_NAME = CC.TABLE_NAME AND TC.CONSTRAINT_NAME = CC.CONSTRAINT_NAME)
         WHERE 
            TC.TABLE_NAME = %(table_name)s AND TC.CONSTRAINT_TYPE = 'PRIMARY KEY'
        ) AS b ON (C.column_name = b.column_name)
        JOIN pg_constraint p ON C.table_name = p.conrelid::regclass::text AND p.contype = 'p'
    WHERE 
       table_schema = %(con_schema)s AND TABLE_NAME = %(table_name)s
    ORDER BY array_position(p.conkey, C.ordinal_position)
    """

        cursor.execute(sql, {'table_name': table_name, 'con_schema': con_schema})

        col_names = map(common.to_lower, [desc[0] for desc in cursor.description])

        if config.__IS_VERSION_3__:
            col_names = list(col_names)

        fetchedCursor = cursor.fetchall()

        for row in fetchedCursor:
            str_row = None
            if config.__IS_VERSION_3__:
                str_row = list(map(str, row))
            else:
                str_row = row
            map_row = dict(zip(col_names, str_row))
            map_row['field_attrs'] = field_attrs
            field = TableField(**map_row)
            rows.append(field)
        cursor.close()
        cnx.close()

    # Mysql
    elif connection_opts['engin'] == config.DB_ENGIN[1]:

        cnx = (mysql.connect(**connection_opts['options']))
        cursor = cnx.cursor()
        cursor.execute("""desc {}""".format(table_name))

        col_names = map(common.to_lower, [desc[0] for desc in cursor.description])

        if config.__IS_VERSION_3__:
            col_names = list(col_names)

        fetchedCursor = cursor.fetchall()

        for row in fetchedCursor:
            str_row = None
            if config.__IS_VERSION_3__:
                str_row = list(map(str, row))
            else:
                str_row = row
            map_row = dict(zip(col_names, str_row))
            map_row['field_attrs'] = field_attrs
            field = TableField(**map_row)
            rows.append(field)
        cursor.close()
        cnx.close()
        pass

    # print('DB Connection End..')
    return rows


def write_file(category, group, file_name, data):
    global tmpfolder
    if category is None or len(category) == 0:
        tmpdir_all = os.path.join(config.__TEMP_DIR__, 'jpa-gen-' + tmpfolder)
        tmpdir = os.path.join(config.__TEMP_DIR__, 'jpa-gen-' + tmpfolder, group)
    else:
        tmpdir_all = os.path.join(config.__TEMP_DIR__, 'jpa-gen-' + tmpfolder, category)
        tmpdir = os.path.join(config.__TEMP_DIR__, 'jpa-gen-' + tmpfolder, category, group)

    if not os.path.exists(tmpdir):
        os.makedirs(tmpdir)

    write_file_core(tmpdir, file_name, data)
    write_file_core(tmpdir_all, file_name, data)


def write_file_core(path, file_name, data):
    with open(os.path.join(path, file_name), 'w') as f:
        f.write(data)


def generate_jpa_files(gen_targets, table_name, category, repository_package, entity_package, field_attrs={}):
    global gen_xml

    table_name = table_name.lower()
    db_fields = get_field_info(table_name, config.DB_CONNECTION_OPTS, config.DB_SCHEMA, field_attrs)

    if (len(db_fields) < 1):
        print("\r\nGenerated FAIL !!! : {} ====> no colums\r\n".format(table_name))
        return

    table = Table(table_name, db_fields, pk=field_attrs.get('pk'))


    is_make_entity = config.__GEN_TARGET__[0] in gen_targets
    is_make_repository = config.__GEN_TARGET__[1] in gen_targets

    # Results ...
    if len(gen_targets) == 0 or is_make_entity:
        in_entity_src = gen_model.make_java_entity_core(_column_info, _package_path_info, table, db_fields, _package_path_info.core_entity_package)
        ex_entity_src = gen_model.make_java_entity_ex(_column_info, _package_path_info, table, db_fields, repository_package, entity_package)

        write_file_core(_package_path_info.core_entity_path, table.table_entity_core_name + '.java', in_entity_src)
        write_file('entity', category, table.table_entity_name + '.java', ex_entity_src)

        if table.is_multiple_key():
            in_entity_id_src = gen_model.make_java_entity_core(_column_info, _package_path_info, table, db_fields, _package_path_info.core_entity_id_package, True)

            write_file_core(_package_path_info.core_entity_id_path, table.table_entity_id_core_name + '.java', in_entity_id_src)

    if len(gen_targets) == 0 or is_make_repository:
        in_querydsl_interface_src = gen_repository.make_querydsl_repository_interface_core(_column_info, _package_path_info, table, db_fields,repository_package, entity_package)
        in_querydsl_impl_src = gen_repository.make_querydsl_repository_impl_core(_column_info, _package_path_info, table, db_fields,repository_package, entity_package)

        ex_interface_src = gen_repository.make_repository_interface_ex(_column_info, _package_path_info, table, db_fields, repository_package,entity_package)
        ex_querydsl_interface_src = gen_repository.make_querydsl_repository_interface_ex(_column_info, _package_path_info, table, db_fields,repository_package, entity_package)
        ex_querydsl_impl_src = gen_repository.make_querydsl_repository_impl_ex(_column_info, _package_path_info, table, db_fields, repository_package,entity_package)

        write_file_core(_package_path_info.core_repository_path, table.table_qdsl_repository_core_interface_name + ".java", in_querydsl_interface_src)
        write_file_core(_package_path_info.core_repository_path, table.table_qdsl_repository_core_impl_name + ".java", in_querydsl_impl_src)
        write_file('repository', category, table.table_repository_interface_name + ".java", ex_interface_src)
        write_file('repository', category, table.table_qdsl_repository_interface_name + ".java", ex_querydsl_interface_src)
        write_file('repository', category, table.table_qdsl_repository_impl_name + ".java", ex_querydsl_impl_src)

    print("Generated : {}".format(table_name))
