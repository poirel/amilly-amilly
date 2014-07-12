#!/usr/bin/env python

import argparse

from stat_parsers.player_stats import PlayerStats
from stat_parsers.ballpark_stats import BallparkStats
from stat_parsers.team_stats import TeamStats
from stat_parsers.league_stats import LeagueStats
#from stat_parsers.daily_stats import DailyStats
from stat_equations import StatEquations
#TODO: Removed DailyStats because we do not use it


CAPACITY = 35000
TEAM_COMP = {'P': 1,
             'C': 1,
             '1B': 1,
             '2B': 1,
             'SS': 1,
             '3B': 1,
             'OF': 3}

def main():
    parser = argparse.ArgumentParser(description='Find dat team.')
    parser.add_argument('salaries', help='File containing player salaries and positions.')
    parser.add_argument('projections', help='File containing projected points.')
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
    #print 'Daily Stats...'
    #daily_stats = DailyStats(args.stats)


    # start computing some stats here
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
    #          'yasiel puig',
    #          'justin upton',
    #          'jean segura']
    # for n in names:
    #     print n
    #     print '\t hits', eq.batter_points_expected_for_hits(n)
    #     print '\t walk', eq.batter_points_expected_for_walks(n)
    #     print '\t hr  ', eq.batter_points_expected_for_hr(n)
    #     print '\t stol', eq.batter_points_expected_for_sb(n)
    #     print '\t rbis', eq.batter_points_expected_for_rbi(n)
    #     print '\t runs', eq.batter_points_expected_for_runs(n)


    names = player_stats.get_active_players()
    names = player_stats.starting_pitchers.values()

    for n in names:
        print n, eq.get_score(n)


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
