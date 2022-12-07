
import pandas as pd, numpy as np
from pandas import DataFrame
from bs4 import BeautifulSoup, Comment, NavigableString
import requests as requests
from urllib.request import Request, urlopen
from urllib.parse import quote
import html5lib

def get_urls(years,circuits):
    
    races = []

    for year in years[::-1]:
        for circuit in circuits:
            req = Request("https://www.procyclingstats.com/races.php?year="+year+"&circuit="+circuit+"&ApplyFilter=Filter", headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/7046A194A'})
            html = urlopen(req).read()
            s = BeautifulSoup(html, "lxml")
            tbl = s.table.findAll("tr")
            for i in range(1,len(tbl)):
                row = tbl[i].findAll("td")
                race = row[2].a["href"][5:].split("/")[0]
                if race not in races:
                    races.append((year,quote(race)))
                    
    return races
                    
def get_results(races):

    df1 = []

    for race2 in races:

            year = race2[0]
            race = race2[1]
            print(year,race)

            req = Request("https://www.procyclingstats.com/race/"+race+"/"+year, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/7046A194A'})
            html = urlopen(req).read()

            s = BeautifulSoup(html, "lxml")
            stages = len(s.select('option[value^="race/'+race+'/'+year+'/stage"]')) or 1
            prologue = len(s.select('option[value^="race/'+race+'/'+year+'/prologue"]'))
            # stages = 21

            for stage in range(1,stages-2):
                if stages == 1:
                    req = requests.get("https://www.procyclingstats.com/race/"+race+"/"+year+"/", headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/7046A194A'})
                elif prologue > 0:
                    req = requests.get("https://www.procyclingstats.com/race/"+race+"/"+year+"/"+"prologue"+"/", headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/7046A194A'})
                else:
                    req = requests.get("https://www.procyclingstats.com/race/"+race+"/"+year+"/"+"stage-"+str(stage), headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/7046A194A'})

                try:
                    dfs = pd.read_html(req.text)
                    df = dfs[0]
                except:
                    column_names = ["Rnk", "GC", "Timelag","BIB","H2H","Rider","Age","Team","UCI","Pnt","Time"]
                    df = pd.DataFrame(columns = column_names)

                df['Race'] = race
                df['Year'] = year
                df['Stage'] = stage

                df1.append(df)

    df1 = pd.concat(df1)
    
    return df1

def get_info(races):

    race_info_df = pd.DataFrame([])

    for race2 in races:

            year = race2[0]
            race = race2[1]
            print(year,race)

            req = Request("https://www.procyclingstats.com/race/"+race+"/"+year, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/7046A194A'})
            html = urlopen(req).read()

            s = BeautifulSoup(html, "lxml")
            stages = len(s.select('option[value^="race/'+race+'/'+year+'/stage"]')) or 1
            # stages = 21

            for stage in range(1,stages-2):
                if stages == 1:
                    req = Request("https://www.procyclingstats.com/race/"+race+"/"+year+"/", headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/7046A194A'})
                else:
                    req = Request("https://www.procyclingstats.com/race/"+race+"/"+year+"/"+"stage-"+str(stage), headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/7046A194A'})
                html = urlopen(req).read()

                s = BeautifulSoup(html, "lxml")

                # race info

                info = []

                for ultag in s.find_all('ul', {'class': 'infolist'}):
                     for litag in ultag.find_all('li'):
                            try:
                                info.append(litag.text.split(':')[1].strip())
                            except:
                                info.append("")

                npa = np.asarray(info)

                headers = ['Date', 'Start Time','Avg_speed_winner', 'Race_category','Distance','Points_scale','Parcours_type','ProfileScore','Vert_meters','Departure','Arrival','Race_ranking','Start_List_Quality','Won_how','Dummy']

                try:
                    if npa.size == 0:
                        race_info = DataFrame(np.array([['','','','','','','','','','','','','','','']]), columns=headers)
                    else:
                        race_info = DataFrame(npa.reshape(-1, len(npa)), columns=headers)
                except:
                    race_info = DataFrame(np.array([['','','','','','','','','','','','','','','']]), columns=headers)

                race_info['Race'] = race
                race_info['Year'] = year
                race_info['Stage'] = stage

                if stages == 1:
                    race_info['len'] = 'one_day'
                else:
                    race_info['len'] = 'stage_race'

                race_info_df = race_info_df.append(race_info)
                
    return(race_info_df)
            