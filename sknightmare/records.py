import queue
import numpy as np
from collections import namedtuple
from enum import IntEnum
from copy import copy

# Some enum and tuple definitions:
PartyStatus = IntEnum("PartyStatus", "ENTERED SEATED ORDERED EATING PAID")
TableStats = namedtuple('TableStats', 'occupancy generated_noise received_noise perceived_crowding')
PartyStats = namedtuple('PartyState', 'satisfaction order perceived_noise wait_time cook_time eat_time')
MealStats = namedtuple('MealStats', 'order cook_time quality')


class RestaurantDay:

    def __init__(self, parties, tables, menu):
        self.parties = parties  # [self.parse_party(p) for p in parties]
        self.tables_stats = {t.name: self.parse_table(t) for t in tables}
        self.menu = menu

    def get_parties(self, table):
        return [p for p in self.parties if p.status >= PartyStatus.SEATED and p.table.name == table.name]

    def parse_table(self, table):
        # return a named tuple for each table's stats
        return TableStats(copy(table.parties), table.generated_noise, table.received_noise, table.perceived_crowding)

    def parse_party(self, party):
        return PartyStats(party.satisfaction, None, party.perceived_noisiness, 0, 0, 0)

        # for each day:
        # parties enter and wait
        # some are seated, some leave
        # the seated ones place orders
        # they experience noise from other diners and service from the staff
        # they wait some time for their food and then receive it at some quality
        # they eat the food
        # they pay/tip and leave
        #
        # things I want to track:
        # characteristics of each party that enters (maybe also of those that don't?)
        # for each party that is seated:
        # attributes of the party
        # where they sat
        # what they ordered
        # what cooked it
        # how long they waited
        # how good the food was
        # how happy they were with it
        # how long they ate for
        # how much they tipped and paid

        # party aggregates:
        # total revenue
        # total tips
        # how much at what time of day?
        # how happy everyone was
        # how many parties there were
        # how many people there were
        # how much of each item was ordered and how good each was
        # how much people tipped
        # how long parties waited for a table and food (including leavers)
        # how long they ate for on average
        # how much noise the restaurant experienced on average

        # table stuff
        # how much traffic each table gets in the day
        # how much noise each table gets on avg
        # how happy people are at each table on avg

        # over the course of the day, let's add each party that enters to this list
        self.parties = []  # lets say that parties can have a status of paid, left_waiting, left_ordered, left_served, or eating

    def get_avg_wait_time(self):
        if len(self.parties) > 0:
            # currently including parties that left before being seated
            wait_times = [p.seating_wait.total_seconds()/60.0 for p in self.parties]
            return np.mean(wait_times), np.std(wait_times)
        else:
            return 0, 0

    def get_avg_cook_time(self):
        '''
            get the mean of the total cook times for each party; this could be buggy right now if orders are incomplete
        '''
        if len(self.parties) > 0:
            # currently including parties that left before being seated
            cook_times = [np.sum(p.order.cook_times).total_seconds()/60.0
                          for p in self.parties if p.status >= PartyStatus.ORDERED]
            return np.mean(cook_times), np.std(cook_times)
        else:
            return 0, 0

    def get_avg_total_cook_time(self):
        if len(self.parties) > 0:
            cook_times = [p.order.get_total_cook_time().total_seconds()/60.0 for p in self.parties if p.status >=
                          PartyStatus.ORDERED]  # currently including parties that left before being seated
            return np.mean(cook_times), np.std(cook_times)
        else:
            return 0, 0

    def get_menu_stats(self):
        meals_served = []
        for p in self.parties:
            if p.status >= PartyStatus.ORDERED:
                meals_served += p.order.get_completed_meals()
        raw_menu_stats = {item["name"]: [m for m in meals_served if m.order["name"] == item["name"]]
                          for item in self.menu}
        menu_stats = {}

        for entry in raw_menu_stats:
            raw = raw_menu_stats[entry]
            quantity = len(raw)
            if quantity > 0:
                quality = np.mean([r.quality for r in raw])  # ,np.std([r.quality for r in raw]))
                # ,np.std([r.cook_time.total_seconds()/60.0 for r in raw]))
                cook_time = np.mean([r.cook_time.total_seconds()/60.0 for r in raw])
            else:
                quality = 0.0
                cook_time = 0.0
            menu_stats[entry] = {
                "volume": quantity,
                "quality": quality,
                "cook_time": cook_time
            }

        return menu_stats

    def get_avg_satisfaction(self):
        if len(self.parties) > 0:
            satisfactions = [p.satisfaction for p in self.parties]
            return np.mean(satisfactions), np.std(satisfactions)
        else:
            return 0, 0

    def get_total_revenue(self):
        if len(self.parties) > 0:
            return np.sum(p.paid_check for p in self.parties if p.status == PartyStatus.PAID)
        else:
            return 0

    def get_avg_party_size(self, seated=False):
        '''
          get the avg party size of all who entered or just those seated
        '''
        if len(self.parties) < 1:
            return 0
        elif seated is False:
            # avg over all entered
            size = [p.size for p in self.parties]
        else:
            size = [p.size for p in self.parties if p.status >= PartyStatus.SEATED]
        return np.mean(size), np.std(size)

    def get_demographics(self, status=None):
        # this should return a dictionary
        if status == None:
            # aggregate over everyone
            return
        elif status == "paid":
            return

    def get_report(self):
        return {
            'entries': len(self.parties),
            'seated': len([p for p in self.parties if p.status >= PartyStatus.SEATED]),
            'served': len([p for p in self.parties if p.status >= PartyStatus.EATING]),
            'paid': len([p for p in self.parties if p.status >= PartyStatus.PAID]),
            'entry_party_size':  np.mean([p.size for p in self.parties]),
            'paid_party_size':  np.mean([p.size for p in self.parties if p.status >= PartyStatus.PAID]),
            'wait_time': self.get_avg_wait_time(),
            'cook_time': self.get_avg_total_cook_time(),
            'food_stats': self.get_menu_stats()
        }


class Ledger:
    def __init__(self, menu, verbose=True, save_messages=True, rdq=None):
        if not rdq:
            self.day_log = queue.Queue()
        else:
            self.day_log = rdq
        self.menu = menu
        self.messages = []
        self.verbose = verbose
        self.save_messages = save_messages
        self.num_days = 0
        self.parties = []  # these are the primary references
        self.tables = []  # cleared every day

    def print(self, message):
        if self.verbose:
            print(message)
        if self.save_messages:
            self.messages.append(message)

    def read_messages(self):
        for m in self.messages:
            print(m)

    def record_day(self, day):
        self.num_days += 1
        self.day_log.append(day)

    def record_current_day(self):
        today = RestaurantDay(self.parties, self.tables, self.menu)
        self.day_log.put(today)
        print("********* Day: {} ************".format(self.num_days))
        print(today.get_report())
        print("\n")
        self.num_days += 1
        self.reset_day()

    def reset_day(self):
        self.parties = []
        self.clear_tables()

    def clear_tables(self):
        for t in self.tables:
            t.generated_noise = []
            t.received_nose = []
            t.perceived_crowding = []
            t.party = None

    def get_menu_stats(self):
        days = list(self.day_log.queue)
        menu_items = [m["name"] for m in self.menu]
        all_stats = [d.get_menu_stats() for d in days]
        menu_stats = {}
        for mi in menu_items:
            menu_stats[mi] = {}
            for stat in all_stats[0][mi].keys():
                extracted_stat = [day[mi][stat] for day in all_stats]
                menu_stats[mi][stat] = (np.mean(extracted_stat), np.std(extracted_stat))
        return menu_stats

    def generate_final_report(self):
        days = list(self.day_log.queue)
        revenue = np.sum([d.get_total_revenue() for d in days])
        cook_times, ct_stds = zip(*[d.get_avg_total_cook_time() for d in days])
        wait_times, wt_stds = zip(*[d.get_avg_wait_time() for d in days])
        satisfactions, s_stds = zip(*[d.get_avg_satisfaction() for d in days])

        report = {"revenue": revenue,
                  "cook_times": (np.mean(cook_times), np.std(cook_times)),
                  "wait_times": (np.mean(wait_times), np.std(wait_times)),
                  "satisfaction": (np.mean(satisfactions), np.std(satisfactions)),
                  "menu_stats": self.get_menu_stats()
                  }
        for entry in report:
            print("{}:{}".format(entry, report[entry]))
        return report
