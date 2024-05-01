#!/usr/bin/env python3
import requests
import pandas as pd
from bs4 import BeautifulSoup
import json

DIVISIONS = ['FTCCMP1FRAN', 'FTCCMP1JEMI', 'FTCCMP1EDIS', 'FTCCMP1OCHO']
NUM_404S_TO_WAIT_FOR = 3
CACHE_FILE = 'cache.json'

try:
  with open(CACHE_FILE, 'r') as f:
    cache = json.load(f)
except FileNotFoundError:
  cache = {}

def add_to_cache(division, match_number, data):
  global cache
  if not division in cache:
    cache[division] = {}
  cache[division][str(match_number)] = json.dumps(data)
  with open(CACHE_FILE, 'w') as f:
    json.dump(cache, f, indent=2)

def get_from_cache(division, match_number):
  data = cache.get(division, {}).get(str(match_number), None)
  if data is None:
    return None
  else:
    return json.loads(data)


for division in DIVISIONS:
  print(division + ' DIVISION')
  print('  RANKINGS')
  url = "https://ftc-events.firstinspires.org/2023/" + division + "/rankings"  # Replace with the actual URL
  response = requests.get(url)
  print('    rankings', response.status_code)
  soup = BeautifulSoup(response.content, 'html.parser')

  table_data = []
  for row in soup.find_all('tr'):
    cols = row.find_all('td')

    #special case for first row with column names
    if len(cols) == 0:
      for th in row.find_all('th'):
        divs = th.find_all('div')
        if len(divs) == 0:
          cols.append(th)
        else:
          cols.append(divs[0])
    cols = [col.text.strip() for col in cols]
    cols.extend(cols[6].split('-')) #split W-L-T into separate cols and add to the end
    del cols[6]

    table_data.append(cols)

  #old special case for first row with column names
  # table_data[0] = ['Rank','Team','Average RP','Average TBP1','Average TBP2','High Score','W-L-T','Matches Played']
  # table_data[0].extend(table_data[0][6].split('-')) #split W-L-T into separate cols
  # del table_data[0][6]

  df = pd.DataFrame(table_data[1:], columns=table_data[0])
  df.to_csv(division + '_rankings.csv', index=False)


  print('  MATCHES')

  #old caching method
  # start_at = None
  # try:
  #   with open(division + '_matches.csv', 'r') as f:
  #     matches = f.readlines()
  #     for i, line in enumerate(matches):
  #       if not line.startswith(f'{i},') and i > 0:
  #         start_at = i
  #         break
  #     if start_at is None:
  #       start_at = len(matches)-1
  # except FileNotFoundError as e:
  #   start_at = 1
  # print(division + ' start at match ' + str(start_at))

  table = []
  match_number = 0
  num_404s = 0
  th = get_from_cache(division, None) #get names of fields from the cache
  while True:
    match_number += 1
    td = get_from_cache(division, match_number)
    if td is not None:
      print('   ', match_number, 'cached')
      num_404s = 0
    else:
      url = "https://ftc-events.firstinspires.org/2023/" + division + "/qualifications/" + str(match_number)
      response = requests.get(url)
      print('   ', match_number, response.status_code)
      if response.status_code == 200:
        num_404s = 0
      else:
        num_404s += 1
        if num_404s >= NUM_404S_TO_WAIT_FOR:
          break
        continue

      content = response.content
      soup = BeautifulSoup(content, 'html.parser')

      th = []
      td = []

      th.append('match_number'); td.append(match_number)
      th.append('red_score'); td.append(soup.find('div', class_='cs-scoreboard-totalpoints-red').text)
      th.append('blue_score'); td.append(soup.find('div', class_='cs-scoreboard-totalpoints-blue').text)

      scoreboard = soup.find('div', class_='cs-scoreboard')
      data = [item.strip() for item in scoreboard.text.split('\n') if item.strip() != '']
      # print(data)
    #   0        1      2     3             4     5                 6     7           8     9               10                 11      12    13                 14    15              
    #['8417', '24474', '40', 'AUTONOMOUS', '25', 'DRIVER-CONTROL', '20', 'END GAME', '30', 'BLUE PENALTY', 'Score Breakdown', 'Auto', '40', 'Backdrop Points', '10', 'Backstage Points',

    #  16   17                   18    19               20    21                   22    23                 24    25                  26   27               28   29                  30   31
    # '0', 'Navigation Points', '10', 'Randomization', '20', 'Driver Controlled', '25', 'Backdrop Points', '18', 'Backstage Points', '7', 'Mosaic Points', '0', 'Set Bonus Points', '0', 'End Game',

    #  32    33          34    35              36   37         38    39      40       41            42    43                44    45         46     47
    # '20', 'Location', '20', 'Drone Points', '0', 'Penalty', '30', '4250', '19066', 'AUTONOMOUS', '83', 'DRIVER-CONTROL', '84', 'END GAME', '70', 'RED PENALTY',

    #  48   49      50    51                 52    53                  54   55                   56   57               58    59                   60    61                 62    63     
    # '0', 'Auto', '83', 'Backdrop Points', '15', 'Backstage Points', '3', 'Navigation Points', '5', 'Randomization', '60', 'Driver Controlled', '84', 'Backdrop Points', '51', 'Backstage Points',

    #  64   65               66    67                  68    69          70    71          72    73              74    75         76
    # '3', 'Mosaic Points', '20', 'Set Bonus Points', '10', 'End Game', '70', 'Location', '40', 'Drone Points', '30', 'Penalty', '0']
      th.append('red_team_1'); td.append(data[0])
      th.append('red_team_2'); td.append(data[1])

      th.append('red_Auto'); td.append(data[12])
      th.append('red_Auto_Backdrop_Points'); td.append(data[14])
      th.append('red_Auto_Backstage_Points'); td.append(data[16])
      th.append('red_Navigation_Points'); td.append(data[18])
      th.append('red_Randomization'); td.append(data[20])
      th.append('red_Driver_Controlled'); td.append(data[22])
      th.append('red_Driver_Backdrop_Points'); td.append(data[24])
      th.append('red_Driver_Backstage_Points'); td.append(data[26])
      th.append('red_Mosaic_Points'); td.append(data[28])
      th.append('red_Set_Bonus_Points'); td.append(data[30])
      th.append('red_End_Game'); td.append(data[32])
      th.append('red_Location'); td.append(data[34])
      th.append('red_Drone_Points'); td.append(data[36])
      th.append('red_Penalty_from_other_team'); td.append(data[38])

      th.append('blue_team_1'); td.append(data[39])
      th.append('blue_team_2'); td.append(data[40])

      th.append('blue_Auto'); td.append(data[50])
      th.append('blue_Auto_Backdrop_Points'); td.append(data[52])
      th.append('blue_Auto_Backstage_Points'); td.append(data[54])
      th.append('blue_Navigation_Points'); td.append(data[56])
      th.append('blue_Randomization'); td.append(data[58])
      th.append('blue_Driver_Controlled'); td.append(data[60])
      th.append('blue_Driver_Backdrop_Points'); td.append(data[62])
      th.append('blue_Driver_Backstage_Points'); td.append(data[64])
      th.append('blue_Mosaic_Points'); td.append(data[66])
      th.append('blue_Set_Bonus_Points'); td.append(data[68])
      th.append('blue_End_Game'); td.append(data[70])
      th.append('blue_Location'); td.append(data[72])
      th.append('blue_Drone_Points'); td.append(data[74])
      th.append('blue_Penalty_from_other_team'); td.append(data[76])
      add_to_cache(division, None, th)
      add_to_cache(division, match_number, td)
    table.append(td)


  df = pd.DataFrame(table, columns=th)
  df.to_csv(division + '_matches.csv', index=False)
