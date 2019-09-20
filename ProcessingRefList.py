import os
import uuid
import re
from selenium import webdriver
from parsel import Selector
from lxml import etree

N = 0
REF_STORAGE = 'links/'
ARTICLE_STORAGE = 'result_data/'
URL_VALUE = 'https://cyberleninka.ru'
END_ARTICLE = ['библиографический список', 'библиографический список:', 'список литературы', 'список литературы:',
               'литература', 'литература:']


def createXML(categoryName, authorList, titleName, keywordList, annotationName, textName, sourceValue):
    root = etree.Element("doc")

    source = etree.SubElement(root, "source", auto='true', type='str', verify='true')
    source.text = etree.CDATA(sourceValue)

    category = etree.SubElement(root, "category", auto='true', type='str', verify='true')
    category.text = etree.CDATA(categoryName)

    author = etree.SubElement(root, "author", auto='true', type='list', verify='true')

    for i in range(0, len(authorList)):
        item_author = etree.SubElement(author, "item", type='str')
        item_author.text = etree.CDATA(authorList[i])

    title = etree.SubElement(root, "title", auto='true', type='str', verify='true')
    title.text = etree.CDATA(titleName)

    keywords = etree.SubElement(root, "keywords", auto='true', type='list', verify='true')
    for i in range(0, len(keywordList)):
        item_keywords = etree.SubElement(keywords, "item", type='str')
        item_keywords.text = etree.CDATA(keywordList[i])

    annotation = etree.SubElement(root, "annotation", auto='true', type='str', verify='true')
    annotation.text = etree.CDATA(annotationName)

    content = etree.SubElement(root, "text", auto='true', type='str', verify='true')
    content.text = etree.CDATA(re.sub(r'\s+', ' ', textName))

    tree = etree.ElementTree(root)
    if not os.path.exists(ARTICLE_STORAGE + categoryName):
        os.makedirs(ARTICLE_STORAGE + categoryName)
    tree.write(ARTICLE_STORAGE + categoryName + "/" + str(uuid.uuid4()) + ".xml", encoding='utf-8', pretty_print=True)


driver = webdriver.Chrome()

fileList = os.listdir(path=REF_STORAGE)
countHref = 1028
for k in range(N, len(fileList)):
    f = open(REF_STORAGE + fileList[k])
    for line in f:
        driver.get(URL_VALUE + line)
        sel = Selector(text=driver.find_element_by_xpath("//*").get_attribute("outerHTML"))

        textName = sel.xpath("//div[@class='main']//h1/i/text()").extract_first()

        textList = sel.xpath("//div[@class='ocr']/p/text()").extract()
        textArticle = ''

        # if set(item.lower() for item in textList).isdisjoint(END_ARTICLE):
        #   continue
        checkGoodContent = True
        for i in range(0, len(textList)):
            textList[i].replace('\ufeff', "")
            if textName.lower() in textList[i].lower() and i < len(textList) - 1:
                i = i + 1
                while textList[i].lower() not in END_ARTICLE and i < len(textList):
                    textArticle = textArticle + textList[i] + " "
                    i = i + 1
                    if i > len(textList) - 1:
                        checkGoodContent = False
                        break
                break

        if textArticle == '' or not checkGoodContent:
            continue
        else:
            keywordsList = sel.xpath("//div[@class='full keywords']/i[@itemprop='keywords']/span/text()").extract()

            textAnnotation = sel.xpath("//div[@class='infoblock'][4]/div[@class='full abstract']/p[@itemprop='description']//text()").extract()

            authorList = sel.xpath("//div[@class='infoblock authors visible']/ul[@class='author-list']/li[@itemprop='author']/span/text()").extract()

            try:
                createXML(fileList[k].replace(".txt", ""), authorList, textName, keywordsList, ''.join(textAnnotation), textArticle, URL_VALUE + line.replace('\n', ''))
            except ValueError:
                continue
            countHref = countHref + 1
            print(str(countHref) + " article get successfuly from CyberLeninka")
driver.close()
