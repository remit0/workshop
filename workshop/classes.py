import os
from typing import List, Tuple

import pandas as pd

from .settings import RESULTS_PATH


class Group:

    """ Models a group of people willing to visit the Santa's Workshop """

    def __init__(self, num: int, days: List[int], size: int):

        self.num = num      # id of the group
        self.days = days   # list of days ranked from most to least wanted
        self.size = size    # size of the group
        self.assigned_day = None    # assigned day

    @staticmethod
    def _cost(rank: int, size: int) -> int:
        """ computes the cost of a group given its size and choice rank """
        if rank == 0:
            return 0
        elif rank == 1:
            return 50
        elif rank == 2:
            return 50 + 9 * size
        elif rank == 3:
            return 100 + 9 * size
        elif rank == 4:
            return 200 + 9 * size
        elif rank == 5:
            return 200 + 18 * size
        elif rank == 6:
            return 300 + 18 * size
        elif rank == 7:
            return 300 + 36 * size
        elif rank == 8:
            return 400 + 36 * size
        elif rank == 9:
            return 500 + (36 + 199) * size
        else:
            return 500 + (36 + 398) * size

    def cost(self) -> int:
        """ evaluates the cost of the group once it has been assigned to a day """
        rank = self.days.index(self.assigned_day) if self.assigned_day in self.days else -1
        return self._cost(rank, self.size)

    def evaluate(self, day: int) -> int:
        """ evaluates the cost of assigning the `day` to the group """
        rank = self.days.index(day) if day in self.days else -1
        return self._cost(rank, self.size)

    def assign(self, day: int):
        """ assigns day to the group """
        self.assigned_day = day


class BookMaker:

    """ Handles assignments of people to visits days. We start from the list of all groups stored
     in `self.groups`, then we iteratively empty this list to fill `self.assigned_groups` while
     keeping other attributes up to date (thus ensuring constraint checking at all times). """

    MIN = 125   # min number of people visiting for a day
    MAX = 300   # max number of people visiting for a day

    def __init__(self, groups: List[Group], verbose: int =1):

        self.groups = groups    # on going groups (not assigned)
        self.assigned_groups = list()   # assigned groups
        self.bookings = pd.Series(0, index=range(1, 101))   # number of people per day
        self.verbose = verbose

    def check_bounds(self) -> bool:
        """ checks that the min/max constraints are satisfied """
        return self.bookings.min() >= self.MIN and self.bookings.max() <= self.MAX

    def check_constraints(self) -> bool:
        """ checks min/max constraint and complete group assignments """
        return self.check_bounds() and len(self.groups) == 0

    @staticmethod
    def accounting_cost(bookings) -> float:
        """ computes the accounting penalty from bookings """
        bookings_lagged = bookings.shift(-1).fillna(method="ffill")    # N_100 = N_101
        exponents = 0.5 + ((abs(bookings - bookings_lagged)) / 50)
        return (((bookings - 125) / 400) * (bookings ** exponents)).sum()

    def cost(self) -> float:
        accounting_cost = self.accounting_cost(self.bookings)
        group_cost = sum([group.cost() for group in self.assigned_groups])
        return group_cost + accounting_cost

    def remove(self, group: Group):
        """ removes the `group` from the waiting list """
        group_idx = [1 if group.num == grp.num else 0 for grp in self.groups].index(1)
        self.groups.pop(group_idx)

    def assign(self, group: Group, day: int):
        """ assigns the `group` to the `day` and updates classes accordingly """
        group.assign(day)
        self.assigned_groups.append(group)
        self.remove(group)
        self.bookings.loc[day] += group.size
        if self.verbose:
            print("**assigned group number {} to day {}.".format(group.num, group.assigned_day))

    def evaluate(self, group: Group, day: int) -> float:
        """ greedily evaluates the cost of assigning the `group` to `day`. Does not actually assign
        the `group`. """
        # todo : is there a way to compute over a smaller vector of bookings ?
        bookings_updated = self.bookings.copy()
        bookings_updated.loc[day] += group.size
        return self.accounting_cost(bookings_updated) + group.evaluate(day)

    def optimise_day(self, group: Group) -> int:
        """
        scores the wishes of a group and returns the less costly given current availabilities
        """
        valid_days = self.bookings[self.bookings <= self.MAX - group.size].index.tolist()
        days = [day for day in valid_days if day in group.days]
        if not days:
            days = [day for day in valid_days if day not in group.days]
        chosen_day, min_cost = -1, float("inf")
        for day in days:
            day_score = self.evaluate(group, day)
            if day_score < min_cost:
                min_cost = day_score
                chosen_day = day
        return chosen_day

    def optimise_group(self, day: int) -> Group:
        pass

    def make_submission(self, name: str):
        """ produces the kaggle submission file """
        assert self.check_constraints(), "Invalid submission."
        group_ids, group_days = [], []
        for group in self.assigned_groups:
            group_ids.append(group.num)
            group_days.append(group.assigned_day)
        submission = pd.DataFrame.from_dict({"family_id": group_ids, "assigned_day": group_days})
        submission.to_csv(os.path.join(RESULTS_PATH, "{}.csv".format(name)), index=False)


def init(data: pd.DataFrame) -> BookMaker:
    """ initializes a `BookMaker` from the input data """

    choices_col = ["choice_{}".format(i) for i in range(10)]
    groups = list()

    for group_id, group_data in data.iterrows():
        group = Group(group_id, group_data[choices_col].values.tolist(), group_data["n_people"])
        groups.append(group)

    return BookMaker(groups)
