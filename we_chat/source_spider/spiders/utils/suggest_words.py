from elasticsearch_dsl.connections import connections
from source_spider.settings import ELS_URI, ELS_DB

es = connections.create_connection(hosts=ELS_URI)


def gen_suggest_words(index, info_tuple):
    used_words = set()
    suggest = list()
    for text, weight in info_tuple:
        if text:
            # 调用es中的接口对字符串进行分词
            words = es.indices.analyze(index=index, analyzer="ik_max_word", params={"filter":["lowercase"]}, body=text)
            analyze_words = set([r["token"] for r in words["tokens"] if len(r["token"]) > 1])
            new_words = analyze_words - used_words
        else:
            new_words = set()
        if new_words:
            suggest.append({"input": list(new_words), "weight": weight})
    return suggest
