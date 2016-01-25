# import unicodecsv as csv
import wikipedia as wiki
import json

MAX_CATEGORY_DEPTH = 3

def is_algorithm_page(page):
    category_match = False
    for category in page.categories:
        if 'Algorithm' in category or 'algorithm' in category:
            category_match = True

    # summary_match = ('algorithm' in page.summary
    #     or 'Algorithm' in page.summary)
    #
    # return category_match and summary_match

    content_match = (page.content.find('algorithm') != -1
        or page.content.find('Algorithm') != -1)

    return category_match and content_match

def get_wiki_page(title, auto_suggest=True):
    try:
        # disable auto_suggest to get the correct page
        # (e.g. auto_suggest will turn 'B*' into 'Bacteria')
        return wiki.page(title, auto_suggest=False)
    except:
        if auto_suggest:
            try:
                # if there's no exact matching page,
                # try the auto_suggest before giving up
                return wiki.page(title)
            except:
                return None

def write_output_from_page(output, page):
    json.dump(
        {'title': page.title,
        'summary': page.summary,
        'categories': page.categories,
        'links': page.links},
        output)
    output.write('\n')

def parse_list_of_algorithms_page():
    output = open('wiki.csv', 'w+')
    # csv_writer = csv.writer(output)

    list_of_algorithms_page = wiki.page('list of algorithms')

    for link in list_of_algorithms_page.links:
        link_page = get_wiki_page(link)
        if link_page is None:
            continue
        if is_algorithm_page(link_page):
            write_output_from_page(output, link_page)

    output.close()

def is_category_title(title):
    return title.encode('utf8').startswith('Category:')

def parse_category_page(page, output, depth, visited):
    print 'looking at page:', page.title
    for member in page.categorymembers:
        print member, depth
        if member in visited:
            print 'visited'
            continue
        visited.add(member)
        if is_category_title(member):        # subcategory page
            if depth < MAX_CATEGORY_DEPTH:
                page = wiki.categorypage(member)
                if page is None:
                    print '-> subcategory not found'
                    continue
                print '-> subcategory'
                parse_category_page(page, output, depth + 1, visited)
        else:                                # member page
            page = get_wiki_page(member)
            if page is None:
                print '-> member page not found'
                continue
            if is_algorithm_page(page):
                print '-> algorithm page'
                write_output_from_page(output, page)
            else:
                print '-> member page of other stuff'

def parse_category(category):
    visited = set()
    try:
        input = open('wiki_algo_category.json')
        for line in input:
            visited.add(json.loads(line)['title'])
        input.close()
    except IOError:
        pass

    output = open('wiki_algo_category.json', 'a')
    # csv_writer = csv.writer(output)

    print 'start parsing...'
    parse_category_page(wiki.categorypage(category), output, 0, visited)
    output.close()

# parse_category('Category:Algorithms')
