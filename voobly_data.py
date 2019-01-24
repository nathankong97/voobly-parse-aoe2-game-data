import requests, pandas as pd
from bs4 import BeautifulSoup
import json
import re, pymongo, time

#rank is 0-19
#game_num is 0-9
#page is 0-20

civ_dict = {'1':'Britons','2':'Franks','3':'Goths','4':'Teutons','5':'Japanese','6':'Chinese','7':'Byzantines',
            '8':'Persians', '9':'Saracens','10':'Turks','11':'Vikings','12':'Mongols','13':'Celts','14':'Spanish',
            '15':'Aztecs','16':'Mayans','17':'Huns','18':'Koreans','19':'Italians',
            '20':'Indians','21':'Incas','22':'Magyars','23':'Slavs','24':'Portuguese','25':'Ethiopians',
            '26':'Malians','27':'Berbers','28':'Khmer','29':'Malay','30':'Burmese','31':'Vietnamese'}


def login(form, rank_num, rank, page, game_num):
    with requests.Session() as s:
        # Get the cookie
        s.get('https://www.voobly.com/login')
        # Post the login form data
        s.post('https://www.voobly.com/login/auth', data=form)

        # open ladder's page
        ladder_page = 'https://www.voobly.com/ladder/ranking/131/' + str(rank_num) + '#pagebrowser1'
        ladder = s.get(ladder_page)  # RM 1v1
        soup = BeautifulSoup(ladder.text,features="html.parser")

        # collect player profile
        profile_link = []
        lst = soup.find_all(name='a')
        key = 'https://voobly.com/profile/'
        for i in lst:
            if key in i.get('href'):
                profile_link.append(i.get('href'))
        profile_link = profile_link[1:]

        # open player's match profile
        player_id = ''.join(x for x in profile_link[rank] if x.isdigit())
        game_page = str(page)
        #https://www.voobly.com/profile/view/123303397/Matches/games/matches/user/123303397/0/0#pagebrowser1
        player = profile_link[rank] + '/Matches/games/matches/user/' + player_id + '/0/' + game_page + '#pagebrowser1'
        profile = s.get(player)

        # collect game record from a player
        game = []
        soup = BeautifulSoup(profile.text,features="html.parser")
        table = soup.find_all("table")[0].find_all('a')
        key = 'https://voobly.com/match/'
        for i in table:
            if key in i.get('href'):
                game.append(i.get('href'))

        # open the game record
        content = game[game_num]
        record = s.get(content)
        soup = BeautifulSoup(record.text,features="html.parser")

        return soup

def match(soup):
    # check the player numbers
    team_list = []
    for i in soup.find_all(name='span', attrs={'style': 'font-size:11px; color:#82909D'}):
        team_list.append(i.text[0])
    if team_list.count('N') != team_list.count('T'):
        return False
    table = soup.find_all(name='td',attrs={'width':'50%','valign': 'top'})[0].find_all('table')[0]
    table_data = [[cell.text for cell in row("td")]
                            for row in table("tr")]
    table_data = [x for x in table_data if x != ['']]

    match_dict = dict(table_data)
    match_dict['Win'] = []
    match_dict['Loss'] = []
    return match_dict

def player(match, soup):
    player = [['ID','Name','Civilzation','Team','Overall','Military','Economy','Technology','Society']]
    player_num = int(match['Players:'])
    table = soup.find_all(name='table',attrs={'width':'100%','border': '0'})[0]
    key = 'https://voobly.com/profile/'

    for i in table.find_all('a'): #this is printing out all id
        if key in i.get('href'):
            num = int(''.join(re.findall('[0-9]',i.get('href'))))
            #print(int(''.join(re.findall('[0-9]',i.get('href')))))
            player.append([num])

    counts = 1
    player_counts = 0
    for i in table.find_all('a'): #this is printing out all name
        if key in i.get('href'):
            player_counts += 1
            name = i.contents[0]
            player[counts].append(name)
            counts+=1
            #print(i.contents[0])

    counts = 1
    key = '/res/games/AOC/civs/'
    for i in soup.find_all('img'): #this is printing out all civ
        if key in i.get('src'):
            civ = str(''.join(x for x in i.get('src') if x.isdigit()))
            player[counts].append(civ_dict[civ])
            counts += 1


    counts = 1
    for i in range(player_num):
        if i >= (player_num/2):
            #print(2)
            player[counts].append(2)
            counts += 1
        else:
            #print(1)
            player[counts].append(1)
            counts += 1

    counts = 1
    for i in range(player_num):
        player[counts].append([])
        player[counts].append([])
        player[counts].append([])
        player[counts].append([])
        player[counts].append([])
        counts += 1
    #player
    df = pd.DataFrame(player[1:],columns=player[0])
    player_dict = df.to_dict("index")
    player_dict = list(player_dict.values())
    return player_dict

def score(soup):
    score = [['Military Score','Economy Score','Technology Score','Society Score','Total']]
    lst = []
    count = 0
    table = soup.find_all(name='table',attrs={'width':'100%','border': '0'})[0]
    for i in table.find_all('center')[5:]:
        if i.find('div'):
            #print(i.find('div').contents[0].replace(',',''))
            num = i.find('div').contents[0].replace(',','')
            lst.append(num)
            count += 1
        else:
            #print(i.contents[0].replace(',',''))
            num = i.contents[0].replace(',','')
            lst.append(num)
            count += 1

        if count == 5:
            score.append(lst)
            lst = []
            count = 0
    df = pd.DataFrame(score[1:],columns = score[0])
    score_dict = df.to_dict("index")
    score_dict = list(score_dict.values())
    return score_dict

def military(soup):
    military = [['Unit Killed','Unit Lost','Building Razed','Building Lost','Units Converted']]
    table = soup.find_all(name='table',attrs={'width':'100%','border': '0'})[1]
    lst = []
    count = 0
    for i in table.find_all('center')[5:]:
        if i.find('div'):
            num = i.find('div').contents[0].replace(',','')
            lst.append(num)
            count += 1
            #print(i.find('div').contents[0].replace(',',''))
        else:
            num = i.contents[0].replace(',','')
            lst.append(num)
            count += 1
            #print(i.contents[0].replace(',',''))
        if count == 5:
            military.append(lst)
            lst = []
            count = 0
    df = pd.DataFrame(military[1:],columns = military[0])
    mil_dict = df.to_dict("index")
    mil_dict = list(mil_dict.values())
    return mil_dict

def economy(soup):
    economy = [['Food','Wood','Stone','Gold','Trade','Received','Sent']]
    table = soup.find_all(name='table',attrs={'width':'100%','border': '0'})[2]
    lst = []
    count = 0
    for i in table.find_all('center')[7:]:
        if i.find('div'):
            num = i.find('div').contents[0].replace(',','')
            lst.append(num)
            count += 1
            #print(i.find('div').contents[0].replace(',',''))
        else:
            num = i.contents[0].replace(',','')
            lst.append(num)
            count += 1
            #print(i.contents[0].replace(',',''))
        if count == 7:
            economy.append(lst)
            lst = []
            count = 0
    df = pd.DataFrame(economy[1:],columns = economy[0])
    eco_dict = df.to_dict("index")
    eco_dict = list(eco_dict.values())
    return eco_dict

def tech(soup):
    technology = [['Fedual Time','Castle Time','Imperial Time','Map Explored','Research Count','Research Percentage']]
    table = soup.find_all(name='table',attrs={'width':'100%','border': '0'})[3]
    lst = []
    count = 0
    for i in table.find_all('center')[6:]:
        if i.find('div'):
            num = i.find('div').contents[0].replace(',','')
            lst.append(num)
            count += 1
            #print(i.find('div').contents[0].replace(',',''))
        else:
            num = i.contents[0].replace(',','')
            lst.append(num)
            count += 1
            #print(i.contents[0].replace(',',''))
        if count == 6:
            technology.append(lst)
            lst = []
            count = 0
    df = pd.DataFrame(technology[1:],columns = technology[0])
    tech_dict = df.to_dict("index")
    tech_dict = list(tech_dict.values())
    return tech_dict

def society(soup):
    society = [['Total Wonders','Total Castles','Relic Capture','Relic Gold','Viliager High']]
    table = soup.find_all(name='table',attrs={'width':'100%','border': '0'})[4]
    lst = []
    count = 0
    for i in table.find_all('center')[5:]:
        if i.find('div'):
            num = i.find('div').contents[0].replace(',','')
            lst.append(num)
            count += 1
            #print(i.find('div').contents[0].replace(',',''))
        else:
            num = i.contents[0].replace(',','')
            lst.append(num)
            count += 1
            #print(i.contents[0].replace(',',''))
        if count == 5:
            society.append(lst)
            lst = []
            count = 0
    df = pd.DataFrame(society[1:],columns = society[0])
    soc_dict = df.to_dict("index")
    soc_dict = list(soc_dict.values())
    return soc_dict

def combine(match,player,score,military,economy,tech,society):
    for i in range(len(player)):
        player[i]['Overall'] = score[i]
        player[i]['Military'] = military[i]
        player[i]['Economy'] = economy[i]
        player[i]['Technology'] = tech[i]
        player[i]['Society'] = society[i]
    win = [i for i in player if i['Team'] == 1]
    loss = [i for i in player if i['Team'] == 2]
    match['Win'] = win
    match['Loss'] = loss
    return match

def write(file):
	#write the collected data into the local MongoDB
    try:
        x = mycol.insert_one(file)
    except:
        print('something wrong')
    else:
        print('success')

#Team game rating should be above 1950
#1v1 game rating should be above 2150
def rule(file):
    f = open("record.txt", "r").read()
    if file['Match Details'] in f:
        print('already have this game')
        return False
    if int(file['Players:']) % 2 == 1:
        print('this game is not balance')
        return False
    if int(file['Match Rating:']) == 1600:
        return True
    if int(file['Players:']) > 2:
        if int(file['Match Rating:']) <= 1950:
            print('team rank is too low')
            return False
    if int(file['Players:']) == 2:
        if int(file['Match Rating:']) <= 2150:
            print('1v1 rank is too low')
            return False
    return True

def write_record(file):
    f = open("record.txt", "a")
    try:
        f.write(file['Match Details'] + '\n')
    except:
        print('something wrong when writing record')
    else:
        print('successfully write the record')

if __name__ == "__main__":
	#Login to the local MongoDB
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient["voobly"]
    mycol = mydb["games"]
    #This is for the voobly account and login to voobly
    form = {'username': USERNAME, 'password': PASSWORD}
    rank_num = 1  # suggesting 1-5
    rank = 20 #1-20
    page = 1 #suggesting 1-30
    game_num = 10 #1-10
    count = 1
    for i in range(rank_num):
        for n in range(rank):
            for x in range(page):
                for y in range(game_num):
                    print('rank page ', i, ' rank ', n, ' page number ', x, ' game number ', y)
                    try:
                        soup = login(form, i, n, x, y)
                        game = match(soup)
                    except:
                        print('error')
                        pass
                    else:
                        if not match(soup):
                            print('game is not even\n')
                            pass
                        else:
                            if not rule(game):
                                print('This match does not meet the requirement')
                                print(game['Match Details'], game['Match Rating:'],'\n')
                            else:
                                try:
                                    play = player(game, soup)
                                    sc = score(soup)
                                    mil = military(soup)
                                    eco = economy(soup)
                                    tec = tech(soup)
                                    soc = society(soup)
                                    file = combine(game,play,sc,mil,eco,tec,soc)
                                    write(file)
                                    write_record(file)
                                    print('success!', count,'\n')
                                    count += 1
                                except:
                                    print('error')
                                    pass


