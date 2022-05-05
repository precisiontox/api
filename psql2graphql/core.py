from typing import Dict, List
import logging

from psycopg2 import connect
from flask import escape
import sqlparse
from graphene import ObjectType, String, Argument, Int, Float, Boolean, List as graphList

from psql2graphql.inputs import (
    StringComparator,
    IntComparator,
    FloatComparator,
    InputType as InputObjectType,
    BooleanComparator
)


class BaseHandler:

    def __init__(self):
        self.connection = {}
        self.conn = None
        self.cur = None

        self.query_fields = []
        self.params = {}
        self.get_query = None
        self.table_name = None
        self.name = None
        self.graph_fields = None
        self.graph_parameters = None
        self.default_limit = 100

        self.operators = {
            "eq": "=",
            "gt": ">",
            "gte": ">=",
            "lt": "<",
            "lte": "<=",
            "like": "LIKE"
        }
        self.comparators = {
            'and': 'AND',
            '&': 'AND',
            'AND': 'and',
            'or': 'OR',
            '|': 'OR',
            'OR': 'OR'
        }

    def set_connection(self, connection: Dict):
        """
        Sets the connection to the database.
        """
        self.connection = {
            "host": connection['HOST'],
            "database": connection['DATABASE_NAME'],
            "user": connection['USER'],
            "password": connection['USER_PWD']
        }
        if 'LOG_LEVEL' in connection and connection['LOG_LEVEL'] == 'INFO':
            logging.basicConfig(level=logging.INFO)

    def get_database_connection(self):
        """
        Creates the connection and cursor to the database.
        """
        self.conn = connect(host=self.connection['host'],
                            database=self.connection['database'],
                            user=self.connection['user'],
                            password=self.connection['password'])
        self.cur = self.conn.cursor()

    def close_connection(self):
        """
        Closes the connection and cursor to the database.
        """
        self.cur.close()
        self.conn.close()

    def limit_query(self, query: str) -> str:
        """
        Limits the query to the first n results.

        :param query: the query to limit
        :return: the limited query
        """
        limit = self.params['limit'] if self.params and 'limit' in self.params else self.default_limit
        if limit == 0:
            return query
        limiter = f" LIMIT {limit};"
        if query.endswith(';'):
            query = query[:-1]
        return query + limiter

    def get_comparator(self) -> str:
        """
        Builds the operators for the query.

        :return: the query with the operators
        """
        if not self.params or 'operator' not in self.params:
            return 'AND'
        else:
            if self.params['operator'] not in self.comparators:
                return 'AND'
            return self.comparators[self.params['operator']]

    def get(self, fields=None, params=None) -> List[Dict]:
        """
        Base get method for the API.
        """
        self.query_fields = fields
        self.params = params
        self.get_query = self.build_base_query(self.name)
        self.get_query = self.limit_query(self.get_query)
        results = self.execute_query(self.get_query)
        return [result[0] for result in results]

    def get_where_clause(self) -> str:
        """
        Builds the where clause for the query.

        @return: the where clause
        """
        where_statements = ''
        comparator = self.get_comparator()
        i = 0
        if self.params:
            for param_name in self.params:
                parameter = self.params[param_name]
                if parameter and param_name != 'operator' and param_name != 'limit':
                    for param in parameter:
                        operator = self.operators[param] if param in self.operators else '='
                        param_value = parameter[param] if param != 'like' else f'%{parameter[param]}%'
                        param_value = escape(param_value)
                        fragment = f'{self.table_name}."{param_name}" {operator} \'{param_value}\''
                        if i == 0:
                            where_statements = f" WHERE {fragment}"
                        else:
                            where_statements += f" {comparator} {fragment}"
                        i += 1
        return where_statements

    def execute_query(self, query: str):
        """
        Executes the query and returns the results.

        @param query: the query to execute
        @return: the results of the query
        """
        message = sqlparse.format(query, reindent=True, keyword_case='upper')
        logging.info(f'Executing query: \n{message}\n---')
        self.get_database_connection()
        self.cur.execute(query)
        results = self.cur.fetchall()
        self.close_connection()
        return results

    def build_base_query(self, alias: str) -> str:
        """
        Builds the base query for the database given an alias for the current table

        @return: the base query
        """
        fields = [f'{self.table_name}."{field}"' for field in self.query_fields]
        query = f"SELECT {', '.join(fields)} FROM {self.table_name}" + self.get_where_clause()
        query = f"WITH {alias} AS ({query}) SELECT row_to_json({alias}) as data FROM {alias};"
        return query


class Handler(BaseHandler):

    def __init__(self, name, table, params, fields):
        super(Handler, self).__init__()
        self.name = name
        self.table_name = table
        self.graph_parameters = params
        self.graph_fields = fields


class Introspector(BaseHandler):

    def get(self, params=None, filters=None):
        outputs = {}
        mapping = {
            'text': 'string',
            'character varying': 'string',
            'integer': 'int',
            'double precision': 'float',
            'boolean': 'boolean',
        }
        get_fields = "SELECT row_to_json(r) AS DATA" \
                     " FROM (" \
                     "     WITH comments as (" \
                     "        SELECT tablename" \
                     "        FROM pg_catalog.pg_tables" \
                     "        WHERE schemaname != 'pg_catalog' AND schemaname != 'information_schema')" \
                     "     SELECT obj_description(oid) as table_comment, relname, TABLE_NAME, COLUMN_NAME, data_type," \
                     "            (SELECT pg_catalog.col_description(c.oid, cols.ordinal_position::int)" \
                     "                FROM pg_catalog.pg_class c" \
                     "                WHERE c.oid = (SELECT ('\"' || cols.table_name || '\"')::regclass::oid)" \
                     "                  AND c.relname = cols.table_name" \
                     "            ) AS column_comment" \
                     "     FROM INFORMATION_SCHEMA.COLUMNS as cols, pg_class, comments" \
                     "     WHERE TABLE_NAME = tablename  AND relname = tablename" \
                     ") r;"

        fields = self.execute_query(get_fields)
        for field in fields:
            field = field[0]
            if self.field_valid(field['column_name']):
                param = {
                    'value': mapping[field['data_type']],
                    'description': field['column_comment']
                }
                if field['table_name'] not in outputs:
                    outputs[field['table_name']] = {
                        'name': field['table_name'],
                        'table_name': field['table_name'],
                        'description': field['table_comment'],
                        'parameters': {}
                    }
                    outputs[field['table_name']]['parameters'][field['column_name']] = param
                else:
                    outputs[field['table_name']]['parameters'][field['column_name']] = param
            else:
                logging.warning(f'Field {field["column_name"]} from table {field["table_name"]} could not be validated '
                                f'during introspection and will be ignored.')
        return [output for output in outputs.values()]

    @staticmethod
    def field_valid(field):
        return '.' not in field and '-' not in field and ' ' not in field


class ClassFactory:

    def __init__(self, table, connector):
        self.mapping = {
            'int': [IntComparator, Int],
            'string': [StringComparator, String],
            'float': [FloatComparator, Float],
            'boolean': [BooleanComparator, Boolean]
        }
        self.fields = table['parameters']
        self.alias = table['name'].capitalize()
        self.graph_parameters = self.generate_graph_parameters()
        self.graph_fields = self.generate_graph_fields()
        self.graphql_object = Handler(self.alias, table['table_name'], self.graph_parameters, self.graph_fields)
        self.graphql_object.set_connection(connector)

    def generate_graph_parameters(self):
        classname = self.alias + 'Parameters'
        options = {}
        parameters = self.fields
        for field_name in parameters:
            field_val = self.mapping[parameters[field_name]['value']][0]
            options[field_name] = Argument(field_val,
                                           required=False,
                                           description='Search %s' % parameters[field_name]['description'])
        return type(classname, (InputObjectType,), options)

    def generate_graph_fields(self):
        classname = self.alias + 'QueryFields'
        options = {}
        parameters = self.fields
        for field_name in parameters:
            field_val = self.mapping[parameters[field_name]['value']][1]
            options[field_name] = field_val(description=parameters[field_name]['description'])
        return type(classname, (ObjectType,), options)


def make_resolver(record_name, handler):
    def resolver(parent, info, filters):
        fields = [field.name.value for field in info.field_nodes[0].selection_set.selections]
        return handler.graphql_object.get(fields, filters)
    resolver.__name__ = 'resolve_%s' % record_name
    return resolver


def generate_queries(handlers):
    options = {}
    for handler in handlers:
        options[handler.alias.lower()] = graphList(handler.graphql_object.graph_fields,
                                                   filters=Argument(handler.graphql_object.graph_parameters),
                                                   description='List of %s' % handler.alias.lower())
        options['resolve_%s' % handler.alias.lower()] = make_resolver(handler.alias.lower(), handler)
    query = type('Query', (ObjectType,), options)
    return query
