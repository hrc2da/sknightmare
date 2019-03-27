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
    self.drink_qualities = []
    self.cook_times = []
    self.mix_times = []
    self.total_cost = 0
    self.meals = []
    self.drinks = []
    self.order_start_time = None
    self.total_cook_time = None
    self.drink_order_times = []


  def place_order(self, kitchen, menu):
    self.env.ledger.print("{}: Placing order of size {} for {}".format(self.env.m_current_time().format("HH:mm:ss"),self.party.size,self.party.name))
    self.order_start_time = self.env.m_current_time()
    # TODO: Refactor to loop over order selection and then loop again to cook orders
    for diner in range(self.party.size):
        # choose a menu item
        meal_order = self.choose_menu_item(menu)
        self.meals.append(meal_order)
        self.bill += meal_order["price"]
        self.total_cost += meal_order["cost"]
        # submit the order
        appliance = yield kitchen.get(lambda appliance: any(req in appliance.capabilities for req in meal_order["requirements"]))
        self.status = "cooking"
        start_time = self.env.m_current_time()
        quality, raw_cook_time = yield self.env.process(appliance.cook(self,meal_order))
        #yield self.env.timeout(4)
        cook_time = self.env.m_current_time()-start_time
        self.cook_time = cook_time
        self.env.ledger.print("Order {}/{} of {} for {} cooked in time {:.2f} with quality {:.2f}.".format(diner+1, self.party.size, meal_order["name"], self.party.name, raw_cook_time, quality))
        self.qualities.append(quality)
        self.cook_times.append(cook_time)
        yield kitchen.put(appliance)
    order_end_time = self.env.m_current_time()
    self.total_cook_time = order_end_time - self.order_start_time

  def place_drink_order(self, kitchen, menu):
    self.env.ledger.print("{}: Placing order of size {} for {}".format(self.env.m_current_time().format("HH:mm:ss"),self.party.size,self.party.name))
    order_start_time = self.env.m_current_time()
    for diner in range(self.party.size):
      drink_order = self.choose_menu_item(menu)
      self.drinks.append(drink_order)
      self.bill += drink_order["price"]
      self.total_cost += drink_order["cost"]
      appliance = yield kitchen.get(lambda appliance: all(req in appliance.capabilities for req in drink_order["requirements"]))
      start_time = self.env.m_current_time()
      quality, raw_mix_time = yield self.env.process(appliance.cook(self,drink_order))
      mix_time = self.env.m_current_time()-start_time
      self.mix_times.append(mix_time)
      self.drink_qualities.append(quality)
      yield kitchen.put(appliance)
    order_end_time = self.env.m_current_time()
    self.drink_order_times.append(order_end_time - order_start_time)



  def selection_noise(self):
    return np.random.normal(0,10)

  def choose_menu_item(self, menu):
      menu_stats = self.env.ledger.get_menu_stats()
      # print(menu_stats)
      budget = self.party.affluence * self.party.max_budget
      appeals = {}
      max_appeal = -1000000
      best_meal = None
      for meal in menu:
        unaffordability = np.abs(budget-meal["price"])
        try:
          stats = menu_stats[meal["name"]]
          quality = stats["quality"][0]
          volume = stats["volume"][0]
          cook_time = stats["cook_time"][0]
        except KeyError as e:
          print("Key error for:",e)
          quality = 0.5
          volume = 0
          cook_time = meal["cook_time"]
        #weight this by user menu)
        appeal = quality*volume/((1-self.party.patience)*cook_time+unaffordability) +self.selection_noise()
        appeals[meal["name"]] = appeal
        if best_meal is None:
          max_appeal = appeal
          best_meal = meal
        elif appeal > max_appeal:
          max_appeal = appeal
          best_meal = meal
      #monetary_taste = self.party.taste * self.party.max_budget
      #price_point = budget #(budget + monetary_taste)/2 + self.selection_noise()
      #return menu[np.argmin([np.abs(price_point-meal["price"]) for meal in menu])]
      return best_meal

  def get_total_cook_time(self):
    if self.order_start_time == None:
      now = self.env.m_current_time()
      return now - now
    if self.total_cook_time == None:
      return self.env.m_current_time() - self.order_start_time
    else:
      return self.total_cook_time

  def get_completed_meals(self):
    completed_meals = []
    for i in range(len(self.qualities)):  
      completed_meals.append(MealStats(self.meals[i],self.cook_times[i],self.qualities[i]))
    return completed_meals

  def get_completed_drinks(self):
    completed_drinks = []
    for i in range(len(self.drink_qualities)):
      completed_drinks.append((MealStats(self.drinks[i],self.mix_times[i],self.drink_qualities[i])))
    return completed_drinks

class Appliance:
  def __init__(self,env, name, attributes):
    self.env = env
    self.name = name
    self.parse_attributes(attributes)
  def cook(self,order,item):
    self.env.ledger.print("{} is cooking an order of {} for {}".format(self.name,item["name"],order.party.name))
    order.status = "cooking NOW"
    # TODO: does the difficulty penalty make sense?
    difficulty_penalty = 1
    difficulty_diff = item["difficulty"] - self.difficulty_rating
    if difficulty_diff > 0:
        difficulty_penalty -= difficulty_diff  
    
    best_capability = None
    for req in item["requirements"]:
      if req in self.capabilities:
        best_capability = self.capabilities[req]
        break
    qmean = best_capability["quality_mean"]
    qstd = best_capability["quality_std"]
    ctmean = best_capability["cook_time_mult"]*item["cook_time"]
    ctstd = best_capability["cook_time_std"]
    quality = np.clip(np.random.normal(loc=qmean, scale=qstd)*difficulty_penalty,0,1)
    cook_time = int(max(0.5,np.random.normal(loc=ctmean, scale=ctstd)))
    yield self.env.timeout(cook_time*60)
    return quality, cook_time
  def parse_attributes(self,attributes):
    self.x = attributes["x"]
    self.y = attributes["y"]
    self.capabilities = attributes["capabilities"]
    self.difficulty_rating = attributes["difficulty_rating"]
    self.daily_upkeep = attributes["daily_upkeep"]
    self.cost = attributes["cost"]
    self.noisiness = attributes["noisiness"]
    self.atmosphere = attributes["atmosphere"]
  def get_generated_noise(self):
    raw_noise = self.env.max_noise_db*self.noisiness
    if "noise_dampening" in self.capabilities:
      raw_noise -= self.capabilities["noise_dampening"]*self.env.max_noise_db
    return raw_noise

# class Bar(Table):
#   '''
#     A special kind of table
#   '''

#   def __init__(self, env, name, attributes):
#     super().__init__(self,env,name,attributes)
    
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
    self.get_service_rating()
    self.env.process(self.update_stats())

  def parse_attributes(self, attributes):
    self.x = attributes["x"]
    self.y = attributes["y"]
    self.radius = attributes["radius"] # each table is circumscribed in a circle
    self.seats = attributes["seats"]
    self.daily_upkeep = attributes["daily_upkeep"]
    self.cost = attributes["cost"]
    self.noisiness = attributes["noisiness"]
    
  def get_service_rating(self):
    '''
      based on the distance to all wait staff, calculate a service rating that will be used
      to update party satisfaction
    '''
    raw_rating = 0
    max_dist = np.linalg.norm((1,1))
    for w in self.env.ledger.staff:
      distance = np.linalg.norm((self.x - w.x, self.y-w.y),2)
      raw_rating += (1-distance/max_dist)/len(self.env.ledger.tables) #self.env.ledger.capacity# 
    self.service_rating = np.clip(raw_rating,0,1)
    # print("SERVICE_RATING:",self.service_rating)


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
      yield self.env.timeout(self.env.sim_loop_delay) # 5 minutes timeout

  def update_generated_noise(self):
    if self.party is not None:
      self.generated_noise.append(self.max_noise_db*self.party.noisiness*self.party.size*self.noisiness)
    else:
      self.generated_noise.append(0)

  def update_received_noise(self):
    current_noise = 0
    for t in self.env.ledger.tables:
      if t != self:
        dist = self.table_distances[t.name]
        assert dist != 0
        current_noise += min(t.get_generated_noise()/(dist**2),self.env.max_noise_db) # capping received noise at max level to prevent exploding noise on overlaps
    if self.env.ledger.appliances:
      for a in self.env.ledger.appliances:
        dist = self.appliance_distances[a.name]
        assert dist != 0
        current_noise += min(a.get_generated_noise()/(dist**2),self.env.max_noise_db)
    self.received_noise.append(max(0,current_noise))

  def update_crowding(self):
    # this goes up based on whether nearby tables are occupied or not
    crowding = 0
    for t in self.env.ledger.tables:
      if t != self:
        if t.party == None:
          occupancy = 0
        else:
          occupancy = t.party.size
        dist = self.table_distances[t.name]
        assert dist != 0
        crowding += occupancy/dist
    self.perceived_crowding.append(crowding)

  def calculate_distances(self):
    self.table_distances = {}
    self.appliance_distances = {}
    for t in self.env.ledger.tables:
      try:
        assert t.name not in self.table_distances
      except AssertionError as e:
        print("Table names must be unique!")
        raise(e)
      if t != self:
        sqrdist = np.linalg.norm(((t.x - self.x), (t.y - self.y)),2)
        assert sqrdist > 0
        self.table_distances[t.name] = sqrdist
    for a in self.env.ledger.appliances:
      sqrdist = max(0.01,np.linalg.norm(((a.x - self.x), (a.y - self.y)),2)) # assuming the only on-top overlaps are from appliance/table hybrids like bars
      assert sqrdist > 0
      self.appliance_distances[a.name] = sqrdist


class Staff:
  '''
    Really dumb basic class for now, but may make more useful later
  '''
  def __init__(self,x,y):
    self.x = x
    self.y = y

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
    self.service = []
    self.env.ledger.print("Welcoming Party {} of size {}.".format(self.name,self.size))
    self.wait_start_time = self.env.m_current_time()
    self.status = PartyStatus.ENTERED
    self.order = Order(self.env,self.env.m_rw(),self,self.table)

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
    self.sensitivity = attributes["sensitivity"]
    self.appetite = attributes["appetite"]
    self.drink_frequency = attributes["drink_frequency"]
    self.bill = 0
    self.paid_check = 0
    self.satisfaction = self.mood
    self.tolerance_weights = {}
    self.max_budget = self.env.max_budget # how much the richest of the rich can/would pay for a meal
    self.max_wait_tolerance = self.patience * self.env.max_wait_time
    self.max_noise_level = self.noise_tolerance * self.env.max_noise_db

  def generate_normalized_weights(self):
    # returns normalized relative weights for things that affect satisfaction
    total_weight = self.taste + self.patience + (1-self.noise_tolerance) + (1-self.space_tolerance) + self.sensitivity
    self.taste_weight = self.taste/total_weight
    self.patience_weight = self.patience/total_weight
    self.noise_weight = (1-self.noise_tolerance)/total_weight
    self.space_weight = (1-self.space_tolerance)/total_weight
    self.sensitivity_weight = self.sensitivity/total_weight
  
  def start_ordering_drinks(self,kitchen,menu):
     while self.status < PartyStatus.PAID:
      if self.status >= PartyStatus.SEATED:
        # order and pay for a drink
        if np.random.uniform(0,1) < self.drink_frequency:
          yield self.env.process(self.order.place_drink_order(kitchen,menu))
        # drink it
      yield self.env.timeout(30*60)

  def chill(self):
    '''
      once seated, spend some time before leaving (essentially this happens when there is no kitchen)
    '''
    self.status = PartyStatus.EATING
    start_time = self.env.m_current_time()
    yield self.env.timeout(30*60*self.size*self.leisureliness)
    self.eating_time = self.env.m_current_time()-start_time

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
    if np.random.uniform(0,1) > 0.05:
      return False
  def place_order(self,kitchen,menu):
    self.status = PartyStatus.ORDERED
    self.env.ledger.print("Ordering")
    self.wait_start_time = self.env.m_current_time()
    yield self.env.process(self.order.place_order(kitchen,menu))

  def eat(self):
    start_time = self.env.m_current_time()
    self.env.ledger.print("Party {} is eating".format(self.name))
    self.status = PartyStatus.EATING
    # self.satisfaction += np.mean(order.satisfactions) #should consider wait time here as well
    # self.bill = self.order.bill
    yield self.env.timeout(30*60*self.size*self.leisureliness)
    self.eating_time = self.env.m_current_time()-start_time
  
  def leave(self, seating):
    self.paid_check = 0
    self.satisfaction = max(0,self.satisfaction)
    self.env.ledger.print("Party {} has left".format(self.name))
    self.status = PartyStatus.LEFT
    if self.table:
      self.status = PartyStatus.PAID
      self.table.party = None
      subtotal = self.order.bill
      tip = max(self.satisfaction,0)*0.3*subtotal
      self.paid_check = subtotal + tip
      yield seating.put(self.table)
      #self.table = None
      self.env.ledger.print("Party {} is paying {} with tip {} with sat {}".format(self.name,self.paid_check,tip,max(self.satisfaction,0)))
    return self.paid_check, self.satisfaction


  def update_satisfaction(self, tables):
    while self.status < PartyStatus.PAID: # do this for as long as we're seated
      if self.status >= PartyStatus.SEATED:
        service_draw = np.random.rand()
        if service_draw <= self.table.service_rating:
          service = 1
        else:
          service = 0
        self.service.append(service)
        self.perceived_noisiness = self.table.get_received_noise()
        if self.status == PartyStatus.SEATED or self.status == PartyStatus.ORDERED:
          total_weight = self.patience_weight + self.noise_weight + self.sensitivity
          current_wait = self.env.m_current_time() - self.wait_start_time
          self.satisfaction = (1-total_weight)*self.satisfaction + self.patience_weight*(1-min(1,current_wait.total_seconds()/self.max_wait_tolerance)) + self.noise_weight*(1-min(1,self.perceived_noisiness/self.max_noise_level))
          self.satisfaction += self.sensitivity_weight*service #split onto a second line just for readability
        elif self.status == PartyStatus.EATING:
          total_weight = self.noise_weight + self.taste_weight + self.sensitivity
          if len(self.order.qualities) > 0:
            food_quality = np.mean(self.order.qualities)
          else:
            food_quality = 0
          self.satisfaction = (1-total_weight)*self.satisfaction + self.noise_weight*(1-min(1,self.perceived_noisiness/self.max_noise_level)) +self.taste_weight*(food_quality) + self.sensitivity_weight*service
        else:
          pass
        # total_weight = self.noise_weight
        # self.satisfaction = self.mood - (1-self.noise_tolerance)*self.perceived_noisiness
      yield self.env.timeout(self.env.sim_loop_delay) # 5 minute loop



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