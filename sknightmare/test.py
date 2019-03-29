import unittest
from restaurant import Restaurant


class HelloTest(unittest.TestCase):
    def test_the_test(self):
        self.assertEqual(1+1, 2)


class RestaurantRuns(unittest.TestCase):
    def test_it_runs(self):
        equipment = [{"name": "Lame Pizza Oven",
                      "attributes": {"capabilities": ["oven", "pizza", "steak"],
                                     "cook_time_mean":7, "cook_time_std":1,
                                     "quality_mean":0.5, "quality_std":0.4,
                                     "difficulty_rating":0.2, "cost":300,
                                     "daily_upkeep":5, "reliability":0.2}},
                     {"name": "Lame Pizza Oven",
                      "attributes": {"capabilities": ["oven", "pizza", "steak"],
                                     "cook_time_mean":7, "cook_time_std":1,
                                     "quality_mean":0.5, "quality_std":0.4,
                                     "difficulty_rating":0.2, "cost":300,
                                     "daily_upkeep":5, "reliability":0.2}},
                     {"name": "Lame Pizza Oven",
                      "attributes": {"capabilities": ["oven", "pizza", "steak"],
                                     "cook_time_mean":7, "cook_time_std":1,
                                     "quality_mean":0.5, "quality_std":0.4,
                                     "difficulty_rating":0.2, "cost":300,
                                     "daily_upkeep":5, "reliability":0.2}},
                     {"name": "Lame Pizza Oven",
                      "attributes": {"capabilities": ["oven", "pizza", "steak"],
                                     "cook_time_mean":7, "cook_time_std":1,
                                     "quality_mean":0.5, "quality_std":0.4,
                                     "difficulty_rating":0.2, "cost":300,
                                     "daily_upkeep":5, "reliability":0.2}},
                     {"name": "Lame Pizza Oven",
                      "attributes": {"capabilities": ["oven", "pizza", "steak"],
                                     "cook_time_mean":7, "cook_time_std":1,
                                     "quality_mean":0.5, "quality_std":0.4,
                                     "difficulty_rating":0.2, "cost":300,
                                     "daily_upkeep":5, "reliability":0.2}},

                     {"name": "Awesome Pizza Oven",
                      "attributes": {"capabilities": ["oven", "pizza", "steak"],
                                     "cook_time_mean":1, "cook_time_std":0.1,
                                     "quality_mean":0.7, "quality_std":0.1,
                                     "difficulty_rating":0.8, "cost":4000,
                                     "daily_upkeep":10, "reliability":0.9}},
                     {"name": "Awesome Pizza Oven",
                      "attributes": {"capabilities": ["oven", "pizza", "steak"],
                                     "cook_time_mean":1, "cook_time_std":0.1,
                                     "quality_mean":0.7, "quality_std":0.1,
                                     "difficulty_rating":0.8, "cost":4000,
                                     "daily_upkeep":10, "reliability":0.9}},
                     {"name": "Bar 1",
                      "attributes": {"capabilities": ["alcohol"],
                                     "cook_time_mean": 0.3, "cook_time_std":0.5,
                                     "quality_mean":0.6, "quality_std":0.1,
                                     "difficulty_rating":0.5, "cost":2000,
                                     "daily_upkeep":200, "reliability":0.8}}
                     ]
        tables = [{"name": "Table 1",
                   "attributes": {"x": 0.21, "y": 0.27, "radius": 4, "seats": 2, "cost": 300, "daily_upkeep": 1}},
                  # {"name":"Table 2",
                  # "attributes":{"x":4.1,"y":5.7,"radius":7,"seats":5,"cost":800,"daily_upkeep":1}},
                  # {"name":"Table 1",
                  # "attributes":{"x":12.1,"y":5.7,"radius":4,"seats":5,"cost":800,"daily_upkeep":1}},
                  {"name": "Table 2",
                   "attributes": {"x": 0.31, "y": 0.37, "radius": 4, "seats": 5, "cost": 800, "daily_upkeep": 1}},
                  {"name": "Table 3",
                   "attributes": {"x": 0.1, "y": 0.7, "radius": 4, "seats": 5, "cost": 800, "daily_upkeep": 1}},
                  {"name": "Bar 1",
                   "attributes": {"x": 0.7, "y": 0.3, "radius": 0.2, "seats": 8, "cost": 1000, "daily_upkeep": 1}}]

        staff = [{'x': 0.2, 'y': 0.6}, {'x': 0.4, 'y': 0.4}]  # ,{'x': 0.7, 'y': 0.7}]
        r = Restaurant("Sophie's Kitchen", equipment, tables, staff)
        r.simulate(days=30)
        # r.ledger.read_messages()
        r.env.ledger.generate_final_report()
        self.assertEqual(1+1, 2)


if __name__ == '__main__':
    unittest.main()
# equipment = [{"name": "Lame Pizza Oven",
#               "attributes": {"capabilities": ["oven", "pizza", "steak"],
#                              "cook_time_mean":10, "cook_time_std":1,
#                              "quality_mean":0.5, "quality_std":0.4}},

#              {"name": "Awesome Pizza Oven",
#               "attributes": {"capabilities": ["oven", "pizza", "steak"],
#                              "cook_time_mean":4, "cook_time_std":0.1,
#                              "quality_mean":0.7, "quality_std":0.1}}]
# tables = [{"name": "Table 1",
#            "attributes": {"x": 0.1, "y": 0.7, "radius": 4, "seats": 2}},
#           {"name": "Table 2",
#            "attributes": {"x": 0.4, "y": 0.2, "radius": 7, "seats": 5}}]

# staff = [{'x': .5, 'y': 0.5}]

# r = Restauraunt("Sophie's Kitchen", equipment, tables, staff)
# r.simulate(days=1)
