import datetime
from collections import defaultdict

class SearchQueryBuilder(object):

    """
    Builds a query based on the given properties
    """

    def __init__(self, q, match_fields=[]):
        self.q = q
        self.query = {
            'query': {}
        }
        self.match_fields = match_fields
        self.has_filters = False

    BOOST_FIELDS = {
        'name': 3,
        'title': 3,
        'alias': 1.5,
        'original_artist': 1.25,
    }

    @classmethod
    def _gen_boost(cls, tokenized_fields):
        for tn in tokenized_fields:
            if cls.BOOST_FIELDS.has_key(tn):
                yield tn+"^%d" % cls.BOOST_FIELDS[tn]
            else:
                yield tn

    def apply_query_string(self, tokenized_fields=[]):
        query_hash = {}

        # Boost fields
        tokenized_fields = list(self._gen_boost(tokenized_fields))

        if not self.q:
            query_hash = {
                'match_all': {}
            }
        elif self.q and self.match_fields:
            match_q = {field: self.q for field in self.match_fields}
            query_hash = {
                'match': match_q
            }

        else:
            if tokenized_fields:
                tokenized_fields.append('_all')

                query_hash = {
                    'multi_match': {
                        'query': self.q,
                        'type': 'most_fields',
                        'fields': tokenized_fields
                    }
                }

            else:
                query_hash = {
                    'match': {
                        '_all': self.q
                    }
                }

        if self.has_filters:
            self.query['query']['filtered']['query'] = query_hash
        else:
            self.query['query'] = query_hash

    def apply_agg(self, agg):
        self.query.update(agg)

    def build_filter_query(self, filters={}, required_fields=[], range={},
                           must_not=[], missing=[]):

        filter_dict = {
            'query': {

            },
            'filter': {

            }
        }

        filter_queries = []
        for field in required_fields:
            filter_queries.append(
                {'exists': {'field': field}}
            )

        for field_name, field_value in filters.iteritems():
            if field_value in [True, False]:
                field_value = int(field_value)

            filter_queries.append(
                {'term': {
                    field_name: field_value
                }}
            )

        # TODO refactor later to be in filters
        must_not_filters = []
        for field_name, field_value in (must_not or []):
            must_not_filters.append(
                {'term': {
                    field_name: field_value
                }}
            )

        if range:
            filter_queries.append({'range': range})

        if filter_queries or must_not_filters or missing:
            filter_dict['filter'] = defaultdict(lambda: dict())

            for m in missing:
                filter_queries.append({'missing':  {'field': m}})

            if filter_queries:
                filter_dict['filter']['bool'].update({
                    'must': filter_queries
                })

            if must_not_filters:
                filter_dict['filter']['bool'].update({
                    'must_not': must_not_filters
                })

            self.has_filters = True

            self.query['query']['filtered'] = dict(filter_dict)

    def build_sort_filter(self, sort):
        order_string = sort.strip()
        sort_filter = {}
        if order_string.startswith("-"):
            order_string = order_string[1:]
            sort_filter = {
                order_string: {
                    'order': 'desc',
                    'ignore_unmapped': 'true'
                }
            }
        else:
            sort_filter = {
                order_string: {
                    'order': 'asc',
                    'ignore_unmapped': 'true'
                }
            }

        return sort_filter

    def build_with_options(self, limit=20, sort=None, filters={},
                           aggregations={}, must_exist=[], range={}, must_not=[], missing=[],
                           *args, **kwargs):
        """
        Based on kwargs generates a number of queries based on selected_fields
        """

        if filters or must_exist or range or missing:
            self.build_filter_query(filters=filters,
                                    required_fields=must_exist, range=range,
                                    must_not=must_not, missing=missing)

        if limit:
            self.query['size'] = limit

        if not sort:
            sort = "-_score"

        sort_filter = self.build_sort_filter(sort)
        self.query['sort'] = [sort_filter]

        if aggregations:
            self.apply_agg(aggregations)

        tokenized_fields = kwargs.pop('tokenized_fields', [])
        self.apply_query_string(tokenized_fields=tokenized_fields)

        # base.print_json(self.query)
        return self.query

    @classmethod
    def build_with_query_and_options(cls, q, *args, **kwargs):
        return cls(q).build_with_options(*args, **kwargs)

    @classmethod
    def build_query_with_entity_and_rules_async(cls, search_dict, rules={}):
        # TODO build query with entity and corresponding options
        """
        You get an entity and want to build a query DSL
        steps:
        1) find search indexed fields
        2) build bool query with `must` and `should`
        3) apply rules for boosting, minimum_should_match, which
            fields should be fuzzy

        {
            "bool" : {
                "must" : {
                    "term" : { "user" : "kimchy" }
                },
                "should" : [
                    {
                        "term" : { "tag" : "wow" }
                    },
                    {
                        "term" : { "tag" : "elasticsearch" }
                    }
                ],
                "minimum_should_match" : 1,
                "boost" : 1.0
            }
        }
        """
        bool_query = {
            'bool': {
                'minimum_should_match': rules.pop('minimum_should_match', 1)
            }
        }

        fuzziness = rules.pop('fuzziness', 0.5)
        # print base.to_json(search_dict, public=True)

        for k, v in rules.iteritems():
            if k == 'must_match':
                condition = 'must'
            elif k == 'should_match':
                condition = 'should'
            else:
                continue

            bool_query['bool'][condition] = []

            for field_dict in v:
                query_dict_list = []
                field_name = field_dict['field']

                if not field_name in search_dict:
                    continue

                if field_dict.get('fuzzy', False):
                    for value in search_dict[field_name]:
                        query_dict = {
                            'flt_field': {
                                field_name: {
                                    'like_text': value,
                                    'fuzziness': fuzziness,
                                    'boost': field_dict.get('boost', 1),
                                }
                            }
                        }

                        query_dict_list.append(query_dict)
                else:
                    for value in search_dict[field_name]:
                        query_dict = {
                            'term': {
                                field_name: {
                                    'value': value,
                                    'boost': field_dict.get('boost', 0)
                                }
                            }
                        }
                        query_dict_list.append(query_dict)

                bool_query['bool'][condition].extend(query_dict_list)

        for condition in ['must', 'should']:
            if condition in bool_query and \
                    not bool_query[condition]:
                bool_query['bool'].pop(condition)

        return {
            'query': bool_query,
        }


class SearchAggregationBuilder(SearchQueryBuilder):
    """Builds aggregations based off of needed information

       Will intelligently construct nested aggregations
    """

    def build_metric(self, metric, field, use_value_count=False):
        metric_dict = {}

        if metric in ['sum', 'avg', 'stats', 'min', 'max']:
            metric_dict = {
                metric: {
                    'field': field
                }
            }
        elif use_value_count:
            metric_dict = {
                "value_count": {
                    'field': field
                }
            }

        return metric_dict


    def build_terms(self, terms, **options):
        terms_dict =  {
            'terms':{'field': terms}
        }

        return terms_dict

    def build_date_range(self, date_field, from_dt, to_dt):
        """
        This depends on elasticsearch date format and
        will need some improvements to accomodate
        first find the time between
        """

        now = datetime.datetime.now().date()
        delta_days = (to_dt - from_dt).days

        skip_to = True if to_dt == now else False


        if delta_days > 90:
            days_in_month = 30

            date_format = "MM-yyyy"
            from_days = (now - from_dt).days or days_in_month
            from_string = "now-%sM/M" % (from_days / days_in_month)
            to_days = (now - to_dt).days or days_in_month
            to_string = "now-%sM/M" % (to_days or days_in_month)

        elif delta_days > 30:
            days_in_week = 7

            date_format = "MM-d-yyyy"
            from_days = (now - from_dt).days or days_in_week
            from_string = "now-%sw/w" % (from_days / days_in_week)
            to_days = (now - to_dt).days or days_in_week
            to_string = "now-%sw/w" % (to_days or days_in_week)

        else:
            date_format = "MM-d-yyyy"
            from_days = (now - from_dt).days
            from_string = "now-%sd" % (from_days)
            to_days = (now - to_dt).days
            to_string = "now-%sd" % (to_days)

        from_dict = {"from": from_string}
        to_dict = {"to": to_string}

        ranges = [from_dict]
        if not skip_to:
            ranges.append(to_dict)


        return {
            "date_range": {
                "field": date_field,
                "format": date_format,
                "ranges": ranges
            }
        }


    def build_date_histogram(self, date_field, interval, from_dt, to_dt):
        """

        date_histogram" : {
            "field" : "license_fulfilled_at",
            "interval" : "day",
            "min_doc_count": 0,
            "extended_bounds": {
                "min": "2015-07-07",
                "max": max_date
            }
        }
        """
        return {
            "date_histogram": {
                "field": date_field,
                "interval": interval,
                "min_doc_count": 0,
                "extended_bounds": {
                    "min": from_dt.strftime("%Y-%m-%d"),
                    "max": to_dt.strftime("%Y-%m-%d"),
                }
            }
        }



    def build_range(self):
        pass

    def build_histogram(self):
        pass

    def build_from_delta_dict(self, delta_dict, date_field="created_at"):
        """
        reads delta_dict and determine appropriate
        aggregation
        """

        delta_min = delta_dict['from']
        delta_max = delta_dict['to']

        interval = delta_dict['interval']

        date_field = delta_dict.get('date_field', date_field)

        delta_agg = {}

        delta_type = "range"

        if interval:
            # histogram
            delta_type = "date_histogram"
            # TODO determine if date or regular histogram
            delta_agg = self.build_date_histogram(date_field, interval, delta_min,
                delta_max)
        else:
            # range
            delta_type = "date_range"
            # TODO determin if date or regular range
            delta_agg = self.build_date_range(date_field, delta_min, delta_max)

        return delta_agg, delta_type

    def build_filter_dict(self, key, value):
        filter_dict = {
            'filter': {
                'term': {
                    key: value
                }
            }
        }
        return filter_dict


    def update_agg(self, agg_dict, new_agg, new_agg_name, do_nest,
        is_tuple_list=False):
        """
        Updates aggregation with newly created aggregation
        Will nest if necessary
        """
        if do_nest:
            if is_tuple_list:
                agg_dict['aggs'] = {}
                for agg_name, agg_d in new_agg:
                    agg_dict['aggs'].update({
                      agg_name: agg_d
                    })
            else:
                agg_dict['aggs'] = {
                  new_agg_name: new_agg
                }
            agg_dict = agg_dict['aggs'][new_agg_name]
        else:
            agg_dict.update(new_agg)

        return agg_dict


    def build_agg_with_options(self, metric, field, delta={}, filters={},
        terms=None, name="request_stats"):

        parent_agg_dict = {
            name: {}
        }

        agg_dict = parent_agg_dict[name]
        do_nest = False


        for filter_key, filter_value in filters.iteritems():
            filter_dict = self.build_filter_dict(filter_key, filter_value)
            agg_name = "filter_%s" % (filter_key)
            agg_dict = self.update_agg(agg_dict, filter_dict, agg_name, do_nest)
            if not do_nest:
                do_nest = True

        if terms:
            term_dict = self.build_terms(terms)
            agg_name = "group_by_%s" % (terms)
            agg_dict = self.update_agg(agg_dict, term_dict, agg_name, do_nest)
            if not do_nest:
                do_nest = True

        if delta.get('from') and delta.get('date_field'):
            delta_agg_dict, delta_type = self.build_from_delta_dict(delta)
            agg_name = "da_%s" % (delta_type)
            self.update_agg(agg_dict, delta_agg_dict, agg_name, do_nest)

        metric_dict_list = []
        field_list = field.split(',')
        for i, field in enumerate(field_list):
            metric_dict = self.build_metric(metric, field.strip())
            if metric_dict:
                agg_name = "%s_%s" % (metric, field)
                metric_dict_list.append((agg_name, metric_dict))

        if metric_dict_list:
            agg_dict = self.update_agg(agg_dict, metric_dict_list,
                metric_dict_list[0][0], do_nest, is_tuple_list=True)
            if not do_nest:
                do_nest = True

        return {'aggs': parent_agg_dict}


    @classmethod
    def build_agg_with_query_and_options(cls, query, metric, field,
        delta={}, filters={}, terms=None, name="request_stats"):
        """
        Takes arguments and builds aggregations like this one:

        "aggs" : {
            "researchers": {
                "terms": {"field": "researched_by",
                          "order": {"_count": "desc"}},
                "aggs": {
                    "licensed_requested_at" : {
                        "date_histogram" : {
                            "field" : "license_fulfilled_at",
                            "interval" : "day",
                            "min_doc_count": 0,
                            "extended_bounds": {
                                "min": "2015-07-07",
                                "max": max_date
                            }
                        }
                    }
                }
            }
        }

        field: requests
        metric: "count",
        delta: "each day",
        each day
        since 2012-07-07
        each day from 2015-07-07 to 2015-07-09
        """

        query_builder = cls(query)
        agg_filter = query_builder.build_agg_with_options(metric, field, delta,
            terms=terms, filters=filters, name=name)

        q = query_builder.build_with_options(aggregations=agg_filter)

        return q