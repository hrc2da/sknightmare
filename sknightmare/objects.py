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
    self.satisfaction = self.mood
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
    self.mood = attributes["mood"]
    self.tolerance_weights = {}
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
    self.satisfaction += np.mean(order.satisfactions) #should consider wait time here as well
    self.bill = order.bill
    yield self.env.timeout(10*60*self.size)
  
  def leave(self, seating):
    self.paid_check = 0
    self.satisfaction = max(0,self.satisfaction)
    self.env.ledger.print("Party {} has left".format(self.name))
    if self.table:
      self.table.party = None
      subtotal = self.bill
      tip = max(self.satisfaction,0)*0.3*subtotal
      self.paid_check = subtotal + tip
      yield seating.put(self.table)
      self.table = None
      self.env.ledger.print("Party {} is paying {} with tip {} with sat {}".format(self.name,self.paid_check,tip,max(self.satisfaction,0)))
    return self.paid_check, self.satisfaction


  def update_satisfaction(self, tables):
    while self.table != None:
      noise = 0.0
      for t in tables:
        if t.party != self and t.party != None:
          try:
            sqrdist = (t.x - self.table.x)**2 + (t.y-self.table.y)**2
            noise += 1*t.party.noisiness*t.party.size/sqrdist
            if sqrdist == 0:
              print(self.noise_tolerance)
              print (self.table)
              print("t: " + str(t))
          except AttributeError as e:
            self.env.ledger.print("Table left while checking for noise")
            return
      self.perceived_noisiness = noise
      self.satisfaction = self.mood + (1-self.noise_tolerance)*self.perceived_noisiness
      yield self.env.timeout(300)



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
                            "daily_upkeep":5, "reliability":0.2}}
            
                # {"name":"Awesome Pizza Oven", 
                # "attributes":{"capabilities":["oven","pizza","steak"],
                #               "cook_time_mean":1, "cook_time_std":0.1, 
                #               "quality_mean":0.7, "quality_std":0.1,
                #               "difficulty_rating":0.8, "cost":4000,
                #               "daily_upkeep":10, "reliability":0.9}},
                # {"name":"Awesome Pizza Oven", 
                # "attributes":{"capabilities":["oven","pizza","steak"],
                #               "cook_time_mean":1, "cook_time_std":0.1, 
                #               "quality_mean":0.7, "quality_std":0.1,
                #               "difficulty_rating":0.8, "cost":4000,
                #               "daily_upkeep":10, "reliability":0.9}}
                              ]
    tables = [{"name":"Table 1", 
            "attributes":{"x":2.1,"y":3.7,"radius":4,"seats":2,"cost":300,"daily_upkeep":1}},
            # {"name":"Table 2", 
            # "attributes":{"x":4.1,"y":5.7,"radius":7,"seats":5,"cost":800,"daily_upkeep":1}},
            # {"name":"Table 1", 
            # "attributes":{"x":12.1,"y":5.7,"radius":4,"seats":5,"cost":800,"daily_upkeep":1}},
            {"name":"Table 1", 
            "attributes":{"x":22.3,"y":3.7,"radius":4,"seats":5,"cost":800,"daily_upkeep":1}},
            {"name":"Table 1", 
            "attributes":{"x":32.1,"y":2.7,"radius":4,"seats":5,"cost":800,"daily_upkeep":1}},]
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