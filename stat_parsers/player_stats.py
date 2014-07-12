"""
Class: PlayerStats
Author: Poirel & Jett
Date: 3 July 2014

This class reads in Player Stats from the following files:
    - /Stats/Pitcher/(YEAR)/(YEAR) (H/A) Pitcher Stats.csv
    - /Stats/Pitcher/(YEAR)/(YEAR) Pitcher Stats vs (handedness).csv
    - /Stats/Pitcher/(YEAR)/(YEAR) Total Pitcher Stats.csv
    - /Stats/Catcher/(YEAR)/(YEAR) Catcher Stats.csv
    - /Stats/Batter/(YEAR)/(YEAR) Batter Stats vs (handedness).csv
    - /Stats/Batter/(YEAR)/(YEAR) Total Batter Stats.csv
    - /Stats/Daily/(DATE)-fanduel-salaries.csv

The following stats are available:
    Batter
        - Plate Appearances (PA) vs RHP/LHP
        - Home runs (HR) vs RHP/LHP
        - Strokeouts (K) vs RHP/LHP
        - wOBA vs RHP/LHP
        - total 1B
        - total 2B
        - total 3B
        - total hits
        - total walks (bb)
        - total walk percentage (bb%) -- format: 34.56%
        - total at bats (ab)
        - total plate appearances (pa)
        - total batting average (ba)
        - total games played (g)
        - total stolen bases (sb)
        - total times caught stealing (cs)
        - throwing hand
        - batting hand
        - team
        - batting position
    Pitcher
        - xFIP allowed (Home/Away Split)
        - hr allowed vs RHB/LHB
        - bb allowed vs RHB/LHB
        - tbf vs RHB/LHB -- (tbf = total batters faced)
        - wOBA allowed vs RHB/LHB
        - total games started
        - total strikeouts (k)
        - total innings pitched (ip)
    Catcher
        - stolen bases (sb) allowed
        - total caught stealing (cs)
    Daily
        - Player fielding position
        - Fanduel salary
        - if player is starting
        - Starting Pitchers
        - Active Players

Source of stats: Fangraphs & FanDuel salary scrape
"""

import time
from team_stats import *
from collections import defaultdict
import csv
import json
import urllib2
import re
from bs4 import BeautifulSoup
import sys

class PlayerStats:

    def __init__(self, statsDir):
        """
        Function: _init_
        -----------------

        This is the initial function. It takes in the stats directory as a parameter,
        and calls the 'read_*' functions.

        Parameters:
            :param statsDir: Directory in Dropbox with all Stats. Should always be:
                        /Dropbox/MDI Fantasy Sports/Stats

        :return nothing
        """
        self.statsDir = statsDir.rstrip('/')

        self.stats = defaultdict(lambda: defaultdict( lambda: defaultdict( lambda: defaultdict (dict))))
        self.starting_pitchers = {}

        self.read_rosters()
        self.read_pitcher_stats_home_away()
        self.read_pitcher_stats_vs_RHB_LHB()
        self.read_pitcher_stats_total()
        self.read_catcher_fielding_stats()
        self.read_batter_stats_vs_RHP_LHP()
        self.read_batter_stats_total()

        # must be read after rosters
        self.read_fanduel_positions_and_salaries()

        # print len([name for name, stats in self.stats.items() if 'bats' in stats])
        # print len([name for name, stats in self.stats.items() if 2014 in stats])
        # print len([name for name, stats in self.stats.items() if 2013 in stats])

        # self.printStats()
        # self.printPitchers()

    def printStats(self):
        """
        Function: printStats
        -----------------
        Prints the stats to the console

        Parameters:
            :param none

        :return none
        """
        print json.dumps(self.stats, indent=4)

    def printPitchers(self):
        """
        Function: printPitchers
        -----------------
        Prints the starting pitchers for the day

        Parameters:
            :param none

        :return none
        """
        print json.dumps(self.starting_pitchers, indent=4)

    def read_pitcher_stats_home_away(self):
        """
        Function: read_pitcher_stats_home_away
        -----------------
        Reads pitcher stats from the following directory:

            (statsDir from _init_)/Pitcher/(YEAR)/(YEAR) (HOME/AWAY) Pitcher Stats.csv

        Parameters:
            :param none

        :return nothing
        """
        stat = 'xfip'
        years = [2013, 2014]
        for year in years:
            for loc in ['Home', 'Away']:
                infile = '%s/Pitcher/%d/%d %s Pitcher Stats.csv' %(self.statsDir, year, year, loc)
                reader = csv.reader(open(infile), quotechar='"')
                header = reader.next()
                for items in reader:
                    player = items[0].lower()
                    xfip = float(items[2])
                    self.stats[player][year][stat][loc.lower()] = xfip

    def get_pitcher_xfip_allowed(self, year, player, homeOrAway):
        """
        Function: get_pitcher_xfip_allowed
        -----------------
        Helper method for pitcher xFIP allowed Home/Away split

        Parameters:
            :param year: the year of the pither stats, also corresponds with file name
            :param player: the pitcher whose stats we are looking for
            :param homeOrAway: whether or not the pitcher is home or away (format: home / away)

        :return pitcher xFIP for Home/Away split defined

        equations used in:
            pitcher_points_expected_for_er
        """
        return self.stats[player][year]['xfip'][homeOrAway]

    def read_pitcher_stats_vs_RHB_LHB(self):
        """
        Function: read_pitcher_stats_vs_RHB_LHB
        -----------------
        Reads pitcher stats from the the following directory:

            (statsDir from _init_)/Pitcher/(YEAR)/(YEAR) Pitcher Stats vs (RHB/LHB).csv

        Parameters:
            :param none

        :return nothing
        """
        stats = ['hr_allowed', 'bb_allowed', 'tbf', 'woba_allowed']
        years = [2013, 2014]
        for year in years:
            for hand in ['RHB', 'LHB']:
                infile = '%s/Pitcher/%d/%d Pitcher Stats vs %s.csv' %(self.statsDir, year, year, hand)
                reader = csv.reader(open(infile), quotechar='"')
                header = reader.next()
                for items in reader:
                    player = items[0].lower()
                    for i, stat_val in enumerate([float(x) for x in items[2:6]]):
                        self.stats[player][year][stats[i]][hand] = stat_val

    def get_pitcher_hr_allowed_vs_RHB_LHB(self, year, player, hand):
        """
        Function: get_pitcher_hr_allowed_vs_RHB_LHB
        -----------------
        Helper method for pitcher hr allowed vs RHB/LHB

        Parameters:
            :param year: the year of the pitcher stats, also corresponds with file name
            :param  player: the pitcher whose stats we are looking for
            :param hand: handedness of the batter who is facing the pitcher (LHB/RHB)

        :return pitcher hrs allowed for RHB/LHB split defined

        equations used in:
            batter_points_expected_for_hr
        """
        if hand.lower()=='left':
            return self.stats[player][year]['hr_allowed']['LHB']
        elif hand.lower()=='right':
            return self.stats[player][year]['hr_allowed']['RHB']
        else:
            return None

    def get_pitcher_bb_allowed_vs_RHB_LHB(self, year, player, hand):
        """
        Function: get_pitcher_bb_allowed_vs_RHB_LHB
        -----------------
        Helper method for pitcher bb allowed vs RHB/LHB

        Parameters:
            :param year: the year of the pitcher stats, also corresponds with file name
            :param player: the pitcher whose stats we are looking for
            :param hand: handedness of the batter who is facing the pitcher (LHB/RHB)

        :return pitcher bb allowed for RHB/LHB split defined

        equations used in:
            batter_points_expected_for_walks
        """
        if hand.lower()=='left':
            return self.stats[player][year]['bb_allowed']['LHB']
        elif hand.lower()=='right':
            return self.stats[player][year]['bb_allowed']['RHB']
        else:
            return None

    def get_pitcher_total_batters_faced_vs_RHB_LHB(self, year, player, hand):
        """
        Function: get_pitcher_total_batters_faced_vs_RHB_LHB
        -----------------
        Helper method for pitcher total batters faced (TBF) vs RHB/LHB

        Parameters:
            :param year: the year of the pitcher stats, also corresponds with file name
            :param player: the pitcher whose stats we are looking for
            :param hand: handedness of the batter who is facing the pitcher (LHB/RHB)

        :return pitcher tbf for RHB/LHB split defined

        equations used in:
            batter_points_expected_for_walks
            batter_points_expected_for_hr
        """
        if hand.lower()=='left':
            return self.stats[player][year]['tbf']['LHB']
        elif hand.lower()=='right':
            return self.stats[player][year]['tbf']['RHB']
        else:
            return None

    def get_pitcher_woba_allowed_vs_RHB_LHB(self, year, player, hand):
        """
        Function: get_pitcher_woba_allowed_vs_RHB_LHB
        -----------------
        Helper method for pitcher wOBA allowed vs RHB/LHB

        Parameters:
            :param year: the year of the pitcher stats, also corresponds with file name
            :param player: the pitcher whose stats we are looking for
            :param hand: handedness of the batter who is facing the pitcher (LHB/RHB)

        :return pitcher wOBA for RHB/LHB split defined

        equations used in:
            batter_points_expected_for_runs
            batter_points_expected_for_rbi
            batter_points_expected_for_hits
        """
        if hand.lower()=='left':
            return self.stats[player][year]['woba_allowed']['LHB']
        elif hand.lower()=='right':
            return self.stats[player][year]['woba_allowed']['RHB']
        else:
            return None

    def read_pitcher_stats_total(self):
        """
        Function: read_pitcher_stats_total
        -----------------
        Reads pitcher stats from the following directory:

            (statsDir from _init_)/Pitcher/(YEAR)/(YEAR) Total Pitcher Stats.csv

        Parameters:
            :param none

        :return nothing
        """
        stats = ['gs_total', 'k_pitched_total', 'ip_total']
        years = [2013, 2014]
        for year in years:
            infile = '%s/Pitcher/%d/%d Total Pitcher Stats.csv' %(self.statsDir, year, year)
            reader = csv.reader(open(infile), quotechar='"')
            header = reader.next()
            for items in reader:
                player = items[0].lower()
                for i, stat_val in enumerate([float(x) for x in items[2:5]]):
                    self.stats[player][year][stats[i]] = stat_val

    def get_pitcher_total_games_started(self, year, player):
        """
        Function: get_pitcher_total_games_started
        -----------------
        Helper method for pitcher total games started

        Parameters:
            year: the year of the pitcher stats, also corresponds with file name
            player: the pitcher whose stats we are looking for

        :return pitcher total games started (gs) for defined year

        equations used in:
            pitcher_points_expected_for_k
            pitcher_expected_ip
        """
        return self.stats[player][year]['gs_total']

    def get_pitcher_total_k(self, year, player):
        """
        Function: get_pitcher_total_k
        -----------------
        Helper method for pitcher total strikeouts (k)

        Parameters:
            year: the year of the pitcher stats, also corresponds with file name
            player: the pitcher whose stats we are looking for

        :return pitcher total strikeouts (k) for defined year

        equations used in:
            pitcher_points_expected_for_k
        """
        return self.stats[player][year]['k_pitched_total']

    def get_pitcher_total_innings_pitched(self, year, player):
        """
        Function: get_pitcher_total_innings_pitched
        -----------------
        Helper method for pitcher total innings pitched (ip)

        Parameters:
            year: the year of the pitcher stats, also corresponds with file name
            player: the pitcher whose stats we are looking for

        :return pitcher total innings pitched (ip) for defined year

        equations used in:
            pitcher_points_expected_for_k
            pitcher_expected_ip
        """
        return self.stats[player][year]['ip_total']

    def read_catcher_fielding_stats(self):
        """
        Function: read_catcher_stats
        -----------------
        Reads catcher fielding stats from the following directory:

            (statsDir from _init_)/Catcher/(YEAR) Catcher Stats.csv

        Parameters: none

        :return nothing
        """
        stats = ['sb_catcher', 'cs_catcher']
        years = [2013, 2014]
        for year in years:
            infile = '%s/Catcher/%d Catcher Stats.csv' %(self.statsDir, year)
            reader = csv.reader(open(infile), quotechar='"')
            header = reader.next()
            for items in reader:
                player = items[0].lower()
                for i, stat_val in enumerate([float(x) for x in items[2:4]]):
                    self.stats[player][year][stats[i]] = stat_val

    def get_catcher_fielding_stolen_bases_allowed(self, year, player):
        """
        Function: get_catcher_fielding_stolen_bases_allowed
        -----------------
        Helper method for the stolen bases allowed from a specific catcher

        Parameters:
            :param year: the year of the catcher stats, also corresponds with file name
            :param player: the catcher whose stats we are looking for

        :return total stolen bases allowed by the specified catcher

        equations used in:
            Not used yet. Would be used in batter_points_expected_for_sb
        """
        return self.stats[player][year]['sb_catcher']

    def get_catcher_fielding_caught_stealing(self, year, player):
        """
        Function: get_catcher_fielding_caught_stealing
        -----------------
        Helper method for the base runners that a catcher caught stealing

        Parameters:
            :param year: the year of the catcher stats, also corresponds with file name
            :param player: the catcher whose stats we are looking for

        :return total base runners a specified catcher caught stealing

        equations used in:
            Not used yet. Would be used in batter_points_expected_for_sb
        """
        return self.stats[player][year]['cs_catcher']

    def read_batter_stats_vs_RHP_LHP(self):
        """
        Function: read_batter_stats_vs_RHP_LHP
        -----------------
        Reads batter stats from the following directory:

            (statsDir from _init_)/Batter/(YEAR)/(YEAR) Batter Stats vs (RHP/LHP).csv

        Parameters:
            :param none

        :return nothing
        """
        stats = ['pa', 'hr', 'k', 'woba']
        years = [2013, 2014]
        for year in years:
            for hand in ['RHP', 'LHP']:
                infile = '%s/Batter/%d/%d Batter Stats vs %s.csv' %(self.statsDir, year, year, hand)
                reader = csv.reader(open(infile), quotechar='"')
                header = reader.next()
                for items in reader:
                    player = items[0].lower()
                    for i, stat_val in enumerate([float(x) for x in items[2:6]]):
                        self.stats[player][year][stats[i]][hand] = stat_val

    def get_batter_plate_appearances_vs_RHP_LHP(self, year, player, hand):
        """
        Function: get_batter_plate_appearances_vs_RHP_LHP
        -----------------
        Helper method for the plate appearances for a specified batter vs RHP/LHP

        Parameters:
            :param year: the year of the batter stats, also corresponds with file name
            :param player: the batter whose stats we are looking for
            :param hand: the throwing handedness of the pitcher that the batter is facing

        :return plate appearances split vs RHP/LHP

        equations used in:
            batter_points_expected_for_hr
        """
        if hand.lower()=='left':
            return self.stats[player][year]['pa']['LHP']
        elif hand.lower()=='right':
            return self.stats[player][year]['pa']['RHP']
        else:
            return None

    def get_batter_hr_vs_RHP_LHP(self, year, player, hand):
        """
        Function: get_batter_hr_vs_RHP_LHP
        -----------------
        Helper method for the home runs for a specified batter vs RHP/LHP

        Parameters:
            :param year: the year of the batter stats, also corresponds with file name
            :param player: the batter whose stats we are looking for
            :param hand: the throwing handedness of the pitcher that the batter is facing

        :return home runs split vs RHP/LHP

        equations used in:
            batter_points_expected_for_hr
        """
        if hand.lower()=='left':
            return self.stats[player][year]['hr']['LHP']
        elif hand.lower()=='right':
            return self.stats[player][year]['hr']['RHP']
        else:
            return None

    def get_batter_k_vs_RHP_LHP(self, year, player, hand):
        #TODO: Check to see why this is not used
        """
        Function: get_batter_k_vs_RHP_LHP
        -----------------
        Helper method for the strikeouts for a specified batter vs RHP/LHP

        Parameters:
            :param year: the year of the batter stats, also corresponds with file name
            :param player: the batter whose stats we are looking for
            :param hand: the throwing handedness of the pitcher that the batter is facing

        :return strikeouts split vs RHP/LHP

        equations used in:
            Not used...interesting.
        """
        if hand.lower()=='left':
            return self.stats[player][year]['k']['LHP']
        elif hand.lower()=='right':
            return self.stats[player][year]['k']['RHP']
        else:
            return None

    def get_batter_woba_vs_RHP_LHP(self, year, player, hand):
        """
        Function: get_batter_woba_vs_RHP_LHP
        -----------------
        Helper method for the wOBA for a specified batter vs RHP/LHP

        Parameters:
            :param year: the year of the batter stats, also corresponds with file name
            :param player: the batter whose stats we are looking for
            :param hand: the throwing handedness of the pitcher that the batter is facing

        :return batter wOBA split vs RHP/LHP

        equations used in:
            batter_points_expected_for_runs
            batter_points_expected_for_rbi
            batter_points_expected_for_hits
        """
        if hand.lower()=='left':
            return self.stats[player][year]['woba']['LHP']
        elif hand.lower()=='right':
            return self.stats[player][year]['woba']['RHP']
        else:
            return None

    def read_batter_stats_total(self):
        """
        Function:read_batter_stats_total
        -----------------
        Reads batter stats from the following directory:

            (statsDir from _init_)/Batter/(YEAR)/(YEAR) Total Batter Stats.csv

        Parameters:
            :param none

        :return nothing
        """
        stats = ['1b_total',
                 '2b_total',
                 '3b_total',
                 'h_total',
                 'bb_total',
                 'bb_percent_total',
                 'hr_total',
                 'ab_total',
                 'pa_total',
                 'ba_total',
                 'g_total',
                 'sb_total',
                 'cs_total']
        years = [2013, 2014]
        for year in years:
            infile = '%s/Batter/%d/%d Total Batter Stats.csv' %(self.statsDir, year, year)
            reader = csv.reader(open(infile), quotechar='"')
            header = reader.next()
            for items in reader:
                player = items[0].lower()
                for i, stat_val in enumerate([float(x.rstrip('%')) for x in items[2:15]]):
                    if stats[i]=='bb_percent_total':
                        stat_val/=100.0
                    self.stats[player][year][stats[i]] = stat_val

    def get_batter_1b_total(self, year, player):
        """
        Function: get_batter_1b_total
        -----------------
        Helper method for the total singles (1B) for a specified batter

        Parameters:
            :param year: the year of the batter stats, also corresponds with file name
            :param player: the batter whose stats we are looking for

        :return batter total singles (1B) for the specified year

        equations used in:
            batter_points_expected_for_hits
        """
        return self.stats[player][year]['1b_total']

    def get_batter_2b_total(self, year, player):
        """
        Function: get_batter_2b_total
        -----------------
        Helper method for the total doubles (2B) for a specified batter

        Parameters:
            :param year: the year of the batter stats, also corresponds with file name
            :param player: the batter whose stats we are looking for

        :return batter total doubles (2B) for the specified year

        equations used in:
            batter_points_expected_for_hits
        """
        return self.stats[player][year]['2b_total']

    def get_batter_3b_total(self, year, player):
        """
        Function: get_batter_3b_total
        -----------------
        Helper method for the total triples (3B) for a specified batter

        Parameters:
            :param year: the year of the batter stats, also corresponds with file name
            :param player: the batter whose stats we are looking for

        :return batter total triples (3B) for the specified year

        equations used in:
            batter_points_expected_for_hits
        """
        return self.stats[player][year]['3b_total']

    def get_batter_hits_total(self, year, player):
        """
        Function: get_batter_hits_total
        -----------------
        Helper method for the total hits (1B,2B,3B,HR) for a specified batter

        Parameters:
            :param year: the year of the batter stats, also corresponds with file name
            :param player: the batter whose stats we are looking for

        :return batter total hits for the specified year

        equations used in:
            batter_points_expected_for_hits
        """
        return self.stats[player][year]['h_total']

    def get_batter_bb_total(self, year, player):
        """
        Function: get_batter_bb_total
        -----------------
        Helper method for the total walks (BB) for a specified batter

        Parameters:
            :param year: the year of the batter stats, also corresponds with file name
            :param player: the batter whose stats we are looking for

        :return batter total walks for the specified year

        equations used in:
            not used...probably because we already have the bb% stat
        """
        return self.stats[player][year]['bb_total']

    def get_batter_bb_percent_total(self, year, player):
        """
        Function: get_batter_bb_percent_total
        -----------------
        Helper method for the total walk percentage (BB%) for a specified batter

        Parameters:
            :param year: the year of the batter stats, also corresponds with file name
            :param player: the batter whose stats we are looking for

        :return batter total walk percentage for the specified year

        equations used in:
            batter_points_expected_for_walks
            batter_points_expected_for_runs
            batter_points_expected_for_rbi
        """
        return self.stats[player][year]['bb_percent_total']

    def get_batter_hr_total(self, year, player):
        """
        Function: get_batter_hr_total
        -----------------
        Helper method for the total home runs (hr) for a specified batter

        Parameters:
            :param year: the year of the batter stats, also corresponds with file name
            :param player: the batter whose stats we are looking for

        :return batter total home runs for the specified year

        equations used in:
            batter_points_expected_for_hits
            batter_points_expected_for_hr
            batter_points_expected_for_runs
            batter_points_expected_for_rbi
        """
        return self.stats[player][year]['hr_total']

    def get_batter_ab_total(self, year, player):
        """
        Function: get_batter_ab_total
        -----------------
        Helper method for the total at bats (ab) for a specified batter

        Parameters:
            :param year: the year of the batter stats, also corresponds with file name
            :param player: the batter whose stats we are looking for

        :return batter total at bats for the specified year

        equations used in:
            batter_points_expected_for_hits
            batter_points_expected_for_walks
            batter_points_expected_for_hr
            batter_points_expected_for_runs
            batter_points_expected_for_rbi
        """
        return self.stats[player][year]['ab_total']

    def get_batter_pa_total(self, year, player):
        """
        Function: get_batter_pa_total
        -----------------
        Helper method for the total plate appearances (pa) for a specified batter

        Note: PA = AB + BB

        Parameters:
            :param year: the year of the batter stats, also corresponds with file name
            :param player: the batter whose stats we are looking for

        :return batter total plate appearances for the specified year

        equations used in:
            batter_points_expected_for_hr
            batter_points_expected_for_runs
            batter_points_expected_for_rbi
        """
        return self.stats[player][year]['pa_total']

    def get_batter_ba_total(self, year, player):
        """
        Function: get_batter_ba_total
        -----------------
        Helper method for the total batting average (ba) for a specified batter

        Note: BA = H / AB

        Parameters:
            :param year: the year of the batter stats, also corresponds with file name
            :param player: the batter whose stats we are looking for

        :return batter total batting average for the specified year

        equations used in:
            batter_points_expected_for_runs
            batter_points_expected_for_rbi
        """
        return self.stats[player][year]['ba_total']

    def get_batter_games_played_total(self, year, player):
        """
        Function: get_batter_games_played_total
        -----------------
        Helper method for the total games played (g) for a specified batter

        Parameters:
            :param year: the year of the batter stats, also corresponds with file name
            :param player: the batter whose stats we are looking for

        :return batter total games played for the specified year

        equations used in:
            batter_points_expected_for_hits
            batter_points_expected_for_walks
            batter_points_expected_for_hr
            batter_points_expected_for_runs
            batter_points_expected_for_rbi
            batter_points_expected_for_sb
        """
        return self.stats[player][year]['g_total']

    def get_batter_sb_total(self, year, player):
        """
        Function: get_batter_sb_total
        -----------------
        Helper method for the total stolen bases (sb) for a specified batter

        Parameters:
            :param year: the year of the batter stats, also corresponds with file name
            :param player: the batter whose stats we are looking for

        :return batter total stolen bases for the specified year

        equations used in:
            batter_points_expected_for_sb
        """
        return self.stats[player][year]['sb_total']

    def get_batter_cs_total(self, year, player):
        #TODO: determine why we dont use this stat
        """
        Function: get_batter_cs_total
        -----------------
        Helper method for the total times caught stealing for a specified batter

        Parameters:
            :param year: the year of the batter stats, also corresponds with file name
            :param player: the batter whose stats we are looking for

        :return batter total times caught stealing for the specified year

        equations used in:
            not used yet...might not use
        """
        return self.stats[player][year]['cs_total']

    def read_fanduel_positions_and_salaries(self):
        """
        Function:read_fanduel_positions_and_salaries
        -----------------
        Reads fanduel info from the following directory:

            (statsDir from _init_)/Daily/(DATE)-fanduel-salaries.csv

        Parameters:
            :param none

        :return nothing
        """
        try:
            date = time.strftime('%Y-%m-%d')
            # TODO: this is a daily stat
            infile = '%s/Daily/%s-fanduel-salaries.csv' %(self.statsDir, date)
            reader = csv.reader(open(infile), quotechar='"')
        except IOError:
            print "Salaries don't exist, dipshit."
        for items in reader:
            # Sample entry:
            # OF,Colby RasmusDL,2.3,37,TAM@TOR,"$3,500 ",Add
            position = items[0]
            player, status = self._clean_name(items[1])
            player = self._normalize_name(player)
            salary = self._clean_salary(items[5])
            self.stats[player]['fielding_position'] = position
            self.stats[player]['salary'] = salary

            # TODO: change to None when we have real lineups
            starting = True
            if status=='P':
                starting = True
            if status=='DL':
                starting = False
            self.stats[player]['starting'] = status

            if status=='P':
                team = self.get_team(player)
                self.starting_pitchers[team] = player

    def _clean_salary(self, salary):
        """
        Function:_clean_salary
        -----------------
        Takes a salary from the fanduel file on Dropbox and removes the '$' and ','.

        Parameters:
            :param salary: value read from the fanduel file (format: $4,000)

        :return salary value in new format (4000) as an integer
        """
        return int(salary.strip().replace('$', '').replace(',', ''))

    def get_player_fielding_position(self, player):
        """
        Function: get_player_fielding_position
        -----------------
        Helper method for the fielding position for a specified player

        Parameters:
            :param player: the player whose position we are looking for

        :return player fielding position (C, 1B, 2B, SS, 3B, OF, P)

        equations used in:
           get_score
        """
        return self.stats[player]['fielding_position']

    def get_player_salary(self, player):
        """
        Function: get_player_salary
        -----------------
        Helper method for the fielding position for a specified player

        Parameters:
            :param player: the player whose position we are looking for

        :return player fielding position (C, 1B, 2B, SS, 3B, OF, P)

        equations used in:
           get_score
        """
        return self.stats[player]['salary']

    def get_player_starting_status(self, player):
        #TODO: Where is this used?

        """
        Function: get_player_starting_status
        -----------------
        Helper method for the starting status for a specified player

        Parameters:
            :param player: the player whose position we are looking for

        :return
            True for Pitchers who are 'P' on Fanduel
            False for Players who are 'DL' on Fanduel
            NOTE: Defaults true. Need to update with real lineups

        equations used in:
           unknown
        """
        return self.stats[player]['starting']

    def read_rosters(self):
        """
        Function:read_rosters
        -----------------
        Reads team rosters from ESPN from the following URL:

            http://espn.go.com/mlb/team/roster/_/name/(TEAM)/sort/lastName/(LOCATION)-(MASCOT)

        Note: This method includes:

            - Mapping for Handedness of Batters and Pitchers
            - Normalization of Team Identifier across ESPN and FanDuel

        Parameters:
            :param none

        :return nothing
        """
        handMap = {'R': 'right',
                   'L': 'left',
                   'B': 'switch',
                   'S': 'switch'}

        for team in get_teams():
            url_team = team
            if team=='LOS':
                url_team = 'LAD'
            elif team=='CWS':
                url_team='CHW'
            elif team=='SDP':
                url_team='SD'
            elif team=='SFG':
                url_team='SF'

            url_mascot = get_team_mascot(team).lower().replace(' ', '-')
            url_location = get_team_location(team).lower().replace(' ', '-')
            url = 'http://espn.go.com/mlb/team/roster/_/name/%s/sort/lastName/%s-%s' %(url_team.lower(), url_location, url_mascot)
            doc = urllib2.urlopen(url).read()
            soup = BeautifulSoup(doc)
            tab = soup.find('table')
            # header = [td.text for td in tab.find_all('tr')[1].find_all('td')]
            # Header for data is : ['NO.', 'NAME', 'POS', 'BAT', 'THW', 'AGE', 'HT', 'WT', 'BIRTH PLACE', 'SALARY']
            player_data = [[td.text for td in tr.find_all('td')] for tr in tab.find_all('tr')[2:]]
            for p in player_data:
                # TODO: could use this DL information.
                player = re.sub('DL[0-9]*$', '', p[1]).strip().lower()
                # TODO: could use this position info
                position = p[2]
                self.stats[player]['team'] = team
                self.stats[player]['bats'] = handMap[p[3]]
                self.stats[player]['throws'] = handMap[p[4]]

    def get_player_throwing_hand(self, player):
        """
        Function: get_player_throwing_hand
        -----------------
        Helper method for the throwing hand (right/left...from HandMap) for a specified player

        Parameters:
            :param player: the player whose throwing hand we are looking for

        :return
            right for RHP
            left for LHP

        equations used in:
           pitcher_points_expected_for_k
           pitcher_points_expected_for_er
           batter_points_expected_for_hits
           batter_points_expected_for_hr
           batter_points_expected_for_runs
           batter_points_expected_for_rbi
        """
        return self.stats[player]['throws']

    def get_player_batting_hand(self, player):
        """
        Function: get_player_batting_hand
        -----------------
        Helper method for the batting hand (right/left/switch...from HandMap) for a specified player

        Parameters:
            :param player: the player whose batting hand we are looking for

        :return
            right for RHP
            left for LHP
            switch for Switch Hitters

        equations used in:
           batter_points_expected_for_hits
           batter_points_expected_for_walks
           batter_points_expected_for_hr
           batter_points_expected_for_runs
           batter_points_expected_for_rbi
        """
        return self.stats[player]['bats']

    def get_player_team(self, player):
        """
        Function: get_player_team
        -----------------
        Helper method for the team of a specified player

        Parameters:
            :param player: the player whose team we are looking for

        :return
            2 or 3 letter team name normalized across ESPN and FanDuel

        equations used in:
            pitcher_points_expected_for_k
            pitcher_points_expected_for_er
            batter_points_expected_for_hits
            batter_points_expected_for_walks
            batter_points_expected_for_hr
            batter_points_expected_for_sb
            batter_points_expected_for_runs
            batter_points_expected_for_rbi
        """
        return self.stats[player]['team']

    def get_player_batting_position(self, player):
        # TODO: not computing position right now
        """
        Function: get_player_batting_position
        -----------------
        Helper method for the position in the batting order of a specified player

        Parameters:
            :param player: the player whose batting order position we are looking for

        :return
            now: 4
            future: batting order value between 1 and 9 (inclusive)

        equations used in:
            batter_points_expected_for_runs
            batter_points_expected_for_rbi
        """
        return 4
        #return randint(1, 9)

    def get_starting_pitcher(self, team):
        """
        Function: get_starting_pitcher
        -----------------
        Helper method for the position in the starting pitcher of a given team

        Parameters:
            :param team: the team whose starting pitcher we are looking for

        :return the SP for the specified team

        equations used in:
            batter_points_expected_for_hits
            batter_points_expected_for_walks
            batter_points_expected_for_hr
            batter_points_expected_for_runs
            batter_points_expected_for_rbi
        """
        return self.starting_pitchers[team]

    def _normalize_name(self, name):
        """
        Function: _normalize_name
        -----------------
        Private method to normalize player names across ESPN and FanDuel

        NOTE: Zach claimed on 2014-06-28 that we will only need this sub for ~30 names.

        Parameters:
            :param name: the player name we want to normalize

        :return the normalized name

        equations used in:
            read_fanduel_positions_and_salaries
        """
        if name.lower()=="tom milone":
            return "tommy milone"
        if name.lower()=="michael bolsinger":
            return "mike bolsinger"
        return name

    def _clean_name(self, name):
        """
        Function: _clean_name
        -----------------
        Private method to clean player names from FanDuel

        Parameters:
            :param name: the player name we want to clean

        :return a tuple (name, status) where status is "P", "DL" or None

        equations used in:
            read_fanduel_positions_and_salaries
        """
        if name.endswith('DL'):
            return name.lower()[:-2], 'DL'
        elif name.endswith('P'):
            return name.lower()[:-1], 'P'
        else:
            return name.lower(), None

    def get_active_players(self):
        """
        Function: get_active_players
        -----------------
        Private method to clean player names from FanDuel

        Parameters:
            :param name: the player name we want to clean

        :return a tuple (name, status) where status is "P", "DL" or None

        equations used in:
            find_team.py
        """
        players = []
        for k, v in self.stats.items():
            # TODO: hack to avoid players when we don't know their starting pitcher.
            # this should not be an issue when we read real rosters.
            if v.get('starting', False) and (v.get('team', None) in self.starting_pitchers):
                players.append(k)
        return players
