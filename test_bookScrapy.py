import pandas as pd
import bookScrapy

from pandas.io import sql


driver = bookScrapy.driver
engine = bookScrapy.engine_init()
default_page = 'https://books.toscrape.com/index.html'


def test_driver_init(url=default_page):
    driver = bookScrapy.driver_init()
    driver.get(url)
    title = "All products | Books to Scrape - Sandbox"
    assert title == driver.title


def test_engine_init():
    engine = bookScrapy.engine_init()
    assert engine.dialect.has_schema(engine, 'book_club')


def test_engine_init2():
    engine = bookScrapy.engine_init()

    assert engine.dialect.has_table(engine, 'books',
                                    schema='book_club') is False


def test_scrapy_category_lists1(driver=driver):
    category_links, category_list = bookScrapy.scrapy_category_lists(driver)

    assert category_links is not None and category_list is not None


def test_scrapy_category_lists2(driver=driver):
    category_links, category_list = bookScrapy.scrapy_category_lists(driver)

    category_from_link = [link.split('/')[6].split('_')[0]
                          .replace('-', ' ').title()
                          for link in category_links]

    irregularity = [x for x, y in zip(category_list, category_from_link)
                    if x.title() != y]

    assert bool(len(irregularity)) is False


def test_scrapy_rows(driver=driver):
    assert bookScrapy.scrapy_rows(driver) is not None


def test_scrapy_rows2(driver=driver, url=default_page):
    driver.get(url)

    rows = bookScrapy.scrapy_rows(driver)
    title = rows[0].find_elements_by_xpath('//h3//a')[0].get_attribute("title")
    assert title == 'A Light in the Attic'


def test_extract_data(driver=driver, url=default_page):
    driver.get(url)
    rows = bookScrapy.scrapy_rows(driver)
    data = bookScrapy.extract_data(rows, 'All products')

    final_data = set([len(data.get('title')), len(data.get('price')),
                      len(data.get('rating')), len(data.get('in_stock')),
                      len(data.get('category'))])

    valid_data = bool(len(final_data)) is True and list(final_data)[0] > 0

    assert valid_data


def test_to_postgress(engine=engine):
    test = ['test'] * 10
    data = {
            'title':  test,
            'price':  test,
            'rating': test,
            'in_stock': test,
            'category': test
            }

    bookScrapy.to_postgres(data, engine, schema='book_club', table='teste')
    df = pd.DataFrame(sql.execute('Select * From book_club.teste', engine),
                      columns=['title', 'price', 'rating',
                               'in_stock', 'category'])
    assert df.shape == (10, 5)


def test_next_page_extration1(driver=driver, url=default_page):
    driver.get(url)
    next_page = bookScrapy.extract_next_page(driver)
    assert next_page == url[:26] + '/catalogue/page-2.html'


def test_next_page_extration2(driver=driver, url=default_page):
    driver.get(url + '/catalogue/page-50.html')
    next_page = bookScrapy.extract_next_page(driver)
    assert next_page is None


def test_extraction_cycle(url=default_page, engine=engine):
    assert bookScrapy.extration_clycle(url, 'test', engine, 'test', 'test')


def test_extraction_cycle2(url=default_page, engine=engine):
    assert bookScrapy.extration_clycle(url[:26] + '/catalogue/category'
                                       + '/books_1/page-50.html',
                                       'test', engine, 'test', 'test') is None


sql.execute('DROP TABLE IF EXISTS book_club.teste', engine)
sql.execute('DROP SCHEMA IF EXISTS book_club', engine)
