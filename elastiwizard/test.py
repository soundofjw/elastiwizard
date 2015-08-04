from elastiwizard.transform import TransformQuestion
from elastiwizard.grammar import GrammarBuilder
import json

test_question_1 = """
    how many requests researched by user/yPyA5n7P since 2015-07-07
"""
test_question_2 = """
    count requests researched by researched_by each day
"""
test_question_3 = """
    sum the total_length of albums released since friday
"""
test_question_4 = """
    how many requests researched each day
"""
test_question_5 = """
    how many requests researched since 2015-07-07
"""
test_question_6 = """
    how many requests researched by researched_by
"""
test_question_7 = """
    how many requests researched by user/yPyA5n7P
"""
test_question_8 = """
    how many requests queued since 2015-07-07
"""
test_question_9 = """
    how many requests fulfilled since 2015-07-07
"""
test_question_10 = """
    how many requests fulfilled by researched_by
"""
test_question_11 = """
    how many requests fulfilled by user/yPyA5n7P each day since 2015-07-07
"""
test_question_12 = """
    how many albums submitted since 2015-07-07
"""
test_question_13 = """
    how many usages fulfilled by completed_license_methods since 2015-07-07
"""

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
        'usages': {
            'group_by': {
                'direct': 'completed_license_methods=1',
                'compulsory': 'completed_license_methods=2'
            },
            'where': {
                'researched': {
                    'filters': '!needs_license_research',
                    'field': 'researched_by'
                },
                'fulfilled':'license_fulfilled_at',
                'queued': 'license_queued_at'
            },
            'delta': {
                'date_field': 'license_fulfilled_at'
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
                },
                'queued': 'license_queued_at'
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
    print question

    assert question['metric'] == "how many"
    assert question['index'] == "requests"
    assert question['delta'] == "since 2015-07-07"
    assert question['where'] == "researched"
    assert question['group_by'] == "user/yPyA5n7P"

    query, question = TransformQuestion.transform(grammar_builder, test_question_2,
        terms_map=terms_map, return_parsed_question=True)

    json_query = json.dumps(query, indent=4, sort_keys=True)
    assert json_query
    print test_question_2
    print json_query

    assert question['metric'] == "count"
    assert question['index'] == "requests"
    assert question['delta'] == "each day"
    assert question['where'] == "researched"
    assert question['group_by'] == "researched_by"

    query, question = TransformQuestion.transform(grammar_builder, test_question_3,
        terms_map=terms_map, return_parsed_question=True)

    json_query = json.dumps(query, indent=4, sort_keys=True)
    assert json_query
    print test_question_3
    print json_query

    query, question = TransformQuestion.transform(grammar_builder, test_question_4,
        terms_map=terms_map, return_parsed_question=True)

    json_query = json.dumps(query, indent=4, sort_keys=True)
    assert json_query
    print test_question_4
    print json_query

    query, question = TransformQuestion.transform(grammar_builder, test_question_5,
        terms_map=terms_map, return_parsed_question=True)

    json_query = json.dumps(query, indent=4, sort_keys=True)
    assert json_query
    print test_question_5
    print json_query

    query, question = TransformQuestion.transform(grammar_builder, test_question_6,
        terms_map=terms_map, return_parsed_question=True)

    json_query = json.dumps(query, indent=4, sort_keys=True)
    assert json_query
    print test_question_6
    print json_query

    query = TransformQuestion.transform(grammar_builder, test_question_7,
        terms_map=terms_map)

    json_query = json.dumps(query, indent=4, sort_keys=True)
    assert json_query
    print test_question_7
    print json_query


    query = TransformQuestion.transform(grammar_builder, test_question_8,
        terms_map=terms_map)

    json_query = json.dumps(query, indent=4, sort_keys=True)
    assert json_query
    print test_question_8
    print json_query


    query = TransformQuestion.transform(grammar_builder, test_question_9,
        terms_map=terms_map)

    json_query = json.dumps(query, indent=4, sort_keys=True)
    assert json_query
    print test_question_9
    print json_query


    query = TransformQuestion.transform(grammar_builder, test_question_10,
        terms_map=terms_map)

    json_query = json.dumps(query, indent=4, sort_keys=True)
    assert json_query
    print test_question_10
    print json_query


    query = TransformQuestion.transform(grammar_builder, test_question_11,
        terms_map=terms_map)

    json_query = json.dumps(query, indent=4, sort_keys=True)
    assert json_query
    print test_question_11
    print json_query

    query = TransformQuestion.transform(grammar_builder, test_question_12,
        terms_map=terms_map)

    json_query = json.dumps(query, indent=4, sort_keys=True)
    assert json_query
    print test_question_12
    print json_query


    query, question = TransformQuestion.transform(grammar_builder, test_question_13,
        terms_map=terms_map, return_parsed_question=True)

    json_query = json.dumps(query, indent=4, sort_keys=True)
    assert json_query
    print test_question_13
    print json_query
    print question
    assert False
