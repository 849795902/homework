def parse_url_type(url):
    mapping = {
        "XUNLEI": "thunder://"
    }
    for type, flag in mapping.items():
        if url.startswith(flag):
            return type
    return "COMMON"
