import scrapy
from scrapy.http import Response


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs):
        next_page_link = response.urljoin(response.css(
            ".next > a::attr(href)"
        ).get())

        urls = response.css(".col-xs-6")
        urls = [u.css("h3 > a::attr(href)").get() for u in urls]
        print(urls)
        for url in urls:
            absolute_url = response.urljoin(url)
            yield response.follow(url=absolute_url, callback=self.parce_book)

        if next_page_link is not None or ["10", 10] in next_page_link:
            yield response.follow(next_page_link, callback=self.parse)

    def parce_book(self, response: Response):
        rating = response.css("p.star-rating::attr(class)").get().split(" ")[1]
        if rating:
            if rating == "One":
                rating = 1
            elif rating == "Two":
                rating = 2
            elif rating == "Three":
                rating = 3
            elif rating == "Four":
                rating = 4
            elif rating == "Five":
                rating = 5

        yield {
            "title": response.css("h1::text").get(),
            "price": response.css("p.price_color::text").get(),
            "amount_in_stock": response.css(
                "p.instock.availability::text"
            ).re_first(r"\d+"),
            "rating": rating,
            "category": response.css(
                "ul.breadcrumb li a::text"
            ).getall()[2],
            "description": response.css(
                ".product_page p:not([class])::text"
            ).get(),
            "upc": response.css(
                "table.table-striped tr td::text"
            ).get()
        }
