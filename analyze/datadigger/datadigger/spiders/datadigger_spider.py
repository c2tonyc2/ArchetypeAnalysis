import scrapy
from datadigger.items import DeckItem

class Datadigger_spider(scrapy.Spider):
    name = "datadigger"
    allowed_domains = ["mtggoldfish.com"]
    start_urls = [
        "http://www.mtggoldfish.com/metagame/standard/full#online",
    ]

    def parse(self, response):
        archetype = """//div[@class="archetype-tile-description"]
                    /h2/span[@class="deck-price-paper"]/a/@href"""
        for href in response.xpath(archetype):
            url = response.urljoin(href.extract())
            yield scrapy.Request(url, callback=self.parse_dir)

    def parse_dir(self, response):
        deckpath = '//table[*]/tr/td[2]/span[@class="deck-price-paper"]/a/@href'
        for href in response.xpath(deckpath):
            url = response.urljoin(href.extract())
            yield scrapy.Request(url, callback=self.parse_dir_contents)

    def parse_dir_contents(self, response):
        cardPath = """(//div[1]/div[1]/div/table/tr/td[@class="deck-col-card"]/a |
                   //div[1]/div[1]/div/table/tr/td[@class="deck-col-card" and not(a)])
                   /text()"""
        item = DeckItem()
        item['name'] = response.xpath('//title/text()').extract()
        item['cards'] = response.xpath(cardPath).extract()
        item['quantities'] = response.xpath(
            '//div[1]/div[1]/div/table/tr/td[@class="deck-col-qty"]/text()'
            ).extract()
        yield item
