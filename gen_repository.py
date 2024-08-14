#!/usr/bin/python
# -*- coding: utf-8 -*-

import common as common

_column_info = None
_package_path_info = None


def make_repository_interface_ex(_c_info, _p_info, table, fields, repository_package, entity_package):
    global _column_info
    global _package_path_info
    _column_info = _c_info
    _package_path_info = _p_info

    repository = """package %(repository_package)s;

%(import_id)s
import %(core_repository_package)s.%(table_class_name)sQDSLRepositoryCore;
import %(entity_package)s.%(table_class_name)s;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.querydsl.QuerydslPredicateExecutor;
import org.springframework.stereotype.Repository;

@Repository 
public interface %(table_class_name)sRepository extends JpaRepository<%(table_class_name)s, %(id_type)s>, QuerydslPredicateExecutor<%(table_class_name)s>, %(table_class_name)sQDSLRepositoryCore, %(table_class_name)sQDSLRepository 
{

}"""
    return repository % {
        'repository_package': repository_package
        , 'core_repository_package': _package_path_info.core_repository_package
        , 'entity_package': entity_package
        , 'table_class_name': common.to_class_name(table.table_name)
        , 'id_type': table.id_java_type
        , 'import_id': common.make_import_code("{}.{}".format(_package_path_info.core_entity_package, table.id_java_type))
    }


def make_querydsl_repository_interface_ex(_c_info, _p_info, table, fields, repository_package, entity_package):
    global _column_info
    global _package_path_info
    _column_info = _c_info
    _package_path_info = _p_info

    repository = """package %(repository_package)s;

public interface %(table_class_name)sQDSLRepository {

}
"""
    return repository % {
        'repository_package': repository_package
        , 'table_class_name': common.to_class_name(table.table_name)
    }


def make_querydsl_repository_impl_ex(_c_info, _p_info, table, fields, repository_package, entity_package):
    global _column_info
    global _package_path_info
    _column_info = _c_info
    _package_path_info = _p_info

    repository = """package %(repository_package)s;

import com.querydsl.jpa.impl.JPAQueryFactory;
import %(core_repository_package)s.%(table_class_name)sQDSLRepositoryCoreImpl;
import lombok.RequiredArgsConstructor;

@RequiredArgsConstructor
public class %(table_class_name)sQDSLRepositoryImpl implements %(table_class_name)sQDSLRepository {
    private final JPAQueryFactory queryFactory;
    private final %(table_class_name)sQDSLRepositoryCoreImpl qdslRepository;
    
    
}
"""
    return repository % {
        'repository_package': repository_package
        , 'core_repository_package': _package_path_info.core_repository_package
        , 'table_class_name': common.to_class_name(table.table_name)
    }


def make_querydsl_repository_interface_core(_c_info, _p_info, table, fields, repository_package, entity_package):
    global _column_info
    global _package_path_info
    _column_info = _c_info
    _package_path_info = _p_info

    key_params = make_mapper_key_params(fields)
    repository = """package %(repository_package)s;

%(import_id)s
import %(entity_package)s.%(table_class_name)s;

import java.util.List;
%(key_params_import)s

public interface %(table_class_name)sQDSLRepositoryCore {
    List<%(id_type)s> findIdAllByWhere(%(table_class_name)s param);
    
    List<%(table_class_name)s> findAllByWhere(%(table_class_name)s param);
    
    List<%(table_class_name)s> findAllByKeyList(List<%(id_type)s> keyList);
    
    %(table_class_name)s findOneByKey(%(key_params)s);
    
    long deleteByKey(%(key_params)s);
    
    long deleteByKeyList(List<%(id_type)s> keyList);
}
"""
    return repository % {
        'repository_package': _package_path_info.core_repository_package
        , 'table_class_name': common.to_class_name(table.table_name)
        , 'id_type': table.id_java_type
        , 'import_id': common.make_import_code("{}.{}".format(_package_path_info.core_entity_package, table.id_java_type))
        , 'key_params': key_params['params_str']
        , 'key_params_import': key_params['import_str']
        , 'entity_package': entity_package
    }


# def make_mapper_core(_c_info, _p_info, table, fields, repository_package, model_package):
#     global _column_info
#     global _package_path_info
#     _column_info = _c_info
#     _package_path_info = _p_info
#
#     key_params = make_mapper_key_params(fields)
#     sequence_mapper_src = ''
#
#     if table.sequence is not None:
#         seq_cls_name = common.to_class_name(table.sequence)
#         sequence_mapper_src = """
# Long getNext{seq_cls_name}();
#
# Long getLast{seq_cls_name}();
#
# Long setLast{seq_cls_name}(Long lastValue);
# """.format(seq_cls_name=seq_cls_name, sequence_name=table.sequence)
#
#     mapper = """package %(repository_package)s;
#
# import %(model_package)s.%(table_class_name)s;
# import java.util.List;
# %(key_params_import)s
#
# public interface %(table_class_name)sMapperCore
# {
# int create%(table_class_name)s(%(table_class_name)s %(table_field_name)s);
#
# %(table_class_name)s create%(table_class_name)sReturn(%(table_class_name)s %(table_field_name)s);
#
# int create%(table_class_name)sList(List<%(table_class_name)s> %(table_field_name)sList);
#
# %(table_class_name)s read%(table_class_name)s(%(table_class_name)s %(table_field_name)s);
#
# %(table_class_name)s read%(table_class_name)sByKey(%(key_params)s);
#
# List<%(table_class_name)s> list%(table_class_name)s(%(table_class_name)s %(table_field_name)s);
#
# int update%(table_class_name)s(%(table_class_name)s %(table_field_name)s);
#
# %(table_class_name)s update%(table_class_name)sReturn(%(table_class_name)s %(table_field_name)s);
#
# int updateForce(%(table_class_name)s %(table_field_name)s);
#
# %(table_class_name)s updateForceReturn(%(table_class_name)s %(table_field_name)s);
#
# int delete%(table_class_name)s(%(table_class_name)s %(table_field_name)s);
#
# int delete%(table_class_name)sByKey(%(key_params)s);
# %(sequence_mapper_src)s
# }
# """
#     return mapper % {'table_class_name': common.to_class_name(table.table_name)
#         , 'table_field_name': common.to_field_name(table.table_name)
#         , 'repository_package': _package_path_info.core_repository_package
#         , 'model_package': model_package
#         , 'sequence_mapper_src': sequence_mapper_src
#         , 'key_params': key_params['params_str']
#         , 'key_params_import': key_params['import_str']
#                      }


def make_mapper_key_params(fields):
    imports = []
    params = []
    for field in fields:
        f = field.name
        java_type = field.java_type
        field_f_name = field.java_field_name
        if (_column_info.include_insert_dt_columns(f)
                or _column_info.include_update_dt_columns(f)
                # or field.is_auto_increment()
                or field.is_pk == False):
            continue

        params.append("@Param(\"{}\") {} {},".format(field_f_name, java_type, field_f_name))
        if field.java_type_package:
            imports.append(common.make_import_code(field.java_type_package))

    if len(params) > 0:
        imports.append(common.make_import_code(_package_path_info.annotations_param))

    params[-1] = params[-1][0:-1]
    return {
        'params_str': (" ").join(params)
        , 'import_str': ("\n").join(imports)
    }
