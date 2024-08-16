#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys, os, io, re
from unicodedata import name

import mysql.connector as mysql
import psycopg2
import gen_typehandler as gen_converter
import config as config
import common as common

print("generate the 'Enum' with payment code.")

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dir_path)


class CodeGroup:
    def __init__(self, **kwargs):
        # print (kwargs)
        self.gcode = kwargs['id']
        self.gname = kwargs['name']
        self.gname_disp = "" if kwargs['name'] == "None" else kwargs['name']
        self.gname_disp_eng = "" if kwargs['name_eng'] == "None" else kwargs['name_eng']
        self.desc = kwargs['description']
        self.genum_name = kwargs['src_name'].replace(' ', '').replace('-', '').replace('/', '')
        self.value_1 = 'null' if kwargs['value_1'] == "None" else '"'+kwargs['value_1']+'"'
        self.value_2 = 'null' if kwargs['value_2'] == "None" else '"'+kwargs['value_2']+'"'
        self.value_3 = 'null' if kwargs['value_3'] == "None" else '"'+kwargs['value_3']+'"'
        self.value_4 = 'null' if kwargs['value_4'] == "None" else '"'+kwargs['value_4']+'"'

        self.codes = []
    def __str__(self):
        return self.gcode + ", " + self.gname + ", codes => [" + ', '.join(map(str, self.codes)) + "]"


class Code:
    def __init__(self, **kwargs):
        self.code = kwargs['id']
        self.pcode = kwargs['pid']
        self.name = kwargs['name']
        self.name_disp = "" if kwargs['name'] == "None" else kwargs['name']
        self.name_disp_eng = "" if kwargs['name_eng'] == "None" else kwargs['name_eng']
        self.desc = kwargs['description']
        self.enum_name = kwargs['src_name'].replace(' ', '').replace('-', '').replace('/', '')
        self.value_1 = 'null' if kwargs['value_1'] == "None" else '"'+ kwargs['value_1']+ '"'
        self.value_2 = 'null' if kwargs['value_2'] == "None" else '"'+ kwargs['value_2']+ '"'
        self.value_3 = 'null' if kwargs['value_3'] == "None" else '"'+ kwargs['value_3']+ '"'
        self.value_4 = 'null' if kwargs['value_4'] == "None" else '"'+ kwargs['value_4']+'"'

    def __str__(self):
        return self.code + ":" + self.name + "[" + self.enum_name + "]"


def get_code_groups(connection_opts):
    rows = []
    sql = 'SELECT * FROM code WHERE pid IS NULL ORDER BY ordr'

    # postgresql
    if connection_opts['engin'] == config.DB_ENGIN[0]:

        cnx = psycopg2.connect(**connection_opts['options'])
        cursor = cnx.cursor()
        cursor.execute(sql, False)

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

            row_obj = CodeGroup(**map_row)
            rows.append(row_obj)
        cursor.close()
        cnx.close()

    # mysql
    else:

        cnx = mysql.connect(**connection_opts['options'])
        cursor = cnx.cursor()
        cursor.execute(sql, False)

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

            row_obj = CodeGroup(**map_row)
            rows.append(row_obj)
        cursor.close()
        cnx.close()

    return rows


def get_codes(code_group, connection_opts):
    sql = "SELECT * FROM code WHERE pid = " + code_group.gcode + " ORDER BY ordr"

    cnx = psycopg2.connect(**connection_opts['options']) if connection_opts['engin'] == config.DB_ENGIN[0] else mysql.connect(
        **connection_opts['options'])
    cursor = cnx.cursor()
    cursor.execute(sql, False)

    col_names = map(common.to_lower, [desc[0] for desc in cursor.description])
    if config.__IS_VERSION_3__:
        col_names = list(col_names)

    fetchedCursor = cursor.fetchall()
    for row in fetchedCursor:
        print(row)
        str_row = None
        if config.__IS_VERSION_3__:
            str_row = list(map(str, row))
        else:
            str_row = row
        map_row = dict(zip(col_names, str_row))

        row_obj = Code(**map_row)
        code_group.codes.append(row_obj)
    cursor.close()
    cnx.close()


def create_src_string(_package_path_info, add_import, src_contents, class_name):
    src_import = """
import com.fasterxml.jackson.annotation.JsonFormat;
import com.fasterxml.jackson.annotation.JsonFormat.Shape;
"""
    code_interface = """
    @JsonFormat(shape = Shape.OBJECT)
    public interface CommonCode
    {
        default Long getPcode() {
            return null;
        }
        Long getCode();
        String getName();
    }

"""

    import_prefix = """package {gen_package};

import java.util.EnumSet;
import java.util.Objects;

import lombok.Getter;
import com.fasterxml.jackson.annotation.JsonIgnore;
import com.fasterxml.jackson.databind.annotation.JsonDeserialize;
import {core_converter_package}.*;
{src_import}

{add_import}
""".format(src_import=src_import, add_import=add_import, gen_package=_package_path_info.enum_package.replace('.'+class_name, ''), core_converter_package=_package_path_info.core_converter_package)

    src_prefix = """{import_prefix}

{annotation}
public class PlatformCodes
{{
    {code_interface}

    public static <T extends Enum<T> & CommonCode> T enumByCode(Class<T> type, Long code)
    {{
        if (code == null)
        {{
            return null;
        }}
        final EnumSet<T> values = EnumSet.allOf(type);
        for (T e : values)
        {{
            if (e.getCode().equals(code))
            {{
                return e;
            }}
        }}
        return null;
    }}

    public static <T extends Enum<T> & CommonCode> T enumByName(Class<T> type, String name)
    {{
        if (Objects.isNull(name) || name.isBlank())
        {{
            return null;
        }}
        final EnumSet<T> values = EnumSet.allOf(type);
        for (T e : values)
        {{
            if (e.getName().equalsIgnoreCase(name))
            {{
                return e;
            }}
        }}
        return null;
    }}

    public static <T extends Enum<T> & CommonCode> String nameByCode(Class<T> type, Long code)
    {{
        T t = enumByCode(type, code);
        if (t == null)
        {{
            return null;
        }}
        return t.getName();
    }}

    public static <T extends Enum<T> & CommonCode> Long codeByName(Class<T> type, String name)
    {{
        T t = enumByName(type, name);
        if (t == null)
        {{
            return null;
        }}
        return t.getCode();
    }}

    public static <T extends Enum<T> & CommonCode> String enumNamesToString(Class<T> type)
    {{
        StringBuilder sb = new StringBuilder();
        final EnumSet<T> names = EnumSet.allOf(type);
        sb.append("[");
        for (T e : names)
        {{
            sb.append(e.getName()).append(",");
        }}
        sb.deleteCharAt(sb.lastIndexOf(",")).append("]");
        return sb.toString();
    }}

    // ###########################################################################
    // Generated Area
    // ###########################################################################
""".format(import_prefix=import_prefix, code_interface=code_interface, class_name=class_name, annotation=config.__FILE_ANNOTATION__)

    return src_prefix + src_contents + "}"


def write_file_core(path, class_name, data):
    file_name = class_name + '.java'
    with open(os.path.join(path, file_name), 'w', encoding='utf-8') as f:
        f.write(data)


template = """    
    @Getter
    @JsonDeserialize(using = {cls_name}.class)
    public enum {ename} implements CommonCode{add_interface}
    {{
		// @formatter:off
        {fields}
        ;
		// @formatter:on

        public final Long pcode = {pcode}L;
        public final String pname = "{pname}";
        private Long code;
        private String name;
        @JsonIgnore
        private String[] values;
        
        private {ename}(Long c , String v, String[] values) {{
            this.code = c;
            this.name = v;
            this.values = values;
        }}
        
        @jakarta.persistence.Converter(autoApply = true)
        static class Converter extends PlatformCodesConverter<{ename}, Long> {{
            public Converter() {{
                super({ename}.class);
            }}
        }}
    }}"""


def gen_code_enum(_package_path_info):
    src_contents = ""
    add_import = ""

    code_groups = get_code_groups(config.DB_CONNECTION_OPTS)
    for cg in code_groups:
        get_codes(cg, config.DB_CONNECTION_OPTS)

        add_interface = ""
        if cg.genum_name in config.ENUM_TYPE_INTERFACE_PACKAGE:
            for package in config.ENUM_TYPE_INTERFACE_PACKAGE[cg.genum_name]:
                add_import += """
    import {package};
    """.format(package=package)
                add_interface += ", " + package.split('.')[-1]

        fields = ",\n\t\t".join(
            map(lambda c: c.enum_name + "(" + c.code + "L, \"" + c.name + "\", new String[]{"+c.value_1+","+c.value_2+","+c.value_3+","+c.value_4+"})", cg.codes))
        cls_name = common.to_class_name(cg.genum_name) + 'Deserializer'
        src_contents = src_contents + template.format(
            ename=cg.genum_name,
            fields=fields,
            cls_name=cls_name,
            pcode=cg.gcode,
            pname=cg.gname_disp,
            add_interface=add_interface
        ) + "\n\n"

    class_name = _package_path_info.enum_package.split('.')[-1:][0]
    to_path = os.path.join(_package_path_info.project_src_path, _package_path_info.enum_package.replace('.', '/').replace(class_name, ''))

    write_file_core(to_path, class_name, create_src_string(_package_path_info, add_import, src_contents, class_name))
    print('Success : Write file -> {}'.format(os.path.join(to_path, class_name)))


def gen_code_handler(_package_path_info):
    code_groups = get_code_groups(config.DB_CONNECTION_OPTS)

    gen_converter.generate_jpa_type_handler(_package_path_info)
    gen_converter.generate_jackson_de_and_serializer(_package_path_info, code_groups)