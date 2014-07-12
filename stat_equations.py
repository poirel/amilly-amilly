"""
Class: StatEquations
Author: Poirel & Jett
Date: 6 July 2014

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

    def pitcher_points_expected_for_k(self, player):
        pitcher_k_per_9 = self.player_stats.get_pitcher_total_k(self.year, player) / (self.player_stats.get_pitcher_total_innings_pitched(self.year, player) / 9.0)
        expected_ip = self.player_stats.get_pitcher_total_innings_pitched(self.year, player) / self.player_stats.get_pitcher_total_games_started(self.year, player)

        playerTeam = self.player_stats.get_player_team(player)
        playerPitchHand = self.player_stats.get_player_throwing_hand(player)
        oppTeam = self.team_stats.get_team_opponent(playerTeam)

        opp_k_percentage = (self.team_stats.get_team_k_vs_RHP_LHP(self.year, oppTeam, playerPitchHand) / self.team_stats.get_team_pa_vs_RHP_LHP(self.year, oppTeam, playerPitchHand)) / self.league_stats.get_league_k_percentage(self.year)

        return pitcher_k_per_9 * (expected_ip/9) * opp_k_percentage

    def pitcher_expected_ip(self, player):
        return self.player_stats.get_pitcher_total_innings_pitched(self.year, player) / self.player_stats.get_pitcher_total_games_started(self.year, player)

    def pitcher_points_expected_for_win(self, player):
        # TODO: need vegas lines
        return 2

    def pitcher_points_expected_for_er(self, player):
        player_team = self.player_stats.get_player_team(player)
        opp_team = self.team_stats.get_team_opponent(player_team)
        player_loc = self.team_stats.get_team_home_or_away(player_team)
        xfip = self.player_stats.get_pitcher_xfip_allowed(self.year, player, player_loc)

        if player_loc=='home':
            park_team = player_team
        else:
            park_team = opp_team
        park_factor = self.ballpark_stats.get_ballpark_factor_overall(park_team)

        player_hand = self.player_stats.get_player_throwing_hand(player)
        pitcher_hand_hits = 1.0 * self.team_stats.get_team_woba_vs_RHP_LHP(self.year, opp_team, player_hand) / self.league_stats.get_league_woba(self.year)

        return -1.0/9 * xfip * park_factor * pitcher_hand_hits * self.pitcher_expected_ip(player)

    ###########
    # BATTERS #
    ###########

    def batter_points_expected_for_hits(self, player):
        adj_slg = (1.0 * self.player_stats.get_batter_1b_total(self.year, player) +
                   2.0 * self.player_stats.get_batter_2b_total(self.year, player) +
                   3.0 * self.player_stats.get_batter_3b_total(self.year, player) -
                   0.25 * (self.player_stats.get_batter_ab_total(self.year, player) - self.player_stats.get_batter_hits_total(self.year, player))) / \
                  (self.player_stats.get_batter_ab_total(self.year, player) - self.player_stats.get_batter_hr_total(self.year, player))

        exp_ab = 1.0 * self.player_stats.get_batter_ab_total(self.year, player) / self.player_stats.get_batter_games_played_total(self.year, player)

        player_team = self.player_stats.get_player_team(player)
        player_hand = self.player_stats.get_player_batting_hand(player)
        opp_team = self.team_stats.get_team_opponent(player_team)
        opp_pitcher = self.player_stats.get_starting_pitcher(opp_team)
        opp_pitcher_woba = self.player_stats.get_pitcher_woba_allowed_vs_RHB_LHB(self.year, opp_pitcher, player_hand)
        opp_pitcher_eff = 1.0 * opp_pitcher_woba / self.league_stats.get_league_woba(self.year)

        opp_pitcher_hand = self.player_stats.get_player_throwing_hand(opp_pitcher)
        player_bat_eff = 1.0 * self.player_stats.get_batter_woba_vs_RHP_LHP(self.year, player, opp_pitcher_hand) / self.league_stats.get_league_woba(self.year)

        if self.team_stats.get_team_home_or_away(player_team)=='home':
            park = player_team
        else:
            park = opp_team
        park_factor = self.ballpark_stats.get_ballpark_factor_batting_average(park, player_hand)

        return adj_slg * exp_ab * opp_pitcher_eff * player_bat_eff * park_factor


    def batter_points_expected_for_walks(self, player):
        batter_walk_percentage = self.player_stats.get_batter_bb_percent_total(self.year, player)

        exp_ab = 1.0 * self.player_stats.get_batter_ab_total(self.year, player) / self.player_stats.get_batter_games_played_total(self.year, player)

        player_team = self.player_stats.get_player_team(player)
        player_hand = self.player_stats.get_player_batting_hand(player)
        opp_team = self.team_stats.get_team_opponent(player_team)
        opp_pitcher = self.player_stats.get_starting_pitcher(opp_team)
        pitcher_bb_perc = 1.0 * self.player_stats.get_pitcher_bb_allowed_vs_RHB_LHB(self.year, opp_pitcher, player_hand) / self.player_stats.get_pitcher_total_batters_faced_vs_RHB_LHB(self.year, opp_pitcher, player_hand)
        league_bb_perc = 1.0 * self.league_stats.get_league_bb(self.year) / self.league_stats.get_league_plate_appearance(self.year)
        pitcher_eff_walk = pitcher_bb_perc / league_bb_perc

        return batter_walk_percentage * exp_ab * pitcher_eff_walk

    def batter_points_expected_for_hr(self, player):
        batter_hr_percentage = 1.0 * self.player_stats.get_batter_hr_total(self.year, player) / self.player_stats.get_batter_pa_total(self.year, player)

        exp_ab = 1.0 * self.player_stats.get_batter_ab_total(self.year, player) / self.player_stats.get_batter_games_played_total(self.year, player)

        player_team = self.player_stats.get_player_team(player)
        player_hand = self.player_stats.get_player_batting_hand(player)
        opp_team = self.team_stats.get_team_opponent(player_team)
        opp_pitcher = self.player_stats.get_starting_pitcher(opp_team)
        opp_pitcher_hr_percentage = 1.0 * self.player_stats.get_pitcher_hr_allowed_vs_RHB_LHB(self.year, opp_pitcher, player_hand) / self.player_stats.get_pitcher_total_batters_faced_vs_RHB_LHB(self.year, opp_pitcher, player_hand)
        league_avg_hr_percentage = 1.0 * self.league_stats.get_league_homerun(self.year) / self.league_stats.get_league_plate_appearance(self.year)
        opp_pitcher_eff_hr = opp_pitcher_hr_percentage / league_avg_hr_percentage

        opp_pitcher_hand = self.player_stats.get_player_throwing_hand(opp_pitcher)
        batter_hr_vs_hand_percentage = self.player_stats.get_batter_hr_vs_RHP_LHP(self.year, player, opp_pitcher_hand) / self.player_stats.get_batter_plate_appearances_vs_RHP_LHP(self.year, player, opp_pitcher_hand)
        batter_eff_hr = batter_hr_vs_hand_percentage / league_avg_hr_percentage

        if self.team_stats.get_team_home_or_away(player_team)=='home':
            park = player_team
        else:
            park = opp_team
        park_factor_hr = self.ballpark_stats.get_ballpark_factor_homerun(park, player_hand)

        return 4.0 * batter_hr_percentage * exp_ab * opp_pitcher_eff_hr * batter_eff_hr * park_factor_hr


    def batter_points_expected_for_sb(self, player):
        batter_sb_per_game = 1.0 * self.player_stats.get_batter_sb_total(self.year, player) / self.player_stats.get_batter_games_played_total(self.year, player)

        player_team = self.player_stats.get_player_team(player)
        opp_team = self.team_stats.get_team_opponent(player_team)
        team_sb_percentage = 1.0 * self.team_stats.get_team_sb_allowed(self.year, opp_team) / (self.team_stats.get_team_sb_allowed(self.year, opp_team) + self.team_stats.get_team_cs_fielding(self.year, opp_team))
        league_sb_percentage =  1.0 * self.league_stats.get_league_stolen_bases(self.year) / (self.league_stats.get_league_stolen_bases(self.year) + self.league_stats.get_league_caught_stealing(self.year))
        team_eff_sb = team_sb_percentage / league_sb_percentage

        return 2.0* batter_sb_per_game * team_eff_sb

    def batter_points_expected_for_runs(self, player):
        batter_runs_per_pa = 0.330 * self.player_stats.get_batter_ba_total(self.year, player) + \
                             0.187 * self.player_stats.get_batter_bb_percent_total(self.year, player) + \
                             0.560 * self.player_stats.get_batter_hr_total(self.year, player) / self.player_stats.get_batter_pa_total(self.year, player)

        exp_ab = 1.0 * self.player_stats.get_batter_ab_total(self.year, player) / self.player_stats.get_batter_games_played_total(self.year, player)

        player_team = self.player_stats.get_player_team(player)
        player_hand = self.player_stats.get_player_batting_hand(player)
        opp_team = self.team_stats.get_team_opponent(player_team)
        opp_pitcher = self.player_stats.get_starting_pitcher(opp_team)
        opp_pitcher_woba = self.player_stats.get_pitcher_woba_allowed_vs_RHB_LHB(self.year, opp_pitcher, player_hand)
        opp_pitcher_eff = 1.0 * opp_pitcher_woba / self.league_stats.get_league_woba(self.year)

        opp_pitcher_hand = self.player_stats.get_player_throwing_hand(opp_pitcher)
        player_bat_eff = 1.0 * self.player_stats.get_batter_woba_vs_RHP_LHP(self.year, player, opp_pitcher_hand) / self.league_stats.get_league_woba(self.year)

        if self.team_stats.get_team_home_or_away(player_team)=='home':
            park = player_team
        else:
            park = opp_team
        park_factor = self.ballpark_stats.get_ballpark_factor_overall(park)

        # TODO: get batting order for runs
        batting_order_factor = 1.0

        team_factor = self.team_stats.get_team_runs_total(self.year, player_team) / (self.league_stats.get_league_runs(self.year) / 30.0)

        return batter_runs_per_pa * exp_ab * opp_pitcher_eff * player_bat_eff * park_factor * batting_order_factor * team_factor


    def batter_points_expected_for_rbi(self, player):
        batter_runs_per_pa = 0.330 * self.player_stats.get_batter_ba_total(self.year, player) + \
                             0.187 * self.player_stats.get_batter_bb_percent_total(self.year, player) + \
                             0.560 * self.player_stats.get_batter_hr_total(self.year, player) / self.player_stats.get_batter_pa_total(self.year, player)

        exp_ab = 1.0 * self.player_stats.get_batter_ab_total(self.year, player) / self.player_stats.get_batter_games_played_total(self.year, player)

        player_team = self.player_stats.get_player_team(player)
        player_hand = self.player_stats.get_player_batting_hand(player)
        opp_team = self.team_stats.get_team_opponent(player_team)
        opp_pitcher = self.player_stats.get_starting_pitcher(opp_team)
        opp_pitcher_woba = self.player_stats.get_pitcher_woba_allowed_vs_RHB_LHB(self.year, opp_pitcher, player_hand)
        opp_pitcher_eff = 1.0 * opp_pitcher_woba / self.league_stats.get_league_woba(self.year)

        opp_pitcher_hand = self.player_stats.get_player_throwing_hand(opp_pitcher)
        player_bat_eff = 1.0 * self.player_stats.get_batter_woba_vs_RHP_LHP(self.year, player, opp_pitcher_hand) / self.league_stats.get_league_woba(self.year)

        if self.team_stats.get_team_home_or_away(player_team)=='home':
            park = player_team
        else:
            park = opp_team
        park_factor = self.ballpark_stats.get_ballpark_factor_overall(park)

        # TODO: get batting order for RBI
        batting_order_factor = 1.0

        team_factor = self.team_stats.get_team_runs_total(self.year, player_team) / (self.league_stats.get_league_runs(self.year) / 30.0)

        return batter_runs_per_pa * exp_ab * opp_pitcher_eff * player_bat_eff * park_factor * batting_order_factor * team_factor

    ###########
    # Overall #
    ###########

    def get_score(self, player):
        position = self.player_stats.get_player_fielding_position(player)
        if position=='P':
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
