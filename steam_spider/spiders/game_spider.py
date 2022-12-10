import scrapy

from ..items import SteamSpiderItem


class GameSpiderSpider(scrapy.Spider):
    name = 'game_spider'
    allowed_domains = ['store.steampowered.com']

    def start_requests(self):

        terms = ['indi', 'arcade', 'rpg']
        for term in terms:
            urls = [
                'https://store.steampowered.com/search/?term=' + term + '&ignore_preferences=1&category1=998&supportedlang=english&ndl=1&page=1',
                'https://store.steampowered.com/search/?term=' + term + '&ignore_preferences=1&category1=998&supportedlang=english&ndl=1&page=2',
                'https://store.steampowered.com/search/?term=' + term + '&ignore_preferences=1&category1=998&supportedlang=english&ndl=1&page=3',
                'https://store.steampowered.com/search/?term=' + term + '&ignore_preferences=1&category1=998&supportedlang=english&ndl=1&page=4',
                'https://store.steampowered.com/search/?term=' + term + '&ignore_preferences=1&category1=998&supportedlang=english&ndl=1&page=5',
            ]
            for url in urls:
                yield scrapy.Request(url, callback=self.parse)


    def parse(self, response):

        list_games = response.xpath('//div[contains(@id, "search_resultsRows")]/a[contains(@class, "search_result_row")]')
        for game in list_games:

            # Проверяем наличие года, а также не идем дальше, если не удовлетворяет условию
            release_date = game.xpath('.//div[contains(@class, "search_released")]/text()').extract()
            if len(release_date) == 0:
                release_date.append(None)
            else:
                year = release_date[0].split(', ')
                if len(year) == 2:
                    if int(year[1]) <= 2000:
                        continue

            game_name = game.xpath('.//span[contains(@class, "title")]/text()').extract()[0]
            price = game.xpath('.//div[contains(@class, "search_price")]/text()').extract()[-2].strip()
            if price == '':
                price = 'To be announced'

            list_platforms = game.xpath('.//span[contains(@class, "platform")]/@class').extract()
            for i in range(len(list_platforms)):
                list_platforms[i] = list_platforms[i].split()[1]

            # Идем по ссылкам
            game_id = game.xpath('.//@data-ds-appid').extract()
            url = 'https://store.steampowered.com/app/' + game_id[0]
            cookies = {'birthtime': '283993201', 'mature_content': '1'}

            # Вносим полученные данные в items
            items = SteamSpiderItem()
            items['release_date'] = release_date[0]
            items['game'] = game_name
            items['price'] = price
            items['platforms'] = list_platforms

            yield scrapy.Request(url, callback=self.parse_game, cookies=cookies,
                                 meta={'game': items['game'],
                                       'release_date': items['release_date'],
                                       'price': items['price'],
                                       'platforms': items['platforms']})


    def parse_game(self, response):

        path = response.xpath('//div[@class="blockbg"]//a/text()').extract()
        path = path[1:]

        # Проверка наличия отзывов
        reviews_info = response.xpath('//span[@class="nonresponsive_hidden responsive_reviewdesc"]/text()').extract()
        if len(reviews_info) == 0:
            reviews_rate = 0
            reviews_count = 0
        elif len(reviews_info) == 1:
            # Недавно выпущена игра, есть только 1 вид обзоров (все)
            no_score = response.xpath('//span[contains(@class, "not_enough_reviews")]/text()').extract()
            if len(no_score) != 0:
                reviews_rate = 0
                reviews_count = no_score[0].split()[0]
            else:
                reviews_info = reviews_info[0].split()
                reviews_rate = reviews_info[1] + ' ' + reviews_info[-1]
                reviews_count = reviews_info[4]
        else:
            reviews_info = reviews_info[1].split()
            reviews_rate = reviews_info[1] + ' ' + reviews_info[-1]
            reviews_count = reviews_info[4]

        developers = response.xpath('//div[@id="developers_list"]/a/text()').extract()
        tags = response.xpath('//div[contains(@class, "glance_tags popular_tags")]/a/text()').extract()
        for i in range(len(tags)):
            tags[i] = tags[i].strip()

        items = SteamSpiderItem()
        items['game'] = response.meta.get('game')
        items['path'] = path
        items['reviews_count'] = reviews_count
        items['reviews_rate'] = reviews_rate
        items['release_date'] = response.meta.get('release_date')
        items['developers'] = developers
        items['tags'] = tags
        items['price'] = response.meta.get('price')
        items['platforms'] = response.meta.get('platforms')
        yield items

