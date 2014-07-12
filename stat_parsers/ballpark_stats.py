"""
Class: BallparkStats
Author: Poirel & Jett
Date: 3 July 2014

This class reads in BallPark Stats from the following file:
    - /Stats/Park Factor/Ball Park Factor.csv

The following stats are available:
    - Overall Park Factor
    - RHB / LHB AVG Factor per Ball Park
    - RHB / LHB HR Factor per Ball Park

Note: The available stats are factors (aka multipliers), not real stats.

Source of stats: Rotowire Ball Park Factors
"""

from collections import defaultdict
import csv
import json

class BallparkStats:

    def __init__(self, statsDir):
        """
        Function: _init_
        -----------------

        This is the initial function. It takes in the stats directory as a parameter,
        and calls the 'read_ballpark_factors' function.

        Parameters:
            :param statsDir: Directory in Dropbox with all Stats. Should always be:
                        /Dropbox/MDI Fantasy Sports/Stats

        :return none
        """
        self.statsDir = statsDir.rstrip('/')

        self.stats = defaultdict(dict)

        self.read_ballpark_factors()

    def read_ballpark_factors(self):
        """
        Function: read_ballpark_factors
        -----------------
        Reads ballpark factors from the following directory:

            (statsDir from _init_)/Park Factor/Ball Park Factor.csv

        Parameters:
            :param none

        :return none
        """
        stats = ['overall', 'avg_lhb', 'avg_rhb', 'hr_lhb', 'hr_rhb']
        infile = '%s/Park Factor/Ball Park Factor.csv' %(self.statsDir)
        reader = csv.reader(open(infile), quotechar='"')
        header = reader.next()
        for items in reader:
            team = items[0].upper()
            for i, stat_val in enumerate([float(x) for x in items[1:6]]):
                self.stats[team][stats[i]] = stat_val

    def get_ballpark_factor_overall(self, team):
        """
        Function: get_ballpark_factor_overall
        -----------------
        Helper method for overall ballpark factor

        Parameters:
            :param team: The team who plays in the park we are looking for

        :return overall park factor, which is a multiplier.

        equations used in:
            pitcher_points_expected_for_er
            batter_points_expected_for_runs
            batter_points_expected_for_rbi
        """
        return self.stats[team]['overall']

    def get_ballpark_factor_batting_average(self, team, hand):
        """
        Function: get_ballpark_factor_batting_average
        -----------------
        Helper method for ballpark factor for RHB or LHB Batting Average

        Parameters:
            :param team: The team who plays in the park we are looking for
            :param hand: hand of the batter (left or right expected)

        :return ballpark factor for Batting Average per batter hand, which is a multiplier.

        equations used in:
            batter_points_expected_for_hits
        """
        if hand.lower()=='left':
            return self.stats[team]['avg_lhb']
        elif hand.lower()=='right':
            return self.stats[team]['avg_rhb']
        else:
            return None

    def get_ballpark_factor_homerun(self, team, hand):
        """
        Function: get_ballpark_factor_homerun
        -----------------
        Helper method for ballpark factor for a RHB or LHB Home Run

        Parameters
            :param team: The team who plays in the park we are looking for
            :param hand: hand of the batter (left or right expected)

        :return ballpark factor for Home Run per batter hand, which is a multiplier.

        equations used in:
            batter_points_expected_for_hr
        """
        if hand.lower()=='left':
            return self.stats[team]['hr_lhb']
        elif hand.lower()=='right':
            return self.stats[team]['hr_rhb']
        else:
            return None

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

    def printStats(self):
        print json.dumps(self.stats, indent=4)
