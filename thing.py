#!/usr/bin/python
#-*- coding:utf-8 -*-


import requests
import codecs
from bs4 import BeautifulSoup as bs

import datetime
from time import sleep

from peewee import *
from ThingModels import *


# Import smtplib for the actual sending function
import smtplib

# Import the email modules we'll need
from email.mime.text import MIMEText

ss=requests.Session()
proxies={
"http":'http://127.0.0.1:8087',
"https":'http://127.0.0.1:8087',
"ftp":'http://127.0.0.1:8087',
}


def get_page(url,proxies=None,save_file_name=None):
    while True:
        try:
            page = ss.get(url,proxies=proxies)
            print page
            if page.status_code==200:
                if save_file_name:
                    with codecs.open(save_file_name,'w',encoding='gbk') as f:
                        f.write(page.text)
                return page.text
        except Exception,e:
            print str(e)

def start_to_grap(url_list):
    i=0
    for url in url_list:
        i=i+1
        #grap(url,save_file_name= '%d.html' % i )
        grap(url)

def grap(url,save_file_name=None):
    while True:
        page=get_page(url,save_file_name=save_file_name)
        soup = bs(page)
        thing_list = soup.find('div',class_='J_TItems') 
        shop_info=soup.find('div',id='LineZing')
        if thing_list != None and shop_info != None:
            break
        else:
            print 'thing_list is None'

    shop_id=int(shop_info.get('shopid'))
    if not Shop.select().where(Shop.id == shop_id).exists():
        shop=Shop.create(id=shop_id,url=url)

    
    things=Thing.select()
    time_now=datetime.datetime.now()
    for thing in thing_list.find_all('dl',class_='item'):

        thing_id= int(thing.get('data-id'))

        price=float(thing.find('span',class_='c-price').string)

        detail_tag=thing.find('dd',class_='detail')
        describe=detail_tag.a.string.encode('utf-8')

        print thing_id
        print price
        print describe

        if things.where(Thing.id == thing_id).exists():
            thing=things.where(Thing.id==thing_id).get()
            if  price != thing.current_price:
                print "price changed!"
                thing_price=ThingPrice.create(thing=thing,price=thing.current_price,time=thing.update_time)
                q=Thing.update(current_price=price,current_describe=describe,update_time=time_now).where(Thing.id==thing_id)
                q.execute()
                mail_content_dict={'id':thing_id,'describe':describe,'old_price':thing.current_price,'new_price':price}
                #send_thing_price_changed_email(mail_content_dict)
        else:
            print "new thing insert!"
            thing=Thing.create(id=thing_id,
                    current_describe=describe,
                    current_price=price,
                    update_time=time_now,
                    shop=shop)
            mail_content_dict={'id':thing_id,'describe':describe,'old_price':0.0,'new_price':price}
            #send_thing_price_changed_email(mail_content_dict)
            


def create_tables():
    mysql_db.connect()
    if not Shop.table_exists():
        Shop.create_table()
    if not Thing.table_exists():
        Thing.create_table()
    if not ThingPrice.table_exists():
        ThingPrice.create_table()
    mysql_db.close()

def drop_tables():
    mysql_db.connect()
    if ThingPrice.table_exists():
        ThingPrice.drop_table(cascade=True)
    if Thing.table_exists():
        Thing.drop_table(cascade=True)
    if Shop.table_exists():
        Shop.drop_table(cascade=True)
    mysql_db.close()



def send_mail(recievers,subject,content):
    msg = MIMEText(content)
    
    #msg['key'] 里面都是RFC-2822 有关内容的实现 所以可以任意填甚至是不填，收件客户端会根据RFC-2822处理这个

    msg['Subject'] =subject 
    msg['From'] = '329210860@qq.com'
    msg['To'] = ";".join(recievers)
    
    try:
        s = smtplib.SMTP()
        s.connect(SMPTServer)
        s.login(username,passwd)

        s.sendmail(sender, recievers, msg.as_string())

        s.quit()
        return True
    except Exception,e:
        print str(e)
        return False



def send_thing_price_changed_email(m):
    with open('mail.tmpl','r') as f:
        s=f.read()
    content = s % (m['id'],m['describe'],m['old_price'],m['new_price'])
    if send_mail(recievers,'价格变动',content):
        print "发送成功"
    else:
        print "发送失败"
            
url_list = ('http://liangpinpuzi.tmall.com/category.htm',
            'http://airland.tmall.com/category.htm',
            'http://cheers.tmall.com/category.htm',)

if __name__=='__main__':
    #drop_tables()
    #create_tables()
    while True:
        start_to_grap(url_list)
        print 'sleep 20s'
        sleep(20)



# select current_describe,url from thing join shop on (thing.shop_id=shop.id);
