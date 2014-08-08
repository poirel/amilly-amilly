"""
Class: StatEquations
Author: Stadium Grinders
Date: 27 July 2014

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
RUN_MULTIPLIER = [0, 1.164, 1.122, 0.979, 0.946, 0.971, 0.921, 0.899, 0.927, 0.973]
RBI_MULTIPLIER = [0, 0.726, 0.839, 1.017, 1.114, 1.038, 0.985, 0.954, 0.904, 0.879]
EXPECTED_PA = [0, 4.67, 4.56, 4.46, 4.35, 4.25, 4.14, 4.03, 3.91, 3.79]

class StatEquations:


    def __init__(self, player_stats, team_stats, ballpark_stats, league_stats):
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
        Equation to determine the total number of points expected for a pitcher's total k's.
        Right now, this will only compute for pitchers with > 0 games started.

        Parameters
            :param pitcher: the pitcher whose points we are trying to determine

        Formula Factors
            - k_per_ip: total_k / ip
            - expected_ip: total_ip / total_games_started

        Formula Multipliers
            - opp_team_k_percent_mult: [(team_k_vs_RHP_LHP) / (team_pa_vs_RHP_LHP)] / [league_k_percentage]

        :return (k_per_ip) * (expected_ip) * (opp_team_k_percent_mult)
        """

        #Initializing Equation
        k_per_ip = 0
        expected_ip = 0
        opp_team_k_percent_mult = 0

        #Only compute for pitchers with > 0 games started
        if self.player_stats.get_pitcher_total_games_started(self.year,pitcher) > 0:
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
            expected_ip = self.pitcher_expected_ip(pitcher)

        return k_per_ip * expected_ip * opp_team_k_percent_mult

    def pitcher_expected_ip(self, pitcher):
        """
        Function: pitcher_expected_ip
        -----------------
        Equation to determine the total number of points expected for a pitcher's total ip
        Right now, this will only compute for pitchers with > 0 games started.

        Parameters
            :param pitcher: the pitcher whose points we are trying to determine

        Formula Factors
            - expected_ip: total_ip / total_games_started
            or
            - expected_ip: total_ip / total_games_played

        Formula Multipliers
            - none

        :return expected_ip
        """
        #Initialize Equation
        expected_ip = 0

        #Only compute for pitchers with > 0 games started
        if self.player_stats.get_pitcher_total_games_started(self.year,pitcher) > 0:
            expected_ip = 1.0 * (self.player_stats.get_pitcher_total_innings_pitched(self.year, pitcher) /
                      self.player_stats.get_pitcher_total_games_started(self.year, pitcher))

        return expected_ip

    def pitcher_points_expected_for_win(self, pitcher):
        # TODO: need vegas lines
        return 2

    def pitcher_points_expected_for_er(self, pitcher):
        """
        Function: pitcher_points_expected_for_er
        -----------------
        Equation to determine the total number of points expected for a pitcher's total er allowed.
        This equation should return negative values
        Right now, this will only compute for pitchers with > 0 games started.

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

        #Initialize Equation
        xfip = 0
        park_factor = 0
        pitcher_hand_hits_mult = 0
        expected_ip = 0

        #Only compute for pitchers with > 0 games started
        if self.player_stats.get_pitcher_total_games_started(self.year,pitcher) > 0:

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

            expected_ip = self.pitcher_expected_ip(pitcher)

        return -1.0 * xfip * expected_ip / 9 * ((park_factor + 2 * pitcher_hand_hits_mult) / 3)

    ###########
    # BATTERS #
    ###########

    def batter_expected_ab_per_game(self, batter):
        """
        Function: batter_expected_ab_per_game
        -----------------
        Equation to determine the expected ab per game for a player
        Will use ESPN averages for PA per player, then subtract a player's expected walks

        Parameters
            :param batter: the batter whose abs we are trying to determine

        Formula Factors
            - ex_pa: expected plate appearances for a batting order position
            - exp_bb: avg bb per game

        Formula Multipliers
            - pitcher_eff: pitcher wOBA vs RHB/LHB / league wOBA
            - batter_eff: batter wOBA vs RHB/LHB / league wOBA
            - park_factor: rotowire factor for batting average

        :return adj_slg * exp_ab * pitcher_eff * batter_eff * park_factor
        """
        ex_pa = EXPECTED_PA[self.player_stats.get_player_batting_position(batter)]
        ex_bb = self.player_stats.get_batter_bb_total(self.year,batter) / \
                self.player_stats.get_batter_games_played_total(self.year, batter)

        return ex_pa - ex_bb

    def batter_points_expected_for_hits(self, batter):
        """
        Function: batter_points_expected_for_hits
        -----------------
        Equation to determine the total number of points expected for a batter's hits (excluding hrs).
        Right now, this only computes for batters with > 0 at bats

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

        #Initialize Equation
        adj_slg = 0
        exp_ab = 0
        pitcher_eff = 0
        batter_eff = 0
        park_factor = 0

        #Only compute if batter has > 0 at bats
        if self.player_stats.get_batter_ab_total(self.year,batter) > 0:

            #Helper Variables
            batter_outs = (self.player_stats.get_batter_ab_total(self.year, batter) -
                           self.player_stats.get_batter_hits_total(self.year, batter))
            batter_team = self.player_stats.get_player_team(batter)
            batter_hand = self.player_stats.get_player_batting_hand(batter)
            opp_team = self.team_stats.get_team_opponent(batter_team)
            opp_pitcher = self.player_stats.get_starting_pitcher(opp_team)

            #Accounts for pitchers without stats by defaulting to league average and a RHP
            if self.player_stats.get_pitcher_total_innings_pitched(self.year, opp_pitcher) > 0:
                opp_pitcher_woba = self.player_stats.get_pitcher_woba_allowed_vs_RHB_LHB(self.year, opp_pitcher, batter_hand)
                opp_pitcher_hand = self.player_stats.get_player_throwing_hand(opp_pitcher)
            else:
                print 'Here in pts for hits for ', batter
                opp_pitcher_woba = self.league_stats.get_league_woba(self.year)
                opp_pitcher_hand = 'right'

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

            exp_ab = self.batter_expected_ab_per_game(batter)

            pitcher_eff = 1.0 * opp_pitcher_woba / self.league_stats.get_league_woba(self.year)

            batter_eff = 1.0 * self.player_stats.get_batter_woba_vs_RHP_LHP(self.year, batter, opp_pitcher_hand) / \
                             self.league_stats.get_league_woba(self.year)

            park_factor = self.ballpark_stats.get_ballpark_factor_batting_average(park, batter_hand)

        return adj_slg * exp_ab * ((1.5 * pitcher_eff + 1.5 * batter_eff + park_factor) / 4)

    def batter_points_expected_for_walks(self, batter):
        """
        Function: batter_points_expected_for_walks
        -----------------
        Equation to determine the total number of points expected for a batter's hits (excluding hrs).
        Right now, this only computes for batters with > 0 at bats

        Parameters
            :param batter: the batter whose points we are trying to determine

        Formula Factors
            - batter_walk_percentage: batter_bb_percent_total
            - exp pa: pa / g

        Formula Multipliers
            - pitcher_eff: pitcher_bb_perc / league_bb_perc

        :return batter_walk_percentage * exp_pa * pitcher_eff
        """

        #Initialize Equation
        batter_walk_percentage = 0
        exp_pa = 0
        pitcher_eff = 0

        #Only compute if batter has > 0 at bats
        if self.player_stats.get_batter_ab_total(self.year,batter) > 0:

            #Helper Variables
            batter_team = self.player_stats.get_player_team(batter)
            batter_hand = self.player_stats.get_player_batting_hand(batter)
            opp_team = self.team_stats.get_team_opponent(batter_team)
            opp_pitcher = self.player_stats.get_starting_pitcher(opp_team)
            league_bb_perc = 1.0 * self.league_stats.get_league_bb(self.year) /\
                     self.league_stats.get_league_plate_appearance(self.year)

            #Accounts for pitchers without stats by defaulting to league average
            if self.player_stats.get_pitcher_total_innings_pitched(self.year, opp_pitcher) > 0:
                pitcher_bb_perc = 1.0 * self.player_stats.get_pitcher_bb_allowed_vs_RHB_LHB(self.year, opp_pitcher, batter_hand) /\
                                  self.player_stats.get_pitcher_total_batters_faced_vs_RHB_LHB(self.year, opp_pitcher, batter_hand)
            else:
                print 'Here in pts for BBs for ', batter
                pitcher_bb_perc = league_bb_perc

            #Equations
            exp_pa = 1.0 * EXPECTED_PA[self.player_stats.get_player_batting_position(batter)]

            batter_walk_percentage = 1.0 * self.player_stats.get_batter_bb_percent_total(self.year, batter)

            pitcher_eff = 1.0 * pitcher_bb_perc / league_bb_perc

            batter_eff = 1.0 * batter_walk_percentage / league_bb_perc

        return batter_walk_percentage * exp_pa * ((pitcher_eff + batter_eff) / 2)

    def batter_points_expected_for_hr(self, batter):
        """
        Function: batter_points_expected_for_hrs
        -----------------
        Equation to determine the total number of points expected for a batter's hrs.
        Right now, this only computes for batters with > 0 at bats

        Parameters
            :param batter: the batter whose points we are trying to determine

        Formula Factors
            - batter_hr_percentage: hr / pa
            - exp_ab: ab / g

        Formula Multipliers
            - pitcher_eff: pitcher hr % bs RHB/LHB / league hr percent
            - batter_eff: hr % vs RHP/LHP / league hr percent
            - park_factor: rotowire factor for HRs

        :return 4.0 * batter_hr_percentage * exp_pa * pitcher_eff * batter_eff * park_factor
        """

        #Initialize Equation
        batter_hr_percentage = 0
        exp_ab = 0
        pitcher_eff = 0
        batter_eff = 0
        park_factor = 0

        #Only compute if batter has > 0 at bats
        if self.player_stats.get_batter_ab_total(self.year,batter) > 0:

            #Helper Variables
            batter_team = self.player_stats.get_player_team(batter)
            batter_hand = self.player_stats.get_player_batting_hand(batter)
            opp_team = self.team_stats.get_team_opponent(batter_team)
            opp_pitcher = self.player_stats.get_starting_pitcher(opp_team)
            league_hr_percentage = 1.0 * self.league_stats.get_league_homerun(self.year) /\
                                       self.league_stats.get_league_plate_appearance(self.year)

            #Accounts for pitchers without stats by defaulting to league average and RHP
            if self.player_stats.get_pitcher_total_innings_pitched(self.year, opp_pitcher) > 0:
                opp_pitcher_hr_percentage = 1.0 * self.player_stats.get_pitcher_hr_allowed_vs_RHB_LHB(self.year, opp_pitcher, batter_hand) /\
                                        self.player_stats.get_pitcher_total_batters_faced_vs_RHB_LHB(self.year, opp_pitcher, batter_hand)
                opp_pitcher_hand = self.player_stats.get_player_throwing_hand(opp_pitcher)
            else:
                print 'Here in pts for HRs for ', batter
                opp_pitcher_hr_percentage = league_hr_percentage
                opp_pitcher_hand = 'right'

            batter_hr_vs_hand_percentage = self.player_stats.get_batter_hr_vs_RHP_LHP(self.year, batter, opp_pitcher_hand) /\
                                           self.player_stats.get_batter_plate_appearances_vs_RHP_LHP(self.year, batter, opp_pitcher_hand)
            if self.team_stats.get_team_home_or_away(batter_team) == 'home':
                park = batter_team
            else:
                park = opp_team

            #Equations
            batter_hr_percentage = 1.0 * self.player_stats.get_batter_hr_total(self.year, batter) /\
                                   self.player_stats.get_batter_pa_total(self.year, batter)

            exp_pa = EXPECTED_PA[self.player_stats.get_player_batting_position(batter)]

            pitcher_eff = opp_pitcher_hr_percentage / league_hr_percentage

            batter_eff = batter_hr_vs_hand_percentage / league_hr_percentage

            park_factor = self.ballpark_stats.get_ballpark_factor_homerun(park, batter_hand)

        if pitcher_eff > 2:
            pitcher_eff = 2

        if batter_eff > 2:
            batter_eff = 2

        return 4.0 * batter_hr_percentage * exp_pa * ((1.5 * pitcher_eff + 1.5 * batter_eff + park_factor) / 4)

    def batter_points_expected_for_sb(self, batter):
        """
        Function: batter_points_expected_for_sbs
        -----------------
        Equation to determine the total number of points expected for a batter's sb.
        Right now, this only computes for batters with > 0 at bats

        Parameters
            :param batter: the batter whose points we are trying to determine

        Formula Factors
            - sb per game = sb / g

        Formula Multipliers
            - oppTeam_sb_allowed_eff: team sb % allowed / league sb % allowed
            - oppTeam_sb_attempts_allowed_eff: team sb attempt against / league avg

        :return 2.0 * batter_sb_per_game * team_eff
        """

        #Initialize Equation
        batter_sb_per_game = 0
        oppTeam_sb_allowed_eff = 0
        oppTeam_sb_attempts_allowed_eff = 0

        #Only compute if batter has > 0 at bats
        if self.player_stats.get_batter_ab_total(self.year,batter) > 0:

            #Helper Variables
            batter_team = self.player_stats.get_player_team(batter)
            opp_team = self.team_stats.get_team_opponent(batter_team)
            oppTeam_sb_allowed_percentage = 1.0 * self.team_stats.get_team_sb_allowed(self.year, opp_team) /\
                                 (self.team_stats.get_team_sb_allowed(self.year, opp_team) + self.team_stats.get_team_cs_fielding(self.year, opp_team))
            league_sb_allowed_percentage =  1.0 * self.league_stats.get_league_stolen_bases(self.year) /\
                                    (self.league_stats.get_league_stolen_bases(self.year) + self.league_stats.get_league_caught_stealing(self.year))
            oppTeam_sb_attempts_against = 1.0 * (self.team_stats.get_team_sb_allowed(self.year, opp_team) + self.team_stats.get_team_cs_fielding(self.year,opp_team))
            league_sb_attempts_against_avg = 1.0 * (self.league_stats.get_league_stolen_bases(self.year) + self.league_stats.get_league_caught_stealing(self.year)) / 30

            #Equations
            batter_sb_per_game = 1.0 * self.player_stats.get_batter_sb_total(self.year, batter) /\
                                 self.player_stats.get_batter_games_played_total(self.year, batter)

            oppTeam_sb_allowed_eff = oppTeam_sb_allowed_percentage / league_sb_allowed_percentage

            oppTeam_sb_attempts_allowed_eff = 1.0 * oppTeam_sb_attempts_against / league_sb_attempts_against_avg

        return 2.0 * batter_sb_per_game * ((oppTeam_sb_allowed_eff + oppTeam_sb_attempts_allowed_eff) / 2)

    def batter_points_expected_for_runs(self, batter):
        """
        Function: batter_points_expected_for_runs
        -----------------
        Equation to determine the total number of points expected for a batter's runs.
        Right now, this only computes for batters with > 0 at bats

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

        #Initialize Equation
        batter_runs_per_pa = 0
        exp_pa = 0
        pitcher_eff = 0
        batter_eff = 0
        park_factor = 0
        batting_order_factor = 0
        team_factor = 0

        #Only compute if batter has > 0 at bats
        if self.player_stats.get_batter_ab_total(self.year,batter) > 0:

            #Helper Variables
            batter_team = self.player_stats.get_player_team(batter)
            batter_hand = self.player_stats.get_player_batting_hand(batter)
            opp_team = self.team_stats.get_team_opponent(batter_team)
            opp_pitcher = self.player_stats.get_starting_pitcher(opp_team)

            #Accounts for pitchers without stats by defaulting to league average and RHP
            if self.player_stats.get_pitcher_total_innings_pitched(self.year, opp_pitcher) > 0:
                opp_pitcher_woba = self.player_stats.get_pitcher_woba_allowed_vs_RHB_LHB(self.year, opp_pitcher, batter_hand)
                opp_pitcher_hand = self.player_stats.get_player_throwing_hand(opp_pitcher)
            else:
                print 'Here in pts for runs for ', batter
                opp_pitcher_woba = self.league_stats.get_league_woba(self.year)
                opp_pitcher_hand = 'right'

            if self.team_stats.get_team_home_or_away(batter_team) == 'home':
                park = batter_team
            else:
                park = opp_team

            #Equations
            batter_runs_per_pa = 0.330 * self.player_stats.get_batter_ba_total(self.year, batter) + \
                                 0.187 * self.player_stats.get_batter_bb_percent_total(self.year, batter) + \
                                 0.560 * (self.player_stats.get_batter_hr_total(self.year, batter) /\
                                 self.player_stats.get_batter_pa_total(self.year, batter))

            exp_pa = 1.0 * EXPECTED_PA[self.player_stats.get_player_batting_position(batter)]

            pitcher_eff = 1.0 * opp_pitcher_woba / self.league_stats.get_league_woba(self.year)

            batter_eff = 1.0 * self.player_stats.get_batter_woba_vs_RHP_LHP(self.year, batter, opp_pitcher_hand) /\
                         self.league_stats.get_league_woba(self.year)

            park_factor = self.ballpark_stats.get_ballpark_factor_overall(park)

            batting_order_factor = RUN_MULTIPLIER[self.player_stats.get_player_batting_position(batter)]

            team_factor = self.team_stats.get_team_runs_total(self.year, batter_team) /\
                          (self.league_stats.get_league_runs(self.year) / 30.0)

        return batter_runs_per_pa * exp_pa * batting_order_factor * ((1.5 * pitcher_eff + 1.5 * batter_eff + park_factor + team_factor) / 5)

    def batter_points_expected_for_rbi(self, batter):
        """
        Function: batter_points_expected_for_rbi
        -----------------
        Equation to determine the total number of points expected for a batter's rbis.
        Right now, this only computes for batters with > 0 at bats

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

        #Initialize Equation
        batter_runs_per_pa = 0
        exp_pa = 0
        pitcher_eff = 0
        batter_eff = 0
        park_factor = 0
        batting_order_factor = 0
        team_factor = 0

        #Only compute if batter has > 0 at bats
        if self.player_stats.get_batter_ab_total(self.year,batter) > 0:

            #Helper Variables
            batter_team = self.player_stats.get_player_team(batter)
            batter_hand = self.player_stats.get_player_batting_hand(batter)
            opp_team = self.team_stats.get_team_opponent(batter_team)
            opp_pitcher = self.player_stats.get_starting_pitcher(opp_team)

            #Accounts for pitchers without stats by defaulting to league average and RHP
            if self.player_stats.get_pitcher_total_innings_pitched(self.year, opp_pitcher) > 0:
                opp_pitcher_woba = self.player_stats.get_pitcher_woba_allowed_vs_RHB_LHB(self.year, opp_pitcher, batter_hand)
                opp_pitcher_hand = self.player_stats.get_player_throwing_hand(opp_pitcher)
            else:
                print 'Here in pts for rbis for ', batter
                opp_pitcher_woba = self.league_stats.get_league_woba(self.year)
                opp_pitcher_hand = 'right'

            if self.team_stats.get_team_home_or_away(batter_team) == 'home':
                park = batter_team
            else:
                park = opp_team

            #Equations
            batter_runs_per_pa = 0.330 * self.player_stats.get_batter_ba_total(self.year, batter) + \
                                 0.187 * self.player_stats.get_batter_bb_percent_total(self.year, batter) + \
                                 0.560 * (self.player_stats.get_batter_hr_total(self.year, batter) /\
                                 self.player_stats.get_batter_pa_total(self.year, batter))

            exp_pa = 1.0 * EXPECTED_PA[self.player_stats.get_player_batting_position(batter)]

            pitcher_eff = 1.0 * opp_pitcher_woba / self.league_stats.get_league_woba(self.year)

            batter_eff = 1.0 * self.player_stats.get_batter_woba_vs_RHP_LHP(self.year, batter, opp_pitcher_hand) /\
                         self.league_stats.get_league_woba(self.year)

            park_factor = self.ballpark_stats.get_ballpark_factor_overall(park)

            batting_order_factor = RBI_MULTIPLIER[self.player_stats.get_player_batting_position(batter)]

            team_factor = self.team_stats.get_team_runs_total(self.year, batter_team) /\
                          (self.league_stats.get_league_runs(self.year) / 30.0)

        return batter_runs_per_pa * exp_pa * batting_order_factor * (((1.5 * pitcher_eff) + (1.5 * batter_eff) + park_factor + team_factor) / 5)

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
