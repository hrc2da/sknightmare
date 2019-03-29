from restaurant import Restaurant

if __name__ == "__main__":
    equipment = [{
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
                "x": 0.2,
                "y": 0.7,
                "radius": 0
            }
        },
        {
            "name": "Mini Bar",
            "attributes": {
                "category": "cooking",
                "capabilities": { "alcohol": {"quality_mean": 0.5, "quality_std" :0.1, "cook_time_mult":1, "cook_time_std":0.1} },
                "difficulty_rating": 0.8,
                "cost": 4000,
                "daily_upkeep": 80,
                "reliability": 0.9,
                "noisiness": 0.01,
                "atmosphere": 0.1,
                "x": 0.1,
                "y": 0.5,
                "radius": 0
            }
        }]

    tables = [{
    "type": "image",
    "size": 40,
    "seats": 2,
    "name": "Mini Bar",
    "svg_path": "svgs/2_bar_rect.svg",
    "attributes": {
        "cost": 350,
    "daily_upkeep": 1,
    "noisiness": 10,
    "privacy": 0.5,
    "x": 0.1,
    "y": 0.5,
    "seats": 2,
    "radius":0.1,
    "appliances": [
      {
        "name": "Mini Bar",
        "attributes": {
          "category": "cooking",
          "capabilities": { "alcohol": {"quality_mean": 0.5, "quality_std" :0.1, "cook_time_mult":1, "cook_time_std":0.1} },
          "difficulty_rating": 0.8,
          "cost": 4000,
          "daily_upkeep": 80,
          "reliability": 0.9,
          "noisiness": 0.01,
          "atmosphere": 0.1,
          "x": 0.1,
          "y": 0.5,
          "radius": 0.1
        }
      }
    ]
    }}]

    staff = [{'x': 0.2, 'y': 0.6}, {'x': 0.4, 'y': 0.4}]  # ,{'x': 0.7, 'y': 0.7}]
    r = Restaurant("Sophie's Kitchen", equipment, tables, staff)
    r.simulate(days=30)
    # r.ledger.read_messages()
    r.env.ledger.verbose = True
    r.env.ledger.generate_final_report()
    # r.ledger.read_messages()
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
