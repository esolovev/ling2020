import requests
from bs4 import BeautifulSoup
import datetime
import pandas as pd


def get_weekend_recommendation():

    def get_links() -> list:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'
        }

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
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'
        }

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
        if 'Без осадков' in html_content:
            precipitation_list = [0] * 10
        else:
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
        if curr_class == 'maxt':
            max_pressure_list.append(curr_value)
            min_pressure_list.append(curr_value)

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

    def load_all_forecasts(links: list) -> list:
        all_forecasts = []
        for link in links:
            all_forecasts.extend(load_forecast(link))

        return all_forecasts

    def find_best_city(all_forecasts: pd.DataFrame) -> list:
        d = datetime.date.today()
        while d.weekday() != 5:
            d += datetime.timedelta(1)
        next_saturday = d.strftime('%Y-%m-%d')
        next_sunday = (d + datetime.timedelta(1)).strftime('%Y-%m-%d')

        mean_max_temp_next_weekend = all_forecasts[(all_forecasts['date'] == next_saturday) | (all_forecasts['date'] == next_sunday)].groupby('city')['max_temp'].mean()
        mean_min_temp_next_weekend = all_forecasts[(all_forecasts['date'] == next_saturday) | (all_forecasts['date'] == next_sunday)].groupby('city')['min_temp'].mean()
        mean_temp_next_weekend = pd.concat([mean_max_temp_next_weekend, mean_min_temp_next_weekend], axis=1)
        mean_temp_next_weekend['mean_temp'] = mean_temp_next_weekend.loc[:, 'max_temp':'min_temp'].mean(axis=1)
        best_cities = list(mean_temp_next_weekend[mean_temp_next_weekend['mean_temp'] == mean_temp_next_weekend['mean_temp'].max()].index)

        return best_cities

    def find_cheapest_ticket(cities: list) -> list:
        d = datetime.date.today()
        while d.weekday() != 5:
            d += datetime.timedelta(1)
        next_saturday = d.strftime('%Y-%m-%d')

        cheapest_tickets = []
        for city in cities:
            if city == 'Москва':
                cheapest_tickets.append({'error_text': 'Можно остаться в Москве'})
                continue

            route_params = {
                'q': 'Москва' + ' ' + city
            }
            route = requests.get('https://www.travelpayouts.com/widgets_suggest_params', params=route_params).json()
            origin = route['origin']['iata']
            destination = route['destination']['iata']

            ticket_params = {
                'origin': origin,
                'destination': destination,
                'one_way': True
            }
            resp = requests.get('http://min-prices.aviasales.ru/calendar_preload', params=ticket_params).json()
            cheapest_ticket = next((t['value'] for t in resp['best_prices'] if t['depart_date'] == next_saturday), None)
            if cheapest_ticket:
                cheapest_tickets.append({'price': cheapest_ticket})
            else:
                cheapest_tickets.append({'error_text': 'Билетов нет'})

        return cheapest_tickets

    links = get_links()
    all_forecasts = load_all_forecasts(links)

    all_forecasts = pd.DataFrame(all_forecasts)
    all_forecasts['date'] = pd.to_datetime(all_forecasts['date'], format='%Y-%m-%d')
    all_forecasts['max_temp_rolling'] = all_forecasts.groupby('city')['max_temp'].transform(lambda x: x.rolling(3).mean())
    all_forecasts['day_of_week'] = all_forecasts['date'].dt.dayofweek

    best_cities = find_best_city(all_forecasts)

    cheapest_tickets = find_cheapest_ticket(best_cities)

    print('Где москвичу провести следующие выходные, чтобы было потеплее?')
    print()
    if len(cheapest_tickets) == 1 and 'price' not in cheapest_tickets[0]:
        print('Можно остаться в Москве')
    else:
        for (ticket, city) in zip(cheapest_tickets, best_cities):
            if 'price' in ticket:
                print(f'Город {city}. Цена билета туда в рублях будет {ticket["price"]}')


def main():
    get_weekend_recommendation()


if __name__ == '__main__':
    main()
