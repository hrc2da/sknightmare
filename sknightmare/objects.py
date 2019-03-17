import simpy
import numpy as np
from scipy.stats import norm
from random import seed, randint
seed(10)
from random_words import RandomWords
import arrow # for nicer datetimes
import math
import queue
from copy import deepcopy, copy


from records import TableStats, PartyStats, PartyStatus, MealStats

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
    self.qualities = []
    self.cook_times = []
    self.total_cost = 0
    self.meals = []
    self.total_cook_time = None

  def place_order(self, kitchen, menu):
    self.env.ledger.print("{}: Placing order of size {} for {}".format(self.env.m_current_time().format("HH:mm:ss"),self.party.size,self.party.name))
    self.order_start_time = self.env.m_current_time()
    for diner in range(self.party.size):
        # choose a menu item
        meal_order = self.choose_menu_item(menu)
        self.meals.append(meal_order)
        self.bill += meal_order["price"]
        self.total_cost += meal_order["cost"]
        # submit the order
        appliance = yield kitchen.get(lambda appliance: all(req in appliance.capabilities for req in meal_order["requirements"]))
        self.status = "cooking"
        start_time = self.env.m_current_time()
        yield self.env.process(appliance.cook(self,meal_order))
        #yield self.env.timeout(4)
        cook_time = self.env.m_current_time()-start_time
        self.env.ledger.print("Order {}/{} of {} for {} cooked in time {:.2f} with quality {:.2f}.".format(diner+1, self.party.size, meal_order["name"], self.party.name, self.cook_time, self.quality))
        self.qualities.append(self.quality)
        self.cook_times.append(cook_time)
        yield kitchen.put(appliance)
    order_end_time = self.env.m_current_time()
    self.total_cook_time = order_end_time - self.order_start_time
  def selection_noise(self):
    return np.random.normal(0,10)

  def choose_menu_item(self, menu):
      budget = self.party.affluence * self.party.max_budget
      #monetary_taste = self.party.taste * self.party.max_budget
      price_point = budget #(budget + monetary_taste)/2 + self.selection_noise()
      return menu[np.argmin([np.abs(price_point-meal["price"]) for meal in menu])]

  def get_total_cook_time(self):
    if self.total_cook_time == None:
      return self.env.m_current_time() - self.order_start_time
    else:
      return self.total_cook_time

  def get_completed_meals(self):
    completed_meals = []
    for i in range(len(self.qualities)):  
      completed_meals.append(MealStats(self.meals[i],self.cook_times[i],self.qualities[i]))
    return completed_meals


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
    self.parties = []
    self.status = "empty"
    self.generated_noise = []
    self.received_noise = []
    self.perceived_crowding = []
    self.max_noise_db = self.env.max_noise_db
    self.parse_attributes(attributes)

  
  def start_simulation(self):
    self.calculate_distances()
    self.env.process(self.update_stats())

  def parse_attributes(self, attributes):
    self.x = attributes["x"]
    self.y = attributes["y"]
    self.radius = attributes["radius"] # each table is circumscribed in a circle
    self.seats = attributes["seats"]
    self.daily_upkeep = attributes["daily_upkeep"]
    self.cost = attributes["cost"]

  def get_generated_noise(self, index = None):
    if len(self.generated_noise) == 0:
      return 0.0
    elif index != None:
      assert len(self.generated_noise) >= index
      return self.generated_noise[index]
    else:
      return self.generated_noise[-1]

  def get_received_noise(self, index = None):
    if len(self.received_noise) == 0:
      return 0.0
    elif index != None:
      assert len(self.received_noise) >= index
      return self.received_noise[index]
    else:
      return self.received_noise[-1]

  def update_stats(self):
    while True: #tables never leave the restaurant
      self.update_generated_noise()
      self.update_received_noise()
      self.update_crowding()
      yield self.env.timeout(5*60) # 5 minutes timeout

  def update_generated_noise(self):
    if self.party is not None:
      self.generated_noise.append(self.max_noise_db*self.party.noisiness*self.party.size)
    else:
      self.generated_noise.append(0)

  def update_received_noise(self):
    current_noise = 0
    for t in self.env.ledger.tables:
      if t != self:
        dist = self.distances[t.name]
        assert dist != 0
        current_noise += t.get_generated_noise()/dist
    self.received_noise.append(current_noise)

  def update_crowding(self):
    # this goes up based on whether nearby tables are occupied or not
    crowding = 0
    for t in self.env.ledger.tables:
      if t != self:
        if t.party == None:
          occupancy = 0
        else:
          occupancy = t.party.size
        dist = self.distances[t.name]
        assert dist != 0
        crowding += occupancy/dist
    self.perceived_crowding.append(crowding)

  def calculate_distances(self):
    self.distances = {}
    for t in self.env.ledger.tables:
      try:
        assert t.name not in self.distances
      except AssertionError as e:
        print("Table names must be unique!")
        raise(e)
      if t != self:
        sqrdist = np.linalg.norm(((t.x - self.x), (t.y-self.y)),2)
        assert sqrdist > 0
        self.distances[t.name] = sqrdist
    
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
    self.generate_normalized_weights()
    self.max_wait_time = self.env.max_wait_time
    self.table = None
    self.perceived_noisiness = 0.0
    self.satisfaction = self.mood
    self.env.ledger.print("Welcoming Party {} of size {}.".format(self.name,self.size))
    self.wait_start_time = self.env.m_current_time()
    self.status = PartyStatus.ENTERED

    
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
    self.paid_check = 0
    self.satisfaction = self.mood
    self.tolerance_weights = {}
    self.max_budget = self.env.max_budget # how much the richest of the rich can/would pay for a meal
    self.max_wait_tolerance = self.patience * self.env.max_wait_time
    self.max_noise_level = self.noise_tolerance * self.env.max_noise_db
  
  def generate_normalized_weights(self):
    # returns normalized relative weights for things that affect satisfaction
    total_weight = self.taste + self.patience + (1-self.noise_tolerance) + (1-self.space_tolerance)
    self.taste_weight = self.taste/total_weight
    self.patience_weight = self.patience/total_weight
    self.noise_weight = (1-self.noise_tolerance)/total_weight
    self.space_weight = (1-self.space_tolerance)/total_weight

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
      self.seating_wait = start_time.replace(seconds=waiting_patience_in_s)-start_time #in case we get interrupted
      res = yield req | self.env.timeout(waiting_patience_in_s)
      self.seating_wait = self.env.m_current_time() - start_time
      #print(res)
      if(req in res):
        self.table = res[req]
        self.table.party = self
        self.table.parties.append(self)
        self.env.ledger.print("Party {} is seated at {} after waiting for {}".format(self.name,self.table.name,self.seating_wait))
        self.status = PartyStatus.SEATED
        return True
      else:
        self.env.ledger.print("Party {} with patience rating {} is tired of waiting for a table after waiting for {}.".format(self.name,self.patience,self.seating_wait))
        return False

  def place_order(self,kitchen,menu):
    self.order = Order(self.env,self.env.m_rw(),self,self.table)
    self.status = PartyStatus.ORDERED
    self.env.ledger.print("Ordering")
    self.wait_start_time = self.env.m_current_time()
    yield self.env.process(self.order.place_order(kitchen,menu))

  def eat(self):
    start_time = self.env.m_current_time()
    self.env.ledger.print("Party {} is eating".format(self.name))
    self.status = PartyStatus.EATING
    # self.satisfaction += np.mean(order.satisfactions) #should consider wait time here as well
    self.bill = self.order.bill
    yield self.env.timeout(10*60*self.size)
    self.eating_time = self.env.m_current_time()-start_time
  
  def leave(self, seating):
    self.paid_check = 0
    self.satisfaction = max(0,self.satisfaction)
    self.env.ledger.print("Party {} has left".format(self.name))
    if self.table:
      self.status = PartyStatus.PAID
      self.table.party = None
      subtotal = self.bill
      tip = max(self.satisfaction,0)*0.3*subtotal
      self.paid_check = subtotal + tip
      yield seating.put(self.table)
      #self.table = None
      self.env.ledger.print("Party {} is paying {} with tip {} with sat {}".format(self.name,self.paid_check,tip,max(self.satisfaction,0)))
    return self.paid_check, self.satisfaction


  def update_satisfaction(self, tables):
    while self.status >= PartyStatus.SEATED and self.status < PartyStatus.PAID: # do this for as long as we're seated
      self.perceived_noisiness = self.table.get_received_noise()
      if self.status == PartyStatus.ORDERED:
        total_weight = self.patience_weight + self.noise_weight
        current_wait = self.env.m_current_time() - self.wait_start_time
        self.satisfaction = (1-total_weight)*self.satisfaction + self.patience_weight*(1-current_wait.total_seconds()/self.max_wait_tolerance) + self.noise_weight*(1-self.perceived_noisiness/self.max_noise_level)
      elif self.status == PartyStatus.EATING:
        total_weight = self.noise_weight + self.taste_weight
        if len(self.order.qualities) > 0:
          food_quality = np.mean(self.order.qualities)
        else:
          food_quality = 0
        self.satisfaction = (1-total_weight)*self.satisfaction + self.noise_weight*(1-self.perceived_noisiness/self.max_noise_level) +self.taste_weight*(food_quality)
      else:
        pass
        # total_weight = self.noise_weight
        # self.satisfaction = self.mood - (1-self.noise_tolerance)*self.perceived_noisiness
      yield self.env.timeout(5*60) # 5 minute loop



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