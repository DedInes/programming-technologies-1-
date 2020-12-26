import requests
import re
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
from sqlalchemy import create_engine, Table, Column, String, Float, MetaData
from sqlalchemy.sql import select


class WeatherProvider:
    def __init__(self, key):
        self.key = key

    def get_data(self, location, start_date, end_date):
        url = 'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/weatherdata/history'
        params = {
            'aggregateHours': 24,
            'startDateTime': f'{start_date}T00:0:00',
            'endDateTime': f'{end_date}T23:59:59',
            'unitGroup': 'metric',
            'location': location,
            'key': self.key,
            'contentType': 'json',
        }
        data = requests.get(url, params).json()
        return [
            {
                'date': row['datetimeStr'][:10],
                'mint': row['mint'],
                'maxt': row['maxt'],
                'location': 'Volgograd,Russia',
                'humidity': row['humidity'],
            }
            for row in data['locations'][location]['values']
        ]


engine = create_engine('sqlite:///weather.sqlite3')
metadata = MetaData()
weather = Table(
    'weather',
    metadata,
    Column('date', String),
    Column('mint', Float),
    Column('maxt', Float),
    Column('location', String),
    Column('humidity', Float),
)
metadata.create_all(engine)

c = engine.connect()

provider = WeatherProvider('EWLYGPYQPMM6CASTQXW4YH9KU')
c.execute(weather.insert(), provider.get_data('Volgograd,Russia', '2020-12-01', '2020-12-31'))

for row in c.execute('SELECT * FROM weather'):
    print(row)

#построение графика температуры
fig, ax = plt.subplots()
ax.set(title='График изменения минимальной температуры за декабрь')

ax.grid(which='major',
        color = 'k')

mint_y =[]
mint_x = []

#делаем выборку минимальной температуры из БД
for row in c.execute('SELECT date FROM weather'):
    mint_x.append(row)

#распаковываем список
mint_x = [i for i, in mint_x]

#делаем выборку дней из БД
for row in c.execute('SELECT mint FROM weather'):
    mint_y.append(row)

#распаковываем список
mint_y = [j for j, in mint_y]

print(mint_y)
print(mint_x)

#устанавливаем границы графика
plt.xlim(0, len(mint_y))
plt.ylim(min(mint_y), max(mint_y))

#строим график
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
plt.gca().xaxis.set_major_locator(mdates.DayLocator())
plt.plot(mint_x, mint_y, color='r', linewidth=3)
plt.gcf().autofmt_xdate()
plt.show()