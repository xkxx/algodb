import unicodecsv as csv
import wikipedia as wiki


def is_algorithm(page):
    category_match = False
    for category in page.categories:
        if 'Algorithm' in category or 'algorithm' in category:
            category_match = True

    summary_match = ('algorithm' in page.summary
        or 'Algorithm' in page.summary)

    return category_match and summary_match

def get_wiki_page(title):
    try:
        # disable auto_suggest to get the correct page
        # (e.g. auto_suggest will turn 'B*' into 'Bacteria')
        return wiki.page(title, auto_suggest=False)
    except:
        try:
            # if there's no exact matching page,
            # try the auto_suggest before giving up
            return wiki.page(title)
        except:
            return None

def write_output_from_page(csv_writer, page):
    csv_writer.writerow([page.title, page.summary,
        page.categories, page.links])

def parse_list_of_algorithms_page():
    output = open('wiki.csv', 'w+')
    csv_writer = csv.writer(output)

    list_of_algorithms_page = wiki.page('list of algorithms')

    for link in list_of_algorithms_page.links:
        link_page = get_wiki_page(link)
        if link_page is None:
            continue
        if is_algorithm(link_page):
            write_output_from_page(csv_writer, link_page)

    output.close()

def parse_category_recursively(category):
    output = open('wiki_algo_category.csv', 'w+')
    csv_writer = csv.writer(output)

    algo_cat = wiki.categorypage(category)
    for member in algo_cat.categorymembers:
        print member
        if member.encode('utf8').startswith('Category:'):  # subcategory page
            parse_category_recursively(member)
        else:                                             # member page
            page = get_wiki_page(member)
            if page is None:
                continue
            if is_algorithm(page):
                write_output_from_page(csv_writer, page)

parse_category_recursively('Category:Algorithms')
