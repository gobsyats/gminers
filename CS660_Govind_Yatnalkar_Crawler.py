#Title: Data Crawling for Play Store
#Author: Govind Yatnalkar (901875614)
#Email: yatnalkar@marshall.edu
#Guide/ Mentor: Dr Haroon Malik
#Group Name: G-Miners.
#Date: 11th December 2018
#Designed & Developed at CITE, Marshall University

#Libraries installed for the Project: 
#beautifulsoup4 - Library Used for Pulling Web Page Data
#request - Library used or opening a specified url
#lxml - A third party library used for parsing HTML content
#mysql.connector - A library for making a connection to a database using python

#Imoport the packages from installed libraries
import urllib.request
import bs4 as bs
from urllib import parse
import mysql.connector
import datetime

#creating a connection to localdb, gminers
#Db hosted on localhost with following mysql credentials 
#(host, root, passwd, database)

#Credentials for local database server
#mydb = mysql.connector.connect(
#  host="localhost",
#  user="root",
#  passwd="Govind@123",
#  database="gminers"
#)

#Credentials for remote database server
mydb = mysql.connector.connect(
  host="10.103.92.251",
  user="gminer",
  passwd="gminer",
  database="gminers"
)

#create a curson using above mydb connection
mycursor = mydb.cursor()
mycursor = mydb.cursor(buffered=True)

#appdata - table for saving details of play store apps
#bestppdata - table for saving details of top rated apps
#delete first the old data from both the tables
#mycursor.execute("delete from appdata2")g
#mycursor.execute("delete from bestappdata2")

print("A Program to Crawl Web Page - PlayStore Apps & Top Rated Apps Web Page")

#Get the link from shell/ command promt and printing it
play_store_link=input("Enter a URL of the Page: ")
print("You Entered the Link: ",play_store_link)    

#Code for checking if a crawled url is present in the database
url_name_temp = ""
#if urls table is not empty, execute this code
mycursor.execute("select * from urls")
if mycursor.rowcount > 0:
    print("URLS TABLE NOT EMPTY")
    #check if entered url of play store is present in the database
    url_get = "select * from urls where url_name = %s"    
    mycursor.execute(url_get, (play_store_link,))
    result_url = mycursor.fetchall()
    #if a URL is present in the database
    if mycursor.rowcount>0:
        for row_url in result_url:
            #get the url (1st element in the string, 0th is id and 2nd is datetime in urls table)
            url_name_temp = row_url[1]
            if(url_name_temp == play_store_link):
                #if url is already present only update the date time of url in urls table
                print("Playstore Link Already Exists. Updating Only Time")
                sql_url = "UPDATE urls set date_time = %s where url_name= %s "
                val_url = (datetime.datetime.now(), play_store_link)  
                mycursor.execute(sql_url, val_url)   
    else:
        #If a new url is found, insert into urls table
        print("New Play Store Link Found But Row Count in URLS Table is Non Zero.")
        #Save this link or url in the database 
        sql_url_p = "INSERT INTO urls (url_name, date_time) values (%s, %s)"
        val_url_p = (play_store_link, datetime.datetime.now())
        mycursor.execute(sql_url_p, val_url_p)    
#Execute this code when the first time code runs or when urls table is empty
else:
    print("URLS TABLE EMPTY")
    print("New Play Store Link Found and NO URLS present in URL Table.")
    #Save this link or url in the database 
    sql_url_new = "INSERT INTO urls (url_name, date_time) values (%s, %s)"
    val_url_new = (play_store_link, datetime.datetime.now())
    mycursor.execute(sql_url_new, val_url_new)      
              
#Link: https://play.google.com/store/apps?hl=en
print("Crawling the Page...(Getting the App-Ids, Names and Their Play Store Links)...");

#A variable sauce to open the url requet
sauce = urllib.request.urlopen(play_store_link)
#open url and .text

#Getting the data into soup variable using a third party xml parser, lxml
soup = bs.BeautifulSoup(sauce, 'lxml')

#From the whole HTML document, 3 specific things are targeted:
#docid - id of the application
#title - name of the application
#link - the link to the playstore for installation
#All the data is available in a "a href" which has the class->'title'
for url in soup.find_all('a', class_= "title"):
    #Get only links (a href links)
    href = url.get('href')
   
    #If the link matches the below format then only get the link else go to next link'
    #Execute the following for each link if the link is in valid format
    if(href.find("/store/apps/details?id=com.") > -1):
        
        #href is like -> https://playstorelink?id=docid
        #Separate the docid and link based on the key 'id'
        docid=parse.parse_qs(parse.urlparse(href).query)['id'][0]
        title = (url.get('title'))
        
        #get url_id, url_name and date_time from urls table for entered play store url
        url_get = "select * from urls where url_name = %s"
        #Variables to store id and date_time, later assigned along with crawled apps found in crawling this url
        url_id_playstore = ""
        date_time_playstore = ""
        mycursor.execute(url_get, (play_store_link,))
        result_url = mycursor.fetchall()
        #get the url_id and date_time
        for row_url in result_url:
            url_id_playstore = row_url[0]
            date_time_playstore = row_url[2]
        
        #Code to check if a crawled app is present in the database
        sql_get = "select * from appdata where docid = %s"
        mycursor.execute(sql_get, (docid,))
        result_set = mycursor.fetchall()
        #A temp docid saves current found app found in for loop iterator of database appdata apps
        temp_docid = ""
        for row in result_set:
            temp_docid = row[0]
           # print(row["hit"], row["docid"])   
           
        #Targets are captured and proceeded to save in database     
        if(temp_docid == docid):
            #If the app crawled is present in the appdata table, DONT INSERT, only update date time
            print("This App Was Found in This Crawl Event. Only Updating Time for Docid: ", docid)
            sql_app_update = "UPDATE appdata set crawl_time = %s where docid= %s "
            val_app_update = (date_time_playstore, docid)  
            mycursor.execute(sql_app_update, val_app_update)              
        else:           
            #If the app crawled is a new one, simply insert into appdata table
            sql = "INSERT IGNORE INTO appdata values(%s, %s, %s, %s, %s)"
            val = (docid, title, href, url_id_playstore, date_time_playstore)
            #Execute Query
            mycursor.execute(sql, val)
            
            #Query only works if commited
            mydb.commit()      
            
            #Printing what is saved in database
            #print(docid, title, href)
            #Printing the status if data was inserted
            if(mycursor.rowcount>0):
                print("Data Was Inserted in MySQL Database for docid: ", docid)
            else:
                print("Data Was Not Inserted.")  

#Intimation of loop completion or end of data crawl
print("\n")
print("Data Crawling Completed for the Link: ", play_store_link)
print("\n")

#Heading to execute in a similar way for top rated apps web page
print("******************Tracking the Best or Top Rated Applications***************")

print("\n")

#Getting and displaying the link for top rated applications
top_rated_apps=input("Enter a Link to Crawl a Page for Top Rated Android Apps:")
print("You Entered the Link: ",top_rated_apps)


#Code for checking if a best apps crawled url is present in the database
url_name_temp_best = ""
#if urls table is not empty, execute this code
mycursor.execute("select * from urls")
if mycursor.rowcount > 0:
    print("URLS TABLE NOT EMPTY")
    #check if entered url of best apps is present in the database
    url_get = "select * from urls where url_name = %s"    
    mycursor.execute(url_get, (top_rated_apps,))
    result_url = mycursor.fetchall()
    #if a URL is present in the database
    if mycursor.rowcount>0:
        for row_url in result_url:
            #get the url (1st element in the string, 0th is id and 2nd is datetime in urls table)
            url_name_temp_best = row_url[1]
            if(url_name_temp_best == top_rated_apps):
                #if url is already present only update the date time of url in urls table
                print("Best Apps Link Already Exists. Updating Only Time")
                sql_url_best = "UPDATE urls set date_time = %s where url_name= %s "
                val_url_best = (datetime.datetime.now(), top_rated_apps)  
                mycursor.execute(sql_url_best, val_url_best)   
    else:
        #If a new url is found, insert into urls table
        print("New Best Apps Link Found But Row Count in URLS Table is Non Zero.")
        #Save this link or url in the database 
        sql_url_p_best = "INSERT INTO urls (url_name, date_time) values (%s, %s)"
        val_url_p_best = (top_rated_apps, datetime.datetime.now())
        mycursor.execute(sql_url_p_best, val_url_p_best)    
#Execute this code when the first time code runs or when urls table is empty
else:
    print("URLS TABLE EMPTY")
    print("New Best Apps Website Found and NO URLS present in URL Table.")
    #Save this link or url in the database 
    sql_url_new_best = "INSERT INTO urls (url_name, date_time) values (%s, %s)"
    val_url_new_best = (top_rated_apps, datetime.datetime.now())
    mycursor.execute(sql_url_new_best, val_url_new_best)      


print("Crawling the Page...(Getting the App-Ids, Names and Their Play Store Links from Best Apps Website)...");

# The Link: https://www.androidpit.com/best-android-apps

sauce = urllib.request.urlopen(top_rated_apps)
#open url and .text
soup = bs.BeautifulSoup(sauce, 'lxml') 

#The difference is the HTML tags
#docid = data-app-id
#title = spantitle

#the docids, names and hrefs are available in <a,href> with the specified class->'articleInstallApp'
for app in soup.find_all('a', class_= "articleInstallApp"):
    besthref = app.get('href')
    bestdocid = app.get('data-app-id')
    
    #title is in span of a specified class->'articleInstallAppTitle'
    spantitle = app.find('span', {'class': 'articleInstallAppTitle'})
    besttitle = spantitle.text
    
    
    #get url_id, url_name and date_time from urls table for entered best app url
    url_get = "select * from urls where url_name = %s"
    #Variables to store id and date_time, later assigned along with crawled apps found in crawling this url
    url_id_bestapps = ""
    date_time_bestapps = ""
    mycursor.execute(url_get, (top_rated_apps,))
    result_url_best = mycursor.fetchall()
    #get the url_id and date_time
    for row_url_best in result_url_best:
        url_id_bestapps = row_url_best[0]
        date_time_bestapps = row_url_best[2]
    
    #Code to check if a crawled app is present in the database
    sql_get_best = "select * from bestappdata where docid = %s"
    mycursor.execute(sql_get_best, (bestdocid,))
    result_set = mycursor.fetchall()
    #A temp docid saves current found app found in for loop iterator of database appdata apps
    temp_docid = ""
    for row in result_set:
        temp_docid = row[0]
       # print(row["hit"], row["docid"])   
       
    #Targets are captured and proceeded to save in database     
    if(temp_docid == bestdocid):
        #If the app crawled is present in the bestappdata table, DONT INSERT, only update date time
        print("This App Was Found in This Crawl Event. Only Updating Time for Docid: ", bestdocid)
        sql_app_update = "UPDATE bestappdata set crawl_time = %s where docid= %s "
        val_app_update = (date_time_bestapps, bestdocid)  
        mycursor.execute(sql_app_update, val_app_update)              
    else:           
        #If the app crawled is a new one, simply insert into bestappdata table with best app website crawl id and datetime
        print("Data Was Inserted in MySQL Database for Best Apps's docid: ", bestdocid)
        sql = "INSERT IGNORE INTO bestappdata values(%s, %s, %s, %s, %s)"
        val = (bestdocid, besttitle, besthref, url_id_bestapps, date_time_bestapps)
        #Execute Query
        mycursor.execute(sql, val)
        
        #Query only works if commited
        mydb.commit()        
        
#Intimation of loop completion or end of data crawl        
print("\n")
print("Data Crawling Completed for the Best Apps Website Link: ", top_rated_apps)
print("\n")

print("******************Thank You for Using the Data Crawler***************")
