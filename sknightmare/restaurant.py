import simpy
import numpy as np
from scipy.stats import norm
from random import seed, randint
seed(10)
from random_words import RandomWords
import arrow # for nicer datetimes
import math
import queue
from objects import Party, Table, Order, Appliance
from records import Ledger

class Restaurant:
  '''
    equipment is a list of Appliances
    tables is a list of Tables

  '''
  waiting_list_max = 20
  menu_items = [
    {
        "name": "Simple Pizza",
        "price": 5.0,
        "requirements": ["pizza"],
        "difficulty": 0.1,
        "cost": 4.0
    },
    {
        "name": "Intermediate Pizza",
        "price": 10.0,
        "requirements": ["pizza"],
        "difficulty": 0.5,
        "cost": 5.0
    },
    {
        "name": "Excessive Pizza",
        "price": 50.0,
        "requirements": ["pizza"],
        "difficulty": 0.9,
        "cost": 15
    }
  ]
  def __init__(self, name, equipment, tables, start_time='2019-01-01T00:00:00', day_log = None):
    self.env = simpy.Environment()
    self.ledger = Ledger(self.menu_items,verbose=False,save_messages=True)
    self.env.ledger = self.ledger
    self.env.day = 0 # just a counter for the number of days
    self.name = name

    # queue for reporting the days internally or externally (if day_log is an rdq, see flask_app for more details)
    if day_log:
      self.day_log = day_log
    else:
      self.day_log = queue.Queue()

    # sim mechanics
    self.setup_neighborhood()
    self.setup_kitchen(equipment)
    self.setup_seating(tables)

    # tools
    self.name_generator = RandomWords()
    self.start_time = arrow.get(start_time) # this doesn't really matter unless we start considering seasons etc.
    self.monkey_patch_env()

    # stats
    self.satisfaction_scores = []
    self.restaurant_rating = 1 #score between 0 and 1
    self.checks = []
    self.generated_parties = []
    self.entered_parties = []
    self.seated_parties = []
    self.order_log = []
    self.daily_costs = []
    self.closing_order = 0
    self.env.process(self.simulation_loop())

  def setup_kitchen(self, equipment):
    self.kitchen = simpy.FilterStore(self.env, capacity=len(equipment))
    self.kitchen.items = [Appliance(self.env,e["name"],e["attributes"]) for e in equipment]
    self.menu_items = [m for m in self.menu_items if any(all(req in appliance.capabilities for req in m["requirements"]) for appliance in self.kitchen.items)]
    self.env.ledger.print("Menu: {}".format(self.menu_items))
    self.env.ledger.appliances = [a for a in self.kitchen.items]

  def setup_seating(self, tables):
    self.seating = simpy.FilterStore(self.env, capacity=len(tables))
    self.seating.items = [Table(self.env,t["name"],t["attributes"]) for t in tables]
    self.max_table_size = max([t.seats for t in self.seating.items])
    self.env.ledger.tables = [t for t in self.seating.items]
    for t in self.env.ledger.tables:
      t.start_simulation()
  
  def setup_neighborhood(self):
    self.max_party_size = 10
    self.neighborhood_size = 10000
    self.max_eating_pop = 0.1*self.neighborhood_size
    self.demographics = ["size","affluence","taste","noisiness","leisureliness","patience","noise_tolerance","space_tolerance", "mood"]
    self.demographic_means = np.array([0.25,0.3,0.3,0.6,0.4,0.5,0.3,0.5, 0.5])
                                        # size aff taste  noi   leis  pat noi_t space_t
    # self.demographic_cov = np.matrix([[ 0.02, 0.00, 0.00, 0.09, 0.02,-0.02, 0.06,-0.02], #size
    #                                   [ 0.00, 0.02, 0.10,-0.02, 0.06,-0.07,-0.07,-0.07], #affluence
    #                                   [ 0.00, 0.10, 0.02,-0.02, 0.07,-0.01,-0.01, 0.0], #taste
    #                                   [ 0.09,-0.02,-0.02, 0.02, 0.01, 0.00, 0.08, 0.03], #noisiness
    #                                   [ 0.02, 0.06, 0.07, 0.01, 0.02, 0.07,-0.06,-0.06], #leisureliness
    #                                   [-0.02,-0.07,-0.01, 0.00, 0.07, 0.02, 0.07, 0.06], #patience
    #                                   [ 0.06,-0.07,-0.01, 0.08,-0.06, 0.07, 0.02, 0.09], #noise tolerance
    #                                   [-0.02,-0.07, 0.00, 0.03,-0.06, 0.06, 0.09, 0.02] #space toleranceseating.put(self.table)
    #                                  ])  
    self.demographic_cov = np.matrix([[ 0.05,  0.0,   0.0,   0.018, 0.004,-0.004, 0.012,-0.004, 0.00],
                                      [ 0.0,   0.05,  0.02, -0.004, 0.012,-0.014,-0.014,-0.014, 0.00],
                                      [ 0.0,   0.02,  0.05, -0.004, 0.014,-0.002,-0.002, 0.0, 0.00  ],
                                      [ 0.018,-0.004,-0.004, 0.05,  0.002, 0.0,   0.016, 0.006, 0.00],
                                      [ 0.004, 0.012, 0.014, 0.002, 0.05,  0.014,-0.012,-0.012, 0.00],
                                      [-0.004,-0.014,-0.002, 0.0,   0.014, 0.05,  0.014, 0.012, 0.00],
                                      [ 0.012,-0.014,-0.002, 0.016,-0.012, 0.014, 0.05,  0.018, 0.00],
                                      [-0.004,-0.014, 0.0,   0.006,-0.012, 0.012, 0.018, 0.05, 0.00],
                                      [0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.05]
                                      ])

  def current_time(self):
    # let's assume the time step is seconds
    return self.start_time.replace(seconds=self.env.now)
  
  def monkey_patch_env(self):
    self.env.m_start_time = self.start_time
    self.env.m_current_time = self.current_time
    self.env.m_rw = self.rw
  
  def rw(self):
    return self.name_generator.random_word()
  
  def handle_party(self, party):
    seated = yield self.env.process(party.wait_for_table(self.seating))
    if seated == False:
      check,satisfaction = yield self.env.process(party.leave(self.seating))
    else:
      self.seated_parties.append(party)
      noise_process = self.env.process(party.update_satisfaction(self.env.ledger.tables))  
      # order = Order(self.env,self.rw(),party,party.table)
      # yield self.env.process(order.place_order(self.kitchen,self.menu_items))
      yield self.env.process(party.place_order(self.kitchen,self.menu_items))
      # self.order_log.append(order)  
      yield self.env.process(party.eat())
      check,satisfaction = yield self.env.process(party.leave(self.seating))
    self.checks.append(check)
    self.satisfaction_scores.append(satisfaction)
  
  
  def get_customer_rate(self):
    hourly_rates = [
        [0,0,0,0,0,0,0.1,0.2,0.5,0.9,0.7,0.5,1,1,0.6,0.2,0.2,0.6,0.8,0.8,0.7,0.3,0.1,0.1,0], #m
        [0,0,0,0,0,0,0.1,0.2,0.5,0.9,0.7,0.5,1,1,0.6,0.2,0.2,0.6,0.9,0.9,0.8,0.3,0.1,0.1,0], #t
        [0,0,0,0,0,0,0.1,0.2,0.5,0.9,0.7,0.5,1,1,0.6,0.2,0.2,0.6,0.9,0.9,0.8,0.3,0.1,0.1,0], #wseating.put(self.table)
        [0,0,0,0,0,0,0.1,0.2,0.5,0.9,0.7,0.5,1,1,0.6,0.2,0.2,0.6,0.9,0.9,0.8,0.3,0.1,0.1,0], #r
        [0,0,0,0,0,0,0.1,0.2,0.5,1,0.7,0.5,1,1,0.6,0.2,0.2,0.6,1,1,0.8,0.8,0.8,0.1,0], #f
        [0,0,0,0,0,0,0.1,0.2,0.5,1,0.7,0.5,1,1,0.6,0.2,0.2,0.6,1,1,0.8,0.8,0.8,0.1,0], #sa
        [0,0,0,0,0,0,0.1,0.5,0.8,1,1,1,1,1,0.6,0.2,0.2,0.6,0.8,0.8,0.6,0.3,0.1,0.1,0]  #su    
    ]
    cur_time = self.env.m_current_time().timetuple()
    raw_rate = hourly_rates[cur_time.tm_wday][cur_time.tm_hour]
    rate = self.max_eating_pop*raw_rate
    return rate# number of groups /hr
  
  def sample_num_parties(self):
    '''
      Sample the number of parties that are looking to eat in the town at that hour
    '''
    num_parties = np.random.poisson(self.get_customer_rate())
    return num_parties
        
  def generate_parties(self,n=1):
    '''
      Randomly generate a party
    '''
    self.env.ledger.print("Time is: {} from {}".format(self.current_time().format("HH:mm:ss"),self.env.now))
    entered_parties = []
    num_entered = 0
    parties = np.clip(np.random.multivariate_normal(self.demographic_means,self.demographic_cov,n),0.01,1)
    num_generated = len(parties)
    for party in parties:
      self.generated_parties.append(party)
      party_attributes = {k:v for (k,v) in zip(self.demographics,party)}
      party_attributes["size"] = int(np.ceil(party_attributes["size"]*self.max_party_size))
      if(self.decide_entry(party_attributes)):
        num_entered += 1
        p = Party(self.env,self.rw().capitalize(),party_attributes)
        self.env.ledger.parties.append(p)
        entered_parties.append(p)
      else:
        continue
    self.env.ledger.print("Total groups generated: {}, total entered: {}".format(num_generated, num_entered))   
    return entered_parties
  
  def decide_entry(self,party_attributes):
    if(party_attributes["size"] > self.max_table_size):
      return False
    elif party_attributes["taste"] > self.restaurant_rating:
      return False
    elif np.random.uniform(0,1) > 0.05:
      return False
    else:
       return True
    
  def simulation_loop(self):
    day_of_week = ""
    daily_customers = 0
    party_index = 0
    while True:
      yield self.env.timeout(60*60) #every hour
      today = self.env.m_current_time().format("dddd")
      if today != day_of_week:
        day_of_week = today
        self.env.day += 1
        self.ledger.record_current_day()
        self.calc_stats()
        #costs = self.run_expenses()
        #self.env.process(self.calc_stats())
        #self.summarize(costs,daily_customers,self.entered_parties[party_index:party_index+daily_customers])
        daily_customers = 0
        party_index += daily_customers
        #self.restaurant_rating = min(0,2)
        #self.restaurant_rating = np.mean(self.satisfaction_scores)
        #day = self.env.m_current_time().format("ddd MMM D")
        #print("Summary for {}: satisfaction: {}".format(day,self.restaurant_rating))
      # generate 0+ parties based on the time of day & popularity of the restaurant
      entering_parties =  self.generate_parties(self.sample_num_parties())
      daily_customers += len(entering_parties) 
      for p in entering_parties:    
        self.env.process(self.handle_party(p))
        
  def simulate(self,seconds=None,days=None):
    if seconds:
      max_seconds = seconds
    elif days:
      max_seconds = days*24*60*60
    else:
      max_seconds = 100
    self.env.run(until=max_seconds)
    
  def run_expenses(self):
    daily_cost = 0
    for a in self.env.ledger.appliances:
      daily_cost += a.daily_upkeep
    for t in self.env.ledger.tables:
      daily_cost += t.daily_upkeep
    for o in self.order_log[self.closing_order:]:
      daily_cost += o.total_cost
      self.closing_order = len(self.order_log)
    self.daily_costs.append(daily_cost)
    return daily_cost
    
  def calc_stats(self):
    if len(self.satisfaction_scores) > 0:
      self.restaurant_rating = np.mean(self.satisfaction_scores)

 
  def summarize(self,costs,volume,parties):
    day = self.env.m_current_time().format("ddd MMM D")
    customers = np.sum([p.size for p in parties])
    if customers > 0:
      noise = np.sum([p.size*p.noisiness for p in parties])/customers
      total_bills = np.sum([p.paid_check for p in parties])
      satisfaction = np.mean([p.satisfaction for p in parties if not np.isnan(p.satisfaction)])
      self.env.ledger.print("Summary for {}: satisfaction: {}".format(day,self.restaurant_rating))
    else:
      noise = 0
      total_bills = 0
      satisfaction = 0
    self.day_log.put({"day": self.env.day,"expenses":costs,"rating":self.restaurant_rating,"num_entered":volume, "noise": noise, "revenue":total_bills, "satisfaction": satisfaction})


  def final_report(self):
    stringbuilder = ""
    stringbuilder += "*"*80+"\n"
    stringbuilder += "Simulation run for {} days.\n".format(self.ledger.num_days)
    stringbuilder += "*"*80+"\n"
    stringbuilder += "Parties entered: {}\nParties seated: {}\nParties paid: {}\n".format(len(self.entered_parties),len(self.seated_parties),len([c for c in self.checks if c > 0]))
    revenue = np.sum(self.checks)
    stringbuilder += "Total Revenue: ${:.2f}\n".format(revenue)
    upfront_costs = np.sum([a.cost for a in self.env.ledger.appliances]) + np.sum([t.cost for t in self.env.ledger.tables])
    stringbuilder += "Total Upfront Costs: ${:.2f}\n".format(upfront_costs)
    costs = np.sum(self.daily_costs)
    stringbuilder += "Total Daily Costs: ${:.2f}\n".format(costs)
    stringbuilder += "Total Profit: ${:.2f}\n".format(revenue-costs-upfront_costs)
    # leftovers = len(self.entered_parties)-len(self.checks) #if we cut off the last day while people were dining
    # if leftovers > 0:
    #   truncated_entered_parties = self.entered_parties[:-leftovers]
    # else:
    #   truncated_entered_parties = self.entered_parties
    num_served = np.sum([p.size for i,p in enumerate(truncated_entered_parties) if p.paid_check>0])
    stringbuilder += "Total individual customers served: {}\nAverage price per entree: ${:.2f}\n".format(num_served,revenue/num_served)
    stringbuilder += "Avg Satisfaction Score: {:.2f}\nStd Satisfaction Score: {:.2f}\n".format(np.mean(self.satisfaction_scores), np.std(self.satisfaction_scores))
    stringbuilder += "Final Restaurant Rating: {:.2f}\n".format(self.restaurant_rating)
    print(stringbuilder)
    return stringbuilder
