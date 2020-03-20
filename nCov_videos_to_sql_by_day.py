#coding:utf-8
import datetime
import time
try:
    from urllib import parse
    import pymysql
    from bs4 import BeautifulSoup
    import requests

    headers = {
       "Cookie":"BD_CK_SAM=1; BDSVRTM=106; sugstore=0; H_PS_645EC=85f2R6tlIFSYMlLNd3LVH22NkccbbpqRzqhNqZblaXlmjyHdHtfMeRDWTboOHHRZ%2FCFwhg; COOKIE_SESSION=86863_0_9_5_16_12_0_0_9_3_5_0_95553_0_30_0_1582270427_0_1582270397%7C9%230_0_1582270397%7C1; BD_UPN=1d314753; H_PS_PSSID=; delPer=0; PSINO=2; ZD_ENTRY=empty; BAIDUID=C34F373EF26783E418748E38104495EE:FG=1; BIDUPSID=926D6BEBC3032EFA425DDBDF6E57496B; PSTM=1581651629; BDORZ=FFFB88E999055A3F8A630C64834BD6D0; BDUSS=NZUTFKdld0OGNEWGtFb0FISU5hU2dReVB3R3J3MnNWUDBTRHhWTy1ES2pkblZlRVFBQUFBJCQAAAAAAAAAAAEAAACtmh02amluZ3FpZHVvYmFuYm8AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAKPpTV6j6U1eSG; BDRCVFR[fb3VbsUruOn]=mk3SLVN4HKm",
       "Referer":"https://www.baidu.com/sf/vsearch?pd=video&tn=vsearch&lid=ce4473a20002690e&ie=utf-8&wd=%E6%96%B0%E5%86%A0&rsv_spt=7&rsv_bp=1&f=8&rsv_pq=ce4473a20002690e",
       "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.18362"}

    list = ["新冠","疫情","肺炎","确诊病例"]

    def write_to_mysql(title,v_url,source,img,keyword):
        sql = '''select count(linkname) from fylink WHERE linkname = "{}" AND instance = "{}"'''.format(title,keyword)
        cursor.execute(sql)
        db.commit()
        if cursor.fetchall()[0][0] == 0:    #查到表中记录为0，才插入，不为0就是已经有记录了
            sql = '''INSERT INTO fylink(uri,instance,link,linkname,sourcetype,source,image) VALUES ("null","{}","{}","{}","视频","{}","{}")'''.format(keyword,v_url,title,source,img)
            cursor.execute(sql)
            db.commit()
            print(sql)

    def linking(title,v_url,source,img):
        with open("all_entities.txt", "r", encoding="utf-8-sig") as fr:
            entities = fr.readlines()
            for keyword in entities:
                if keyword.strip() in title:
                    write_to_mysql(title,v_url,source,img,keyword.strip())

    while 1:
        now = datetime.datetime.now()
        now_str = str(now)[10:19]
        # print(now_str)
        if "00:00:00" in now_str:

            db = pymysql.connect(host="39.100.31.203", user="root", password="edukg@mysql", database="bookinfo", charset="utf8")
            cursor = db.cursor()

            for word in list:
                print("############################",word,"#######################")
                # wd = parse.quote(str(word))
                for page in range(20):
                    url = "https://www.baidu.com/sf/vsearch?pd=video&tn=vsearch&lid=ce4473a20002690e&ie=utf-8&wd={}&rsv_spt=7&rsv_bp=1&f=8&rsv_pq=ce4473a20002690e&async=1&pn={}0".format(word,page)
                    print(url)
                    r = requests.get(url,headers = headers)
                    soup = BeautifulSoup(r.text,"html.parser")

                    for item in soup.find_all("div", class_="video_list video_short"):
                        # print(item)
                        if item.find_all("span")[-1].string != None:
                            if any(word in item.find_all("span")[-1].string for word in ["分钟前", "小时前","天前"]):
                                title = item.find("a",class_="video_list_title_small").text.strip()
                                v_url = item.find("a",class_="video_list_title_small").get("href").strip() #url
                                if item.find(class_="wetSource") != None:
                                    source = item.find(class_="wetSource").text.replace("来源：","")  # source
                                else:
                                    source = ""
                                img = item.find("img").get("src").replace("amp;","")  #img
                                print("爬取一条数据：",title,img)
                                linking(title,v_url,source,img)
                    time.sleep(10)
                time.sleep(10)
            cursor.close()
            db.close()
        time.sleep(1)
except Exception as e:
    print(datetime.datetime.now(),e)

