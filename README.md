# elastiwizard
English to elasticsearch query/aggregations


# Overview

Elastiwizard is a simple parser that gives you the ability to translate questions written in english to Elasticsearch aggregations customized to your data

Go from this:

``` how many posts published since July 1st 2015```

To:

```json

{
    "query": {
        "match_all": {}
    },
    "aggs": {

    }
}
```
