# tabulaRDF
Create RDF graphs from tabular data.
Use a yaml configuration file to create RDF graph (or Neo if [rdflib-neo4j](https://neo4j.com/labs/rdflib-neo4j/) is used).

## How to execute:
1.- Clone repository.

2.- Run poetry install.

3.- Execute: poetry run python tabulardf/core/graphdf.py --table data/batch8_targeted_proteomics_final.csv  --config data/proteomics.yml --output-file xxx.ttl
