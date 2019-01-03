from datetime import datetime
from elasticsearch_dsl import DocType, Date, Nested, Boolean, \
    analyzer, Completion, Keyword, Text, Integer
from source_spider.settings import ELS_URI, ELS_DB
# 使用版本5.2.0新版本不支持
from elasticsearch_dsl.connections import connections

from elasticsearch_dsl.analysis import CustomAnalyzer as _CustomAnalyzer

connections.create_connection(hosts=ELS_URI)


class CustomAnalyzer(_CustomAnalyzer):
    def get_analysis_definition(self):
        return {}


ik_analyzer = CustomAnalyzer("ik_max_word", filter=["lowercase"])


class MovieType(DocType):
    suggest = Completion(analyzer=ik_analyzer)  # 添加自动补全功能
    title = Text(analyzer="ik_max_word")
    url = Keyword()
    url_cate = Keyword()
    movie_cate = Keyword()
    year = Integer()
    create_time = Date()

    class Meta:
        index = ELS_DB  # index名
        doc_type = "iidvd"  # type名


if __name__ == "__main__":
    MovieType.init()
