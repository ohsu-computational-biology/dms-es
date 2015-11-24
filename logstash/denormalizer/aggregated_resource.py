# create an `aggregated resource`, denormalized with fields from individual
# and sample

import os
from elasticsearch import Elasticsearch

# TODO throw error if not set
es = Elasticsearch([os.environ['ELASTIC_SEARCH']])

# delete the index
es.indices.delete(index='aggregated-resource', ignore=[400, 404])
print("dropped aggregated-resource index")

# for each search, get all the data
MAX_RECORDS=99999999

count = 0
# get all individuals
individuals = es.search(
    doc_type='individual',
    body={"size":MAX_RECORDS, "query": {"match_all": {} }}
    )
# for each individual, get their samples
for individual in individuals['hits']['hits']:
    print("I:"+individual['_id'])
    samples = es.search(
        doc_type='sample',
        body={"size":MAX_RECORDS, "query": {"query_string": {"query":"individual_id:\"" + individual['_id'] +"\"" }}}
        )
    # for each sample, get its resources
    for sample in samples['hits']['hits']:
        print("  S:" + sample['_id'])
        resources = es.search(
            doc_type='resource',
            body={"size":MAX_RECORDS, "query": {"query_string": {"query":"sample_id:\"" + sample['_id'] +"\""}}}
            )
        # for each resource, create an aggregated resource
        for resource in resources['hits']['hits']:
            aggregated_resource = individual['_source'].copy()
            aggregated_resource.update(sample['_source'])
            aggregated_resource.update(resource['_source'])
            es.create(
                index="aggregated-resource",
                doc_type="aggregated-resource",
                body=aggregated_resource,
                id=resource['_id']
            )
            print("Created R:" + resource['_id'])
            count += 1
print("Created {} resources".format(count))
