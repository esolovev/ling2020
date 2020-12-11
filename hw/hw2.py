import requests
from bs4 import BeautifulSoup
import bs4
import re
import datetime


headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'
    }


def get_links() -> list:
    resp = requests.get('https://www.gismeteo.ru/', headers=headers)
    html_content = resp.text
    soup = BeautifulSoup(html_content, 'html.parser')
    cities = soup.find_all(lambda tag: tag.has_attr('data-url'))
    links = []
    for city in cities:
        link = city.attrs['data-url']
        if link not in links:
            links.append(link)
    links = ['https://www.gismeteo.ru' + l + '10-days/' for l in links]

    return links


def load_forecast(link: str) -> list:
    resp = requests.get(link, headers=headers)
    html_content = resp.text
    soup = BeautifulSoup(html_content, 'html.parser')

    date_list = [(datetime.datetime.today() + datetime.timedelta(days=x)).strftime('%Y-%m-%d') for x in range(10)]

    city = soup.find('div', {'class': 'subnav_search_city js_citytitle'}).text

    summary_list = []
    for i in soup.find_all(lambda tag: tag.has_attr('data-text')):
        summary_list.append(i.attrs['data-text'])

    max_temp_list = []
    min_temp_list = []
    for n, i in enumerate(soup.find_all('span', {'class': 'unit unit_temperature_c'})[:20]):
        if n % 2 == 0:
            max_temp_list.append(int(i.text.replace('−', '-')))
        else:
            min_temp_list.append(int(i.text.replace('−', '-')))

    max_wind_speed_list = []
    for i in soup.find_all('span', {'class': 'unit unit_wind_m_s'})[:10]:
        max_wind_speed_list.append(int(i.text.strip()))

    precipitation_list = []
    for i in soup.find_all('div', {'class': 'w_prec__value'})[:10]:
        precipitation_list.append(float(i.text.strip().replace(',', '.')))

    max_pressure_list = []
    min_pressure_list = []
    pressure_container = str(soup.find('div', {'class': 'chart chart__pressure'}))
    soup_pressure = BeautifulSoup(pressure_container, 'html.parser')
    prev_class = None
    prev_value = None
    for i in soup_pressure.find_all(lambda tag: tag.has_attr('class') and ('maxt' in tag.attrs['class'] or 'mint' in tag.attrs['class'])):
        soup_pressure_value = BeautifulSoup(str(i), 'html.parser')
        curr_class = i.attrs['class'][0]
        curr_value = int(soup_pressure_value.find('span', {'class': 'unit unit_pressure_mm_hg_atm'}).text)
        if curr_class == 'maxt':
            if prev_class == 'maxt':
                max_pressure_list.append(prev_value)
                min_pressure_list.append(prev_value)
        else:
            max_pressure_list.append(prev_value)
            min_pressure_list.append(curr_value)
        prev_class = curr_class
        prev_value = curr_value

    forecast = []
    for i in range(10):
        day_forecast = {
            'date': date_list[i],
            'city': city,
            'summary': summary_list[i],
            'max_temp': max_temp_list[i],
            'min_temp': min_temp_list[i],
            'max_wind_speed': max_wind_speed_list[i],
            'precipitation': precipitation_list[i],
            'max_pressure': max_pressure_list[i],
            'min_pressure': min_pressure_list[i]
        }
        forecast.append(day_forecast)

    return forecast


if __name__ == '__main__':
    links = get_links()
    for i in links:
        print(load_forecast(i))
