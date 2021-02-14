import random

import pandas as pd
import plotly.express as px
from collections import defaultdict
import copy


# Custom Errors
class CountryNotFoundError(Exception):
    def __init__(self, country):
        print("%s does not exist!" % country)


class ColorNotFoundError(Exception):
    def __init__(self, color):
        print("%s does not exist!" % color)


class ConstraintViolationError(Exception):
    def __init__(self, country1, country2):
        print("%s and %s are neighbors and they have the same color!" % (country1, country2))


class AssignmentError(Exception):
    def __init__(self, country):
        print("Your assignment is not complete! %s was not colored!" % country)


# Do not modify the line below.
countries = ["Argentina", "Bolivia", "Brazil", "Chile", "Colombia", "Ecuador", "Falkland Islands", "Guyana", "Paraguay",
             "Peru", "Suriname", "Uruguay", "Venezuela"]

# Do not modify the line below.
colors = ["blue", "green", "red", "yellow"]


# Constraint to check if a color is legal for a country
def adjacent_c_constraint(count1, color, neighbors_dict, assignment):
    """
    :param count1: the country we want to color
    :param color: the color we want to use for count1
    :param neighbors_dict: dictionary of neighbors
    :param assignment: the current assignment done by bts
    :return: True is the color is legal, False otherwise
    """
    for country in neighbors_dict[count1]:
        if country in assignment:
            if assignment[country] == color:
                return False
    return True


# Backtracking search function
def bts(csp):
    """
    Function to perform BT on a CSP
    :param csp: a constraint satisfaction problem
    :return: Result of BT or Failure if no solution is possible
    """
    return backtrack({}, csp)


# Minimum remaining value
def mrv(csp, assignment):
    """
    Function to find the country that has the minimum number of legal colors to use
    :param csp: the Constraint Satisfaction Problem we want to solve
    :param assignment: The assignment achieved so far
    :return: the unassigned country that has the fewest legal options
    """
    country = csp.unassigned[0]
    minimum = len(csp.possible_values(country, assignment))
    for value in csp.unassigned:
        if len(csp.possible_values(value, assignment)) < minimum:
            country = value
            minimum = len(csp.possible_values(value, assignment))
    return country


# Backtrack function
def backtrack(assignment, csp):
    """
    Function that performs the BT algorithm to solve a CSP - Recursive
    MRV and FC used for optimization
    :param assignment: the assignment achieved by the BT so far
    :param csp: the CSP we are trying to solve
    :return: a solution dictionary of 'Failure' if no solution found
    """

    # If all countries are assigned a color return the result
    if len(csp.unassigned) == 0:
        return assignment

    # Get the country that has the least possible legal values
    country = mrv(csp, assignment)

    # For running the algorithm without mrv uncomment the line below
    # country = csp.unassigned[0]

    # Assign a color in random order and call the function recursively
    sh_list = csp.domains
    random.shuffle(sh_list)
    for color in sh_list:

        # Check if the assignment (country , color) is consistent
        if csp.constraints(country, color, neighbors_dict, assignment):
            assignment[country] = color
            csp.unassigned.remove(country)

            # Forward Checking
            for neighbor in csp.neighbors_dict[country]:
                # Terminate if the neighbor has no legal values possible
                if len(csp.possible_values(neighbor, assignment)) == 0:
                    return 'Failure'

            # Recursive call
            result = backtrack(assignment, csp)
            if result != 'Failure':
                return result

        # Delete the assignment if it is not consistent
        if country in assignment:
            del assignment[country]
            csp.unassigned.append(country)

    return 'Failure'


# Function to check the final result
def check(result, countries, colors, neighbors):
    for country in countries:
        if country not in result:
            raise AssignmentError(country)

    for key, value in result.items():

        if key not in countries:
            raise CountryNotFoundError(key)

        if value not in colors:
            raise ColorNotFoundError(value)

        for country in neighbors[key]:
            if result[country] == value:
                raise ConstraintViolationError(key, country)


# Do not modify this method, only call it with an appropriate argument.
# colormap should be a dictionary having countries as keys and colors as values.
def plot_choropleth(colormap):
    fig = px.choropleth(locationmode="country names",
                        locations=countries,
                        color=countries,
                        color_discrete_sequence=[colormap[c] for c in countries],
                        scope="south america")
    fig.show()


# Class definition of a Constraint Satisfaction Problem
class CSP:
    """
    Class of a Constraint Satisfaction Problem

    class members
    variables: the countries we want to color
    domains: the possible colors to use
    neighbors_dict: dictionary that associates each country with a list of its neighbors
    constraint: rules to follow when coloring , here: no 2 neighbors have the same color
    unassigned: countries that are still uncolored

    functions
    possible_values: returns the legal colors for a country w.r.t an assignment by removing the colors that do not
                     satisfy the constraints
    """

    def __init__(self, variables, domains, neighbors_dict, constraints):
        self.variables = variables
        self.domains = domains
        self.neighbors_dict = neighbors_dict
        self.constraints = constraints
        self.unassigned = variables
        self.initial = ()

    def possible_values(self, country, assignment):
        possible = copy.deepcopy(self.domains)
        for value in self.domains:
            if not self.constraints(country, value, self.neighbors_dict, assignment):
                possible.remove(value)
        return possible


# Implement main to call necessary functions
if __name__ == "__main__":

    # Initializing the neighborhood dictionary
    neighbors_dict = defaultdict(list)

    # Filling the dictionary with neighbors:
    neighbors_dict['Argentina'] = ['Bolivia', 'Brazil', 'Chile', 'Paraguay', 'Uruguay']
    neighbors_dict['Bolivia'] = ['Argentina', 'Brazil', 'Chile', 'Paraguay', 'Peru']
    neighbors_dict['Brazil'] = ['Argentina', 'Bolivia', 'Colombia', 'Guyana', 'Paraguay', 'Peru', 'Suriname', 'Uruguay',
                                'Venezuela']
    neighbors_dict['Chile'] = ['Argentina', 'Bolivia', 'Peru']
    neighbors_dict['Colombia'] = ['Brazil', 'Ecuador', 'Peru', 'Venezuela']
    neighbors_dict['Ecuador'] = ['Colombia', 'Peru']
    neighbors_dict['Falkland Islands'] = []
    neighbors_dict['Guyana'] = ['Brazil', 'Suriname', 'Venezuela']
    neighbors_dict['Paraguay'] = ['Argentina', 'Bolivia', 'Brazil']
    neighbors_dict['Peru'] = ['Bolivia', 'Brazil', 'Chile', 'Colombia', 'Ecuador']
    neighbors_dict['Suriname'] = ['Brazil', 'Guyana']
    neighbors_dict['Uruguay'] = ['Argentina', 'Brazil']
    neighbors_dict['Venezuela'] = ['Brazil', 'Colombia', 'Guyana']

    counts = copy.deepcopy(countries)

    # Initializing the problem
    csp = CSP(counts, colors, neighbors_dict, adjacent_c_constraint)

    # Performing Backtracking search on the problem
    result = bts(csp)

    # Plotting the colored map if a solution is found
    if result != 'Failure':
        check(result, countries, colors, neighbors_dict)
        plot_choropleth(colormap=result)
    else:
        print('No solution found!')
