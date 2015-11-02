import unicodecsv as csv
import wikipedia as wiki

output = open('wiki.csv', 'w+')
csv_writer = csv.writer(output)

def is_algorithm(page):
    category_match = False
    for category in page.categories:
        if 'Algorithm' in category or 'algorithm' in category:
            category_match = True

    summary_match = ('algorithm' in page.summary
        or 'Algorithm' in page.summary)

    return category_match and summary_match

list_of_algorithms_page = wiki.page('list of algorithms')
links = list_of_algorithms_page.links
print len(links)

for link in links:
    try:
        link_page = wiki.page(link, auto_suggest=False)
    except wiki.exceptions.PageError:
        try:
            link_page = wiki.page(link)
        except wiki.exceptions.PageError:
            continue
    print link
    if is_algorithm(link_page):
        csv_writer.writerow([link, link_page.summary,
            link_page.categories, link_page.links])

output.close()
