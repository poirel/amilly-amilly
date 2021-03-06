#!/usr/bin/env python

import argparse
import sys

import urllib2
from bs4 import BeautifulSoup

from stat_parsers.player_stats import PlayerStats
from stat_parsers.ballpark_stats import BallparkStats
from stat_parsers.team_stats import TeamStats
from stat_parsers.league_stats import LeagueStats
from stat_equations import StatEquations


CAPACITY = 35000
TEAM_COMP = {'P': 1,
             'C': 1,
             '1B': 1,
             '2B': 1,
             'SS': 1,
             '3B': 1,
             'OF': 3}


def parseRotoGrinders(player_stats, team_stats):
    team_map = {'Arizona Diamondbacks': 'ARI',
                 'Atlanta Braves': 'ATL',
                 'Baltimore Orioles': 'BAL',
                 'Boston Red Sox': 'BOS',
                 'Chicago Cubs': 'CHC',
                 'Chicago White Sox': 'CWS',
                 'Cincinnati Reds': 'CIN',
                 'Cleveland Indians': 'CLE',
                 'Colorado Rockies': 'COL',
                 'Detroit Tigers': 'DET',
                 'Houston Astros': 'HOU',
                 'Kansas City Royals': 'KAN',
                 'Los Angeles Angels': 'LAA',
                 'Los Angeles Dodgers': 'LOS',
                 'Miami Marlins': 'MIA',
                 'Milwaukee Brewers': 'MIL',
                 'Minnesota Twins': 'MIN',
                 'New York Mets': 'NYM',
                 'New York Yankees': 'NYY',
                 'Oakland Athletics': 'OAK',
                 'Philadelphia Phillies': 'PHI',
                 'Pittsburgh Pirates': 'PIT',
                 'San Diego Padres': 'SDP',
                 'San Francisco Giants': 'SFG',
                 'Seattle Mariners': 'SEA',
                 'St. Louis Cardinals': 'STL',
                 'Tampa Bay Rays': 'TAM',
                 'Texas Rangers': 'TEX',
                 'Toronto Blue Jays': 'TOR',
                 'Washington Nationals': 'WAS'}

    url = 'http://rotogrinders.com/lineups/index/Baseball/FanDuel'
    doc = urllib2.urlopen(url).read()
    soup = BeautifulSoup(doc)
    headers_and_lineups = []
    for ul in soup.find_all('ul', class_='schedule-list'):
        headers = ul.find_all('header')
        grids = ul.find_all('div', class_='grid-3-3')
        headers_and_lineups.extend(zip(headers, grids))

    for h,l in headers_and_lineups:
        pitchers = _parseHeader(h)
        team_players, teams = _parseLineups(l)

        teams, pitchers, team_players

        teams = [team_map[t] for t in teams]

        # update team stats
        team_stats.set_team_home_or_away(teams[0], 'away')
        team_stats.set_team_home_or_away(teams[1], 'home')
        team_stats.set_team_opponent(teams[0], teams[1])

        # update batter player stats
        for i, players in enumerate(team_players):
            for p in players:
                #Normalizing pitcher names between FanGraphs and RotoGrinder
                #print 'Enter Full Name Equation', p['name'][0], p['name'].split()[-1], teams[i]
                curr_team = teams[i]
                name_and_team = player_stats.get_player_full_name(p['name'][0], p['name'].split()[-1], curr_team)
                if name_and_team==None:
                    print 'WARNING: Skipping batter %s' %(p['name'])
                    continue

                if p['hand'] == 'right' or p['hand'] == 'left':
                    player_stats.set_player_batting_hand(name_and_team, p['hand'])
                elif p['hand'] == 'both':
                    if i==0:
                        opp_throw_hand = pitchers[1]['hand']
                    else:
                        opp_throw_hand = pitchers[0]['hand']

                    if opp_throw_hand=='left':
                        player_stats.set_player_batting_hand(name_and_team, 'right')
                    elif opp_throw_hand=='right':
                        player_stats.set_player_batting_hand(name_and_team, 'left')
                    else:
                        print 'ERROR: Couldn\'t determine opposing pitching hand -- skipping team.'
                        continue
                else:
                    print 'WARNING: Skipping batter %s' %(p['name'])
                    continue

                player_stats.set_player_batting_hand(name_and_team, p['hand'])
                player_stats.set_player_batting_position(name_and_team, p['counter'])
                player_stats.set_player_salary(name_and_team, p['salary'])
                player_stats.set_player_fielding_position(name_and_team, p['position'].upper())
                player_stats.set_player_team(name_and_team, curr_team)
                player_stats.set_player_active(name_and_team)


        # update pitcher stats
        for i, pitcher in enumerate(pitchers):
            #Normalizing pitcher names between FanGraphs and RotoGrinder
            name_and_team = player_stats.get_player_full_name(pitcher['name'][0], pitcher['name'].split()[-1], teams[i])
            if name_and_team==None:
                print 'WARNING: Skipping pitcher %s' %(pitcher['name'])
                continue

            #Defaults to right if a player's hand is not available on rotogrinders
            player_stats.set_player_salary(name_and_team, pitcher['salary'])
            if pitcher['hand'] == 'right' or pitcher['hand'] == 'left':
                player_stats.set_player_throwing_hand(name_and_team, pitcher['hand'])
            else:
                player_stats.set_player_throwing_hand(name_and_team, 'right')
                player_stats.set_player_salary(name_and_team, 35000)
            player_stats.set_player_fielding_position(name_and_team, 'P')
            player_stats.set_starting_pitcher(teams[i], name_and_team)
            player_stats.set_player_team(name_and_team, curr_team)
            player_stats.set_player_active(name_and_team)


def _parseHeader(header):
    pitchers = []
    for h in header.find('div', class_='match-teams').text.split('@'):
        h = h.replace('(','\t').replace(')','\t')
        items = h.strip().split('\t')
        if len(items)==1:
            name = items[0].strip()
            hand = None
            salary = None
        else:
            name, hand, salary = h.replace('(','\t').replace(')','\t').split('\t')
            name = name.strip()
            hand = 'right' if hand.lower()=='r' else 'left'
            salary = _convertSalary(salary)
        player = {'name': name.lower(),
                  'hand': hand,
                  'salary': salary
                 }
        pitchers.append(player)
    return pitchers

def _convertSalary(str):
    str = '0' + str
    return float(''.join(n for n in str if n in '0123456789.'))*1000

def _parseLineups(lineups):
    teams = [t.text.strip().split('\n')[0] for t in lineups.find_all('div', class_='team')]
    player_lists = []
    for i, l in enumerate(lineups.find_all('ul', class_='lineup-list')):
        newLineup = []
        for p in l.find_all('li', class_='player'):
            items = [x.lower().strip() for x in p.text.replace('(', '').replace(')', '').split()]
            if len(items) in [6, 7]:
                if len(items)==5:
                    items.insert(3, 'r')
                counter = int(items[0])
                name = items[1]
                idx = 2
                while len(items[idx])>1:
                    name += ' ' + items[idx]
                    idx+=1
                hand = items[idx]
                idx += 1
                if hand=='r':
                    hand = 'right'
                elif hand=='l':
                    hand = 'left'
                elif hand=='s':
                    hand = 'both'
                else:
                    hand = 'unknown'
                salary = _convertSalary(items[idx])
                idx += 1
                position = items[idx]
                idx += 1
                player = {'counter': counter,
                          'name': name.lower(),
                          'hand': hand,
                          'salary': salary,
                          'position': position
                         }
                newLineup.append(player)
        player_lists.append(newLineup)
    if lineups.find('div', class_='away').text.find("Check Back Soon")>=0:
        player_lists.insert(0, [])
    if lineups.find('div', class_='home').text.find("Check Back Soon")>=0:
        player_lists.append([])

    return player_lists, teams

def main():
    parser = argparse.ArgumentParser(description='Find dat team.')
    parser.add_argument('stats', help='Directory containing all stats.')
    parser.add_argument('--knapsack', help='Find a team using the modified knapsack approach.')
    parser.add_argument('--mcmc', action='store_true', help='Find a team using the MCMC approach.')
    args = parser.parse_args()

    print 'Player Stats...'
    player_stats = PlayerStats(args.stats)
    print 'Ballpark Stats...'
    ballpark_stats = BallparkStats(args.stats)
    print 'Team Stats...'
    team_stats = TeamStats(args.stats)
    print 'League Stats...'
    league_stats = LeagueStats(args.stats)

    print 'Parsing Rotogrinders...'
    parseRotoGrinders(player_stats, team_stats)

    # start computing some stats here
    print 'Computing Equations...'
    eq = StatEquations(player_stats, team_stats, ballpark_stats, league_stats)
    #TODO: removed daily_stats from params. See stat_equations class for deets

    # names = ['felix hernandez',
    #          'chris tillman',
    #          'cliff lee']
    # for n in names:
    #     print n
    #     print '\t', eq.pitcher_points_expected_for_win(n)
    #     print '\t', eq.pitcher_points_expected_for_er(n)
    #     print '\t', eq.pitcher_points_expected_for_k(n)
    #     print '\t', eq.pitcher_expected_ip(n)
    #
    # names = ['mike trout',
    #           'chris davis',
    #           'jacoby ellsbury']
    # for n in names:
    #    print n
    #    print '\t hits', eq.batter_points_expected_for_hits(n)
    #    print '\t walk', eq.batter_points_expected_for_walks(n)
    #    print '\t hr  ', eq.batter_points_expected_for_hr(n)
    #    print '\t stol', eq.batter_points_expected_for_sb(n)
    #    print '\t rbis', eq.batter_points_expected_for_rbi(n)
    #    print '\t runs', eq.batter_points_expected_for_runs(n)
    #    print '\t total', eq.get_score(n)

    #names = player_stats.get_active_players()
    #names = player_stats.starting_pitchers.values()

    #for n in names:
       #print n, eq.get_score(n)

    # players = PlayerSalaryScores()
    # players.read_positions_and_salaries(args.salaries)
    # players.read_projections(args.projections)
    #
    # names = players.get_names()
    # classes = [playerget_player_teams.get_player_fielding_position(n) for n in names]
    # values = [players.get_score(n) for n in names]
    # weights = [players.get_player_salary(n) for n in names]
    #
    # if args.knapsack:
    #     knapsack = ModifiedKnapsack(names, classes, values, weights, CAPACITY, TEAM_COMP)
    #    #knapsack.find_solution()

    from mcmc import TeamMCMC
    candidate_players = list(player_stats.get_active_players())

    names = []
    classes = []
    values = []
    weights = []

    for i,p in enumerate(candidate_players,1):
        #Used to check how far we get through the names
        try:
            score = eq.get_score(p)
        except:
            print "ERROR: Couldn't get score for ", p
            continue

        #print '%d/%d %s %s %s' %(i, len(candidate_players), p, player_stats.get_player_team(p), player_stats.get_player_fielding_position(p)), score
        names.append(p)
        classes.append(player_stats.get_player_fielding_position(p))
        values.append(eq.get_score(p))
        weights.append(player_stats.get_player_salary(p))

        #Print Statements for getting players and scores in csv format
        #if player_stats.get_player_fielding_position(p) == 'P':
        #    print p,',',eq.get_score(p),',',eq.pitcher_points_expected_for_win(p),',',eq.pitcher_points_expected_for_er(p),',',eq.pitcher_points_expected_for_k(p),',',eq.pitcher_expected_ip(p), ','
        #else:
        #    p,',',eq.get_score(p),',',eq.batter_points_expected_for_hits(p),',',eq.batter_points_expected_for_hr(p),',',eq.batter_points_expected_for_rbi(p),',',eq.batter_points_expected_for_runs(p),',',eq.batter_points_expected_for_sb(p),',',eq.batter_points_expected_for_walks(p),','

    if args.mcmc:
        mcmc = TeamMCMC(names, classes, values, weights, CAPACITY, TEAM_COMP)
        mcmc.find_simulated_annealing_solution()


if __name__ == '__main__':
    main()