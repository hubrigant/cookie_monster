import requests
from bs4 import BeautifulSoup
import re
from time import sleep
import sqlite3
import logging

logging.basicConfig(filename="output.log", level=logging.INFO,
                    format=('%(asctime)s - %(levelname)s - %(message)s'))


conn = sqlite3.connect('recipes.db')
c = conn.cursor()


base_url = "http://www.foodnetwork.com"
url_base = "http:"


def recipe_search(query, page=1, sortby="Best Match"):
    """
    max of 10 recipes per request
    return: RThumbnail list
    """
    url = "http://www.foodnetwork.com/search/" + query
    url = url + "-/p/" + page + "/CUSTOM_FACET:RECIPE_FACET"
    articles = []
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html5lib")
    recipe_cards = soup.findAll('div',
                    attrs={'class': 'o-ResultCard__m-MediaBlock m-MediaBlock'})
    for row in recipe_cards:
        title_raw = row.h3.a.span.text
        title = re.sub("-", ":", title_raw)
        uri = row.h3.a.get("href")
        url = url_base + uri
        t = (url, title)
        recipe_id = url.split('-')[-1]
        c.execute("INSERT INTO urls (url, title) VALUES (?, ?)", t)
        conn.commit()
        articles.append({"title": title, "url": url, "recipe_id": recipe_id})
    return articles


def get_n_recipes(query, n=10):
    # n = 2840
    calls = n / 10
    page = 1
    query = "cookies"
    rthumbnails = []
    logging.info("DEV> len(rthumbnails): ", len(rthumbnails))
    logging.debug("Searching for ", n, " recipes related to ", query,
          "calls: ", calls, "; page: ", page)
    while calls >= 0:
        curr_rthumbnails = recipe_search(query, page)
        if len(curr_rthumbnails) == 0:
            break
        rthumbnails.extend(curr_rthumbnails)
        print("DEV> page: ", page, "; calls: ", calls)
        page += 1
        calls -= 1
        sleep(1)
    return rthumbnails


def main():
    # Get list of cookie recipes
    #
    # The first version grabs the list of recipe URLs from FN
    # The second grabs from the local database cache created by the first
    #
    # url_list = get_n_recipes("cookies", n=2840)
    # c.execute("SELECT title, url FROM urls")
    # url_list = c.fetchall()
    # logging.debug("url_list is a: ", type(url_list[0]))
    # sys.stdout.flush()
    recipes = dict()
    ingredients = []
    cnt = 0

    # Loop through recipe list and process each recipe
    for (title, url) in c.execute("SELECT title, url FROM urls"):
        sleep(1)
        # r = requests.get(recipe["url"])
        # logging.debug("Recipe is: ", recipe[0])
        recipe_id = url.split('-')[-1]
        recipe_key = title + "-" + recipe_id
        recipe_key = re.sub("\s+", '_', recipe_key)
        r = requests.get(url)
        soup = BeautifulSoup(r.text, "html5lib")
        # ingredients_list = soup.find("li",
        #                    attrs={"class": "o-Ingredients__a-ListItem"})
        ingredients_list = soup.find("label",
                            attrs={"class": "o-Ingredients__a-ListItemText"})
        # ingredients.extend(ingredients_list.findAll("label"))
        #                attrs={"class": "o-Ingredients__a-ListItem"}))
        try:
            # if not ingredients_list.match("^\s+$"):
            # for entry in ingredients_list:
            #    logging.debug("Entry: ", entry)
            logging.debug("Size of ingredients: ", len(ingredients_list))
            for raw_ing in ingredients_list:
                # t = (raw_ing,)
                # c.execute("INSERT INTO raw_ingredients (ingredient) VALUES (?)",
                #          raw_ing)
                # conn.commit()
                sql_str = "INSERT INTO raw_ingredients (ingredient) VALUES "
                sql_str = sql_str + "(\'" + raw_ing + "\')"
                logging.debug(sql_str)
                ingredients.append(sql_str)
                # recipes.update(title = sql_str)
                if recipe_key not in recipes:
                    recipes[recipe_key] = []
                recipes[recipe_key].append({"title": title,
                                            "sql_str": sql_str})
                if cnt % 100 == 0:
                    logging.info("DEV[" + str(cnt) + "]> " + recipe_key)
                cnt += 1
        except TypeError as e:
            logging.error("Error thrown: ", e)
            continue
    max_title_len = 0
    max_sql_len = 0
    for key in recipes:
        title = recipes[key]["title"]
        sql_str = recipes[key]["sql_str"]
        print(sql_str)
        if len(title) > max_title_len:
            max_title_len = len(title)
        if len(sql_str) < max_sql_len:
            max_sql_len = len(sql_str)
    print("Max title: ", max_title_len)
    print("Max sql: ", max_sql_len)
    conn.close()


if __name__ == "__main__":
    main()
