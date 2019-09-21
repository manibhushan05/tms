"""
JSON Schema helper, provides methods for constructing fine JSON schemas on the fly. See `schema.py` files under
`customer`, `fms` or `driver` app for implementation examples
"""
import json

import jsonschema
from jsonschema.exceptions import ValidationError, SchemaError

from api.utils import merge


def any_schema():
    return {}


def null_schema():
    return {'type': 'null'}


def num_schema(gt=None, lt=None, multiple_of=None):
    s = {'type': 'number'}
    if gt is not None:
        s['minimum'] = gt
    if lt is not None:
        s['maximum'] = lt
    if multiple_of is not None:
        s['multipleOf'] = multiple_of
    return s


def str_schema(min_len=None, max_len=None):
    s = {'type': 'string'}
    if min_len is not None:
        s['minLength'] = min_len
    if max_len is not None:
        s['maxLength'] = max_len
    return s


def enum_schema(args, type=None):
    s = {'enum': args}
    if type is not None:
        s['type'] = type
    return s


def bool_schema():
    return {'type': 'boolean'}


def null_num_schema(gt=None, lt=None, multiple_of=None):
    return {'anyOf': [num_schema(gt, lt, multiple_of), null_schema()]}


def null_str_schema(min_len=None, max_len=None):
    return {'anyOf': [str_schema(min_len, max_len), null_schema()]}


def dict_schema(required_schema_properties=None, **properties):
    s = {'type': 'object'}
    if properties:
        s['properties'] = properties
        if required_schema_properties is None:
            s['required'] = properties.keys()
        elif len(required_schema_properties) > 0:
            invalid_required_props = set(required_schema_properties) - set(properties.keys())
            assert not invalid_required_props, 'schema error, required keys %s not present in properties'
            s['required'] = required_schema_properties
    return s


def null_dict_schema(required_schema_properties=None, **properties):
    return {'anyOf': [dict_schema(required_schema_properties, **properties), null_schema()]}


def list_schema(schema=None, min_items=None, max_items=None):
    s = {'type': 'array'}
    if schema:
        s['items'] = schema
    if min_items is not None:
        s['minItems'] = min_items
    if max_items is not None:
        s['maxItems'] = max_items
    return s


def null_list_schema(schema=None, min_items=None, max_items=None):
    return {'anyOf': [list_schema(schema, min_items, max_items), null_schema()]}


def merge_dict_schema(schema1, schema2):
    return dict_schema(**merge(schema1.get('properties', {}), schema2.get('properties', {})))


def status_msg_schema():
    return dict_schema(status=str_schema(), msg=str_schema())


def status_msg_extra_schema(**properties):
    return merge_dict_schema(status_msg_schema(), dict_schema(**properties))


def validate_json(data, schema):
    try:
        jsonschema.validate(data, schema)
        return None
    except (ValidationError, SchemaError) as e:
        return e
