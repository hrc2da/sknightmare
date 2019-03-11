import simpy
import numpy as np
from scipy.stats import norm
from random import seed, randint
seed(10)
from random_words import RandomWords
import arrow # for nicer datetimes
import math

class Ledger:
  def __init__(self,verbose=True,save_messages=True):
    self.messages = []
    self.verbose = verbose
    self.save_messages = save_messages
    self.num_days = 0
    self.days = []
  def print(self,message):
    if self.verbose:
      print(message)
    if self.save_messages:
      self.messages.append(message)
  def read_messages(self):
    for m in self.messages:
      print(m)
  def record_day(self):
    self.num_days += 1
    
class Restaurant:
  '''
    equipment is a list of Appliances
    tables is a list of Tables

  '''
  def __init__(self, name, equipment, tables, start_time='2019-01-01T00:00:00'):
    self.env = simpy.Environment()
    self.ledger = Ledger(verbose=False,save_messages=True)
    self.env.ledger = self.ledger
    self.env.day = 0
    self.name = name
    self.menu_items = [
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

    self.setup_neighborhood()
    self.setup_kitchen(equipment)
    self.setup_seating(tables)
    self.name_generator = RandomWords()
    self.satisfaction_scores = []
    self.restaurant_rating = 1 #score between 0 and 1
    self.checks = []
    self.waiting_list_max = 20
    self.start_time = arrow.get(start_time) # this doesn't really matter unless we start considering seasons etc.
    self.monkey_patch_env()
    self.generated_parties = []
    self.entered_parties = []
    self.seated_parties = []
    self.order_log = []
    self.daily_costs = []
    self.closing_order = 0
    #let's place an order for fun
#     orders = [Order(env,"Dusfrene Party of Two",None,None),
#               Order(env,"Bush Party of Three",None,None)]
#     print("Serving tables...")
#     placed_orders = [env.process(o.placewhere o.day == self.env.today_order(self.kitchen)) for o in orders]
    self.env.process(self.simulation_loop())

  def setup_kitchen(self, equipment):
    self.kitchen = simpy.FilterStore(self.env, capacity=len(equipment))
    self.kitchen.items = [Appliance(self.env,e["name"],e["attributes"]) for e in equipment]
    self.menu_items = [m for m in self.menu_items if any(all(req in appliance.capabilities for req in m["requirements"]) for appliance in self.kitchen.items)]
    self.env.ledger.print("Menu: {}".format(self.menu_items))
    self.appliances = [a for a in self.kitchen.items]
  def setup_seating(self, tables):
    self.seating = simpy.FilterStore(self.env, capacity=len(tables))
    self.seating.items = [Table(self.env,t["name"],t["attributes"]) for t in tables]
    self.max_table_size = max([t.seats for t in self.seating.items])
    self.tables = [t for t in self.seating.items]
  
  def setup_neighborhood(self):
    self.max_party_size = 10
    self.neighborhood_size = 10000
    self.max_eating_pop = 0.1*self.neighborhood_size
    self.demographics = ["size","affluence","taste","noisiness","leisureliness","patience","noise_tolerance","space_tolerance"]
    self.demographic_means = np.array([0.25,0.3,0.3,0.6,0.4,0.3,0.6,0.5])
                            # size aff taste noi leis  pat noi_t space_t
    self.demographic_cov = np.matrix([[ 0.02, 0.00, 0.00, 0.09, 0.02,-0.02, 0.06,-0.02], #size
                                      [ 0.00, 0.02, 0.10,-0.02, 0.06,-0.07,-0.07,-0.07], #affluence
                                      [ 0.00, 0.10, 0.02,-0.02, 0.07,-0.01,-0.01, 0.0], #taste
                                      [ 0.09,-0.02,-0.02, 0.02, 0.01, 0.00, 0.08, 0.03], #noisiness
                                      [ 0.02, 0.06, 0.07, 0.01, 0.02, 0.07,-0.06,-0.06], #leisureliness
                                      [-0.02,-0.07,-0.01, 0.00, 0.07, 0.02, 0.07, 0.06], #patience
                                      [ 0.06,-0.07,-0.01, 0.08, 0.06, 0.07, 0.02, 0.09], #noise tolerance
                                      [-0.02,-0.07, 0.00, 0.03,-0.06, 0.06, 0.09, 0.02] #space toleranceseating.put(self.table)
                                     ])  
    

  def current_time(self):
    # let's assume the time step is seconds
    return self.start_time.replace(seconds=self.env.now)
  
  def monkey_patch_env(self):
    self.env.m_start_time = self.start_time
    self.env.m_current_time = self.current_time
  
  def rw(self):
    return self.name_generator.random_word()
  
  def handle_party(self, party):
    seated = yield self.env.process(party.wait_for_table(self.seating))
    if seated == False:
      check,satisfaction = yield self.env.process(party.leave(self.seating))
    else:
      self.seated_parties.append(party)
      noise_process = self.env.process(party.check_noise(self.tables))  
      order = Order(self.env,self.rw(),party,party.table)
      yield self.env.process(order.place_order(self.kitchen,self.menu_items))
      self.order_log.append(order)  
      yield self.env.process(party.eat(order))
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
#     cur_time = self.env.m_current_time().timetuple()
#     # check day of week
#     if cur_time.tm_wday in (5,6):
#       # weekend
#       if cur_time.tm_hour in range(0,9):
#         m = 0
#         sd = 0.05
#       elif cur_time.tm_hour in range(9,15):
#         m = 4
#         sd = 4
#       elif cur_time.tm_hour in range (15,18):
#         m = 1
#         sd = 2
#       else:
#         m = 5imulation_loop
#         sd = 3
#     #elif cur_time.tm_wday == 4:
#       # friday
#     imulation_loop
#     imulation_loop
#       if cur_time.tm_hour in range(12,14):
#         m = 4
#         sd = 3
#       elif cur_time.tm_hour in range(18,21):
#         m = 4
#         sd = 3
#       else:
#         m = 0
#         sd = 0.05
#     num_parties = int(max(0,np.random.normal(m,sd)))
    num_parties = np.random.poisson(self.get_customer_rate())
    return num_parties
        
  def generate_parties(self,n=1):
    '''
      Randomly generate a party
    '''
    self.env.ledger.print("Time is: {} from {}".format(self.current_time().format("HH:mm:ss"),self.env.now))
    
    num_entered = 0
    parties = np.clip(np.random.multivariate_normal(self.demographic_means,self.demographic_cov,n),0.01,1)
    num_generated = len(parties)
    for party in parties:
      self.generated_parties.append(party)
      party_attributes = {k:v for (k,v) in zip(self.demographics,party)}
      party_attributes["size"] = int(np.ceil(party_attributes["size"]*self.max_party_size))
  #     party_attributes["size"] = int(np.clip(np.random.normal(4,1),1,10))
  #     party_attributes["noisiness"] = np.clip(np.random.normal(2.5,1),0,5)
  #     party_attributes["patience"] = np.clip(np.random.normal(2.5,1),0,5)
  #     party_attributes["affluence"]= np.clip(np.random.normal(2.5,1),0,5)
  #     party_attributes["space_tolerance"] = np.clip(np.random.normal(2.5,1),0,5)
      if(self.decide_entry(party_attributes)):
        num_entered += 1
        self.entered_parties.append(party)
        p = Party(self.env,self.rw().capitalize(),party_attributes)
        self.env.process(self.handle_party(p))
      else:
        continue
    self.env.ledger.print("Total groups generated: {}, total entered: {}".format(num_generated, num_entered))   
  
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
    while True:
      yield self.env.timeout(60*60) #every hour
      today = self.env.m_current_time().format("dddd")
      if today != day_of_week:
        day_of_week = today
        self.env.day += 1
        self.ledger.record_day()
        self.calc_stats()
        self.run_expenses()
        #self.env.process(self.calc_stats())
        #self.summarize()
        #self.restaurant_rating = min(0,2)
        #self.restaurant_rating = np.mean(self.satisfaction_scores)
        #day = self.env.m_current_time().format("ddd MMM D")
        #print("Summary for {}: satisfaction: {}".format(day,self.restaurant_rating))
      # generate 0+ parties based on the time of day & popularity of the restaurant
      self.generate_parties(self.sample_num_parties())     
        
        
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
    for a in self.appliances:
      daily_cost += a.daily_upkeep
    for t in self.tables:
      daily_cost += t.daily_upkeep
    for o in self.order_log[self.closing_order:]:
      daily_cost += o.total_cost
      self.closing_order = len(self.order_log)
    self.daily_costs.append(daily_cost)
    
  def calc_stats(self):
    if len(self.satisfaction_scores) > 0:
      self.restaurant_rating = np.mean(self.satisfaction_scores)

 
  def summarize(self):
    day = self.env.m_current_time().format("ddd MMM D")
    self.env.ledger.print("Summary for {}: satisfaction: {}".format(day,self.restaurant_rating))

  def final_report(self):
    print("*"*80)
    print("Simulation run for {} days.".format(self.ledger.num_days))
    print("*"*80)
    print("Parties entered: {}\nParties seated: {}\nParties paid: {}".format(len(self.entered_parties),len(self.seated_parties),len([c for c in self.checks if c > 0])))
    revenue = np.sum(self.checks)
    print("Total Revenue: {}".format(revenue))
    upfront_costs = np.sum([a.cost for a in self.appliances]) + np.sum([t.cost for t in self.tables])
    print("Total Upfront Costs: {}".format(upfront_costs))
    costs = np.sum(self.daily_costs)
    print("Total Daily Costs: {}".format(costs))
    print("Total Profit: {}".format(revenue-costs-upfront_costs))
    leftovers = len(self.entered_parties)-len(self.checks) #if we cut off the last day while people were dining
    if leftovers > 0:
      truncated_entered_parties = self.entered_parties[:-leftovers]
    else:
      truncated_entered_parties = self.entered_parties
    num_served = np.sum([p.size for i,p in enumerate(truncated_entered_parties) if self.checks[i]>0])
    print("Total individual customers served: {}\nAverage price per entree: {}".format(num_served,revenue/num_served))
    print("Avg Satisfaction Score: {}\nStd Satisfaction Score: {}".format(np.mean(self.satisfaction_scores), np.std(self.satisfaction_scores)))
    print("Final Restaurant Rating: {}".format(self.restaurant_rating))

class Order:
  def __init__(self, env, name, party, table):
    self.env = env
    self.day = self.env.day
    self.name = name
    self.party = party
    self.table = table
    self.status = "placed"
    self.equipment_type = "oven"
    self.bill = 0
    self.satisfactions = []
    self.cook_times = []
    self.total_cost = 0
  def place_order(self, kitchen, menu):
    self.env.ledger.print("{}: Placing order of size {} for {}".format(self.env.m_current_time().format("HH:mm:ss"),self.party.size,self.party.name))
    for diner in range(self.party.size):
        # choose a menu item
        meal_order = self.choose_menu_item(menu)
        self.bill += meal_order["price"]
        self.total_cost += meal_order["cost"]
        # submit the order
        appliance = yield kitchen.get(lambda appliance: all(req in appliance.capabilities for req in meal_order["requirements"]))
        self.status = "cooking"
        yield self.env.process(appliance.cook(self,meal_order))
        #yield self.env.timeout(4)
        self.env.ledger.print("Order {}/{} of {} for {} cooked in time {:.2f} with quality {:.2f}.".format(diner+1, self.party.size, meal_order["name"], self.party.name, self.cook_time, self.quality))
        self.satisfactions.append(self.quality)
        self.cook_times.append(self.cook_time)
        yield kitchen.put(appliance)
  
  def choose_menu_item(self, menu):
      budget = self.party.affluence * self.party.max_budget
      monetary_taste = self.party.taste * self.party.max_budget
      price_point = (budget + monetary_taste)/2
      return menu[np.argmin([np.abs(price_point-meal["price"]) for meal in menu])]

class Appliance:
  def __init__(self,env, name, attributes):
    self.env = env
    self.name = name
    self.parse_attributes(attributes)
  def cook(self,order,item):
    self.env.ledger.print("{} is cooking an order of {} for {}".format(self.name,item["name"],order.party.name))
    order.status = "cooking NOW"
    difficulty_penalty = 1
    difficulty_diff = item["difficulty"] - self.difficulty_rating
    if difficulty_diff > 0:
        difficulty_penalty -= difficulty_diff  
    order.quality = np.clip(self.quality.rvs()*difficulty_penalty,0,1)
    order.cook_time = self.cook_time.rvs()
    yield self.env.timeout(order.cook_time*60)
  def parse_attributes(self,attributes):
    self.capabilities = attributes["capabilities"]
    self.cook_time = norm(attributes["cook_time_mean"],attributes["cook_time_std"])
    self.quality = norm(attributes["quality_mean"],attributes["quality_std"])
    self.difficulty_rating = attributes["difficulty_rating"]
    self.daily_upkeep = attributes["daily_upkeep"]
    self.cost = attributes["cost"]

class Table:
  '''
    Tables are resources that can be filled by parties
  '''
  def __init__(self, env, name, attributes):
    self.env = env
    self.name = name
    self.party = None # a party object
    self.status = "empty"
    self.parse_attributes(attributes)
  
  def parse_attributes(self, attributes):
    self.x = attributes["x"]
    self.y = attributes["y"]
    self.radius = attributes["radius"] # each table is circumscribed in a circle
    self.seats = attributes["seats"]
    self.daily_upkeep = attributes["daily_upkeep"]
    self.cost = attributes["cost"]

class Party:
  '''
    Parties are generated and wait in a queue to be seated
    They may renege if they lose patience. Once seated, parties take time to 
    order, then they wait for food (again reneging if too long, noisy, etc), then
    they eat (renege if food quality is below their threshold), pay and leave
  '''
  def __init__(self, env, name, attributes):
    self.env = env
    self.name = name
    self.cum_noise = 0
    self.noise_counter = 0
    self.parse_attributes(attributes)
    self.max_wait_time = 60
    self.table = None
    self.perceived_noisiness = 0.0
    self.satisfaction = 0
    self.env.ledger.print("Welcoming Party {} of size {}.".format(self.name,self.size))
    
  def parse_attributes(self, attributes):
    #  ["size","affluence","taste","noisinesself.table.party = selfss","patience","noise_tolerance","space_tolerance"]
    self.size = attributes["size"] # number self.table.party = selfe party
    self.affluence = attributes["affluence"]
    self.taste = attributes["taste"]
    self.noisiness = attributes["noisiness"]
    self.leisureliness = attributes["leisureliness"]
    self.patience = attributes["patience"]
    self.noise_tolerance = attributes["noise_tolerance"]
    self.space_tolerance = attributes["space_tolerance"]
    self.max_budget = 100 # how much the richest of the rich can/would pay for a meal
    
  def wait_for_table(self, seating):
    start_time = self.env.m_current_time()
    waiting_patience_in_s = (self.patience)*self.max_wait_time*60 
#     with seating.get(lambda table: table.seats >= self.size) as req:
#       results = yield req #| self.env.timeout(self.patience)
#       print(type(req),results)
#     if req in results:
#       self.table = resultsget
#       print("Party {} is seated at {}".format(self.name,self.table.name))
#     # no reneg yet
#     else:get
#       print("Party {} is tired of waiting for a table.").format(self.name)
    with seating.get(lambda table: table.seats >= self.size) as req:
      res = yield req | self.env.timeout(waiting_patience_in_s)
      self.seating_wait = self.env.m_current_time() - start_time
      #print(res)
      if(req in res):
        self.table = res[req]
        self.table.party = self
        self.env.ledger.print("Party {} is seated at {} after waiting for {}".format(self.name,self.table.name,self.seating_wait))
        return True
      else:
        self.env.ledger.print("Party {} with patience rating {} is tired of waiting for a table after waiting for {}.".format(self.name,self.patience,self.seating_wait))
        return False
  def eat(self,order):
    self.env.ledger.print("Party {} is eating".format(self.name))
    self.satisfaction = np.mean(order.satisfactions) #should consider wait time here as well
    self.bill = order.bill
    yield self.env.timeout(10*60*self.size)
  
  def leave(self, seating):
    check = 0
    self.env.ledger.print("Party {} has left".format(self.name))
    if self.table:
      self.table.party = None
      subtotal = self.bill
      tip = self.satisfaction*0.3*subtotal
      check = subtotal + tip
      yield seating.put(self.table)
    return check, self.satisfaction

  def check_noise(self, tables):
    while True:
      yield self.env.timeout(120)
      noise = 0.0
      for t in tables:
        if t.party != self and t.party != None:
          sqrdist = (t.x - self.table.x)**2 + (t.y-self.table.y)**2
          noise += t.party.noisiness*t.party.size/sqrdist
      self.perceived_noisiness = noise
      perceived_noise_penalty = noise-self.noise_tolerance
      if perceived_noise_penalty > 0:
        self.satisfaction = np.max(self.satisfaction-perceived_noise_penalty,0)
      #print(noise)
      self.cum_noise += noise
      self.noise_counter += 1


if __name__=="__main__":
    equipment = [{"name":"Lame Pizza Oven", 
              "attributes":{"capabilities":["oven","pizza","steak"],
                            "cook_time_mean":7, "cook_time_std":1, 
                            "quality_mean":0.5, "quality_std":0.4,
                            "difficulty_rating":0.2, "cost":300,
                            "daily_upkeep":5, "reliability":0.2}},
                            {"name":"Lame Pizza Oven", 
              "attributes":{"capabilities":["oven","pizza","steak"],
                            "cook_time_mean":7, "cook_time_std":1, 
                            "quality_mean":0.5, "quality_std":0.4,
                            "difficulty_rating":0.2, "cost":300,
                            "daily_upkeep":5, "reliability":0.2}},
                            {"name":"Lame Pizza Oven", 
              "attributes":{"capabilities":["oven","pizza","steak"],
                            "cook_time_mean":7, "cook_time_std":1, 
                            "quality_mean":0.5, "quality_std":0.4,
                            "difficulty_rating":0.2, "cost":300,
                            "daily_upkeep":5, "reliability":0.2}},
                            {"name":"Lame Pizza Oven", 
              "attributes":{"capabilities":["oven","pizza","steak"],
                            "cook_time_mean":7, "cook_time_std":1, 
                            "quality_mean":0.5, "quality_std":0.4,
                            "difficulty_rating":0.2, "cost":300,
                            "daily_upkeep":5, "reliability":0.2}},
                            {"name":"Lame Pizza Oven", 
              "attributes":{"capabilities":["oven","pizza","steak"],
                            "cook_time_mean":7, "cook_time_std":1, 
                            "quality_mean":0.5, "quality_std":0.4,
                            "difficulty_rating":0.2, "cost":300,
                            "daily_upkeep":5, "reliability":0.2}},
            
                {"name":"Awesome Pizza Oven", 
                "attributes":{"capabilities":["oven","pizza","steak"],
                              "cook_time_mean":1, "cook_time_std":0.1, 
                              "quality_mean":0.7, "quality_std":0.1,
                              "difficulty_rating":0.8, "cost":4000,
                              "daily_upkeep":10, "reliability":0.9}},
                {"name":"Awesome Pizza Oven", 
                "attributes":{"capabilities":["oven","pizza","steak"],
                              "cook_time_mean":1, "cook_time_std":0.1, 
                              "quality_mean":0.7, "quality_std":0.1,
                              "difficulty_rating":0.8, "cost":4000,
                              "daily_upkeep":10, "reliability":0.9}}
                              ]
    tables = [{"name":"Table 1", 
            "attributes":{"x":2.1,"y":3.7,"radius":4,"seats":2,"cost":300,"daily_upkeep":1}},
            # {"name":"Table 2", 
            # "attributes":{"x":4.1,"y":5.7,"radius":7,"seats":5,"cost":800,"daily_upkeep":1}},
            # {"name":"Table 1", 
            # "attributes":{"x":12.1,"y":5.7,"radius":4,"seats":5,"cost":800,"daily_upkeep":1}},
            {"name":"Table 1", 
            "attributes":{"x":23.1,"y":13.7,"radius":4,"seats":5,"cost":800,"daily_upkeep":1}},
            {"name":"Table 1", 
            "attributes":{"x":26.1,"y":23.7,"radius":4,"seats":5,"cost":800,"daily_upkeep":1}},]
    r = Restaurant("Sophie's Kitchen", equipment, tables)
    r.simulate(days=7)
    #r.ledger.read_messages()
    r.final_report()
    #r.ledger.read_messages()
    # equipment2 = [
    #             {"name":"Awesome Pizza Oven", 
    #             "attributes":{"capabilities":["oven","pizza","steak"],
    #                           "cook_time_mean":4, "cook_time_std":0.1, 
    #                           "quality_mean":0.7, "quality_std":0.1,
    #                           "difficulty_rating":0.8,
    #                           "daily_upkeep":10, "reliability":0.9}}]
    # tables2 = [{"name":"Table 1", 
    #         "attributes":{"x":2.1,"y":3.7,"radius":4,"seats":2,"daily_upkeep":1}},
    #         {"name":"Table 2", 
    #         "attributes":{"x":14.1,"y":4.7,"radius":7,"seats":5,"daily_upkeep":1}},
    #         {"name":"Table 3", 
    #         "attributes":{"x":7.1,"y":2.7,"radius":7,"seats":8,"daily_upkeep":1}},
    #         {"name":"Table 4", 
    #         "attributes":{"x":11.1,"y":15.7,"radius":7,"seats":5,"daily_upkeep":1}}]



    # r2 = Restaurant("Sophie's Kitchen 2", equipment2, tables2)
    # r2.simulate(days=7)
    # r2.final_report()


    # equipment = [{"name":"Lame Pizza Oven", 
    #       "attributes":{"capabilities":["oven","pizza","steak"],
    #                     "cook_time_mean":10, "cook_time_std":1, 
    #                     "quality_mean":0.5, "quality_std":0.4,
    #                     "difficulty_rating":0.2,
    #                     "daily_upkeep":5, "reliability":0.2}},
        
    #           {"name":"Awesome Pizza Oven", 
    #           "attributes":{"capabilities":["oven","pizza","steak"],
    #                         "cook_time_mean":4, "cook_time_std":0.1, 
    #                         "quality_mean":0.7, "quality_std":0.1,
    #                         "difficulty_rating":0.8,
    #                         "daily_upkeep":10, "reliability":0.9}}]
    # tables = [{"name":"Table 1", 
    #         "attributes":{"x":2.1,"y":3.7,"radius":4,"seats":2,"daily_upkeep":1}},
    #         {"name":"Table 2", 
    #         "attributes":{"x":22.1,"y":55.7,"radius":7,"seats":5,"daily_upkeep":1}}]
    # r = Restaurant("Sophie's Kitchen", equipment, tables)
    # r.simulate(days=7)
    # r.final_report()