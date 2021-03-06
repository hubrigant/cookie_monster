from __future__ import print_function
import requests
from bs4 import BeautifulSoup
import re
from time import sleep, time
import sqlite3
import sys
import logging

logging.basicConfig(filename="output.log", level=logging.DEBUG,
                    format=('%(asctime)s - %(levelname)s - %(message)s'))

conn = sqlite3.connect('recipes.db')
c = conn.cursor()
runtime = str(int(time()))
tup = (runtime,)
logging.info("DEV> started at ", runtime)
# c.execute("UPDATE urls SET cached_at = ? WHERE cached_at < 1", tup)
# conn.commit

base_url = "http://www.foodnetwork.com"
url_base = "http:"


# def eprint(*args, **kwargs):
#    print(*args, file=sys.stderr, **kwargs)


def recipe_search(query, page=1, sortby="Best Match"):
    """
    max of 10 recipes per request
    return: RThumbnail list
    """
    url = "http://www.foodnetwork.com/search/" + query
    url = url + "-/p/" + page
    url = url + "/CUSTOM_FACET:RECIPE_FACET/DISH_DFACET:0/tag%23dish:cookie"
    articles = []
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html5lib")
    recipe_cards = soup.findAll('div',
                    attrs={'class': 'o-ResultCard__m-MediaBlock m-MediaBlock'})
    for row in recipe_cards:
        title_raw = row.h3.a.span.text
        title = re.sub("-", ":", title_raw)
        p = re.compile('\xae', re.UNICODE)
        title = p.sub('(r)', title)
        uri = row.h3.a.get("href")
        if re.match("^\/\/", uri):
            url = url_base + uri
        else:
            url = base_url + uri
        t = (url, title, runtime)
        recipe_id = url.split('-')[-1]
        c.execute("INSERT INTO urls (url, title, cached_at) VALUES (?, ?, ?)",
                  t)
        conn.commit()
        articles.append({"title": title, "url": url, "recipe_id": recipe_id})
    return articles


def get_n_recipes(query, n=10):
    # n = 2840
    calls = n / 10
    page = 1
    query = "cookies"
    rthumbnails = []
    logging.debug("DEV> len(rthumbnails): ", len(rthumbnails))
    logging.info("Searching for ", n, " recipes related to ", query,
          "calls: ", calls, "; page: ", page)
    while calls >= 0:
        curr_rthumbnails = recipe_search(query, page)
        if len(curr_rthumbnails) == 0:
            break
        rthumbnails.extend(curr_rthumbnails)
        logging.debug("DEV> page: ", page, "; calls: ", calls)
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
    recipes = dict()
    ingredients = []
    cnt = 0

    # Loop through recipe list and process each recipe
    # c.execute("SELECT title, url FROM urls")
    # all_rows = c.fetchall()
    # qry_str = "SELECT title, url, cached_at FROM urls"
    # c.execute(qry_str)
    # for row in c.fetchall:
    for row in c.execute("SELECT title, url FROM urls"):
        # error returned:
        #   ValueError: not enough values to unpack (expected 2, got 1)
        title, url = row
        # error returned:
        #   ValueError: not enough values to unpack (expected 3, got 2)
        # title, url, cached_at = row
        logging.warning(type(row))
        sleep(1)
        # r = requests.get(recipe["url"])
        # logging.debug("Recipe is: ", recipe[0])
        recipe_id = url.split('-')[-1]
        proc_at = c.execute("SELECT processed_at from raw_ingredients")
        result = proc_at.fetchone()
        if int(result[0]) > 1:
            logging.debug("The recipe " + title + " has been processed")
            continue
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
            # logging.debug("Size of ingredients: ", len(ingredients_list))
            for raw_ing in ingredients_list:
                # t = (raw_ing,)
                # logging.debug("raw_ing is: ", raw_ing, ":")
                # sys.stdout.flush()
                # logging.debug("DEV> inside ingredients loop")
                # c.execute("INSERT INTO raw_ingredients (ingredient) VALUES (?)",
                #          raw_ing)
                # conn.commit()
                raw_ing = re.sub('\([^\)]+\)', '', raw_ing)
                sql_str = "INSERT INTO raw_ingredients (ingredient, "
                sql_str = sql_str + "processed_at, recipe_id) VALUES "
                sql_str = sql_str + "(\'" + raw_ing + "\', " + runtime
                sql_str = sql_str + ", \'" + recipe_id + "\');"
                logging.debug(sql_str)
                ingredients.append(sql_str)
                # recipes.update(title = sql_str)
                if recipe_key not in recipes:
                    recipes[recipe_key] = []
                recipes[recipe_key].append({"title": title,
                                            "sql_str": sql_str})
                if cnt % 20 == 0:
                    logging.info("STATUS[" + str(cnt) + "]> " + recipe_key)
                cnt += 1
        except (TypeError, UnicodeEncodeError) as e:
            logging.warning("Error thrown: ", e)
            continue
    max_title_len = 0
    max_sql_len = 0
    for key in recipes:
        title = recipes[key]["title"]
        sql_str = recipes[key]["sql_str"]
        # logging.debug(sql_str)
        if len(title) > max_title_len:
            max_title_len = len(title)
        if len(sql_str) < max_sql_len:
            max_sql_len = len(sql_str)
    logging.info("Max title: ", max_title_len)
    logging.info("Max sql: ", max_sql_len)
    conn.close()


if __name__ == "__main__":
    main()
