from elastiwizard.transform import TransformQuestion
from elastiwizard.grammar import GrammarBuilder
import json

test_question_1 = """count requests since 2015-07-07 researched by user/yPyA5n7P"""
test_question_2 = """count requests each day researched by researched_by"""

def test_parse():
    grammar_builder = GrammarBuilder()
    question = TransformQuestion.transform(grammar_builder, test_question_1,
        just_parse=True)

    print question
    print test_question_1

    assert question['metric'] == "count"
    assert question['index'] == "requests"
    assert question['delta'] == "since 2015-07-07"
    assert question['where'] == "researched"
    assert question['group_by'] == "user/yPyA5n7P"


def test_transform():
    grammar_builder = GrammarBuilder()

    terms_map = {
        'researched': '!needs_license_research',
        'requests': 'researched_by',
        '*default_date_field': 'license_fulfilled_at'
        "r'user\/[a-zA-Z0-9]+'"
    }

    # sum of albums sold since friday
    """
        {
            'metric': 'sum',
            'field': 'albums',
            'delta': 'since friday',
            'where': 'sold'
        }
    """

    terms_map = {
       'requests': {
            'group_by': {
                'user/*': 'researched_by',
            },
            'where': {
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

    query = TransformQuestion.transform(grammar_builder, test_question_1,
        terms_map=terms_map)

    json_query = json.dumps(query, indent=4, sort_keys=True)

    assert json_query

    query = TransformQuestion.transform(grammar_builder, test_question_2,
        terms_map=terms_map)

    json_query = json.dumps(query, indent=4, sort_keys=True)

    print json_query
