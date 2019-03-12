from sknightmare.restaurant import Restaurant

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