"""
Class: LeagueStats
Author: Poirel & Jett
Date: 3 July 2014

This class reads in League Stats from the following file:
    - /Stats/League/(YEAR) League Stats.csv

The following stats are available:
    - Batter Strike Out Percentage (K %) -- format: 20.22%
    - Batter OPS -- format: 0.772
    - Total Stolen Bases (SB)
    - Total Caught Stealing (CS)
    - Total Home Run (HR)
    - Total Plate Appearances (PA)
    - Total Walks (BB)
    - Total Runs (R)
    - Weighted On Base Average (wOBA) -- format: 0.313

Source of stats: Fangraphs
"""

from collections import defaultdict
import csv
import json

class LeagueStats:

    def __init__(self, statsDir):
        """
        Function: _init_
        -----------------

        This is the initial function. It takes in the stats directory as a parameter,
        and calls the 'read_league_stats' function.

        Parameters:
            :param statsDir: Directory in Dropbox with all Stats. Should always be:
                        /Dropbox/MDI Fantasy Sports/Stats

        :return nothing
        """
        self.statsDir = statsDir.rstrip('/')

        self.stats = defaultdict(dict)

        self.read_league_stats()

    def read_league_stats(self):
        """
        Function: read_league_stats
        -----------------
        Reads league stats from the following directory:

            (statsDir from _init_)/League/(YEAR) League Stats.csv

        Parameters:
            :param none

        :return nothing
        """
        stats = ['k_percent', 'ops', 'sb', 'cs', 'hr', 'pa', 'bb', 'r', 'woba']
        years = [2014]
        for year in years:
            infile = '%s/League/%d League Stats.csv' %(self.statsDir, year)
            reader = csv.reader(open(infile), quotechar='"')
            header = reader.next()
            for items in reader:
                for i, stat_val in enumerate([float(x.rstrip('%')) for x in items[1:10]]):
                    if stats[i]=='k_percent':
                        stat_val/=100.0
                    self.stats[year][stats[i]] = stat_val

    def get_league_k_percentage(self, year):
        """
        Function: get_league_k_percentage
        -----------------
        Helper method for league strike out (k) percentage

        Parameters:
            :param year: the year of the league stats, also corresponds with file name

        :return league k % for the defined year

        note:
            file format: 20.30%. We divide by 100 in 'read_league_stats'
            format we return: 0.2030

        equations used in:
            pitcher_points_expected_for_k
        """
        return self.stats[year]['k_percent']

    def get_league_ops(self, year):
        """
        Function: get_league_ops
        -----------------
        Helper method for league ops

        Parameters:
            :param year: the year of the league stats, also corresponds with file name

        :return league ops for the defined year

        equations used in:
            None yet. May be used when Day/Night splits are acquired
        """
        return self.stats[year]['ops']

    def get_league_stolen_bases(self, year):
        """
        Function: get_league_stolen_bases
        -----------------
        Helper method for league stolen bases

        Parameters:
            :param year: the year of the league stats, also corresponds with file name

        :return league sb for the defined year

        equations used in:
            batter_points_expected_for_sb
        """
        return self.stats[year]['sb']

    def get_league_caught_stealing(self, year):
        """
        Function: get_league_caught_stealing
        -----------------
        Helper method for league caught stealing, or the total amount of times a player was caught stealing

        Parameters:
            :param year: the year of the league stats, also corresponds with file name

        :return league caught stealing total for the defined year

        equations used in:
            batter_points_expected_for_sb
        """
        return self.stats[year]['cs']

    def get_league_homerun(self, year):
        """
        Function: get_league_homerun
        -----------------
        Helper method for league home runs

        Parameters:
            :param year: the year of the league stats, also corresponds with file name

        :return league hrs for the defined year

        equations used in:
            batter_points_expected_for_hr
        """
        return self.stats[year]['hr']

    def get_league_plate_appearance(self, year):
        """
        Function: get_league_plate_appearance
        -----------------
        Helper method for league plate appearances

        Parameters:
            :param year: the year of the league stats, also corresponds with file name

        :return league plate appearance for the defined year

        equations used in:
            batter_points_expected_for_walks
            batter_points_expected_for_hr
        """
        return self.stats[year]['pa']

    def get_league_bb(self, year):
        """
        Function: get_league_bb
        -----------------
        Helper method for league walks (BB)

        Parameters:
            :param year: the year of the league stats, also corresponds with file name

        :return league total walks for the defined year

        equations used in:
            batter_points_expected_for_walks
        """
        return self.stats[year]['bb']

    def get_league_runs(self, year):
        """
        Function: get_league_runs
        -----------------
        Helper method for league runs

        Parameters:
            :param year: the year of the league stats, also corresponds with file name

        :return league total runs for the defined year

        equations used in:
            batter_points_expected_for_runs
            batter_points_expected_for_rbi
        """
        return self.stats[year]['r']

    def get_league_woba(self, year):
        """
        Function: get_league_woba
        -----------------
        Helper method for league weighted on base average (woba)

        Parameters:
            :param year: the year of the league stats, also corresponds with file name

        :return league woba for the defined year

        equations used in:
            pitcher_points_expected_for_er
            batter_points_expected_for_hits
            batter_points_expected_for_runs
            batter_points_expected_for_rbi
        """
        return self.stats[year]['woba']

    def print_stats(self):
        """
        Function: printStats
        -----------------
        Prints the stats to the console

        Parameters:
            :param none

        :return none
        """
        print json.dumps(self.stats, indent=4)