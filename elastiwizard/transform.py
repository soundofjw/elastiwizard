from parser import ElastiwizardParser
from grammar import GrammarBuilder
from query import SearchAggregationBuilder

import types
import datetime
from dateutil.relativedelta import relativedelta

WEEKDAYS = {
    'monday': 0,
    'tuesday': 1,
    'wednesday': 2,
    'thursday': 3,
    'friday': 4,
    'saturday': 5,
    'sunday': 6,
}


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

        def find_date(date_string):
            day = datetime.datetime.now().date()
            if day.weekday() == WEEKDAYS[date_string]:
                return day
            else:
                return day - datetime.timedelta(
                    days=(day.weekday() - WEEKDAYS[date_string] - 1) % 7 + 1)

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
        else:
            # default to 6 months
            if interval == 'year':
                from_date = datetime.datetime.now().date() - relativedelta(years=+3)
            elif interval == 'month':
                from_date = datetime.datetime.now().date() - relativedelta(months=+6)
            elif interval == 'week':
                from_date = datetime.datetime.now().date() - relativedelta(months=+3)
            elif interval == 'day':
                from_date = datetime.datetime.now().date() - relativedelta(weeks=+4)
            else:
                from_date = datetime.datetime.now().date() - relativedelta(weeks=+4)


        if 'to' in delta_string:
            date_string = _get_substr_by_term(delta_string, 'to')
            to_date = datetime.datetime.strptime(date_string, dateformat).date()
        else:
            to_date = datetime.datetime.now().date()

        if 'since' in delta_string:
            date_string = _get_substr_by_term(delta_string, 'since')
            if date_string in WEEKDAYS:
                from_date = find_date(date_string)
            else:
                from_date = datetime.datetime.strptime(
                    date_string, dateformat).date()

        if not date_field:
            try:
                date_field = self.terms_map['delta'].get('date_field',
                    "created_at")
            except KeyError:
                date_field = 'created_at'

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
        where_term_map = self.terms_map.get('where', {})

        filter_map = {}
        for field in filter_terms:
            value = "1"
            field = field.strip()

            if field in where_term_map.keys():
                field = where_term_map.get(field, {})
                if isinstance(field, dict) and field.get('filters'):
                    filters = field['filters']
                    if isinstance(filters, basestring):
                        f = filters
                        if f.startswith("!"):
                            value = "0"
                            f = f[1:]
                    elif isinstance(filters, list):
                        # TODO too lazy to do it now, sorry
                        continue
                    else:
                        continue

                    filter_map[f] = value
        return filter_map

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

        field_map = self.terms_map.get('field', {})

        if metric_field and metric_field in field_map.keys():
            metric_field = field_map.get(metric_field)
        elif not metric_field:
            metric_field = field_map.get('default', 'title')

        return metric_field

    def transform_group_by(self, group_by_string):
        """
        Have a way to determine if group_by value is field name
        or field value.

        If field value, return field name that contains that field value
        and assign field_value to filters dict
        """

        filter_dict = None
        if self.terms_map.get('group_by'):
            group_by_map = self.terms_map['group_by']
            for k in group_by_map:
                if k.endswith('*') and group_by_string.startswith(k[:-1]):
                    filter_dict = {
                        group_by_map[k]: group_by_string
                    }
                    group_by_string = group_by_map[k]
                    break
                elif group_by_string == k:
                    filter_dict = {
                        group_by_map[k]: group_by_string
                    }
                    group_by_string = group_by_map[k]
                    break

        return group_by_string, filter_dict

    @classmethod
    def transform(cls, grammar, text, terms_map={}, group_by_validator=None,
        just_parse=False, return_parsed_question=False):

        text = text.strip()

        transformer = cls(grammar, terms_map, group_by_validator)
        question = transformer.parse(text)
        if just_parse:
            return question

        # update terms map to index
        transformer.terms_map = terms_map[question['index']]

        options = {}

        options['metric'] = transformer.transform_metric(question['metric'])
        options['field'] = transformer.transform_metric_field(
            question.get('field'))

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

        if return_parsed_question:
            return q, question
        else:
            return q
