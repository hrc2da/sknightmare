import Restauraunt

equipment = [{"name":"Lame Pizza Oven", 
              "attributes":{"capabilities":["oven","pizza","steak"],
                                          "cook_time_mean":10, "cook_time_std":1, 
                                          "quality_mean":0.5, "quality_std":0.4}},
            
            {"name":"Awesome Pizza Oven", 
             "attributes":{"capabilities":["oven","pizza","steak"],
                                          "cook_time_mean":4, "cook_time_std":0.1, 
                                          "quality_mean":0.7, "quality_std":0.1}}]
tables = [{"name":"Table 1", 
           "attributes":{"x":2.1,"y":3.7,"radius":4,"seats":2}},
          {"name":"Table 2", 
           "attributes":{"x":4.1,"y":5.7,"radius":7,"seats":5}}]
r = Restauraunt("Sophie's Kitchen", [equipment[1]], tables)
r.simulate(days=1)