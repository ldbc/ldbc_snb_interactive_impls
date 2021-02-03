from neo4j import GraphDatabase, time
from datetime import datetime
from neo4j.time import DateTime
import time
import pytz
import csv
import re

#@unit_of_work(timeout=300)
def query_fun(tx, query_spec, query_parameters):
    result = tx.run(query_spec, query_parameters)
    return result.value()

def run_query(session, query_id, query_spec, query_parameters):
    print(f'Q{query_id}: {query_parameters}')
    start = time.time()
    result = session.read_transaction(query_fun, query_spec, query_parameters)
    print(f'{len(result)} results')
    end = time.time()
    duration = end - start
    #print("Q{}: {:.4f} seconds, {} tuples".format(query_id, duration, result[0]))
    return (duration, result)

def convert_to_datetime(timestamp):
    dt = datetime.strptime(timestamp, '%Y-%m-%d')
    return DateTime(dt.year, dt.month, dt.day, 0, 0, 0, pytz.timezone('GMT'))

driver = GraphDatabase.driver("bolt://localhost:7687")

with driver.session() as session:
    for query_id in range(1, 21):
        query_file = open(f'queries/bi-{query_id}.cypher', 'r')
        query_spec = query_file.read()

        parameters_csv = csv.DictReader(open(f'parameters/bi-{query_id}.txt'), delimiter='|')
        
        for query_parameters in parameters_csv:
            query_parameters = {k: int(v) if re.match(r'^[0-9]+$', v) else v for k, v in query_parameters.items()}
            query_parameters = {
              k.replace('[]', ''):
              v.split(';') if re.findall('\[\]$', k) else v for k, v in query_parameters.items()
            }
            #re.findall('\[\]$', 'A')
            query_parameters = {k: convert_to_datetime(v) if re.findall('date', k.lower()) else v for k, v in query_parameters.items()}
            print(query_parameters)
            run_query(session, query_id, query_spec, query_parameters)

driver.close()
