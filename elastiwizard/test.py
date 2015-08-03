from elastiwizard.transform import TransformQuestion
from elastiwizard.grammar import GrammarBuilder
import json

test_question_1 = """how many requests researched by user/yPyA5n7P since 2015-07-07"""
test_question_2 = """count requests researched by researched_by each day"""
test_question_3 = """sum the total_length of albums released since friday"""

def test_parse():
    grammar_builder = GrammarBuilder()
    question = TransformQuestion.transform(grammar_builder, test_question_1,
        just_parse=True)

    print question
    print test_question_1

    assert question['metric'] == "how many"
    assert question['index'] == "requests"
    assert question['delta'] == "since 2015-07-07"
    assert question['where'] == "researched"
    assert question['group_by'] == "user/yPyA5n7P"

    question = TransformQuestion.transform(grammar_builder, test_question_3,
        just_parse=True)

    print question
    # {'field': 'total_length', 'metric': 'sum', 'delta': 'since friday', 'where': 'released', 'index': 'albums'}
    assert question['metric'] == 'sum'
    assert question['index'] == 'albums'
    assert question['delta'] == 'since friday'
    assert question['field'] == 'total_length'
    assert question['where'] == 'released'

def test_transform():
    grammar_builder = GrammarBuilder()

    terms_map = {
        'researched': '!needs_license_research',
        'requests': 'researched_by',
        '*default_date_field': 'license_fulfilled_at',
        "r'user\/[a-zA-Z0-9]+'": "researched_by"
    }

    # sum of albums sold since friday
    """
        {
            'metric': 'sum',
            'index': 'albums',
            'field': 'total_length'
            'delta': 'since friday',
        }


    metric field delta where group_by
    sum the total length of albums released since friday
    metric field

    """

    terms_map = {
        'albums': {
            'index': 'rdalbum_production',
            'field': {
                'default': 'title',
                'length': 'total_length'
            },
            'where': {
                'released': {
                    'field': 'release_date'
                }
            },
            'delta': {
                'date_field': 'release_date'
            }
        },

        'requests': {
            'field': {
                'default': 'researched_by'
            },
            'index': [
                'rdlicenserequest_production',
                'rdsoundrecording_production',
                'rdtrack_production'
            ],
            'group_by': {
                'user/*': 'researched_by',
            },
            'where': {
                'default': 'some required field',
                'researched': {
                    'filters': '!needs_license_research',
                    'field': 'researched_by'
                }
            },
            'delta': {
                'date_field': 'license_fulfilled_at'
            }
        }
    }

    query, question = TransformQuestion.transform(grammar_builder, test_question_1,
        terms_map=terms_map, return_parsed_question=True)

    json_query = json.dumps(query, indent=4, sort_keys=True)
    assert json_query
    print test_question_1
    print json_query

    assert question['metric'] == "how many"
    assert question['index'] == "requests"
    assert question['delta'] == "since 2015-07-07"
    assert question['where'] == "researched"
    assert question['group_by'] == "user/yPyA5n7P"

    query = TransformQuestion.transform(grammar_builder, test_question_2,
        terms_map=terms_map)

    json_query = json.dumps(query, indent=4, sort_keys=True)
    assert json_query
    print test_question_2
    print json_query


    query = TransformQuestion.transform(grammar_builder, test_question_3,
        terms_map=terms_map)

    json_query = json.dumps(query, indent=4, sort_keys=True)
    assert json_query
    print test_question_3
    print json_query
