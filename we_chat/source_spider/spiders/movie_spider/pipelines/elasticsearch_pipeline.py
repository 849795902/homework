from .es_models import MovieType
import logging
from source_spider.spiders.utils.suggest_words import gen_suggest_words


class ElasticsearchPipeline(object):

    def process_item(self, item, spider):
        # 将item转换为ES的数据
        movie = MovieType()

        movie.title = item.get('title')
        movie.url = item.get('url')
        movie.url_cate = item.get('url_cate')
        movie.movie_cate = item.get('movie_cate')
        movie.year = item.get('year')
        movie.create_time = item.get('create_time')
        movie.meta.id = item.get("id")  # 设置id
        # todo:添加搜索关键字并添加权重
        movie.suggest = gen_suggest_words(MovieType._doc_type.index, ((movie.title, 10),))
        movie.save()
        logging.getLogger(__name__).info(f"save movie to es title:{movie.title} url:{movie.url}")
        return item
