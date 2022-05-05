from graphene import Schema
from psql2graphql.core import generate_queries, ClassFactory, Introspector


def generate_endpoints(config):
    introspector = get_introspector(config)
    tables = introspector.get()
    return Schema(query=generate_queries([ClassFactory(table, config) for table in tables]),
                  auto_camelcase=False), tables


def get_introspector(config):
    introspector = Introspector()
    introspector.set_connection(config)
    return introspector
