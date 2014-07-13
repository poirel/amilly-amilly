"""
Class: StatEquations
Author: Poirel & Jett
Date: 12 July 2014

This class computes the following stats:

    pitcher_points_expected_for_k
    pitcher_expected_ip
    pitcher_points_expected_for_win
    pitcher_points_expected_for_er
    batter_points_expected_for_hits
    batter_points_expected_for_walks
    batter_points_expected_for_hr
    batter_points_expected_for_sb
    batter_points_expected_for_runs
    batter_points_expected_for_rbi

Source of stats: internal classes
"""


class StatEquations:

    def __init__(self, player_stats, team_stats, ballpark_stats, league_stats):
        #TODO: removed daily_stats from params -- class is messed up and var is never used
        self.player_stats = player_stats
        ''':type: PlayerStats'''
        self.ballpark_stats = ballpark_stats
        ''':type: BallparkStats'''
        self.team_stats = team_stats
        ''':type: TeamStats'''
        self.league_stats = league_stats
        ''':type: LeagueStats'''
        #self.daily_stats = daily_stats
        #''':type: DailyStats'''

        self.year = 2014

    ############
    # PITCHERS #
    ############

    def pitcher_points_expected_for_k(self, pitcher):
        """
        Function: pitcher_points_expected_for_k
        -----------------
        Equation to determine the total number of points expected for a pitcher's total k's

        Parameters
            :param pitcher: the pitcher whose points we are trying to determine

        Formula Factors
            - k_per_ip: total_k / ip
            - expected_ip: total_ip / total_games_started

        Formula Multipliers
            - opp_team_k_percent_mult: [(team_k_vs_RHP_LHP) / (team_pa_vs_RHP_LHP)] / [league_k_percentage]

        :return (k_per_ip) * (expected_ip) * (opp_team_k_percent_mult)
        """

       #Helper variables
        pitcherTeam = self.player_stats.get_player_team(pitcher)
        pitcherPitchHand = self.player_stats.get_player_throwing_hand(pitcher)
        oppTeam = self.team_stats.get_team_opponent(pitcherTeam)

       #Equations
        k_per_ip = 1.0 * (self.player_stats.get_pitcher_total_k(self.year, pitcher) /
                          (self.player_stats.get_pitcher_total_innings_pitched(self.year, pitcher)))

        opp_team_k_percent_mult = 1.0 * ((self.team_stats.get_team_k_vs_RHP_LHP(self.year, oppTeam, pitcherPitchHand) /
                            self.team_stats.get_team_pa_vs_RHP_LHP(self.year, oppTeam, pitcherPitchHand)) /
                           self.league_stats.get_league_k_percentage(self.year))

        return k_per_ip * self.pitcher_expected_ip(pitcher) * opp_team_k_percent_mult

    def pitcher_expected_ip(self, pitcher):
        """
        Function: pitcher_expected_ip
        -----------------
        Equation to determine the total number of points expected for a pitcher's total ip

        Parameters
            :param pitcher: the pitcher whose points we are trying to determine

        Formula Factors
            - expected_ip: total_ip / total_games_started

        Formula Multipliers
            - none

        :return expected_ip
        """
        return 1.0 * (self.player_stats.get_pitcher_total_innings_pitched(self.year, pitcher) /
                      self.player_stats.get_pitcher_total_games_started(self.year, pitcher))

    def pitcher_points_expected_for_win(self, pitcher):
        # TODO: need vegas lines
        return 2

    def pitcher_points_expected_for_er(self, pitcher):
        """
        Function: pitcher_points_expected_for_er
        -----------------
        Equation to determine the total number of points expected for a pitcher's total er allowed.
        This equation should return negative values

        Parameters
            :param pitcher: the pitcher whose points we are trying to determine

        Formula Factors
            - xfip: value normalized to ERA
            - expected_ip: total_ip / total_games_started

        Formula Multipliers
            - park_factor: factor from rotowire
            - pitcher_hand_hits_mult: team_woba_vs_RHP_LHP / league_woba

        :return -1.0 * xfip * ballpark_mult * pitcher_hand_hits_mult * (self.pitcher_expected_ip(player)/9)
        """

        #Helper variables
        pitcher_team = self.player_stats.get_player_team(pitcher)
        opp_team = self.team_stats.get_team_opponent(pitcher_team)
        pitcher_loc = self.team_stats.get_team_home_or_away(pitcher_team)
        pitcher_hand = self.player_stats.get_player_throwing_hand(pitcher)
        if pitcher_loc == 'home':
            park_team = pitcher_team
        else:
            park_team = opp_team

        #Variables
        xfip = self.player_stats.get_pitcher_xfip_allowed(self.year, pitcher, pitcher_loc)

        park_factor = self.ballpark_stats.get_ballpark_factor_overall(park_team)

        pitcher_hand_hits_mult = 1.0 * self.team_stats.get_team_woba_vs_RHP_LHP(self.year, opp_team, pitcher_hand) / \
                            self.league_stats.get_league_woba(self.year)

        return -1.0 * xfip * park_factor * pitcher_hand_hits_mult * (self.pitcher_expected_ip(pitcher) / 9)

    ###########
    # BATTERS #
    ###########

    def batter_points_expected_for_hits(self, batter):
        """
        Function: batter_points_expected_for_hits
        -----------------
        Equation to determine the total number of points expected for a batter's hits (excluding hrs).

        Parameters
            :param batter: the batter whose points we are trying to determine

        Formula Factors
            - adj_slg: proprietary formula for determining hits
            - exp_ab: ab / g

        Formula Multipliers
            - pitcher_eff: pitcher wOBA vs RHB/LHB / league wOBA
            - batter_eff: batter wOBA vs RHB/LHB / league wOBA
            - park_factor: rotowire factor for batting average

        :return adj_slg * exp_ab * pitcher_eff * batter_eff * park_factor
        """

        #Helper Variables
        batter_outs = (self.player_stats.get_batter_ab_total(self.year, batter) -
                       self.player_stats.get_batter_hits_total(self.year, batter))
        batter_team = self.player_stats.get_player_team(batter)
        batter_hand = self.player_stats.get_player_batting_hand(batter)
        opp_team = self.team_stats.get_team_opponent(batter_team)
        opp_pitcher = self.player_stats.get_starting_pitcher(opp_team)
        opp_pitcher_woba = self.player_stats.get_pitcher_woba_allowed_vs_RHB_LHB(self.year, opp_pitcher, batter_hand)
        opp_pitcher_hand = self.player_stats.get_player_throwing_hand(opp_pitcher)
        if self.team_stats.get_team_home_or_away(batter_team) == 'home':
            park = batter_team
        else:
            park = opp_team

        #Equations
        adj_slg = (1.0 * self.player_stats.get_batter_1b_total(self.year, batter) +
                   2.0 * self.player_stats.get_batter_2b_total(self.year, batter) +
                   3.0 * self.player_stats.get_batter_3b_total(self.year, batter) -
                   0.25 * (batter_outs)) / \
                  (self.player_stats.get_batter_ab_total(self.year, batter) -
                   self.player_stats.get_batter_hr_total(self.year, batter))

        #TODO: expected at bats should come from a batter's lineup position
        exp_ab = 1.0 * self.player_stats.get_batter_ab_total(self.year, batter) / \
                 self.player_stats.get_batter_games_played_total(self.year, batter)

        pitcher_eff = 1.0 * opp_pitcher_woba / self.league_stats.get_league_woba(self.year)

        batter_eff = 1.0 * self.player_stats.get_batter_woba_vs_RHP_LHP(self.year, batter, opp_pitcher_hand) / \
                         self.league_stats.get_league_woba(self.year)

        park_factor = self.ballpark_stats.get_ballpark_factor_batting_average(park, batter_hand)

        return adj_slg * exp_ab * pitcher_eff * batter_eff * park_factor

    def batter_points_expected_for_walks(self, batter):
        """
        Function: batter_points_expected_for_walks
        -----------------
        Equation to determine the total number of points expected for a batter's hits (excluding hrs).

        Parameters
            :param batter: the batter whose points we are trying to determine

        Formula Factors
            - batter_walk_percentage: batter_bb_percent_total
            - exp pa: pa / g

        Formula Multipliers
            - pitcher_eff: pitcher_bb_perc / league_bb_perc

        :return batter_walk_percentage * exp_pa * pitcher_eff
        """

        #Helper Variables
        batter_team = self.player_stats.get_player_team(batter)
        batter_hand = self.player_stats.get_player_batting_hand(batter)
        opp_team = self.team_stats.get_team_opponent(batter_team)
        opp_pitcher = self.player_stats.get_starting_pitcher(opp_team)
        pitcher_bb_perc = 1.0 * self.player_stats.get_pitcher_bb_allowed_vs_RHB_LHB(self.year, opp_pitcher, batter_hand) /\
                          self.player_stats.get_pitcher_total_batters_faced_vs_RHB_LHB(self.year, opp_pitcher, batter_hand)
        league_bb_perc = 1.0 * self.league_stats.get_league_bb(self.year) /\
                         self.league_stats.get_league_plate_appearance(self.year)

        #Equations
        #TODO: expected at bats should come from a batter's lineup position...but this is PA
        exp_pa = 1.0 * self.player_stats.get_batter_pa_total(self.year, batter) /\
                 self.player_stats.get_batter_games_played_total(self.year, batter)

        batter_walk_percentage = self.player_stats.get_batter_bb_percent_total(self.year, batter)

        pitcher_eff = pitcher_bb_perc / league_bb_perc

        return batter_walk_percentage * exp_pa * pitcher_eff

    def batter_points_expected_for_hr(self, batter):
        """
        Function: batter_points_expected_for_hrs
        -----------------
        Equation to determine the total number of points expected for a batter's hrs.

        Parameters
            :param batter: the batter whose points we are trying to determine

        Formula Factors
            - batter_hr_percentage: hr / pa
            - exp_ab: ab / g

        Formula Multipliers
            - pitcher_eff: pitcher hr % bs RHB/LHB / league hr percent
            - batter_eff: hr % vs RHP/LHP / league hr percent
            - park_factor: rotowire facotr for HRs

        :return 4.0 * batter_hr_percentage * exp_pa * pitcher_eff * batter_eff * park_factor
        """

        #Helper Variables
        batter_team = self.player_stats.get_player_team(batter)
        batter_hand = self.player_stats.get_player_batting_hand(batter)
        opp_team = self.team_stats.get_team_opponent(batter_team)
        opp_pitcher = self.player_stats.get_starting_pitcher(opp_team)
        opp_pitcher_hr_percentage = 1.0 * self.player_stats.get_pitcher_hr_allowed_vs_RHB_LHB(self.year, opp_pitcher, batter_hand) /\
                                    self.player_stats.get_pitcher_total_batters_faced_vs_RHB_LHB(self.year, opp_pitcher, batter_hand)
        league_hr_percentage = 1.0 * self.league_stats.get_league_homerun(self.year) /\
                                   self.league_stats.get_league_plate_appearance(self.year)
        opp_pitcher_hand = self.player_stats.get_player_throwing_hand(opp_pitcher)
        batter_hr_vs_hand_percentage = self.player_stats.get_batter_hr_vs_RHP_LHP(self.year, batter, opp_pitcher_hand) /\
                                       self.player_stats.get_batter_plate_appearances_vs_RHP_LHP(self.year, batter, opp_pitcher_hand)
        if self.team_stats.get_team_home_or_away(batter_team) == 'home':
            park = batter_team
        else:
            park = opp_team

        #Equations
        batter_hr_percentage = 1.0 * self.player_stats.get_batter_hr_total(self.year, batter) /\
                               self.player_stats.get_batter_ab_total(self.year, batter)
        
        #TODO: expected at bats should come from a batter's lineup position
        exp_ab = 1.0 * self.player_stats.get_batter_ab_total(self.year, batter) /\
                 self.player_stats.get_batter_games_played_total(self.year, batter)

        pitcher_eff = opp_pitcher_hr_percentage / league_hr_percentage

        batter_eff = batter_hr_vs_hand_percentage / league_hr_percentage

        park_factor = self.ballpark_stats.get_ballpark_factor_homerun(park, batter_hand)

        #TODO: Do we want the 'batter_hr_percentage' to be vs RHP/LHP since we have a batter_eff multiplier?
        return 4.0 * batter_hr_percentage * exp_ab * pitcher_eff * batter_eff * park_factor

    def batter_points_expected_for_sb(self, batter):
        """
        Function: batter_points_expected_for_sbs
        -----------------
        Equation to determine the total number of points expected for a batter's sb.

        Parameters
            :param batter: the batter whose points we are trying to determine

        Formula Factors
            - sb per game = sb / g

        Formula Multipliers
            - team_eff: team sb % allowed / league sb % allowed

        :return 2.0 * batter_sb_per_game * team_eff
        """
        
        #Helper Variables
        batter_team = self.player_stats.get_player_team(batter)
        opp_team = self.team_stats.get_team_opponent(batter_team)
        team_sb_allowed_percentage = 1.0 * self.team_stats.get_team_sb_allowed(self.year, opp_team) /\
                             (self.team_stats.get_team_sb_allowed(self.year, opp_team) + self.team_stats.get_team_cs_fielding(self.year, opp_team))
        league_sb_allowed_percentage =  1.0 * self.league_stats.get_league_stolen_bases(self.year) /\
                                (self.league_stats.get_league_stolen_bases(self.year) + self.league_stats.get_league_caught_stealing(self.year))
        
        #Equations
        batter_sb_per_game = 1.0 * self.player_stats.get_batter_sb_total(self.year, batter) /\
                             self.player_stats.get_batter_games_played_total(self.year, batter)

        team_eff = team_sb_allowed_percentage / league_sb_allowed_percentage

        return 2.0 * batter_sb_per_game * team_eff

    def batter_points_expected_for_runs(self, batter):
        """
        Function: batter_points_expected_for_runs
        -----------------
        Equation to determine the total number of points expected for a batter's runs.

        Parameters
            :param batter: the batter whose points we are trying to determine

        Formula Factors
            - batter_runs_per_pa: proprietary formula
            - exp_pa: pa / g

        Formula Multipliers
            - pitcher_eff: pitcher wOBA vs RHB/LHB / league wOBA
            - batter_eff: batter wOBA vs RHP/LHP / league wOBA
            - park_factor: rotowire factor overall
            - team factor: team total runs / league avg total runs
            - batting order factor: proprietary formula

        :return batter_runs_per_pa * exp_pa * pitcher_eff * batter_eff * park_factor * batting_order_factor * team_factor
        """
        
        #Helper Variables
        batter_team = self.player_stats.get_player_team(batter)
        batter_hand = self.player_stats.get_player_batting_hand(batter)
        opp_team = self.team_stats.get_team_opponent(batter_team)
        opp_pitcher = self.player_stats.get_starting_pitcher(opp_team)
        opp_pitcher_woba = self.player_stats.get_pitcher_woba_allowed_vs_RHB_LHB(self.year, opp_pitcher, batter_hand)
        opp_pitcher_hand = self.player_stats.get_player_throwing_hand(opp_pitcher)
        if self.team_stats.get_team_home_or_away(batter_team) == 'home':
            park = batter_team
        else:
            park = opp_team
        
        #Equations
        batter_runs_per_pa = 0.330 * self.player_stats.get_batter_ba_total(self.year, batter) + \
                             0.187 * self.player_stats.get_batter_bb_percent_total(self.year, batter) + \
                             0.560 * (self.player_stats.get_batter_hr_total(self.year, batter) /\
                             self.player_stats.get_batter_pa_total(self.year, batter))

        exp_pa = 1.0 * self.player_stats.get_batter_pa_total(self.year, batter) /\
                 self.player_stats.get_batter_games_played_total(self.year, batter)
        
        pitcher_eff = 1.0 * opp_pitcher_woba / self.league_stats.get_league_woba(self.year)

        batter_eff = 1.0 * self.player_stats.get_batter_woba_vs_RHP_LHP(self.year, batter, opp_pitcher_hand) /\
                     self.league_stats.get_league_woba(self.year)

        park_factor = self.ballpark_stats.get_ballpark_factor_overall(park)

        # TODO: get batting order for runs
        batting_order_factor = 1.0

        team_factor = self.team_stats.get_team_runs_total(self.year, batter_team) /\
                      (self.league_stats.get_league_runs(self.year) / 30.0)

        return batter_runs_per_pa * exp_pa * pitcher_eff * batter_eff * park_factor * batting_order_factor * team_factor

    def batter_points_expected_for_rbi(self, batter):
        """
        Function: batter_points_expected_for_rbi
        -----------------
        Equation to determine the total number of points expected for a batter's rbis.

        Parameters
            :param batter: the batter whose points we are trying to determine

        Formula Factors
            - batter_runs_per_pa: proprietary formula
            - exp_pa: pa / g

        Formula Multipliers
            - pitcher_eff: pitcher wOBA vs RHB/LHB / league wOBA
            - batter_eff: batter wOBA vs RHP/LHP / league wOBA
            - park_factor: rotowire factor overall
            - team factor: team total runs / league avg total runs
            - batting order factor: proprietary formula

        :return batter_runs_per_pa * exp_pa * pitcher_eff * batter_eff * park_factor * batting_order_factor * team_factor
        """
        
        #Helper Variables
        batter_team = self.player_stats.get_player_team(batter)
        batter_hand = self.player_stats.get_player_batting_hand(batter)
        opp_team = self.team_stats.get_team_opponent(batter_team)
        opp_pitcher = self.player_stats.get_starting_pitcher(opp_team)
        opp_pitcher_woba = self.player_stats.get_pitcher_woba_allowed_vs_RHB_LHB(self.year, opp_pitcher, batter_hand)
        opp_pitcher_hand = self.player_stats.get_player_throwing_hand(opp_pitcher)
        if self.team_stats.get_team_home_or_away(batter_team) == 'home':
            park = batter_team
        else:
            park = opp_team
        
        #Equations
        batter_runs_per_pa = 0.330 * self.player_stats.get_batter_ba_total(self.year, batter) + \
                             0.187 * self.player_stats.get_batter_bb_percent_total(self.year, batter) + \
                             0.560 * (self.player_stats.get_batter_hr_total(self.year, batter) /\
                             self.player_stats.get_batter_pa_total(self.year, batter))

        exp_pa = 1.0 * self.player_stats.get_batter_pa_total(self.year, batter) /\
                 self.player_stats.get_batter_games_played_total(self.year, batter)
        
        pitcher_eff = 1.0 * opp_pitcher_woba / self.league_stats.get_league_woba(self.year)

        batter_eff = 1.0 * self.player_stats.get_batter_woba_vs_RHP_LHP(self.year, batter, opp_pitcher_hand) /\
                     self.league_stats.get_league_woba(self.year)

        park_factor = self.ballpark_stats.get_ballpark_factor_overall(park)

        # TODO: get batting order for runs
        batting_order_factor = 1.0

        team_factor = self.team_stats.get_team_runs_total(self.year, batter_team) /\
                      (self.league_stats.get_league_runs(self.year) / 30.0)

        return batter_runs_per_pa * exp_pa * pitcher_eff * batter_eff * park_factor * batting_order_factor * team_factor

    ###########
    # Overall #
    ###########

    def get_score(self, player):
        position = self.player_stats.get_player_fielding_position(player)
        if position == 'P':
            return self.pitcher_expected_ip(player) + \
                   self.pitcher_points_expected_for_er(player) + \
                   self.pitcher_points_expected_for_k(player) + \
                   self.pitcher_points_expected_for_win(player)
        else:
            return self.batter_points_expected_for_runs(player) + \
                   self.batter_points_expected_for_hits(player) + \
                   self.batter_points_expected_for_rbi(player) + \
                   self.batter_points_expected_for_hr(player) + \
                   self.batter_points_expected_for_sb(player) + \
                   self.batter_points_expected_for_walks(player)
