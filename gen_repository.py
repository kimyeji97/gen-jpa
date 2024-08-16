#!/usr/bin/python
# -*- coding: utf-8 -*-

import common as common
import config as config


# Repository Interface 생성
def make_repository_interface_ex(_column_info, _package_path_info, table, fields, repository_package, entity_package):
    class_name = table.table_repository_interface_name
    repository = """package %(repository_package)s;

%(import_id)s
import %(core_repository_package)s.%(qdsl_core_class_name)s;
import %(entity_package)s.%(table_class_name)s;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.querydsl.QuerydslPredicateExecutor;
import org.springframework.stereotype.Repository;

@Repository 
public interface %(class_name)s extends JpaRepository<%(table_class_name)s, %(id_type)s>, QuerydslPredicateExecutor<%(table_class_name)s>, %(qdsl_core_class_name)s, %(qdsl_class_name)s 
{

}"""
    return repository % {
        'repository_package': repository_package
        , 'core_repository_package': _package_path_info.core_repository_package
        , 'entity_package': entity_package
        , 'table_class_name': table.table_entity_name
        , 'class_name': class_name
        , 'qdsl_core_class_name': table.table_qdsl_repository_core_interface_name
        , 'qdsl_class_name': table.table_qdsl_repository_interface_name
        , 'id_type': table.primary_keys_java_type
        ,
        'import_id': common.make_import_code(
            "{}.{}".format(_package_path_info.core_entity_id_package, table.primary_keys_java_type))
    }


# QdslRepository Interface 생성
def make_querydsl_repository_interface_ex(_column_info, _package_path_info, table, fields, repository_package, entity_package):
    class_name = table.table_qdsl_repository_interface_name
    repository = """package %(repository_package)s;

public interface %(table_class_name)s {

}
"""
    return repository % {
        'repository_package': repository_package
        , 'table_class_name': class_name
    }


# QdslRepositoryImpl 생성
def make_querydsl_repository_impl_ex(_column_info, _package_path_info, table, fields, repository_package, entity_package):
    class_name = table.table_qdsl_repository_impl_name
    repository = """package %(repository_package)s;

import com.querydsl.jpa.impl.JPAQueryFactory;
import %(core_repository_package)s.%(qdsl_core_impl_class_name)s;
import lombok.RequiredArgsConstructor;

@RequiredArgsConstructor
public class %(class_name)s implements %(qdsl_class_name)s {
    private final JPAQueryFactory queryFactory;
    private final %(qdsl_core_impl_class_name)s qdslRepository;
    
    
}
"""
    return repository % {
        'repository_package': repository_package
        , 'core_repository_package': _package_path_info.core_repository_package
        , 'class_name': class_name
        , 'qdsl_class_name': table.table_qdsl_repository_interface_name
        , 'qdsl_core_impl_class_name': table.table_qdsl_repository_core_impl_name
    }


# QdslRepositoryCore Interface 생성
def make_querydsl_repository_interface_core(_column_info, _package_path_info, table, fields, repository_package, entity_package):
    class_name = table.table_qdsl_repository_core_interface_name

    key_params = make_pk_params(_column_info, fields)
    repository = """package %(repository_package)s;

%(import_id)s
import %(entity_package)s.%(table_class_name)s;
import com.querydsl.core.types.Path;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;

import java.util.List;
%(key_params_import)s

%(annotation)s
public interface %(class_name)s {
    /**
     * 조건에 해당하는 목록 페이징 조회
     */
    Page<%(table_class_name)s> findPageByWhere(%(table_class_name)s param, Pageable pageable, Path sortField);
    
    /**
     * 조건에 해당하는 목록 조회
     */
    List<%(table_class_name)s> findAllByWhere(%(table_class_name)s param);
    
    /**
     * PK 리스트로 목록 조회 
     */
    List<%(table_class_name)s> findAllByKeyList(List<%(id_type)s> keyList);
    
    /**
     * 조건에 해당하는 PK 목록 조회
     */
    List<%(id_type)s> findAllKeyByWhere(%(table_class_name)s param);
    
    /**
     * PK로 단건 조회
     */
    %(table_class_name)s findOneByKey(%(key_params)s);
    
    /**
     * PK로 단건 삭제
     */
    long deleteByKey(%(key_params)s);
    
    /**
     * PK 리스트로 일괄 삭제
     */
    long deleteByKeyList(List<%(id_type)s> keyList);
}
"""
    return repository % {
        'repository_package': _package_path_info.core_repository_package
        , 'table_class_name': common.to_class_name(table.table_name)
        , 'id_type': table.primary_keys_java_type
        , 'import_id': common.make_import_code("{}.{}".format(_package_path_info.core_entity_id_package, table.primary_keys_java_type))
        , 'key_params': key_params['params_str']
        , 'key_params_import': key_params['import_str']
        , 'entity_package': entity_package
        , 'class_name': class_name
        , 'annotation': config.__FILE_ANNOTATION__.format(table.table_name)
    }


# QdslRepositoryCoreImpl#getKeySelectFrom 메소드 생성
def make_method_pk_select(table):
    pk_qclass_columns = []
    for pk in table.primary_keys:
        pk_qclass_columns.append("{}.{}".format(table.table_field_name, pk.java_field_name))

    return """public JPAQuery<%(primary_keys_java_type)s> getKeySelectFrom() 
    {
        return jpaQueryFactory.select(Projections.fields(%(primary_keys_java_type)s.class,
                        %(pk_qclass_columns)s
                )).from(%(table_field_name)s);
    }    
""" % {
        'primary_keys_java_type': table.primary_keys_java_type
        , 'pk_qclass_columns': ", ".join(pk_qclass_columns)
        , 'table_field_name': table.table_field_name
    }


# QdslRepositoryCoreImpl#getWhereBuilder 메소드의 본문 생성
def make_method_columns_where(_column_info, table, fields):
    like_field_list = ['uri', 'host', 'method']
    columns_where = []
    postfix_columns_where = []
    for field in fields:
        f = field.name
        if _column_info.include_update_dt_columns(f) or _column_info.include_insert_dt_columns(f):
            continue

        getter = common.to_getter("param", field)
        java_field = field.java_field_name
        null_check_string = field.null_check_string
        oper = 'eq({})'
        if (java_field in like_field_list) or common.endswith_ignore_case(f, "NM", "NAME"):
            oper = 'likeIgnoreCase({})'

        # 일반 컬럼
        columns_if = """if (%(null_check_string)s)
        {
            builder.and(%(qclass_name)s.%(field_namd)s.%(oper)s);            
        }""" % {
            'null_check_string': null_check_string[0]
            , 'qclass_name': table.table_field_name
            , 'field_namd': java_field
            , 'oper': oper.format(getter)
        }
        columns_where.append(columns_if)

        # 날짜 컬럼
        if field.is_date() or field.is_datetime() or field.is_datetime3() or field.is_time():
            columns_if = """if (%(null_check_string)s)
        {
            builder.and(%(qclass_name)s.%(field_namd)s.between(%(start_field)s, %(end_field)s));            
        }""" % {
                'null_check_string': null_check_string[1]
                , 'qclass_name': table.table_field_name
                , 'field_namd': java_field
                , 'start_field': getter.replace("()", _column_info.period_search_start_postfix + "()")
                , 'end_field': getter.replace("()", _column_info.period_search_end_postfix + "()")
            }
            postfix_columns_where.append(columns_if)

    method = """public BooleanBuilder getWhereBuilder(%(table_class)s param) 
    {
        BooleanBuilder builder = new BooleanBuilder();
        %(columns_where)s
        return builder;
    }"""

    return method % {
        'table_class': table.table_entity_name
        , 'columns_where': ("\n" + config._SP8).join(columns_where + postfix_columns_where)
    }


# QdslRepositoryCoreImpl#getWhereBuilderByKey 메소드 생성
def make_method_pk_where(table, fields, pk_params):
    columns_where = []
    for pk in table.primary_keys:
        columns_where.append(".and({}.{}.eq({}))".format(table.table_field_name, pk.java_field_name, pk.java_field_name))

    method = """public BooleanBuilder getWhereBuilderByKey(%(params)s) 
    {
        return new BooleanBuilder()
            %(columns_where)s;
    }"""

    return method % {
        'params': pk_params['params_str']
        , 'columns_where': ("\n" + config._SP12).join(columns_where)
    }


# QdslRepositoryCoreImpl#getWhereBuilderByKeyList 메소드 생성
def make_method_pk_in_where(table):
    t_field_name = table.table_field_name

    pk_columns_where = None
    for pk in table.primary_keys:
        if pk_columns_where is None:
            pk_columns_where = '{}.{}.eq({})'.format(t_field_name, pk.java_field_name, common.to_getter("key", pk))
        else:
            pk_columns_where += ('\r\n' + config._SP12 + config._SP12 + '.and({}.{}.eq({}))'
                                 .format(t_field_name, pk.java_field_name, common.to_getter("key", pk)))

    method = """public BooleanBuilder getWhereBuilderByKeyList(List<%(primary_keys_java_type)s> keyList) 
    {
        BooleanBuilder builder = new BooleanBuilder();
        for (%(primary_keys_java_type)s key : keyList) 
        {
            builder.or(%(pk_columns_where)s
            );
        }
        return builder;
    }"""

    return method % {
        'primary_keys_java_type': table.primary_keys_java_type
        , 'pk_columns_where': pk_columns_where
    }


# QdslRepositoryCoreImpl#findxxx 메소드 생성
def make_method_find(_column_info, table, fields, type):
    class_name = table.table_entity_name
    where_method_name = 'getWhereBuilder'
    dml = 'jpaQueryFactory.selectFrom({})'.format(table.table_field_name)
    fetch = 'fetch'
    if type == 'AllByWhere':
        return_type = 'List<{}>'.format(class_name)
        params = '{} param'.format(class_name)
        params_values = 'param'
    elif type == 'AllKeyByWhere':
        dml = 'getKeySelectFrom()'
        return_type = 'List<{}>'.format(table.primary_keys_java_type)
        params = '{} param'.format(class_name)
        params_values = 'param'
    elif type == 'AllByKeyList':
        return_type = 'List<{}>'.format(class_name)
        params = 'List<{}> keyList'.format(table.primary_keys_java_type)
        params_values = 'keyList'
        where_method_name = 'getWhereBuilderByKeyList'
    elif type == 'OneByKey':
        pk_params = make_pk_params(_column_info, fields)
        return_type = class_name
        params = pk_params['params_str']
        params_values = pk_params['params_value_str']
        where_method_name = 'getWhereBuilderByKey'
        fetch += 'One'

    method = """@Override
    public %(return_type)s %(method_name)s(%(params)s) {
        return %(dml)s
                .where(this.%(where_method_name)s(%(params_values)s))
                .%(fetch)s();
    }"""
    return method % {
        'return_type': return_type
        , 'method_name': 'find' + type
        , 'params': params
        , 'dml': dml
        , 'where_method_name': where_method_name
        , 'params_values': params_values
        , 'fetch': fetch
    }


# QdslRepositoryCoreImpl#findPageByWhere 메소드 생성
def make_method_find_page(table):
    method = """@Override
    public Page<%(t_class_name)s> findPageByWhere (%(t_class_name)s param, Pageable pageable, Path sortField)
    {
        List<%(t_class_name)s> list = jpaQueryFactory.selectFrom(%(t_field_name)s)
                .where(this.getWhereBuilder(param))
                .orderBy(new OrderSpecifier<>(Order.DESC, sortField))
                .offset(pageable.getOffset())
                .limit(pageable.getPageSize())
                .fetch();

        JPAQuery<Long> countQuery = jpaQueryFactory.select(%(t_field_name)s.count())
                .from(%(t_field_name)s)
                .where(this.getWhereBuilder(param));

        return PageableExecutionUtils.getPage(list, pageable, countQuery::fetchOne);
    }"""
    return method % {
        't_class_name': table.table_entity_name
        , 't_field_name': table.table_field_name
    }


# QdslRepositoryCoreImpl#deletByKeyexxx 메소드 생성
def make_method_delete_by_id(table, fields, pk_params, is_list=False):
    t_field_name = table.table_field_name
    if len(table.delete_column) < 1:
        dml = 'jpaQueryFactory.delete({})'.format(t_field_name)
    else:
        dml = """jpaQueryFactory.update({})
                .set({}.{}, true)""".format(t_field_name, t_field_name, table.delete_column[0].java_field_name)

    method = """@Override
    public long %(method_name)s (%(pk_params)s) {
        return %(dml)s
                .where(this.%(where_method_name)s(%(pk_values)s))
                .execute();
    }"""

    return method % {
        'method_name': 'deleteByKey' if not is_list else 'deleteByKeyList'
        , 'where_method_name': 'getWhereBuilderByKey' if not is_list else 'getWhereBuilderByKeyList'
        , 'pk_params': pk_params['params_str'] if not is_list else "List<{}> keyList".format(table.primary_keys_java_type)
        , 'dml': dml
        , 'pk_values': pk_params['params_value_str'] if not is_list else 'keyList'
    }


# QdslRepositoryCoreImpl 생성
def make_querydsl_repository_impl_core(_column_info, _package_path_info, table, fields, repository_package, entity_package):
    class_name = table.table_qdsl_repository_core_impl_name
    t_class_name = table.table_entity_name
    t_field_name = table.table_field_name

    pk_params = make_pk_params(_column_info, fields)
    import_src = [
        common.make_import_code("{}.{}".format(_package_path_info.core_entity_id_package, table.primary_keys_java_type))
        , common.make_import_code("{}.{}".format(entity_package, t_class_name))
    ]
    import_qclass_src = common.make_import_code('static {}.{}.{}'.format(entity_package, table.table_qclass_name, t_field_name))
    pk_select = make_method_pk_select(table)
    columns_where = make_method_columns_where(_column_info, table, fields)
    pk_where = make_method_pk_where(table, fields, pk_params)
    pk_in_where = make_method_pk_in_where(table)
    find_page_by_where = make_method_find_page(table)
    find_all_by_where = make_method_find(_column_info, table, fields, 'AllByWhere')
    find_all_by_id_list = make_method_find(_column_info, table, fields, 'AllByKeyList')
    find_all_id_by_where = make_method_find(_column_info, table, fields, 'AllKeyByWhere')
    find_one_by_id = make_method_find(_column_info, table, fields, 'OneByKey')
    delete_by_id = make_method_delete_by_id(table, fields, pk_params)
    delete_by_id_list = make_method_delete_by_id(table, fields, pk_params, True)

    repository = """package %(gen_package)s;
    
import com.querydsl.core.BooleanBuilder;
import com.querydsl.core.types.Order;
import com.querydsl.core.types.OrderSpecifier;
import com.querydsl.core.types.Path;
import com.querydsl.core.types.Projections;
import com.querydsl.jpa.impl.JPAQuery;
import com.querydsl.jpa.impl.JPAQueryFactory;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.support.PageableExecutionUtils;
import java.util.List;
import java.util.Objects;
%(import_src)s

%(import_qclass_src)s

%(annotation)s
@RequiredArgsConstructor
public class %(class_name)s implements %(interface_class_name)s 
{
    private final JPAQueryFactory jpaQueryFactory;
    
    /**
     * pk select 문
     */
    %(pk_select)s
     
     /**
     * columns where 절
     */
    %(columns_where)s
     
     /**
     * pk 단건 where 절
     */
    %(pk_where)s
     
     /**
     * pk list where 절
     */
    %(pk_in_where)s
    
    
    %(find_page_by_where)s
     
    %(find_all_by_where)s
    
    %(find_all_by_id_list)s
    
    %(find_all_id_by_where)s
    
    %(find_one_by_id)s
    
    %(delete_by_id)s
    
    %(delete_by_id_list)s
}
"""
    return repository % {
        'gen_package': _package_path_info.core_repository_package
        , 'import_src': "\r\n".join(import_src) + '\r\n' + pk_params['import_str']
        , 'import_qclass_src': import_qclass_src
        , 'table_class_name': t_class_name
        , 'pk_select': pk_select
        , 'columns_where': columns_where
        , 'pk_where': pk_where
        , 'pk_in_where': pk_in_where
        , 'find_page_by_where': find_page_by_where
        , 'find_all_by_where': find_all_by_where
        , 'find_all_by_id_list': find_all_by_id_list
        , 'find_all_id_by_where': find_all_id_by_where
        , 'find_one_by_id': find_one_by_id
        , 'delete_by_id': delete_by_id
        , 'delete_by_id_list': delete_by_id_list
        , 'class_name': class_name
        , 'interface_class_name': table.table_qdsl_repository_core_interface_name
        , 'annotation': config.__FILE_ANNOTATION__.format(table.table_name)
    }


def make_pk_params(_column_info, fields):
    imports = []
    params = []
    values = []
    for field in fields:
        f = field.name
        java_type = field.java_type
        field_f_name = field.java_field_name
        if (_column_info.include_insert_dt_columns(f)
                or _column_info.include_update_dt_columns(f)
                or field.is_pk is False):
            continue

        params.append("{} {},".format(java_type, field_f_name))
        values.append("{},".format(field_f_name))
        if field.java_type_package:
            imports.append(common.make_import_code(field.java_type_package))

    # if len(params) > 0:
    #     imports.append(common.make_import_code(_package_path_info.annotations_param))

    params[-1] = params[-1][0:-1]
    values[-1] = values[-1][0:-1]
    return {
        'params_str': (" ").join(params)
        , 'params_value_str': (" ").join(values)
        , 'import_str': ("\n").join(imports)
    }
