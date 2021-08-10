import urllib3
import json
from datetime import datetime


def delivery(pindex, weight=4000):
    url_base = 'https://delivery.pochta.ru/v2/calculate/delivery?json&object=27030&from=125476'
    params = f'&to={pindex}&weight={weight}&pack=40&date={datetime.now().strftime("%Y%m%d")}'
    http = urllib3.PoolManager()
    rjs = json.loads(http.urlopen('GET', url_base + params).data)
    try:
        return f'~{rjs["delivery"]["max"] + 2} дней,до {datetime.strptime(rjs["delivery"]["deadline"][0:8], "%Y%m%d").strftime("%d.%m.%Y")}'
    except KeyError:
        return rjs['errors'][0]['msg']
    
    
def url_short(url):
    url_long = 'https://clck.ru/--?url=' + url
    http = urllib3.PoolManager()
    url_sh = http.urlopen('GET', url_long).data
    return str(url_sh)[2:-1]