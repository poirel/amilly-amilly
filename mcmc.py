from random import choice, shuffle, random
from collections import defaultdict
from math import exp
from numpy import arange
from stat_parsers.player_stats import PlayerStats

import argparse

class TeamMCMC:

    def __init__(self, names, classes, values, costs, capacity, object_composition):


        self.names = names
        self.values = dict(zip(names, values))
        self.costs = dict(zip(names, costs))
        self.classes = dict(zip(names, classes))
        self.capacity = capacity
        self.valid_comp = []
        for c, count in object_composition.items():
            self.valid_comp.extend([c]*count)

        self.available_names_by_class = defaultdict(list)
        for i, n in enumerate(names):
            self.available_names_by_class[classes[i]].append(n)

        # current team status to be updated during MCMC
        self.current_team = []
        self.current_value = None
        self.current_cost = None

    def get_available(self, object_class):
        return self.available_names_by_class[object_class]

    def add_player(self, name):
        self.current_team.append(name)
        self.available_names_by_class[self.classes[name]].remove(name)
        self.current_value += self.values[name]
        self.current_cost += self.costs[name]

    def remove_player(self, name):
        self.current_team.remove(name)
        self.available_names_by_class[self.classes[name]].append(name)
        self.current_value -= self.values[name]
        self.current_cost -= self.costs[name]

    def make_random_team(self):
        team_found = False
        self.clear_team()
        while len(self.current_team) < len(self.valid_comp):
            self.clear_team()
            random_comp = list(self.valid_comp)
            shuffle(random_comp)
            for new_class in random_comp:
                candidates = [name for name in self.get_available(new_class) if (self.costs[name] + self.current_cost) <= self.capacity]
                if len(candidates) > 0:
                    self.add_player(choice(candidates))

    def clear_team(self):
        for name in self.current_team:
            self.available_names_by_class[self.classes[name]].append(name)
        self.current_team = []
        self.current_value = 0
        self.current_cost = 0

    def get_neighbor(self):
        neighbors = []
        for name in self.current_team:
            for candidate in self.get_available(self.classes[name]):
                if (self.current_cost - self.costs[name] + self.costs[candidate]) <= self.capacity:
                    neighbors.append( (name, candidate) )
        old, new = choice(neighbors)
        return old, new

    def transition_to_neighbor(self, old_name, new_name):
        # remove old_name from the team
        self.current_team.remove(old_name)
        self.available_names_by_class[self.classes[old_name]].append(old_name)
        self.current_cost -= self.costs[old_name]
        self.current_value -= self.values[old_name]

        # add new_name to the team
        self.current_team.append(new_name)
        self.available_names_by_class[self.classes[new_name]].remove(new_name)
        self.current_cost += self.costs[new_name]
        self.current_value += self.values[new_name]

    def print_team(self):
        print '$%d' % self.current_cost, self.current_value, sorted(self.current_team), "\n", self.current_team

    def should_transition(self, old_val, new_val, temp):
        if old_val < new_val:
            return True
        delta = old_val - new_val
        if random < exp(1.0*delta/temp):
            return True
        else:
            return False

    def find_simulated_annealing_solution(self):
        for i in range(10):
            print 'Stadium Grinders Team ',i
            self.make_random_team()
            for temp in arange(1000, 0, -0.25):
                old_name, new_name = self.get_neighbor()
                new_team_value = self.current_value - self.values[old_name] + self.values[new_name]
                if self.should_transition(self.current_value, new_team_value, temp):
                    self.transition_to_neighbor(old_name, new_name)
                else:
                    continue
            self.print_team()