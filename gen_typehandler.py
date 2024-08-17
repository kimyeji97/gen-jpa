#!/usr/bin/python3
# -*- coding: utf-8 -*-


import sys, os
import datetime
import common

print("generate the 'Typehandler' with payment code.")

__IS_VERSION_3__ = sys.version_info.major == 3

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dir_path)


def generate_jpa_type_handler(_package_path_info):
    code_class_name = _package_path_info.enum_package.split('.')[-1:][0]
    class_name = code_class_name + 'Converter'
    src = """package %(gen_package)s;

import %(enumpackage)s;
import jakarta.persistence.AttributeConverter;

import java.util.Arrays;
import java.util.Objects;
import java.util.Optional;

public abstract class %(class_name)s<T extends %(code_class_name)s.CommonCode, Long> implements AttributeConverter<T, Long> {
    private final Class<T> clazz;
    
    public PlatformCodesConverter(Class<T> clazz) {
        this.clazz = clazz;
    }
    
    @Override
    public Long convertToDatabaseColumn(T attribute) {
        if (Objects.isNull(attribute)) {
            return null;
        }
        return (Long) attribute.getCode();
    }
    
    @Override
    public T convertToEntityAttribute(Long dbData) {
        if (Objects.isNull(dbData)) {
            return null;
        }
        Optional<T> first = Arrays.stream(clazz.getEnumConstants()).filter(e -> e.getCode().equals(dbData)).findFirst();
        return first.orElse(null);
    }
}""" % {
        'class_name': class_name
        , 'code_class_name': code_class_name
        , 'gen_package': _package_path_info.core_converter_package
        , 'enumpackage': _package_path_info.enum_package
    }

    path = os.path.join(_package_path_info.project_src_path, _package_path_info.core_converter_package.replace(".", "/"))
    write_file_core(path, class_name + '.java', src)

    print('JPA AttributeConverter have been generated. Copy the sources and paste to source directory.')


def generate_jackson_de_and_serializer(_package_path_info, code_groups):
    path = os.path.join(_package_path_info.project_src_path, _package_path_info.core_converter_package.replace(".", "/"))
    code_class_name = _package_path_info.enum_package.split('.')[-1:][0]
    for cg in code_groups:
        enum = cg.genum_name
        de_cls_name = common.to_class_name(enum) + 'Deserializer'

        deserializer_src = """package {gen_package};

import com.fasterxml.jackson.core.JsonParser;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.DeserializationContext;
import com.fasterxml.jackson.databind.JsonDeserializer;
import org.springframework.core.convert.converter.Converter;
import org.springframework.stereotype.Component;
import java.io.IOException;
import java.util.Objects;

import {enumpackage};
import {enumpackage}.CommonCode;
import {enumpackage}.{type_name};

@Component
public class {cls_name} extends JsonDeserializer<{type_name}> implements Converter<String,{type_name}>
{{
    @Override
    public {type_name} deserialize(JsonParser jp, DeserializationContext ctxt)
        throws IOException, JsonProcessingException
    {{
        if (jp.isExpectedStartObjectToken())
        {{
            CommonCode cd = jp.readValueAs(CommonCode.class);
            if (cd == null)
            {{
                return null;
            }}

            if (cd.getCode() != null)
            {{
                return {code_class_name}.enumByCode({type_name}.class, cd.getCode());
            }}

            if (Objects.isNull(cd.getName()) || cd.getName().isEmpty())
            {{
                return {code_class_name}.enumByName({type_name}.class, cd.getName());
            }} else
            {{
                // Invalid Data
                return null;
            }}
        }}
        else
        {{
            return convertFromString(jp.getValueAsString());
        }}
    }}

    private {type_name} convertFromString(String value)
    {{
        if (Objects.isNull(value) || value.isEmpty())
        {{
            return null;
        }}
        {type_name} pr = {code_class_name}.enumByName({type_name}.class, value);
        if (pr == null)
        {{
            try {{
                pr = {code_class_name}.enumByCode({type_name}.class , Long.parseLong(value));
            }} catch (NumberFormatException e) {{
                return null;
            }}
        }}

        return pr;
    }}

    @Override
    public Class<{type_name}> handledType()
    {{
        return {type_name}.class;
    }}

    // Converter Implementation
    @Override
    public {type_name} convert(String source)
    {{
        return convertFromString(source);
    }}
}}
""".format(enumpackage=_package_path_info.enum_package, cls_name=de_cls_name, type_name=enum,
           code_class_name=code_class_name,
           gen_package=_package_path_info.core_converter_package)
        write_file_core(path, de_cls_name + '.java', deserializer_src)

    print('Jackson Deserializer have been generated. Copy the sources and paste to source directory.')


def write_file_core(path, file_name, data):
    with open(os.path.join(path, file_name), 'w') as f:
        f.write(data)

############################################
## main()
############################################
