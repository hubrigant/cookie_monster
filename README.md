# cookie_monster
Attempting to learn about machine learning by analyzing cookie recipes. There are two goals of this project:
1. To be able to classify a previously-unseen recipe as being for cookies or for something else
1. To be able to generate an idealized cookie recipe

Eventually, there will be analysis done on the ingredients, the ratio of each ingredient to the overall recipe, and the rating/popularity of the recipe. This will theoretically help build a system to generate a net-new recipe to see how well that works out.

The current incarnation of scrape_pot.py is supposed to get the list of URLs for all cookie recipes from FN, then slowly look at each one to grab ingredient lists, cook/prep time, etc. to be stored in a local database for later parsing and eventually training the yet-to-be-built machine learning algorithm.

The file [ingredient-training.csv](ingredient-training.csv) is intended to be used to train a transformation model to convert from the raw, unstructured ingredient item from the ingredients list into:
* A label (ingredient)
* Several features
  * quantity: the quantity of the given measure (0.5 for 1/2 cup)
  * measure: the unit of measure (tablespoons, teaspoons, grams, cups, pounds, etc.)
  * condition: any special condition the ingredient should be in ("packed" for "packed brown sugar", "crushed" for "crushed walnuts", etc.)
  * recipe count: the total number of recipes for which this ingredient is included
  * rating total: the sum of all ratings (to be used to derrive weighted quality and popularity of recipes)
  * review count: the count of all reviews (to be used to derrive weighted quality and popularity of recipes)
  * cookieness total: the total of cookieness values for all recipes that include this ingredient

This data has already been manually preprocessed, but the features are not yet numerically indexed, nor is the data formatted properly for input into the machine learning model.
