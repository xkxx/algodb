import mwclient as mw
import mwparserfromhell as parser

site = mw.Site('rosettacode.org', path='/mw/')

for page in site.Pages['Category:Programming Tasks']:
    print page.page_title
