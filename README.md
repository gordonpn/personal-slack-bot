# Personal Butler Slack bot

## Description
This project started as a Golang cli script to ping internal IP addresses and return me if they are connected. I wanted an easier way to run the script without having to ssh into my Raspberry Pi server. so I decided to rewrite it in Python and turn it into a Slack Bot I could ping through the Slack app. 

Seeing how useful a Slack bot could be, I started writing more features for the Slack bot and it turned into a personal Slack bot that responds to my needs between interacting with my Jenkins server, Raspberry Pi server while I'm not at home.  

## Features
*  Can ping a list of internal IP addresses
*  Can ping a subset of those addresses
*  Can set up a watch for certain addresses or all
*  Can tell the uptime of the server it's currently running on
*  Can tell the average CPU load
*  Can start build Jenkins jobs on demand
*  Can notify when a Jenkins job is no longer in progress

## Prerequisites
````bash
pip install -r requirements.txt
````

## Roadmap/Todo

* [x]  Rewrite in Python
* [x]  Develop a Slack Bot to communicate the information
* [x]  Info on uptime
* [x]  Info on cpu load
* [x]  Refactor code to make more object-oriented
* [x]  watch all addresses feature
* [x]  load from external sources for addresses and jenkins url
* [ ]  stop all threads or stop one thread