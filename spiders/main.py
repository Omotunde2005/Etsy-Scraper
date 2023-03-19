import scrapy
from scrapy.crawler import CrawlerProcess
import pandas


FROM = 2
TO = 3
START_URL = 'https://www.etsy.com/c/jewelry-and-accessories?explicit=1&category_landing_page=2'
NAME = []
TAGS = []
OLD_PRICE = []
NEW_PRICE = []
RATING = []
IMAGE = []
LINK = []


# A PRODUCT LISTING LINK

class EtsySpider(scrapy.Spider):
    name = 'image_scraper'
    custom_settings = {
        'REQUEST_FINGERPRINTER_IMPLEMENTATION': "2.7"
    }
    start_urls = [START_URL]

    def __init__(self, category='', **kwargs):
        super().__init__(**kwargs)
        self.Page = kwargs['Page']
        self.Basis = kwargs['Basis']
        self.myBaseUrl = category + self.Page
        self.start_urls.append(self.myBaseUrl)

    def parse(self, response, **kwargs):
        container = response.css('a.listing-link').get()
        with open('new.html', mode='w') as file:
            file.write(container)


class EtsyCrawlSpider(scrapy.Spider):
    name = "product"
    custom_settings = {
        'DOWNLOAD_DELAY': 7,
        'DEPTH_LIMIT': 10,
    }

    def start_requests(self):

        # List of Pages to Scrape
        urls = [f'https://www.etsy.com/c/home-and-living/home-decor/frames-and-displays?ref=pagination&page={i}'
                for i in range(FROM, TO)]

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)
        df = pandas.DataFrame(
            {'Name': NAME,
             'Price': NEW_PRICE,
             'Old Price': OLD_PRICE,
             'Rating': RATING,
             'Tag': TAGS,
             'Images': IMAGE,
             'Links': LINK
             }

        )
        df.to_csv('record.csv')

    def parse(self, response, **kwargs):

        container = response.css('a.listing-link')
        for c in range(len(container)):
            price_container = container[c].css('div.n-listing-card__price')
            image = container[c].css('img::attr(src)').get()
            link = container[c].attrib['href']
            real_price = price_container.css('span.currency-value::text').get()
            old_price = price_container.css('span.wt-text-strikethrough span.currency-value::text').get()
            if old_price:
                pass
            else:
                old_price = "Nan"
            tag = container[c].css('p.wt-text-caption-title::text').get()
            if not tag:
                tag = "Nan"
            name = container[c].css('h3.wt-text-caption::text').get()
            rating = container[c].css('span.wt-text-body-01::text').get()
            if name is not None:
                name = name.strip()
            NAME.append(name)
            NEW_PRICE.append(real_price)
            OLD_PRICE.append(old_price)
            IMAGE.append(image)
            LINK.append(link)

            if rating is not None:
                rating = rating.strip().split('(')[1].split(')')[0]
            RATING.append(rating)
            TAGS.append(tag)


if __name__ == "__main__":
    process = CrawlerProcess()
    process.crawl(EtsyCrawlSpider)
    process.start()


