# elastiwizard
English to elasticsearch query/aggregations


# Overview

Elastiwizard is a simple parser that gives you the ability to translate questions written in english to Elasticsearch aggregations customized to your data

Go from this:

``` how many posts published since 07/01/2015```

To:

```json

{
    "aggs": {
        "post_stats": {
            "date_range": {
                "field": "published_at",
                "format": "MM-d-yyyy",
                "ranges": [
                    {
                        "from": "now-9w/w" // today being 09/01/2015
                    }
                ]
            }
        }
    },
    "query": {
        "match_all": {}
    },
    "size": 20,
    "sort": [
        {
            "_score": {
                "ignore_unmapped": "true",
                "order": "desc"
            }
        }
    ]
}
```
