import pandas as pd
import bookScrapy

from pandas.io import sql
from sqlalchemy import create_engine


driver = bookScrapy.driver

def test_driver_init():
    driver = bookScrapy.driver_init()
    driver.get('http://books.toscrape.com/index.html')
    title = "All products | Books to Scrape - Sandbox"
    assert title == driver.title

def test_engine_init():
    engine = bookScrapy.engine_init()
    assert engine.dialect.has_schema(engine,'book_club')

def test_engine_init2():
    engine = bookScrapy.engine_init()
    assert engine.dialect.has_table(engine, 'books', schema='book_club') == False


def test_scrapy_category_lists1(driver=driver):
    category_links, category_list = bookScrapy.scrapy_category_lists(driver)
    assert category_links != None and category_list != None

def test_scrapy_category_lists2(driver=driver):
    category_links, category_list = bookScrapy.scrapy_category_lists(driver)

    category_from_link = [link.split('/')[6].split('_')[0].replace('-', ' ').title() 
                     for link in category_links]
    
    irregularity = [x for x, y in zip(category_list, category_from_link) if x.title() != y]
    
    assert len(irregularity) == False



def test_scrapy_rows(driver=driver):
    assert bookScrapy.scrapy_rows(driver) != None

def test_scrapy_rows2(driver=driver):
    driver.get('http://books.toscrape.com/index.html')
    rows = bookScrapy.scrapy_rows(driver)
    title = rows[0].find_elements_by_xpath('//h3//a')[0].get_attribute("title") 
    assert title == 'A Light in the Attic'

def test_extract_data(driver=driver):
    driver.get('http://books.toscrape.com/index.html')
    rows = bookScrapy.scrapy_rows(driver)
    data = bookScrapy.extract_data(rows, 'All products')

    final_data = [len(data.get('title')),len(data.get('price')),
                  len(data.get('rating')),len(data.get('in_stock')),
                  len(data.get('category'))]

    valid_data = len(set(final_data)) == True and list(set(final_data))[0] > 0
    assert valid_data

def test_to_postgress():
    engine = bookScrapy.engine_init()
    data = {
            'title':  ['teste' for x in range(10)],
            'price':  ['teste' for x in range(10)],
            'rating': ['teste' for x in range(10)],
            'in_stock': ['teste' for x in range(10)],
            'category': ['teste' for x in range(10)]
            }

    sql.execute('DROP TABLE IF EXISTS book_club.teste', engine)
    bookScrapy.to_postgres(data,engine, schema='book_club', table='teste')
    df = pd.DataFrame(sql.execute('Select * From book_club.teste', engine),        
    columns = ['title','price','rating','in_stock','category'])
    assert df.shape == (10,5)

def test_next_page_extration1(driver=driver):
    driver.get('http://books.toscrape.com/index.html')
    next_page = bookScrapy.extract_next_page(driver)
    assert next_page == 'http://books.toscrape.com/catalogue/page-2.html'

def test_next_page_extration2(driver=driver):
    driver.get('http://books.toscrape.com/catalogue/page-50.html')
    next_page = bookScrapy.extract_next_page(driver)
    assert next_page == None
