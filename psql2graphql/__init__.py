from graphene import Schema
from psql2graphql.core import generate_queries, ClassFactory, Introspector


def generate_endpoints(config):
    introspector = get_introspector(config)
    tables = introspector.get()
    query = generate_queries([ClassFactory(table, config) for table in tables],
                             [table['name'] for table in tables],
                             config)
    return Schema(query=query,
                  auto_camelcase=False), tables


def get_introspector(config):
    introspector = Introspector()
    introspector.set_connection(config)
    return introspector
