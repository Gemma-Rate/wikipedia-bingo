import pywikibot as pw
from pywikibot import pagegenerators as pg

site = pw.Site("en", "wikipedia")
# Make site object to get the data from.
repo = site.data_repository()