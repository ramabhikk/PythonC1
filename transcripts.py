import scrapy
import json
from w3lib.html import remove_tags

class TranscriptsSpider(scrapy.Spider):
    name = 'transcripts'
    

    def __init__(self, name=None, page=-1, **kwargs):
        super().__init__(name=name, **kwargs)

        self.allowed_domains = ['seekingalpha.com']
        self.start_urls = ['https://seekingalpha.com/earnings/earnings-call-transcripts']
        self.page = int(page)


    def parse(self, response):
        scripts = response.xpath('//li[@class="list-group-item article"]/@data-id').getall()

        for script in scripts:
            url = f"https://seekingalpha.com/api/v3/articles/{script}?include=author%2CprimaryTickers%2CsecondaryTickers%2CotherTags%2Cpresentations%2Cpresentations.slides%2Cauthor.authorResearch%2Cco_authors%2CpromotedService%2Csentiments"
            yield scrapy.Request(url, callback=self.parse_script)
     
        next = response.xpath('//li[@class="next"]/a/@href').get()
        if next:
            page_no = next.split(r'/')[-1]
            if self.page < 0 or (int(page_no) <= self.page):
                yield response.follow(next, callback=self.parse)
                self.logger.info(f"Pagination to page: {page_no}")


    def parse_script(self, response):
        data = json.loads(response.text)

        attributes = data['data']['attributes']
        published_date = attributes['publishOn']
        title = attributes['title']
        content = remove_tags(attributes['content']).replace('\n', '')

        id = data['data']['relationships']['primaryTickers']['data'][0]['id']
        included = data['included']

        for item in included:
            if item['id'] == id:
                ticker = item['attributes']['name']
                company = item ['attributes']['company']

        
        yield {
            'Title' : title,
            'Ticker' : ticker,
            'Company' : company,
            'Published Date' : published_date,
            'Content' : content
        }

        self.logger.info(f"Scrpaed: {company} ({ticker}) {published_date}")
