import json
import matplotlib as mpl
mpl.use('TkAgg')
from skopt.plots import plot_convergence
from matplotlib import pyplot as plt
from skopt import gp_minimize
from skopt.space import Real, Integer, Categorical
import time
from restaurant import Restaurant



def construct_equipment(eq_type,x,y):
    equipment_choices = [{
                            "name": "Basic Oven",
                            "type": "image",
                            "size": 25,
                            "attributes": {
                            "category": "cooking",
                            "capabilities": { "pizza": {"quality_mean": 0.5, "quality_std" :0.4, "cook_time_mult":2, "cook_time_std":0.1}},
                            "path": "svgs/oven.svg",
                            "difficulty_rating": 0.2,
                            "cost": 300,
                            "daily_upkeep": 5,
                            "reliability": 0.2,
                            "noisiness": 0.1,
                            "atmosphere": 0.1,
                            "x": -1,
                            "y": -1,
                            "radius": 0
                            }
                         },
                         {
                            "name": "Brick Pizza Oven",
                            "type": "image",
                            "size": 35,
                            "attributes": {
                            "category": "cooking",
                            "capabilities": { "pizza": {"quality_mean": 0.7, "quality_std" :0.1, "cook_time_mult":0.8, "cook_time_std":1} },
                            "path": "svgs/kiln.svg",
                            "difficulty_rating": 0.8,
                            "cost": 4000,
                            "daily_upkeep": 10,
                            "reliability": 0.9,
                            "noisiness": 0.2,
                            "atmosphere": 0.6,
                            "x": -1,
                            "y": -1,
                            "radius": 0
                            }
                        },
                        {
                            "name": "Sushi Robot",
                            "type": "image",
                            "size": 25,
                            "attributes": {
                            "category": "cooking",
                            "capabilities": { "sushi": {"quality_mean": 0.5, "quality_std" :0.1, "cook_time_mult":1.2, "cook_time_std":0.1} },
                            "path": "svgs/robot.svg",
                            "difficulty_rating": 0.8,
                            "cost": 4000,
                            "daily_upkeep": 80,
                            "reliability": 0.9,
                            "noisiness": 0.4,
                            "atmosphere": 0.1,
                            "x": -1,
                            "y": -1,
                            "radius": 0
                            }
                        },
                        {
                            "name": "Sushi Master",
                            "type": "image",
                            "size": 25,
                            "attributes": {
                            "category": "cooking",
                            "capabilities": { "sushi": {"quality_mean": 0.9, "quality_std" :0.1, "cook_time_mult":0.9, "cook_time_std":0.1} },
                            "path": "svgs/sushimaster.svg",
                            "difficulty_rating": 1,
                            "cost": 100,
                            "daily_upkeep": 200,
                            "reliability": 0.9,
                            "noisiness": 0.1,
                            "atmosphere": 0.6,
                            "x": -1,
                            "y": -1,
                            "radius": 0
                            }
                        },
                        {
                            "name": "Pianist",
                            "type": "image",
                            "size": 25,
                            "attributes": {
                            "category": "entertainment",
                            "capabilities": { "noise_dampening": 1 },
                            "path": "svgs/piano.svg",
                            "cook_time_mean": 1,
                            "cook_time_std": 0.1,
                            "quality_mean": 0.9,
                            "quality_std": 0.1,
                            "difficulty_rating": 1,
                            "cost": 100,
                            "daily_upkeep": 200,
                            "reliability": 0.9,
                            "noisiness": 0.3,
                            "atmosphere": 0.6,
                            "x": -1,
                            "y": -1,
                            "radius": 0
                            }
                        }]
    eq =  equipment_choices[eq_type]
    eq["attributes"]["x"] = x
    eq["attributes"]["y"] = y
    return eq

def construct_table(x, y, seats, cost, svg_path):
    radius = 20 + 10*int(seats/4)
    return {"name": "Table " + str((x, y)),
            "attributes": {"x": x, 
                            "y": y, 
                            "radius": radius, 
                            "seats": seats, 
                            "cost": cost, 
                            "daily_upkeep": 1, 
                            "svg_path": svg_path,
                            "noisiness": 1,
                            "appliances":[]}}


def construct_waiter(x, y):
    return {"x": x, "y": y}


def construct_restaurant_json(x, profit):
    equipment = []
    tables = []
    waiters = []
    num_eq_slots = 5
    t_0 = num_eq_slots * 2

    for i in range(0, t_0, 2):
        if x[i] >= 0 and x[i+1] > 0:
            equipment.append(construct_equipment(i//2,x[i],x[i+1]))

    for i in range(t_0, len(x), 2):
        seats = 2
        cost = 275
        if (i >= 6):
            seats = 4
            cost = 600
            svg_path = "svgs/4_table_round.svg"
        if (i >= 8):
            seats = 8
            cost = 1050
            svg_path = "svgs/8_table_round.svg"
        if(i < 16 and x[i] >= 0 and x[i+1]) > 0:
            tables.append(construct_table(x[i], x[i+1], seats, cost, svg_path))
        if i >= 16 and x[i] >= 0 and x[i+1] > 0:
            waiters.append({"x": x[i], "y": x[i+1]})

    r_json = {"tables": tables, "equipment": equipment, "waiters": waiters, "profit": float(profit)}
    return r_json


def construct_restaurant(x):
    r_json = construct_restaurant_json(x, 0)
    r = Restaurant("Sophie's Kitchen", r_json["equipment"], r_json["tables"], r_json["waiters"])
    r.env.ledger.verbose = False
    return r


def reward(x):
    try:
        r = construct_restaurant(x)
        r.simulate(days=7)
        report = r.env.ledger.generate_final_report()
        return -1*report["profit"]
    except Exception as e:
        print("exception", e)
        return 10000000


def run_gp_agent():
    r_dim = Real(-1, 1)
    i_dim = Integer(0, 1)
    bounds = [i_dim, i_dim, r_dim, r_dim, r_dim, r_dim, r_dim, r_dim, r_dim, r_dim,
              r_dim, r_dim, r_dim, r_dim, r_dim, r_dim, r_dim, r_dim, r_dim, r_dim]
    res = gp_minimize(reward, bounds, acq_func="EI", n_random_starts=10, n_calls=50, random_state=int(time.time()))
    explored_points = res.x_iters
    r_json = {"restaurants": [construct_restaurant_json(x) for x in explored_points]}
    with open('result.json', 'w') as fp:
        json.dump(r_json, fp)
    print(res)
    plot_convergence(res)
    plt.show()


def run_gp_flask():
    r_dim = Real(-1, 1)
    i_dim = Integer(0, 1)
    bounds = [i_dim, i_dim, r_dim, r_dim, r_dim, r_dim, r_dim, r_dim, r_dim, r_dim,
              r_dim, r_dim, r_dim, r_dim, r_dim, r_dim, r_dim, r_dim, r_dim, r_dim]
    res = gp_minimize(reward, bounds, acq_func="EI", n_random_starts=10, n_calls=50, random_state=int(time.time()))
    profits = res.func_vals
    explored_points = res.x_iters
    return {"restaurants": [construct_restaurant_json(x, profits[i]) for i, x in enumerate(explored_points)]}


if __name__ == "__main__":
    run_gp_agent()


# x_test = [1, 1, 0.4304078120246819, 0.9960036919103774, -0.9397321202425597, -0.8524417103310282, 0.7546197789972506, 0.9123879858557826, -0.11687817846678272, 0.20825147793702126, 0.20087630761667152, 0.9975689614831686, 0.9149215231674757, 0.31227181969046014, 0.5847394296660067, -0.6922485599353478]

# r_test = construct_restaurant(x_test)
# r_test.simulate(days=30)
# report_test = r_test.env.ledger.generate_final_report()
