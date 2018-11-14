#Title: Data Crawling for Play Store
#Author: Govind Yatnalkar (901875614)
#Email: yatnalkar@marshall.edu
#Guide/ Mentor: Dr Haroon Malik
#Group Name: G-Miners
#Date: November 4th 2018
#CITE, Marshall University

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

#creating a connection to localdb, gminers
#Db hosted on localhost with following mysql credentials 
#(host, root, passwd, database)
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  passwd="Govind@123",
  database="gminers"
)

#create a curson using above mydb connection
mycursor = mydb.cursor()

#appdata - table for saving details of play store apps
#bestppdata - table for saving details of top rated apps
#delete first the old data from both the tables
mycursor.execute("delete from appdata")
mycursor.execute("delete from bestappdata")

print("A Program to Crawl Web Page - PlayStore Apps & Top Rated Apps Web Page")

#Get the link from shell/ command promt and printing it
play_store_link=input("Enter a URL of the Page: ")
print("You Entered the Link: ",play_store_link)    

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
        
        #Targets are captured and proceeded to save in database
        #An insert query for inserting data
        sql = "INSERT IGNORE INTO appdata values(%s, %s, %s)"
        val = (docid, title, href)
        
        #Execute Query
        mycursor.execute(sql, val)
        
        #Query only works if commited
        mydb.commit()      
        
        #Printing what is saved in database
        print(docid, title, href)
        #Printing the status if data was inserted
        if(mycursor.rowcount>0):
            print("Data Was Inserted in MySQL Database.")
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
print("Crawling the Page...(Getting the App-Ids, Names and Their Play Store Links)...");

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
    
    #Required data captured and proceeded to save in database
    bsql = "INSERT IGNORE INTO bestappdata values(%s, %s, %s)"
    bval = (bestdocid, besttitle , besthref)
    
    #Execute insert query
    mycursor.execute(bsql, bval)
    
    #Data not inserted until commmited
    mydb.commit()      
    print(bestdocid, besttitle, besthref)
    
    #Printing the status of the cursor
    if(mycursor.rowcount>0):
        print("Data Was Inserted in MySQL Database.")
    else:
        print("Data Was Not Inserted.")
        
#Intimation of loop completion or end of data crawl        
print("\n")
print("Data Crawling Completed for the Link: ", top_rated_apps)
print("\n")

print("******************Thank You for Using the Data Crawler***************")