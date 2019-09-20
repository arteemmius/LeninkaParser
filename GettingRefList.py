import re
from selenium import webdriver
from parsel import Selector

URL_VALUE = 'https://cyberleninka.ru'
REF_STORAGE = 'links/'
N = 0

driver = webdriver.Chrome()
driver.get(URL_VALUE)

sel = Selector(text=driver.find_element_by_xpath("//*").get_attribute("outerHTML"))

categoryLinksList = sel.xpath("//div[@class='half']/ul[@class='grnti']//a/@href").extract()
categoryLinksList = categoryLinksList + sel.xpath("//div[@class='half-right']/ul[@class='grnti']//a/@href").extract()

categoryNameList = sel.xpath("//div[@class='half']/ul[@class='grnti']//a/text()").extract()
categoryNameList = categoryNameList + sel.xpath("//div[@class='half-right']/ul[@class='grnti']//a/text()").extract()

for i in range(N, len(categoryLinksList)):
    f = open(REF_STORAGE + categoryNameList[i] + '.txt', 'a')
    driver.get(URL_VALUE + categoryLinksList[i])
    sel = Selector(text=driver.find_element_by_xpath("//*").get_attribute("outerHTML"))
    if sel.xpath("//ul[@class='paginator']//li/span/text()").extract_first() is None:
        f.write("\n".join(str(x) for x in sel.xpath("//div[@class='full']//a/@href").extract()))
        f.write("\n")
    else:
        if sel.xpath("//ul[@class='paginator']//a[@class='icon']/@href").extract_first() is None:
            lastNumber = sel.xpath("//ul[@class='paginator']/li[last()]/a/text()").extract_first()
        else:
            lastHref = sel.xpath("//ul[@class='paginator']//a[@class='icon']/@href").extract_first()
            lastNumber = lastHref[lastHref.rfind("/") + 1:len(lastHref)]
        for j in range(1, int(lastNumber) + 1):
            if j == 1:
                f.write("\n".join(str(x) for x in sel.xpath("//div[@class='full']//a/@href").extract()))
                f.write("\n")
                continue
            driver.get(URL_VALUE + categoryLinksList[i] + "/" + str(j))
            sel = Selector(text=driver.find_element_by_xpath("//*").get_attribute("outerHTML"))
            f.write("\n".join(str(x) for x in sel.xpath("//div[@class='full']//a/@href").extract()))
            f.write("\n")
driver.close()
