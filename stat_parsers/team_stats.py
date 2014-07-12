"""
Class: TeamStats
Author: Poirel & Jett
Date: 6 July 2014

This class reads in Team Stats from the following file:
    - /Stats/Team/(YEAR) Team Stats.csv
    - /Stats/Team/(YEAR) Team Stats vs (RHP/LHP).csv
    - /Stats/Team/(YEAR) Team Fielding Stats.csv
    - (statsDir from _init_)/Daily/(DATE)-fanduel-salaries.csv

The following stats are available:
    - Total Runs
    - SO vs RHP/LHP
    - PA vs RHP/LHP
    - wOBA vs RHP/LHP
    - SB Allowed
    - Total CS
    - Home or Away
    - Opponent

Source of stats: FanGraphs & FanDuel
"""

from collections import defaultdict
import csv
import json

TEAM_NAMES = {
    'COL': {'mascot': 'Rockies',
            'location': 'Colorado',
            'league': 'NL'},
    'TOR': {'mascot': 'Blue Jays',
            'location': 'Toronto',
            'league': 'AL'},
    'DET': {'mascot': 'Tigers',
            'location': 'Detroit',
            'league': 'AL'},
    'OAK': {'mascot': 'Athletics',
            'location': 'Oakland',
            'league': 'AL'},
    'MIA': {'mascot': 'Marlins',
            'location': 'Miami',
            'league': 'NL'},
    'LAA': {'mascot': 'Angels',
            'location': 'Los Angeles',
            'league': 'AL'},
    'LOS': {'mascot': 'Dodgers',
            'location': 'Los Angeles',
            'league': 'NL'},
    'CWS': {'mascot': 'White Sox',
            'location': 'Chicago',
            'league': 'AL'},
    'CLE': {'mascot': 'Indians',
            'location': 'Cleveland',
            'league': 'AL'},
    'TEX': {'mascot': 'Rangers',
            'location': 'Texas',
            'league': 'AL'},
    'BAL': {'mascot': 'Orioles',
            'location': 'Baltimore',
            'league': 'AL'},
    'MIL': {'mascot': 'Brewers',
            'location': 'Milwaukee',
            'league': 'NL'},
    'NYY': {'mascot': 'Yankees',
            'location': 'New York',
            'league': 'AL'},
    'SFG': {'mascot': 'Giants',
            'location': 'San Francisco',
            'league': 'NL'},
    'PIT': {'mascot': 'Pirates',
            'location': 'Pittsburgh',
            'league': 'NL'},
    'BOS': {'mascot': 'Red Sox',
            'location': 'Boston',
            'league': 'AL'},
    'MIN': {'mascot': 'Twins',
            'location': 'Minnesota',
            'league': 'AL'},
    'HOU': {'mascot': 'Astros',
            'location': 'Houston',
            'league': 'AL'},
    'TAM': {'mascot': 'Rays',
            'location': 'Tampa Bay',
            'league': 'AL'},
    'STL': {'mascot': 'Cardinals',
            'location': 'St Louis',
            'league': 'NL'},
    'WAS': {'mascot': 'Nationals',
            'location': 'Washington',
            'league': 'NL'},
    'PHI': {'mascot': 'Phillies',
            'location': 'Philadelphia',
            'league': 'NL'},
    'ARI': {'mascot': 'Diamondbacks',
            'location': 'Arizona',
            'league': 'NL'},
    'ATL': {'mascot': 'Braves',
            'location': 'Atlanta',
            'league': 'NL'},
    'CIN': {'mascot': 'Reds',
            'location': 'Cincinnati',
            'league': 'NL'},
    'NYM': {'mascot': 'Mets',
            'location': 'New York',
            'league': 'NL'},
    'CHC': {'mascot': 'Cubs',
            'location': 'Chicago',
            'league': 'NL'},
    'SEA': {'mascot': 'Mariners',
            'location': 'Seattle',
            'league': 'AL'},
    'KAN': {'mascot': 'Royals',
            'location': 'Kansas City',
            'league': 'AL'},
    'SDP': {'mascot': 'Padres',
            'location': 'San Diego',
            'league': 'NL'}
}

def get_teams():
    """
    Function: get_teams
    -----------------
    Helper method for the TEAM_NAMES array(not an array?)

    Parameters:
        :param none

    :return The TEAM_NAMES array above

    equations used in:
        none...
    """
    return TEAM_NAMES.keys()

def get_team_by_mascot(mascot):
    """
    Function: get_team_by_mascot
    -----------------
    Helper method for get a team (ie BAL, ATL) from TEAM_NAMES by its mascot (ie Orioles, Braves, etc)

    Parameters:
        :param mascot: team's mascot (Orioles, Braves, etc)

    :return team 2 or 3 letter name (ie BAL, ATL, etc)

    equations used in:
        read_team_stats_total
        read_team_stats_vs_RHP_LHP
        read_team_stats_fielding
    """
    for k,v in TEAM_NAMES.items():
        if v['mascot'].lower()==mascot.lower():
            return k
    return None

def get_team_by_location(location):
    """
    Function: get_team_by_location
    -----------------
    Helper method for get a team (ie BAL, ATL) from TEAM_NAMES by its location (ie Baltimore, Atlanta, etc)

    Parameters:
        :param location: team's location (Baltimore, Atlanta, etc)

    :return team 2 or 3 letter name (ie BAL, ATL, etc)

    equations used in:
        not used...
    """
    for k,v in TEAM_NAMES.items():
        if v['location'].lower()==location.lower():
            return k
    return None

def get_team_mascot(team):
    """
    Function: get_team_mascot
    -----------------
    Helper method for get a team's (ie BAL, ATL) mascot (ie Orioles, Braves, etc)

    Parameters:
        :param team: team 2 or 3 letter name (ie BAL, ATL, etc)

    :return team mascot (ie Orioles, Braves, etc)

    equations used in:
        read_rosters (from player_stats.py)
    """
    return TEAM_NAMES[team]['mascot']

def get_team_location(team):
    """
    Function: get_team_location
    -----------------
    Helper method for get a team's (ie BAL, ATL) location (ie Baltimore, Atlanta, etc)

    Parameters:
        :param team: team 2 or 3 letter name (ie BAL, ATL, etc)

    :return team location (ie Baltimore, Atlanta, etc)

    equations used in:
        read_rosters (from player_stats.py)
    """
    return TEAM_NAMES[team]['location']

def get_team_league(team):
    """
    Function: get_team_league
    -----------------
    Helper method for get a team's (ie BAL, ATL) league (AL or NL)

    Parameters:
        :param team: team 2 or 3 letter name (ie BAL, ATL, etc)

    :return team league (AL or NL)

    equations used in:
        not used..
    """
    return TEAM_NAMES[team]['league']

class TeamStats:

    def __init__(self, statsDir):
        """
        Function: _init_
        -----------------

        This is the initial function. It takes in the stats directory as a parameter,
        and calls the 'read_*' function.

        Parameters:
            :param statsDir: Directory in Dropbox with all Stats. Should always be:
                        /Dropbox/MDI Fantasy Sports/Stats

        :return nothing
        """
        self.statsDir = statsDir.rstrip('/')
        self.stats = defaultdict(lambda: defaultdict( lambda: defaultdict( lambda: defaultdict (dict))))

        self.read_team_stats_total()
        self.read_team_stats_vs_RHP_LHP()
        self.read_daily_matchups()
        self.read_team_fielding_stats()

        # self.printStats()


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

    def read_team_stats_total(self):
        """
        Function: read_team_stats_total
        -----------------
        Reads team stats from the following directory:

            (statsDir from _init_)/Team/(YEAR)Team Stats.csv

        Parameters:
            :param none

        :return nothing
        """
        years = [2013, 2014]
        for year in years:
            infile = '%s/Team/%d Team Stats.csv' %(self.statsDir, year)
            reader = csv.reader(open(infile), quotechar='"')
            header = reader.next()
            for items in reader:
                team = get_team_by_mascot(items[0])
                self.stats[team][year]['runs_team'] = float(items[1])

    def get_team_runs_total(self, year, team):
        """
        Function: get_team_stats_runs_total
        -----------------
        Helper method for the total runs for a specified team

        Parameters:
            :param year: the year of the team stats, also corresponds with file name
            :param team: the team whose stats we are looking for

        :return total team runs

        equations used in:
           batter_points_expected_for_runs
           batter_points_expected_for_rbi
        """
        return self.stats[team][year]['runs_team']

    def read_team_stats_vs_RHP_LHP(self):
        """
        Function: read_team_stats_vs_RHP_LHP
        -----------------
        Reads team stats from the following directory:

            (statsDir from _init_)/Team/(YEAR)Team Stats vs (RHP/LHP).csv

        Parameters:
            :param none

        :return nothing
        """
        stats = ['so', 'pa', 'woba']
        years = [2013, 2014]
        for year in years:
            for hand in ['RHP', 'LHP']:
                infile = '%s/Team/%d Team Stats vs %s.csv' %(self.statsDir, year, hand)
                reader = csv.reader(open(infile), quotechar='"')
                header = reader.next()
                for items in reader:
                    team = get_team_by_mascot(items[0])
                    for i, stat_val in enumerate([float(x) for x in items[1:4]]):
                        self.stats[team][year][stats[i]][hand] = stat_val

    def get_team_k_vs_RHP_LHP(self, year, team, hand):
        """
        Function: get_team_k_vs_RHP_LHP
        -----------------
        Helper method for the strikeouts (K) for a specified team vs RHP/LHP

        Parameters:
            :param year: the year of the team stats, also corresponds with file name
            :param team: the team whose stats we are looking for
            :param hand: handedness (RHP/LHP) of the opposing pitcher

        :return team runs split vs RHP/LHP

        equations used in:
           pitcher_points_expected_for_k
        """
        if hand.lower()=='left':
            return self.stats[team][year]['so']['LHP']
        elif hand.lower()=='right':
            return self.stats[team][year]['so']['RHP']
        else:
            return None

    def get_team_pa_vs_RHP_LHP(self, year, team, hand):
        """
        Function: get_team_pa_vs_RHP_LHP
        -----------------
        Helper method for the plate appearances (PA) for a specified team vs RHP/LHP

        NOTE: PA = AB + BB

        Parameters:
            :param year: the year of the team stats, also corresponds with file name
            :param team: the team whose stats we are looking for
            :param hand: handedness (RHP/LHP) of the opposing pitcher

        :return team plate appearances split vs RHP/LHP

        equations used in:
           pitcher_points_expected_for_k
        """
        if hand.lower()=='left':
            return self.stats[team][year]['pa']['LHP']
        elif hand.lower()=='right':
            return self.stats[team][year]['pa']['RHP']
        else:
            return None

    def get_team_woba_vs_RHP_LHP(self, year, team, hand):
        """
        Function: get_team_woba_vs_RHP_LHP
        -----------------
        Helper method for the weighted on base average (wOBA) for a specified team vs RHP/LHP

        Parameters:
            :param year: the year of the team stats, also corresponds with file name
            :param team: the team whose stats we are looking for
            :param hand: handedness (RHP/LHP) of the opposing pitcher

        :return team wOBA split vs RHP/LHP

        equations used in:
           pitcher_points_expected_for_er
        """
        if hand.lower()=='left':
            return self.stats[team][year]['woba']['LHP']
        elif hand.lower()=='right':
            return self.stats[team][year]['woba']['RHP']
        else:
            return None

    def read_daily_matchups(self):
        # TODO: hard-coded daily stats
        # TODO: need to get from the same fanduel stats we get in player_stats.read_fanduel_positions_and_salaries
        """
        Function: read_daily_matchups
        -----------------
        Reads hard coded daily matchup info from the following directory:

            hard coded: (statsDir from _init_)/Test Data/Salaries/...
            Should be: (statsDir from _init_)/Daily/(DATE)-fanduel-salaries.csv

        Parameters:
            :param none

        :return nothing
        """
        infile = '%s/Test Data/Salaries/Fanduel- 6.3.2014 Salaries.csv' %(self.statsDir)
        reader = csv.reader(open(infile), quotechar='"')
        for items in reader:
            away, home = items[4].split('@')
            self.stats[home]['home_or_away'] = 'home'
            self.stats[away]['home_or_away'] = 'away'
            self.stats[home]['opponent'] = away
            self.stats[away]['opponent'] = home

    def get_team_home_or_away(self, team):
        """
        Function: get_team_home_or_away
        -----------------
        Helper method for whether a team is Home or Away

        Parameters:
            :param team: the team whose Home/Away info we are looking for

        :return home or away for a specific team

        equations used in:
           pitcher_points_expected_for_er
           batter_points_expected_for_hits
           batter_points_expected_for_hr
           batter_points_expected_for_runs
           batter_points_expected_for_rbi
        """
        return self.stats[team]['home_or_away']

    def get_team_opponent(self, team):
        """
        Function: get_team_opponent
        -----------------
        Helper method for getting a team's opponent

        Parameters:
            :param team: the team whose opponent we are looking for

        :return team's opponent

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
        return self.stats[team]['opponent']


    def read_team_fielding_stats(self):
        """
        Function: read_team_fielding_stats
        -----------------
        Reads team fielding stats from the following file:

            (statsDir from _init_)/Team/(YEAR) Team Fielding Stats.csv

        Parameters:
            :param none

        :return nothing
        """
        years = [2013, 2014]
        for year in years:
            infile = '%s/Team/%d Team Fielding Stats.csv' %(self.statsDir, year)
            reader = csv.reader(open(infile), quotechar='"')
            header = reader.next()
            for items in reader:
                team = get_team_by_mascot(items[0])
                self.stats[team][year]['sb_allowed'] = float(items[1])
                self.stats[team][year]['cs_fielding'] = float(items[2])

    def get_team_sb_allowed(self, year, team):
        """
        Function: get_team_sb_allowed
        -----------------
        Helper method for getting a team's total SB allowed

        Parameters:
            :param team: the team whose stats we are looking for
            :param year: the year of the team stats, also corresponds with file name

        :return total SB's allowed by the team for a given year

        equations used in:
            batter_points_expected_for_sb
        """
        return self.stats[team][year]['sb_allowed']

    def get_team_cs_fielding(self, year, team):
        """
        Function: get_team_cs_allowed
        -----------------
        Helper method for getting a team's total player's their catcher caught stealing

        Parameters:
            :param team: the team whose stats we are looking for
            :param year: the year of the team stats, also corresponds with file name

        :return total player's caught stealing by the team for a given year

        equations used in:
            batter_points_expected_for_sb
        """
        return self.stats[team][year]['cs_fielding']
