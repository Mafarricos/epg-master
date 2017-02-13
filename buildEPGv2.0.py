#!/usr/bin/env python
# -*- coding: utf-8 -*-

##########################################
## buildEPG.py - Builds EPG file for channels present in channels file, taking in account the TV schedule in services.sapo.pt
## by warlockPT
## v1.0 - 2015/04/10
##########################################

#imports
import urllib
import datetime
from xml.dom.minidom import parse
from xml.dom.minidom import Document
import xml.dom.minidom
import xml.etree.cElementTree as ET

##########################################
## Log flag
# log=0 - No logging
# log=1 - Minimal logging
# log=2 - Full logging
log=1
##########################################

##########################################
## epgFilename - Full filename (including path) for file which will contain EPG
epgFilename="epgFile.xml"
##########################################

##########################################
## channelFilename - Full filename (including path) for file which contains channels
## File format:
##  meoCode - Code for which channel is recognized in services.sapo.pt
##  tvg-id - EPG code ID for channel under m3u list
##  name - channel name under m3u list
channelFilename="channelList.xml"
##########################################

#get current and next day
today= datetime.datetime.now()
if log>0: print "Start: {0}".format(today)
sDate=str(today.year)+"-"+str(today.month).zfill(2)+"-"+str(today.day).zfill(2) 
tomorrow=today+datetime.timedelta(days=8)
eDate=str(tomorrow.year)+"-"+str(tomorrow.month).zfill(2)+"-"+str(tomorrow.day).zfill(2) 

if log>0: print "Today: {0}  Tomorrow: {1}".format(sDate, eDate)

url="http://services.sapo.pt/EPG/GetChannelByDateInterval?channelSigla={0}&startDate={1}+00%3A00%3A00&endDate={2}+00%3A00%3A00"

# open epg file
if log>0: print "Opening epgfilename <{0}>...".format(epgFilename)
epgFile = open(epgFilename, 'w')
epgFile.write('<?xml version="1.0" encoding="UTF-8?>\n')
epgFile.write('<tv>\n')

#read channel list
if log>0: print "Opening channel list <{0}>...".format(channelFilename)

DOMTree = xml.dom.minidom.parse(channelFilename)
collection = DOMTree.documentElement
channels = collection.getElementsByTagName("channel")
if log>0: print "Reading channels..."
for channel in channels:
    meoCode = channel.getElementsByTagName('meoCode')[0]
    tvgID = channel.getElementsByTagName('tvg-id')[0]
    name = channel.getElementsByTagName('name')[0]

    if tvgID.firstChild is None:
        if log>0:
            print "  TVG is empty"
        continue

    if meoCode.firstChild is None:
        if log>0:
            print "  MeoCode is empty"
        continue

    if name.firstChild is None:
        if log>0:
            print "  Name is empty"
        continue
    
    if log>0:
        print "  MeoCode: <{0}>  TVG: <{1}>  Name: <{2}>".format(meoCode.firstChild.data,tvgID.firstChild.data,name.firstChild.data)
        
    #format link to web-service
    link = url.format(meoCode.firstChild.data, sDate, eDate)
    if log>1: print "    Link: {0}".format(link)

    # add channel info to epgfile
    epgFile.write('\t<channel id="{0}">\n'.format(tvgID.firstChild.data))
    epgFile.write('\t\t<display-name>{0}</display-name>\n'.format(name.firstChild.data))
    epgFile.write('\t</channel>\n')
    
    #read web-service
    f = urllib.urlopen(link)
    myfile = f.read()

    #xml parse
    DOMTree = xml.dom.minidom.parseString(myfile)
    collection = DOMTree.documentElement
    programs = collection.getElementsByTagName("Program")
    if log>0: print "    Reading programs..."
    n=0
    for program in programs:
        title = program.getElementsByTagName('Title')[0]
        desc = program.getElementsByTagName('Description')[0]
        startTime = program.getElementsByTagName('StartTime')[0]
        endTime = program.getElementsByTagName('EndTime')[0]
        sTime=str(startTime.firstChild.data).translate(None,'-: ')+" +0100"
        eTime=str(endTime.firstChild.data).translate(None,'-: ')+" +0100"
        n=n+1
        if log>1:
            print "      Title: ",title.firstChild.data.encode('UTF-8'),"\n    Desc: ",desc.firstChild.data.encode('UTF-8'),"\n    Start: ",startTime.firstChild.data," ",sTime,"\n    End: ",endTime.firstChild.data," ",eTime
            print "      --------------"
        
        #add program info to epgfile
        epgFile.write('\t<programme channel="{0}" start="{1}" stop="{2}">\n'.format(tvgID.firstChild.data, sTime, eTime))
        epgFile.write('\t\t<title lang="pt">{0}</title>\n'.format(title.firstChild.data.encode( "utf-8" )))
        epgFile.write('\t\t<desc lang="pt">{0}</desc>\n'.format(desc.firstChild.data.encode( "utf-8" )))
        epgFile.write('\t</programme>\n')
##        pr = ET.SubElement(root, "programme", channel=tvgID.firstChild.data, stop=eTime, start=sTime)
##        doc = ET.SubElement(pr, "title", lang="pt").text=title.firstChild.data.encode( "utf-8" )
##        doc = ET.SubElement(pr, "desc", lang="pt").text=desc.firstChild.data.encode( "utf-8" )

            
    if log>0: print "    {0} programs read!".format(n)

#epg xml close
if log>0: print "Closing epgfilename..."
epgFile.write('</tv>\n')
epgFile.close()

today= datetime.datetime.now()
if log>0: print "End: {0}".format(today)
if log>0: print "DONE"
