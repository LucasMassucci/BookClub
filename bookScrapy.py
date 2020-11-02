import pandas as pd

from pandas.io import sql
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options 
from word2number import w2n
from sqlalchemy import create_engine



def driver_init():
    option = Options()
    option.headless = True

    driver = webdriver.Chrome(options=option)

    return driver

def scrapy_category_lists(driver):
    driver.get('http://books.toscrape.com/index.html')

    web_elements =  driver.find_elements_by_xpath(
        '//div[@class="side_categories"]//ul[@class="nav nav-list"]//li//ul//li//a')
    
    category_links = [web_elements[item].get_attribute("href") 
                     for item in range(len(web_elements))]

    category_list = [web_elements[item].text 
                     for item in range(len(web_elements))]
    
    return category_links, category_list


def scrapy_rows(driver):
    return driver.find_elements_by_xpath(
        '//li[@class="col-xs-6 col-sm-4 col-md-3 col-lg-3"]'
        +'//article[@class="product_pod"]')

def extract_data(rows:list, category: str):

    row_texts = [rows[r].text.split('\n') for r in range(len(rows))]  
    titles = rows[0].find_elements_by_xpath('//h3//a')
    ratings_data = rows[0].find_elements_by_xpath('//p')

    data = {
            'title':  [my_title.get_attribute("title") 
                       for my_title in titles ],

            'price':  [text[1].replace('£', '') for text in row_texts],

            'rating': [w2n.word_to_num(
                       rating.get_attribute('class')
                       .replace('star-rating ', '')) 
                       for rating in ratings_data 
                       if rating.get_attribute('class')
                       .__contains__('star-rating')],

            'in_stock':  [True if text[2] == 'In stock' else False 
                          for text in row_texts],

            'category': [category for text in row_texts]
            }

    return data

def to_postgres(data,engine,schema='book_club_basic', table='books'):
    df = pd.DataFrame (data, columns = ['title','price','rating',
                                        'in_stock','category'])
    df.to_sql(table, engine, schema, 
              if_exists='append',index=False)

def extract_next_page(driver):
    next_page = driver.find_elements_by_xpath(
        '//div//ul[@class="pager"]//li[@class="next"]//a')
    for np in next_page:
        return np.get_attribute("href")      

def sql_image_to_csv(engine):
    pd.DataFrame(
        sql.execute('Select * From book_club_basic.books', engine),
        columns = ['title','price','rating','in_stock','category']
        ).to_csv('out.csv', index=False)


def extration_clycle(url, category,engine):
    driver.get(url)
    data = extract_data(scrapy_rows(driver), category)
    to_postgres(data,engine)
    return extract_next_page(driver)

def process(driver):
    engine = create_engine('postgresql://postgres:postgres@localhost:5432/postgres')
    sql.execute('DROP TABLE IF EXISTS book_club_basic.books', engine)
    
    category_links, category_list = scrapy_category_lists(driver)
    
    for item in range(len(category_links)):    
        category = category_list[item] 
        url = category_links[item]
        next_page = extration_clycle(url,category,engine)
        
        while next_page:
            next_page = extration_clycle(next_page, category, engine)

driver = driver_init()

if __name__ == '__main__':
    process(driver)
