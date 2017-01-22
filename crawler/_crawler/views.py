from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import urllib2
from bs4 import BeautifulSoup
import json
from urlparse import urljoin
from datetime import datetime


def get_html_tag_data(soup, tag):
    data = []
    for i in soup.find_all(tag):
        data.append(i.text.strip('\r\n\t '))
    return data


def get_html_data(soup):
    title = soup.title.string;
    headline = {
        'h1': get_html_tag_data(soup, 'h1'),
        'h2': get_html_tag_data(soup, 'h2'),
        'h3': get_html_tag_data(soup, 'h3'),
        'h4': get_html_tag_data(soup, 'h4'),
        'h5': get_html_tag_data(soup, 'h5'),
        'h6': get_html_tag_data(soup, 'h6')
    }
    return {
        'title': title,
        'headline': headline
    }


def fetch_content_from_url(url):
    try:
        response = urllib2.urlopen(url)
        response = response.read()
        soup = BeautifulSoup(response, 'html.parser')
        error = False
    except Exception, e:
        soup = str(e)
        error = True
    return {
        'url': url,
        'soup': soup,
        'error': error
    }


@csrf_exempt
def index(request):
    if request.method == 'POST':
        url = json.loads(request.body)
        limit_value = url["limit"]
        url=url["url"]
        limit= True if limit_value!=-1 else False
        display_data = {}

        urls_crawled_status = {
            'crawled': [],
            'uncrawled': [url]
        }
        page = 0
        while page < len(urls_crawled_status['uncrawled']):
            if limit and page >= limit_value:
                break
            url = urls_crawled_status['uncrawled'][page]
            if url in urls_crawled_status['crawled']:
                page=page+1;
                continue
            urls_crawled_status['crawled'].append(url)
            data_fetched = fetch_content_from_url(url)
            if (data_fetched['error']):
                display_data[data_fetched['url']] = data_fetched['soup']
                page = page + 1
            else:
                soup = data_fetched['soup']
                url = data_fetched['url']
                data_required = get_html_data(soup)
                display_data[url] = data_required['title']
                for link in soup.find_all('a'):
                    href = link.get('href')
                    if (href):
                        href = href.strip()
                        href = urljoin(url, href)
                        if href not in urls_crawled_status['crawled'] and href not in urls_crawled_status['uncrawled']:
                            urls_crawled_status['uncrawled'].append(href)
                page = page + 1

        return HttpResponse(json.dumps(display_data))
