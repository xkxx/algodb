import mwclient as mw
import unicodecsv as csv
import json
import mwparserfromhell as parser
import re

site = mw.Site('rosettacode.org', path='/mw/')
matchHeader = re.compile(r"\{\{header\|(.+)\}\}")

class Task:
    def _parse_language_from_header(self, title):
        # e.g. '{{header|8th}}'
        result = matchHeader.match(title)
        return result and result.group(1)

    def _parse_solutions(self, solution_nodes):
        self.solutions = list()
        current_solution = None
        for node in solution_nodes:
            print '================================node: ', \
                node.encode('utf8'), \
                'task:', self.task_name
            print type(node)
            if type(node) is parser.nodes.heading.Heading:
                lang = \
                    self._parse_language_from_header(node.title.encode('utf8'))
                if lang is None:
                    current_solution['content'].append({'type': 'description',
                        'value': node.title.encode('utf8')})
                    continue
                if current_solution is not None:
                    self.solutions.append(current_solution)
                current_solution = dict()
                current_solution['language'] = lang
                current_solution['content'] = list()
            if type(node) is parser.nodes.text.Text:
                current_solution['content'].append({'type': 'description',
                    'value': node.value.encode('utf8')})
            if type(node) is parser.nodes.tag.Tag and node.tag == 'lang':
                current_solution['content'].append({'type': 'code',
                    'value': node.contents.encode('utf8')})
        print '================================'

    def _parse_summary(self):
        self.task_summary = list()
        for i in range(len(self.nodeslist)):
            curr = self.nodeslist[i]
            if type(curr) is parser.nodes.heading.Heading:
                print curr
                if self._parse_language_from_header(curr.title.encode('utf8')):
                    print curr
                    self._parse_solutions(self.nodeslist[i:])
                    break
                else:
                    self.task_summary.append(curr.title.encode('utf8'))
            if type(curr) is parser.nodes.text.Text:
                self.task_summary.append(curr.value.encode('utf8'))

    def __init__(self, page, task_name):
        self.nodeslist = parser.parse(page.text()).nodes
        self.task_name = task_name
        self._parse_summary()

    def toJson(self):
        return json.dumps(
            {'task': self.task_name,
            'task_summary': self.task_summary,
            'solutions': self.solutions}
        )

def parse_rosetta_task_names():
    output = open('rosetta_task_names.csv', 'w+')
    csv_writer = csv.writer(output)

    category = site.Pages['Category:Programming Tasks']
    for page in category:
        csv_writer.writerow([page.name])

def parse_rosetta_task_pages():
    output = open('rosetta_task_pages.json', 'w+')

    category = site.Pages['Category:Programming Tasks']
    for page in category:
        output.write(Task(page, page.page_title).toJson())
        output.write('\n')

parse_rosetta_task_pages()
