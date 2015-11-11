import mwclient as mw
import unicodecsv as csv

site = mw.Site('rosettacode.org', path='/mw/')

def parse_rosetta_task_names():
    output = open('rosetta_task_names.csv', 'w+')
    csv_writer = csv.writer(output)

    category = site.Pages['Category:Programming Tasks']
    for page in category:
        csv_writer.writerow([page.name])

def parse_rosetta_task_pages():
    output = open('rosetta_task_pages.csv', 'w+')
    csv_writer = csv.writer(output)

    category = site.Pages['Category:Programming Tasks']
    for page in category:
        csv_writer.writerow([page.name, page.text()])
