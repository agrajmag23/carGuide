from libs.lib import *
from bs4 import BeautifulSoup as bsp
import requests as req
preprocessed_data = []
raw_data=[]
links = []
dataWPara={}
link_queue=[]
uni_words = []
index_table = []
robots=[]
restricted=[]

def get_links(url):
    response = req.get(url)
    #print(response.text)
    soup = bsp(response.text, 'html.parser')
    links = []
    for link in soup.find_all('a'):
        href = link.get('href')
        try:
            if not(href in restricted) and href.startswith('/'):
                links.append('http://www.truecar.com'+href)
        except AttributeError:
            pass
    # print(links,'links')
    return links

def niche_crawl(url, depth):
    if depth == 0:
        return
    links = get_links(url)
    for link in links:
        print('getting links ',link)
        if link not in link_queue:
            link_queue.append(link)
        niche_crawl(link, depth-1)
def st():
    fileptr=open('database/robots.txt','r')
    data=fileptr.read()
    data =data.split('\n')
    for lnk in data:
            if len(lnk)>0:
                j=lnk.split(' ')
                if j[0].startswith('Disallow'):
                    #robots.append(j[1])
                    restricted.append(j[1])

def crawl():
    counter=0
    for i in link_queue:
        counter+=1
        k=i+'specs'
        print('retrieving link {0} of {1}, {2}'.format(str(counter),str(len(link_queue)),k))
        response = req.get(i)
        soup = bsp(response.text, 'lxml')
        cont = []
        h = soup.find_all('h1')
        for head in h:
            cont.append(head.text)
        content = getContent(k)
        content = cont+content
        if len(content) > 0:
            contentList=[]
            raw_data.append(content[0].strip())
            dataWPara[i] = content[1:]
            for j in content:
                print('processing document ', j)
                if len(j.strip())>0:
                    contentList.append(preproccesing(j))
            contentList=' '.join(contentList)
            preprocessed_data.append(contentList)
            links.append(i)
def getContent(url):
    response = req.get(url)
    soup = bsp(response.text, 'lxml')
    content = []
    h =soup.find_all('h1')
    p =soup.find_all('p')
    for i in h:
        content.append(i.text)
    for i in p:
            content.append(i.text)
    return content


def indexer():
    global index_table,uni_words
    index_table,uni_words=indexing(preprocessed_data)
    print(index_table)

def saveData():
    save_table(index_table,'database/index.csv')
    save_documents(raw_data,dataWPara,'database/documents.txt',links)
    save_words(uni_words,'database/unique_words.txt')
def loadData():
    global index_table,uni_words,raw_data,link_queue, dataWPara
    index_table=load_table('database/index.csv')
    uni_words = load_words('database/unique_words.txt')
    raw_data,link_queue,dataWPara = load_documents('database/documents.txt')
    print(len(index_table['12']))
    print('unique words retrieved ', len(uni_words))
    print('number of links ', len(links))
    print('number of documents ',len(raw_data))
def search_query(q):
    ranks = evaluate_query(preproccesing(q),raw_data,uni_words,index_table,link_queue)
    rank_dic ={}
    for i in range(len(ranks)):
        rank_dic[i] = ranks[i]
    print(rank_dic)
    return rank_dic

def start():
    st()
    niche_crawl('https://www.truecar.com/new-cars-for-sale/listings/',1)
    crawl()
    indexer()

#start()
#saveData()
loadData()
