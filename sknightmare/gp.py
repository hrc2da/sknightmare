from skopt import gp_minimize
from skopt.space import Real, Integer, Categorical
import time
from restaurant import Restaurant
from skopt.plots import plot_convergence
from matplotlib import pyplot as plt
import json

def construct_equipment(table_type):
  equipment_choices = [{"name": "Lame Pizza Oven",
                  "attributes": {"capabilities": ["oven", "pizza", "steak"],
                                 "cook_time_mean":7, "cook_time_std":1,
                                 "quality_mean":0.5, "quality_std":0.4,
                                 "difficulty_rating":0.2, "cost":300,
                                 "daily_upkeep":5, "reliability":0.2, "radius": 25}},
               {"name": "Awesome Pizza Oven",
                  "attributes": {"capabilities": ["oven", "pizza", "steak"],
                                 "cook_time_mean":1, "cook_time_std":0.1,
                                 "quality_mean":0.7, "quality_std":0.1,
                                 "difficulty_rating":0.8, "cost":4000,
                                 "daily_upkeep":10, "reliability":0.9, "radius":25}}]
  return equipment_choices[table_type]


def construct_table(x,y,seats,cost):
  radius = 20 + 10*int(seats/4)
  return {"name": "Table " + str((x,y)),
               "attributes": {"x": x, "y": y, "radius": radius, "seats": seats, "cost": cost, "daily_upkeep": 1}}

def construct_waiter(x,y):
    return {"x":x, "y":y}

def construct_restaurant_json(x):
  equipment = []
  tables = []
  waiters = []
  if (x[0] == 1):
    equipment.append(construct_equipment(0))
  if (x[1] == 1):
    equipment.append(construct_equipment(1))
    
  for i in range(2,len(x),2):
    seats = 2
    cost = 275
    if (i >= 6):
      seats = 4
      cost = 600
    if (i>=8):
      seats = 8
      cost = 1050
    if(i <16 and x[i] >=0 and x[i+1]) > 0:
      tables.append(construct_table(x[i],x[i+1],seats,cost))
    if i >= 16 and x[i] >=0 and x[i+1] > 0:
        waiters.append({"x": x[i], "y": x[i+1]})
  r_json = {"tables" : tables, "equipment" : equipment, "waiters" : waiters}
  return r_json

def construct_restaurant(x):
  r_json = construct_restaurant_json(x)
  r = Restaurant("Sophie's Kitchen", r_json["equipment"], r_json["tables"], r_json["waiters"])
  return r

def reward(x):
  try:
    r = construct_restaurant(x)
    r.simulate(days=14)
    report = r.env.ledger.generate_final_report()
    return -1*report["revenue"]
  except:
    return 10000

def run_gp_agent():
    r_dim = Real(-1,1)
    i_dim = Integer(0,1)
    bounds = [i_dim, i_dim, r_dim,r_dim,r_dim,r_dim,r_dim,r_dim,r_dim, r_dim, r_dim,r_dim, r_dim,r_dim, r_dim,r_dim,r_dim,r_dim,r_dim,r_dim]
    res = gp_minimize(reward, bounds, acq_func = "EI", n_random_starts=10, n_calls = 50, random_state = int(time.time()))
    explored_points = res.x_iters
    r_json = {"restaurants" : [construct_restaurant_json(x) for x in explored_points]}
    with open('result.json', 'w') as fp:
      json.dump(r_json, fp)
    print(res)
    plot_convergence(res)
    plt.show() 

if __name__ == "__main__":
    run_gp_agent()
    


# x_test = [1, 1, 0.4304078120246819, 0.9960036919103774, -0.9397321202425597, -0.8524417103310282, 0.7546197789972506, 0.9123879858557826, -0.11687817846678272, 0.20825147793702126, 0.20087630761667152, 0.9975689614831686, 0.9149215231674757, 0.31227181969046014, 0.5847394296660067, -0.6922485599353478]

# r_test = construct_restaurant(x_test)
# r_test.simulate(days=30)
# report_test = r_test.env.ledger.generate_final_report()
     