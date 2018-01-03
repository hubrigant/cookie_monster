import requests
from bs4 import BeautifulSoup
import RThumbnail
import Recipe
import re
from time import sleep
import sqlite3
import hashlib
# import sys

conn = sqlite3.connect('recipes.db')
c = conn.cursor()


base_url = "http://www.foodnetwork.com"
url_base = "http:"


def _parse_recipe_thumbnail(recipe_thumbnail):
    print("DEV> inside _parse_recipe_thumbnail")
    # Parse title and URL
    try:
        for row in recipe_thumbnail:
            title = row.find(
                "span", {"class": "m-MediaBlock__a-HeadlineText"}).text.strip()
            url = base_url + row.find("a").attrs['href']
    except (AttributeError, UnboundLocalError) as e:
        print("Parcing title/url threw error", e)
        title = ""
        url = ""

    # Parse author
    try:
        author_res = recipe_thumbnail[0].find("span",
                                {"class": "m-Info__a-AssetInfo"}).text.strip()
        author = author_res.replace("Courtesy of ", '')
    except AttributeError as e:
        author = ""
        print("DEV> parse author error: ", e)

    # Parse reviews/review_count
    try:
        # rev_rate = recipe_thumbnail[0].findAll("a",
        #                                       attrs={"class":
        #                                              "m_Rating__a-StarsLink"})
        print("DEV> : ", type(recipe_thumbnail))
        # rating = recipe_thumbnail.select_one("span",
        #                                  attrs={"class":
        #                                         "gig-rating-stars"})['title']
        for row in recipe_thumbnail:
            # rating = row.find("spam", attrs={"class": "gig-rating-stars"})['title']
            print("DEV> row: ", row)
            # newbowl = BeautifulSoup(str(row))
            # rating = newbowl.h3.a.
            rating = 5.0
        # rating = recipe_thumbnail.select_one("m-MediaBlock__m-Rating.a.gig-rating-stars")
        # print("DEV> rating: ", rating)
    except AttributeError as e:
        rating = ""
        review_count = ""
        print("DEV> error in rating/review: ", e)

    # Parse total_time
    try:
        total_time = recipe_thumbnail.find("dl", class_="flat").find("dd").text
    except AttributeError:
        total_time = ""

    # Parse picture_url
    try:
        picture_url = recipe_thumbnail.find("div", class_="pull-right").find("img").attrs['src']
    except AttributeError:
        picture_url = ""

    return RThumbnail(title, url, author, picture_url,
                      total_time, rating, review_count)


def _parse_recipe_list(recipe_thumbnails):
    articles = []
    print("DEV> in _parse_recipe_list, len(recipe_thumbnails): ",
          len(recipe_thumbnails))
    for row in recipe_thumbnails:
        article = row.findAll(
            #"div", {"class": "m-MediaBlock__m-TextWrap"})
            "section", attrs={"class": "o-SiteSearchResults"})
        if len(article) > 0:
            articles.append(article)
            print("DEV> found ", len(article), " articles")
    return list(map(_parse_recipe_thumbnail, articles))


def recipe_search(query, page=1, sortby="Best Match"):
    """
    max of 10 recipes per request
    return: RThumbnail list
    """
    url = "http://www.foodnetwork.com/search/%s-/p/%s/CUSTOM_FACET:RECIPE_FACET" % (query, page)
    articles = []
    # recipe_thumbnails = []
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html5lib")  # "lxml")
    # title = soup.h3.a.span.text
    # url = soup.h3.a.get("href")
    # print("Title: ", title, "; URL: ", url)
    # recipe_thumbnails = soup.findAll("section",
    #            attrs={"class": "o-RecipeResult o-ResultCard"})
    recipe_cards = soup.findAll('div',
                    attrs={'class': 'o-ResultCard__m-MediaBlock m-MediaBlock'})
    for row in recipe_cards:
        # print(row.h3.a.get("href"))
        title = row.h3.a.span.text
        uri = row.h3.a.get("href")
        url = url_base + uri
        # print("Title: ", title.encode('ascii', 'backslashreplace'),
        #      "; URL: ", url)
        # sql = "INSERT INTO urls VALUES (?)", (url, title)
        # print(sql)
        t = (url, title)
        c.execute("INSERT INTO urls (url, title) VALUES (?, ?)", t)
        conn.commit()
        # sleep(1)
        articles.append({"title": title, "url": url})
    return articles


#    if not recipe_thumbnails:
#        print("DEV> recipe_thumbnails is None")
#        return []
#    else:
#        # Parse URL
#        print("DEV> len(recipe_thumbnails): ", len(recipe_thumbnails))
#        for row in recipe_thumbnails:
#            article = row.findAll(
#                # "section", attrs={"class": "o-SiteSearchResults"}
#                "section", attrs={"class": "o-RecipeResult o-ResultCard"}
#            )
#            # print("=================================================")
#            # print("DEV> inside for loop, len(article): ", str(row))
#        try:
#            for row in article:
#                print("DEV> inside recipe_search.for loop", str(row))
#                # title = row.find(
#                #    "span",
#                #    {"class": "m-MediaBlock__a-HeadlineText"}).text.strip()
#                uri = row.find("a").attrs['href']
#                print("DEV> uri: ", uri)
#                url = base_url + uri  # row.find("a").attrs['href']
#                articles.extend(url)
#                print("DEV> url: ", url)
#        except (AttributeError, UnboundLocalError) as e:
#            print("Parsing title/url threw error", e)
#            # title = ""
#            url = ""
#        print("DEV> articles: ", len(articles))
#        # _parse_recipe_list(recipe_thumbnails)


def get_n_recipes(query, n=10):
    # n = 2833
    calls = n / 10
    page = 1
    query = "cookies"
    rthumbnails = []
    print("DEV> len(rthumbnails): ", len(rthumbnails))
    print("Searching for ", n, " recipes related to ", query,
          "calls: ", calls, "; page: ", page)
    while calls >= 0:
        curr_rthumbnails = recipe_search(query, page)
        if len(curr_rthumbnails) == 0:  # or len(rthumbnails) >= n:
            break
        rthumbnails.extend(curr_rthumbnails)
        print("DEV> page: ", page, "; calls: ", calls)
        page += 1
        calls -= 1
        sleep(1)
    return rthumbnails


def _parse_recipe(recipe_html):
    try:
        title = recipe_html.find("span",
                                 attrs={'class':
                                        'o-AssetTitle__a-HeadlineText'}).text
    except AttributeError:
        title = ""
    try:
        for span in recipe_html.findAll("span", attrs={'class': 'o-Attribution__a-Author--Prefix'}):
            for namespan in span.findAll("span", attrs={'class': 'o-Attribution__a-Name'}):
                author = namespan.find("a").contents[0]
    except (AttributeError, IndexError):
        author = ""
    try:
        times = recipe_html.find("section", attrs={'class': "o-RecipeInfo o-Time"}).find_all("dd")
    except AttributeError:
        times = []
    try:
        total_time = times[0].text
    except IndexError:
        total_time = ""
    try:
        prep_time = times[1].text
    except IndexError:
        prep_time = ""
    try:
        tot_hrs = tot_mins = total_minutes = prep_hrs = prep_mins = prep_minutes = int()
        get_tot_matches = re.match('((\d+) hr )?((\d+) min)?', total_time)
        get_prep_matches = re.match('((\d+) hr )?((\d+) min)?', prep_time)
        try:
            tot_hrs = int(get_tot_matches.group(2))
        except (AttributeError, ValueError):
            tot_hrs = int(0)
        try:
            tot_mins = int(get_tot_matches.group(4))
        except (AttributeError, ValueError):
            tot_mins = int(0)
        total_minutes = (tot_hrs * 60) + tot_mins
        try:
            prep_hrs = int(get_prep_matches.group(2))
        except (AttributeError, ValueError, TypeError):
            prep_hrs = int(0)
        try:
            prep_mins = int(get_prep_matches.group(4))
        except (AttributeError, ValueError, TypeError):
            prep_mins = int(0)
        prep_minutes = (prep_hrs * 60) + prep_mins
        cook_time_minutes = total_minutes - prep_minutes
        cook_time_mins = int(cook_time_minutes % 60)
        cook_time_hrs = int(cook_time_minutes / 60)
        if cook_time_hrs > 0:
            cook_time = str(cook_time_hrs) + " hr " + str(cook_time_minutes) + " min"
        else:
            cook_time = str(cook_time_minutes) + " min"
    except IndexError:
        cook_time = ""
    try:
        picture_url = recipe_html.find("div", attrs={'class': 'o-AssetMultiMedia__m-MediaWrap'}).find("img").attrs['src']
    except AttributeError:
        picture_url = ""
    try:
        for section in recipe_html.findAll("section", attrs={'class': 'o-RecipeInfo o-Level'}):
            level = section.find("dd", attrs={'class': 'o-RecipeInfo__a-Description'}).string.strip()
    except AttributeError:
        level = ""
    try:
        for section in recipe_html.findAll("section", attrs={'class': 'o-RecipeInfo o-Yield'}):
            servings = section.find("dd", attrs={'class': 'o-RecipeInfo__a-Description'}).string.strip()
    except IndexError:
        servings = ""
    try:
        ings_div = recipe_html.find("div", attrs={'class': "o-Ingredients__m-Body"})
        ingredients = list(map(lambda x: x.text, ings_div.find_all("li", attrs={'class': 'o-Ingredients__a-ListItem'})))
        ingredients = [i.replace('\n', '') for i in ingredients]
    except AttributeError:
        ingredients = []
    try:
        for desc_div in recipe_html.findAll("div", attrs={'class': 'o-Method__m-Body'}):
            directions = list(map(lambda x: x.text, desc_div.find_all("p")))
            directions = [d.replace('\n', '') for d in directions]
            directions = [d.strip() for d in directions]
    except AttributeError:
        directions = []
    try:
        categories = []
        for tag in recipe_html.findAll("a", attrs={'class': 'o-Capsule__a-Tag a-Tag'}):
            categories.append(tag.text)
        if not categories:
            raise ValueError('Categories list is empty')
    except (ValueError, UnboundLocalError) as ex:
        categories = []
        print("Categories parsing threw error: ", ex)

    return Recipe(title, author, picture_url, total_time, prep_time, cook_time,
                  servings, level, ingredients, directions, categories)


def scrape_recipe(url):
    """
    parameter: url to Food Network recipe
    return: Recipe object
    """
    sleep(1)
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html5lib")
    return _parse_recipe(soup)


def main():
    # print("Starting execution ...")
    # Get list of cookie recipes
    #
    # The first version grabs the list of recipe URLs from FN
    # The second grabs from the local database cache created by the first
    #
    # url_list = get_n_recipes("cookies", n=2840)
    # c.execute("SELECT title, url FROM urls")
    # url_list = c.fetchall()
    # print("url_list is a: ", type(url_list[0]))
    # sys.stdout.flush()
    recipes = dict()
    # seen = {}
    ingredients = []
    cnt = 0

    # Loop through recipe list and process each recipe
    for (title, url) in c.execute("SELECT title, url FROM urls"):
        sleep(1)
        # r = requests.get(recipe["url"])
        # print("Recipe is: ", recipe[0])
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
            #    print("Entry: ", entry)
            # print("Size of ingredients: ", len(ingredients_list))
            for raw_ing in ingredients_list:
                # t = (raw_ing,)
                # print("raw_ing is: ", raw_ing, ":")
                # sys.stdout.flush()
                # print("DEV> inside ingredients loop")
                # c.execute("INSERT INTO raw_ingredients (ingredient) VALUES (?)",
                #          raw_ing)
                # conn.commit()
                sql_str = "INSERT INTO raw_ingredients (ingredient) VALUES (\'" + raw_ing + "\')"
                # print(sql_str)
                ingredients.append(sql_str)
                # recipes.update(title = sql_str)
                recipes[hashlib.md5(title)].append({"title": title,
                                                    "sql_str": sql_str})
        except TypeError as e:
            print("Error thrown: ", e)
            continue
        # if cnt > 10:
        #    break
        # cnt += 1
    max_title_len = 0
    max_sql_len = 0
    for key in recipes:
        title = recipes[key]["title"]
        sql_str = recipes[key]["sql_str"]
        if len(title) > max_title_len:
            max_title_len = len(title)
        if len(sql_str) < max_sql_len:
            max_sql_len = len(sql_str)
    print("Max title: ", max_title_len)
    print("Max sql: ", max_sql_len)
    conn.close()


if __name__ == "__main__":
    main()
