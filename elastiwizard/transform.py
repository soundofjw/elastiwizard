from parser import ElastiwizardParser
from grammar import GrammarBuilder
from query import SearchAggregationBuilder

import types
import datetime

class TransformQuestion(object):

    def __init__(self, grammar_builder, terms_map=None,
        group_by_validator=None):
        assert isinstance(grammar_builder, GrammarBuilder), \
            "grammar must be an instance of GrammarBuilder not %s" \
            % (type(GrammarBuilder))
        self.grammar = grammar_builder.grammar

        self.terms_map = terms_map or {}
        self.group_by_validator = group_by_validator

    def parse(self, text):
        parsed = ElastiwizardParser(self.grammar, text)
        question = parsed.question
        return question

    def transform_delta(self, delta_string, dateformat="%Y-%m-%d",
        date_field=None):
        """takes a string in returns a dict that describes the
        date range

        eg. {
            'interval': '',
            'from': '',
            'to': ''
        }
        """

        def _get_substr_by_term(string, term):
            return string.replace(' ', '*').split('%s*'%(term), 1)[1:][0]\
                .split('*',1)[0]

        from_date = None

        if 'each' in delta_string:
            interval = _get_substr_by_term(delta_string, 'each')
            assert interval in ['day', 'week', 'month', 'year'], \
                "Invalid time interval"
        else:
            interval = None

        if 'from' in delta_string:
            date_string = _get_substr_by_term(delta_string, 'from')
            from_date = datetime.datetime.strptime(date_string, dateformat).date()

        if 'to' in delta_string:
            date_string = _get_substr_by_term(delta_string, 'to')
            to_date = datetime.datetime.strptime(date_string, dateformat).date()
        else:
            to_date = datetime.datetime.now().date()

        if 'since' in delta_string:
            date_string = _get_substr_by_term(delta_string, 'since')
            from_date = datetime.datetime.strptime(date_string, dateformat).date()

        if not date_field:
            date_field = self.terms_map.get('*default_date_field', "created_at")

        return  {
            'interval': interval,
            'from': from_date,
            'to': to_date,
            'date_field': date_field
        }

    def transform_where(self, where):
        """map the where text somehow
        have support for "not" or ! syntax as well
        """
        filter_terms = where.split("and")

        filters = {}
        for f in filter_terms:
            value = "1"
            f = f.strip()

            if f in self.terms_map.keys():
               f = self.terms_map.get(f)
               if f.startswith("!"):
                    value = "0"
                    f = f[1:]

            filters[f] = value # what about "not" ?

        return filters

    def transform_metric(self, metric_term):
        """map term to metric"""
        metric_map = {
          "how many": "count",
          "total": "sum",
          "best": "max",
          "worst": "min"
        }

        if metric_term in metric_map.keys():
            metric_term = metric_map.get(metric_term)
        return metric_term

    def transform_metric_field(self, metric_field):
        """map the metric field somehow"""
        if metric_field in self.terms_map.keys():
            metric_field = self.terms_map.get(metric_field)

        return metric_field

    def transform_group_by(self, group_by_string):
        """
        Have a way to determine if group_by value is field name
        or field value.

        If field value, return field name that contains that field value
        and assign field_value to filters dict
        """

        filter_dict = None
        if self.group_by_validator and \
            isinstance(self.group_by_validator, types.FunctionType):
            new_string = self.group_by_validator(group_by_string)

            if new_string:
                filter_dict = {
                    new_string: group_by_string
                }
                group_by_string = new_string

        return group_by_string, filter_dict

    @classmethod
    def transform(cls, grammar, text, terms_map={}, group_by_validator=None,
        just_parse=False):

        transformer = cls(grammar, terms_map, group_by_validator)
        question = transformer.parse(text)
        if just_parse:
            return question

        options = {}

        options['metric'] = transformer.transform_metric(question['metric'])
        options['field'] = transformer.transform_metric_field(question['field'])

        if question.get('delta'):
            options['delta'] = transformer.transform_delta(question['delta'])

        if question.get('where'):
            options['filters'] = transformer.transform_where(question['where'])

        """
        researched by user/SJFWEOJ
        ^ where     ^ group by
        """
        if question.get("group_by"):
            options['terms'], filter_dict = transformer.transform_group_by(
                question['group_by'])

            if filter_dict:
                options['filters'].update(filter_dict)

        q = SearchAggregationBuilder.build_agg_with_query_and_options(
            "", **options)

        return q