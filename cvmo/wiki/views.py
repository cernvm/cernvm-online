from django.http import Http404
import re
from cvmo.wiki.models import Page, PageCategory
from django.shortcuts import render_to_response
from django.template import RequestContext
from wikimarkup import parse

def show_wiki(request, url):
    # Check URL
    url_parts = __get_url_parts(url)
    
    # Find the page
    page = __find_page(url_parts)
    if page is None:
        # Try find a category
        category = __find_category(url_parts)
        if category is None:
            raise Http404
        else:
            return show_category(request, url, category)
    else:
        return show_page(request, url, page)

def show_category(request, url, category):
    # Get the category pages
    pages = Page.objects.filter(categories=category).order_by("ordering")
    
    # Set pages their urls
    for page in pages:
        page.url = __get_page_url(page, category)
        
    # Set category it's url
    category.url = __get_category_url(category)
    
    # Get category path
    rev_category_path = []
    cat = category
    while cat != None:
        rev_category_path.append(cat)
        cat = cat.parent        
        
    # Reverse the category path and add urls
    category_path = []
    for i in range(0, len(rev_category_path)):
        cat = rev_category_path[len(rev_category_path) - i - 1]
        cat.url = __get_category_url(cat)
        category_path.append(cat)
    
    # Render the page
    context = {
        "category": category,
        "parent": category.parent,
        "pages": pages,
        "category_path": category_path
    }
    return render_to_response('pages/wiki_category.html', context, RequestContext(request))

def show_page(request, url, page):        
    # Render page content
    if page.contents_type == Page.CT_HTML:
        page_contents = page.contents
    elif page.contents_type == Page.CT_WIKI:
        page_contents = parse(page.contents, False)
    else:
        page_contents = page.contents
        
    # Get category path
    rev_category_path = []    
    cat = page.selected_category
    while cat != None:
        rev_category_path.append(cat)
        cat = cat.parent        
        
    # Reverse the category path and add urls
    category_path = []
    for i in range(0, len(rev_category_path)):
        cat = rev_category_path[len(rev_category_path) - i - 1]
        cat.url = __get_category_url(cat)
        category_path.append(cat)
        
    # Set page URL
    page.url = __get_page_url(page, page.selected_category)

    # Render the page
    context = {
        "page": page,
        "contents": page_contents,
        "categories": page.categories,
        "category_path": category_path
    }
    return render_to_response('pages/wiki_page.html', context, RequestContext(request))

####################################################################################################
# HELPERS
####################################################################################################

def __get_url_parts(url):
    # Split the URL by "/"
    temp_url_parts = url.split("/")
    url_parts = []
    # Remove the empty ones
    for part in temp_url_parts:
        if re.match("^\s*$", part) is None:
            url_parts.append(part)
    return url_parts

def __get_category(alias, parent):
    # Find category
    try:
        category = PageCategory.objects.get(alias__iexact=alias, parent=parent)
        return category
    except Exception:
        return None
    
def __find_category(path):
    # Find category
    category = None
    for i in range(0, len(path)):
        category = __get_category(path[i], category)
        if category == None:
            return None
    return category

def __find_page(path):
    # Find category
    category = __find_category(path[ 0 : len(path) - 1 ])
    if category is None:
        return None
        
    # Find page in category
    try:
        page = Page.objects.get(alias__iexact=path[len(path) - 1], categories=category)
        page.selected_category = category
        return page 
    except Exception:
        return None
    
def __get_category_url(cat):
    # Get the category path
    rev_cat_path_arr = []
    while cat is not None:
        rev_cat_path_arr.append(cat)
        cat = cat.parent
        
    # Get the URL
    category_path_str = ""
    for i in range(0, len(rev_cat_path_arr)):
        category_path_str += "/" + rev_cat_path_arr[len(rev_cat_path_arr) - i - 1].alias
        
    return category_path_str + ".html"

def __get_page_url(page, cat=None):
    # If category not defined, select the first of the page categories
    if cat == None:
        cat = page.categories.all()[0]
        
    # Is selected category a category of the page?
    if cat not in page.categories.all():
        return None
    
    # Get category url
    category_url = __get_category_url(cat)
    
    # Remove the .html part
    matches = re.match(r"^(.*)\.html$", category_url)
    if not matches:
        # Wtf?
        return None
    category_path = matches.group(1)
    
    return category_path + "/" + page.alias + ".html"

