#SQL Scripts for CS 660 Big Data Project - Google Play Store Data Crawl
#Author: Govind Yatnalkar
#Mentor/ Guide: Dr. Haroon Malik
#Date: 11th December 2018
#Designed & Developed at Marshall University.

#Dropping the database initally for a clean startup
drop database gminer;

#Query for Database Creation & Showing Tables
create database gminers;
use gminers;
show tables;

#Select Query for all tables
select * from appdata order by crawl_time desc;
select * from bestappdata order by crawl_time desc;
select * from urls order by date_time desc;

#View Structure of all tables
desc urls;
desc appdata;
desc bestappdata;

#Create App Data Table for storing play store crawled apps
create table appdata(
	docid varchar(100),
    app_name text,
    app_url text,
    url_id int(3),
    crawl_time datetime
);

#Create Best App Data table for storing apps crawled from a Website showing best applications
create table bestappdata(
    docid varchar(100),
    app_name text,
    app_url text,
    url_id int(3),
	crawl_time datetime
);

#Create table urls for saving urls along with date time and urlid
create table urls(
	url_id int(3) auto_increment primary key,
	url_name varchar(300),
    date_time datetime
);

#Dropping Tables
drop table appdata;
drop table bestappdata;
drop table urls;
