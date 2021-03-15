import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import ValleItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class ValleSpider(scrapy.Spider):
	name = 'valle'
	start_urls = ['https://vallbanc.ad/en/blog']

	def parse(self, response):
		articles = response.xpath('//div[@class="article-teaser__content"]')
		for article in articles:
			date = article.xpath('.//div[@class="article-teaser__date"]/text()').get()
			post_links = article.xpath('.//div[@class="article-teaser__cta"]/a/@href').get()
			yield response.follow(post_links, self.parse_post,cb_kwargs=dict(date=date))

		next_page = response.xpath('//li[@class="pager__item pager__item--next"]/a/@href').get()
		if next_page:
			yield response.follow(next_page, self.parse)

	def parse_post(self, response,date):

		title = response.xpath('(//span[@property="schema:name"])[1]/text()').get()
		content = response.xpath('//div[@class="node-article__body"]//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=ValleItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
