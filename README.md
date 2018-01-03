# cookie_monster
Attempting to learn about machine learning by analyzing cookie recipes

The current incarnation of scrape_pot.py is supposed to get the list of URLs for all cookie recipes from FN, then slowly look at each one to grab ingredient lists, cook/prep time, etc. to be stored in a local database for later parsing and eventually training the yet-to-be-built machine learning algorithm.

Eventually, there will be analysis done on the ingredients, the ratio of each ingredient to the overall recipe, and the rating/popularity of the recipe. This will theoretically help build a system to generate a net-new recipe to see how well that works out.

This is definitely a work-in-progress. As it stands, the scrape_pot code doesn't work (I'm stuck building a list of unique ingredients that will eventually become a list of columns in the parsed data table)
