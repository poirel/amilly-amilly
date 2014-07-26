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
        players, teams = _parseLineups(l)

        print teams, pitchers, players
        print

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
        player = {'name': name,
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
            if len(items)==5:
                items.insert(3, 'r')
            counter = int(items[0])
            name = items[1] + ' ' + items[2]
            hand = items[3]
            if hand=='r':
                hand = 'right'
            elif hand=='l':
                hand = 'left'
            else:
                hand = 'both'
            salary = _convertSalary(items[4])
            position = items[5]
            player = {'counter': counter,
                      'name': name,
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
    #names = ['mike trout',
    #           'chris davis',
    #           'jacoby ellsbury']
    #for n in names:
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
    # classes = [players.get_player_fielding_position(n) for n in names]
    # values = [players.get_score(n) for n in names]
    # weights = [players.get_player_salary(n) for n in names]
    #
    # if args.knapsack:
    #     knapsack = ModifiedKnapsack(names, classes, values, weights, CAPACITY, TEAM_COMP)
    #    #knapsack.find_solution()
    #
    # if args.mcmc:
    #     mcmc = TeamMCMC(names, classes, values, weights, CAPACITY, TEAM_COMP)
    #     mcmc.find_simulated_annealing_solution()


if __name__ == '__main__':
    main()