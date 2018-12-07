from django.shortcuts import render
from django.http.response import HttpResponse, JsonResponse
from selenium import webdriver
from django.conf import settings


def js_render(request):
    """
    xxxxx?url=xxx
    """
    chrome_path = settings.CHROME_DRIVER_PATH
    url = request.GET.get('url')
    image_flag = request.GET.get("image_render")
    if not url:
        return JsonResponse({
            "status": 0,
            "msg": "Dont gotted url"
        })
    chrome_opt = webdriver.ChromeOptions()
    if image_flag == "0" or image_flag == 0 or image_flag is None:
        # 不加载图片，设置的参数很固定
        prefs = {"profile.managed_default_content_settings.images": 2}
        # 将参数设置到chrome_opt里面
        chrome_opt.add_experimental_option("prefs", prefs)
        # 模拟浏览器的时候将chrome_opt添加进去
    browser = webdriver.Chrome(executable_path=chrome_path, chrome_options=chrome_opt)
    browser.get(url)
    browser.implicitly_wait(20)
    page_source = browser.page_source
    browser.close()
    return HttpResponse(page_source)
