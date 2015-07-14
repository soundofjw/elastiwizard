from elastiwizard.transform import TransformQuestion
from elastiwizard.grammar import GrammarBuilder
import json

test_question_1 = """count requests since 2015-07-07 researched by user/yPyA5n7P"""

def test_parse():
    grammar_builder = GrammarBuilder()
    question = TransformQuestion.transform(grammar_builder, test_question_1,
        just_parse=True)

    assert question['metric'] == "count"
    assert question['field'] == "requests"
    assert question['delta'] == "since 2015-07-07"
    assert question['where'] == "researched"
    assert question['group_by'] == "user/FDwlkfw"


def test_transform():
    grammar_builder = GrammarBuilder()

    terms_map = {
        'researched': '!needs_license_research',
        'requests': 'researcehd_by',
        '*default_date_field': 'license_fulfilled_at'
    }

    def group_by_validator(group_by_string):
        if "user" in group_by_string:
            return "researched_by"
        return group_by_string

    query = TransformQuestion.transform(grammar_builder, test_question_1,
        terms_map=terms_map, group_by_validator=group_by_validator)

    print json.dumps(query, indent=4)

    assert False