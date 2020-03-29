import requests as req
from bs4 import BeautifulSoup
import sqlite3
from multiprocessing import Pool
import webbrowser
import time
import random

user_agent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0'

headers = {
    'User-Agent' : user_agent
    }
debug = True


dbname = 'anime1.db'

def delay():
    delay = 100+random.randint(0,400)
    #print('delay :',delay,'ms')
    time.sleep(delay*0.001)

def updateDB():
    initDB(update=True)

def initDB(update=False):
    conn = sqlite3.connect(dbname)
    c =  conn.cursor()
    
    resp = c.execute('select name from sqlite_master where type=\'table\'')
    tables = [t[0] for t in resp.fetchall()]
    print("Tables present in DB:")
    print(tables,"\n\n\n")

    if 'anime' in tables:
        if not update:
            return False        
        else:
            c.execute('drop table anime;')
            
    print("Creating table anime")
    c.execute('''create table if not exists anime(
        id integer primary key autoincrement,
        name varachar(30),
        url varchar(100)
        );
        ''')
    conn.commit()
    conn.close()
    return True

    

def insert(name,url):
    conn = sqlite3.connect(dbname)
    c =  conn.cursor()
    values = (name,url)
    c.execute('insert into anime value(NULL,?,?)',values)
    conn.commit()
    conn.close()

def insertmany(anime_list):
    conn = sqlite3.connect(dbname)
    c =  conn.cursor()
    
    values = [(a['name'],a['url']) for a in anime_list]
    for anime in values:
        print(anime)
    
    c.executemany('insert into anime values(NULL,:name,:url)',anime_list)
    conn.commit()
    conn.close()

def search(pattern=None,animeID=None,n=None):
    conn = sqlite3.connect(dbname)
    c =  conn.cursor()
    values = {}
    query = 'select * from anime'
    if pattern:
        values['pat'] = '%'+pattern+'%'
        query = query + ' where name like :pat'
        if animeID:
            query = query + ' and id=:id'
            values['id']=animeID
    else:
        if animeID:
            query = query + ' where id=:id'
            values['id']=animeID
    
    query = query + ' order by name'
    if n:
        values['n']= n
        query = query+' limit :n'
    print(query)
    resp = c.execute(query,values)
    resp_list = [{'id':a[0],'name':a[1],'url':a[2]} for a in resp.fetchall()]
    conn.close()
    
    return resp_list

def getlist(update=False):
    if initDB(update):
        anime_list = []
        list_url = r'http://www.anime1.com/content/list/'
        resp     = req.get(list_url,headers=headers)
        soup     = BeautifulSoup(resp.content,features="html.parser")
        tags     = soup.find_all(class_='anime-list')

        "debug"
        if debug:
            with open('log.txt','w',encoding='utf-8') as f:
                for tag in tags:
                    f.write(tag.prettify())
        "debug"
        
        for tag in tags:
            a_tags = tag.find_all('a')
            for a in a_tags:
                anime = {'name':a.text,'url':a.get('href')}
                anime_list.append(anime)
        print("inserting many")
        insertmany(anime_list)
        
        with open('list.txt','w',encoding='utf-8') as f:
            for anime in anime_list:
                f.write(anime['name'])
                f.write('\t\t')
                f.write(anime['url'])
                f.write('\n')
    return
        
    

def getURLs(url):
    #anime = search(animeID=animeID)
    #url = anime['url']
    print('getting all urls from :')
    print(url)
    url_list = []
    resp     = req.get(url,headers=headers)
    soup     = BeautifulSoup(resp.content,features="html.parser")
    tags     = soup.find_all(class_='anime-list')
    if len(tags)>1:
        tags = tags[1]
    else:
        tags = tags[0]

    "debug"
    if debug:
        with open('loglist.txt','w',encoding='utf-8') as f:
            f.write(tags.prettify())
    "debug"
    
    a_tags = tags.find_all('a')
    print('length ',len(a_tags))
    for a in a_tags:
        anime = {'name':a.text,'url':a.get('href')}
        url_list.append(anime)
    return url_list

def get_anime1(url):
    delay()
    for i in range(3):
        print(url)
        resp     = req.get(url,headers=headers)
        text     = resp.content
        
        link = text[text.find("file:".encode('utf-8')):]
        
        if link != '':
            link = link[link.find("http://".encode('utf-8')):]
            link = link[:link.find("\"".encode('utf-8'))]
        size =  get_size(link)
        if(size>0):
            break
        print("retrying")
    
    return link,size

def get_size(url):
    delay()
    if url=='' or url==None:
        return 0
    size = 0
    try:
        resp = req.head(url, headers = headers)
    except Exception as e:
        #print(e)
        return 0
    if resp.status_code == 404:
        print(url,"\n not found error code:404")
    for test in ["content-length","Content-Length"]:
        try:
            size = int(resp.headers[test])
            break
        except Exception as e:
            pass
            #print(e)
    return size

def main():
    pattern = input("Enter anime to be found:")
    anime_list = search(pattern,n=15)
    while not len(anime_list):
        pattern = input(pattern+" not found re enter anime:")
        anime_list = search(pattern,n=15)
    print("\n\n\n")
    i=0
    while i<len(anime_list):
        anime = anime_list[i]
        print("%2d: %4d\t"%(i+1,anime['id']),anime['name'])
        i = i+1
    ch = int(input("Enter your choice: "))-1
    url = anime_list[ch]['url']
    name = anime_list[ch]['name']
    url_list = getURLs(url)
    with open("out.txt","w",encoding='utf-8') as f:
        i = 0
        while i<len(url_list):
            f.write(str(i+1)+" "+url_list[i]['name']+"\n")
            i+=1
    ep_no = len(url_list)-5
    for ep in url_list[-5:]:
        print(ep_no+1,ep['name'],'\n')#,ep['url'])
        ep_no = ep_no+1
        
    while True:
        start   = input("Enter lower limit: ")
        if start=='<':
            ep_no = ep_no-10
            if ep_no<0:
                if ep_no==-5:
                    ep_no = len(url_list)-5
                else:
                    ep_no = 0
            for ep in url_list[ep_no:ep_no+5]:
                print(ep_no+1,ep['name'],'\n')#,ep['url'])
                ep_no = ep_no+1
        elif start=='>':
            ep_no = ep_no%len(url_list)
            for ep in url_list[ep_no:ep_no+5]:
                print(ep_no+1,ep['name'],'\n')#,ep['url'])
                ep_no = ep_no+1
        elif start=='quit':
            return
        else:
            break
        
    end = 0
    if start=='all':
        start = 0
        end = len(url_list)
    else:
        start   = int(start)-1
        end     = int(input("Enter upper limit: "))
    
    link_list = []
    size_list = []
    SIZE = 5
    with Pool(SIZE) as executor:
        URLs  = [url['url'] for url in url_list[start:end]]
        names = [url['name'] for url in url_list[start:end]]
        link_list = executor.map(get_anime1,URLs)
        size_list = [size[1] for size in link_list]
        link_list = [link[0] for link in link_list]
        link_list = [{'link':link,'name':name} for link,name in zip(link_list,names)]

    #with Pool(SIZE) as executor:
    #size_list = executor.map(get_size,[link['link'] for link in link_list])
    """
    for url in url_list[start:end]:
        link = get_anime1(url['url'])
        link_list.append({'link':link,'name':url['name']})
    """
    total_size = 0
    with open(name+'.html','w',encoding='utf-8') as out:
        out.write("<html>\n\t<body>")
        out.write("<a href=%s>%s</a></br></br>"%(url,name))
        #for link in link_list:
        for link,size in zip(link_list,size_list):
            #print(link['link'])
            print('Scraping ',link['name'])
            link_url  = link['link'].decode("utf-8")
            link_name = link['name']

            #html start
            html = "<a href='%s' download='%s.mp4'>%s</a>"%(link_url,link_name,link_name)
            #size = get_size(link_url)
            size = size/(2**20)
            total_size += size
            style = "color:"
            if size<35:
                style += 'Green;'
            elif size<50:
                style += 'Grey;'
            elif size<70:
                style += 'Orange;'
            else:
                style += 'Red;'
            html += "<span style='%s'> %.2f MB </span></br>\n"%(style,size)
            #html end
            
            out.write(html)
        out.write("<span> Total size = %.2f MB </span></br>\n"%total_size)
        out.write("\t</body>\n</html>")
        
    webbrowser.open(name+'.html')
    #getlist()
    #getlist(update=True)
    
if __name__=="__main__":
    main()
