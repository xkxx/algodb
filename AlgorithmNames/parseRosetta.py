import mwclient as mw
import unicodecsv as csv
import json
import mwparserfromhell as parser
import re
from impl_languages_deduplication import get_standardized_lang
import redis

site = mw.Site('rosettacode.org', path='/mw/')
search_pattern = re.compile(r"([\s\S]*?)<lang (\w+)>([\s\S]+?)<\/lang>")
trim_pattern = re.compile(r"{{.+?}}")
rd = redis.StrictRedis(host='localhost', port=6379, db=0)

class Task:
    """
        self.solutions: a list of implementations.
                        each entry in list is a map,
                            with keys:'language', 'content'
                        each entry in content has attribute 'type', 'content'
        self.task_name: a string
        self.task_summary: a list of sentences
        self.nodeslist: a list of mediawiki nodes from the page's text
    """
    def _parse_language_from_header(self, title):
        # e.g. '{{header|8th}}'
        matchHeader = re.compile(r"\{\{header\|(.+?)\}\}")
        result = matchHeader.match(title)
        return result and result.group(1).strip()

    # find the first commentary block and the first code block,
    # if match found, return (commentary, code, entirematch),
    # otherwise return (commentary, None, None).
    def parse_text(self, text):
        match = search_pattern.search(text)
        if match is None:
            return (text, None, None)
        # print '--------------------------------------------------------------'
        # print 'text:', text
        # print '------'
        # print 'g1:', match.group(1)
        # print '------'
        # print 'g3:', match.group(3)
        # print '------'
        # print 'g0:', match.group(0)
        # print '------'
        return (match.group(1), match.group(3), match.group(0))

    def trim(self, commentary):
        commentary = re.sub(trim_pattern, '', commentary).strip()
        # print '------'
        # print 'commentary', commentary
        return commentary

    def _parse_solutions(self, solution_nodes):
        self.solutions = list()
        current_solution = None
        for node in solution_nodes:
            # print '================================node: ', \
                # node.encode('utf8'), \
                # 'task:', self.task_name
            # print type(node)
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
                current_solution['language'] = get_standardized_lang(lang, rd)
                current_solution['content'] = list()
            if type(node) is parser.nodes.tag.Tag and node.tag == 'lang':
                current_solution['content'].append({'type': 'code',
                    'content': node.contents.encode('utf8')})
            if type(node) is parser.nodes.text.Text:
                text = str(node.value.encode('utf8'))
                (commentary, code, entirematch) = self.parse_text(text)
                while code is not None:
                    current_solution['content'].append({'type': 'code',
                        'content': code})
                    commentary = self.trim(commentary)
                    if len(commentary) > 0:
                        current_solution['content'].append({'type':
                            'commentary', 'content': commentary})
                    text = text[len(entirematch):]
                    (commentary, code, entirematch) = self.parse_text(text)

        # print '================================'

    def _parse_summary(self):
        self.task_summary = list()
        for i in range(len(self.nodeslist)):
            curr = self.nodeslist[i]
            if type(curr) is parser.nodes.heading.Heading:
                # print curr
                if self._parse_language_from_header(curr.title.encode('utf8')):
                    # print curr
                    self._parse_solutions(self.nodeslist[i:])
                    break
                else:
                    self.task_summary.append(curr.title.encode('utf8'))
            if type(curr) is parser.nodes.text.Text:
                self.task_summary.append(curr.value.encode('utf8'))

    def __init__(self, page):
        self.nodeslist = parser.parse(page.text()).nodes
        self.task_name = page.page_title
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
        csv_writer.writerow([page.page_title])

def parse_rosetta_task_pages():
    output = open('rosetta.json', 'w+')

    category = site.Pages['Category:Programming Tasks']
    i = 0
    for page in category:
        print '#', i
        print page.page_title
        output.write(Task(page).toJson())
        output.write('\n')
        i += 1

if __name__ == '__main__':
    parse_rosetta_task_pages()
    # page = site.Pages['fractran']
    # print Task(page).toJson()
