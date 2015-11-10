import json
import unicodecsv as csv

dump = open('algorithms.json')
algorithms = json.loads(dump.read())
print len(algorithms)

def write_output():
    output = open('algorithmia.csv', 'w+')
    csv_writer = csv.writer(output)

    for algorithm in algorithms:
        name = algorithm['algolabel']
        summary_html = algorithm.get('summary', '')
        card_line = algorithm.get('card_line', '')
        language = algorithm.get('language', '')
        call_count = algorithm.get('call_count', '')
        csv_writer.writerow([name, summary_html, card_line, language,
            call_count])

    output.close()
