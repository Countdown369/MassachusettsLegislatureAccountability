#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Aug 21 15:51:41 2022

@author: cabrown802
"""

from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import ssl
from time import sleep
import pandas as pd
import numpy as np
import ast

def oneCom(master, link, gcontext):
    
    reqsub = Request(master + link)
    html_pagesub = urlopen(reqsub, context = gcontext)
    soupsub = BeautifulSoup(html_pagesub, "lxml")
    
    dfto = str(soupsub)[str(soupsub).find('<title>'):]
    committee = dfto[7:dfto.find('</title>')]
    members = str(soupsub).split("Members Tab",1)[1]
    
    if 'Senate' in committee:
        
        members = members[members.find('<a href="/Legislators/Profile'):]
        members = members[36:]
        senateChair = members[:members.find('</a>')]
        
        if 'Rules' not in committee:
            members = members[members.find('<a href="/Legislators/Profile'):]
            members = members[36:]
            senateViceChair = members[:members.find('</a>')]
    
        nonrankingSenate = []
        while (members.find('Legislators') < members.find('Upcoming Hearings')):
            members = members[members.find('<a href="/Legislators/Profile'):]
            members = members[36:]
            nonrankingSenate.append(members[:members.find('</a>')])
        
        if 'Rules' not in committee:
            return [committee, senateChair, senateViceChair, nonrankingSenate]
        else:
            return [committee, senateChair, nonrankingSenate]
            
    elif 'House' in committee:
        
        members = members[members.find('<a href="/Legislators/Profile'):]
        members = members[36:]
        houseChair = members[:members.find('</a>')]
    
        members = members[members.find('<a href="/Legislators/Profile'):]
        members = members[36:]
        houseViceChair = members[:members.find('</a>')]
    
        nonrankingHouse = []
        while (members.find('Legislators') < members.find('Upcoming Hearings')):
            members = members[members.find('<a href="/Legislators/Profile'):]
            members = members[36:]
            nonrankingHouse.append(members[:members.find('</a>')])
            
        return [committee, houseChair, houseViceChair, nonrankingHouse]
        
    else:
        
        members = members[members.find('<a href="/Legislators/Profile'):]
        members = members[36:]
        senateChair = members[:members.find('</a>')]
        
        if 'Rules' not in committee:
            members = members[members.find('<a href="/Legislators/Profile'):]
            members = members[36:]
            senateViceChair = members[:members.find('</a>')]
    
        nonrankingSenate = []
        while (members.find('Legislators') < members.find('House Members')):
            members = members[members.find('<a href="/Legislators/Profile'):]
            members = members[36:]
            nonrankingSenate.append(members[:members.find('</a>')])
            
        members = members[members.find('<a href="/Legislators/Profile'):]
        members = members[36:]
        houseChair = members[:members.find('</a>')]
    
        members = members[members.find('<a href="/Legislators/Profile'):]
        members = members[36:]
        houseViceChair = members[:members.find('</a>')]
    
        nonrankingHouse = []
        while (members.find('Legislators') < members.find('Upcoming Hearings')):
            members = members[members.find('<a href="/Legislators/Profile'):]
            members = members[36:]
            nonrankingHouse.append(members[:members.find('</a>')])
        if 'Rules' not in committee:
            return [committee, senateChair, senateViceChair, nonrankingSenate, houseChair, houseViceChair, nonrankingHouse]
        else:
            return [committee, senateChair, nonrankingSenate, houseChair, houseViceChair, nonrankingHouse]

def grabComstruct(master, nakedcomlinks, gcontext):
    
    colnames = ["Committee", "Senate Chair", "Senate Vice Chair", "Senate Nonranking Member", "House Chair", "House Vice Chair", "House Nonranking Member"]
    comStruct = pd.DataFrame(columns = colnames)
    
    for link in nakedcomlinks:
        
        vals = oneCom(master, link, gcontext)
        
        if 'Rules' in vals[0] and 'Joint' in vals[0]:
            committee = vals[0]
            senateChair = vals[1]
            nonrankingSenate = vals[2]
            houseChair = vals[3]
            houseViceChair = vals[4]
            nonrankingHouse = vals[5]
            comStruct.loc[len(comStruct.index)] = [committee, senateChair, np.nan, nonrankingSenate, houseChair, houseViceChair, nonrankingHouse]
            print("Done with " + committee)
            
        elif len(vals) == 7:
            committee = vals[0]
            senateChair = vals[1]
            senateViceChair = vals[2]
            nonrankingSenate = vals[3]
            houseChair = vals[4]
            houseViceChair = vals[5]
            nonrankingHouse = vals[6]
            comStruct.loc[len(comStruct.index)] = [committee, senateChair, senateViceChair, nonrankingSenate, houseChair, houseViceChair, nonrankingHouse]
            print("Done with " + committee)
            
        elif len(vals) == 4:
            if 'Senate' in vals[0]:
                if 'Rules' not in vals[0]:
                    committee = vals[0]
                    senateChair = vals[1]
                    senateViceChair = vals[2]
                    nonrankingSenate = vals[3]
                    comStruct.loc[len(comStruct.index)] = [committee, senateChair, senateViceChair, nonrankingSenate, np.nan, np.nan, np.nan]
                    print("Done with " + committee)
                else:
                    committee = vals[0]
                    senateChair = vals[1]
                    nonrankingSenate = vals[2]
                    comStruct.loc[len(comStruct.index)] = [committee, senateChair, np.nan, nonrankingSenate, np.nan, np.nan, np.nan]
                    print("Done with " + committee)
                
            elif 'House' in vals[0]:
                committee = vals[0]
                houseChair = vals[1]
                houseViceChair = vals[2]
                nonrankingHouse = vals[3]
                comStruct.loc[len(comStruct.index)] = [committee, np.nan, np.nan, np.nan, houseChair, houseViceChair, nonrankingHouse]
                print("Done with " + committee)
                
        sleep(1)

    comStruct.to_excel("GeneralCourtCommitteeAppointments.xlsx")
    
    return comStruct

def rankMembers(og):
    names = []
    
    for i, r in og.iterrows():
        for t in r[2:]:
            if not isinstance(t, float) and '[' not in t and t not in names:
                names.append(t)
            elif not isinstance(t, float) and '[' in t:
                t = ast.literal_eval(t)
                for k in t:
                    if k not in names:
                        names.append(k)
            else:
                pass
        

    infos = []
    for name in names:
        custom = [name, 0, 0]
        for i, r in og.iterrows():
            colnum = 1
            for t in r[2:]:
                colnum = colnum + 1
                if not isinstance(t, float) and '[' not in t:
                    if t == name:
                        if og.columns[colnum] == 'Senate Chair' or og.columns[colnum] == 'House Chair':
                            custom[1] = custom[1] + 2
                        else:
                            custom[1] = custom[1] + 1
                        custom[2] = custom[2] + 1
                        custom.append(og.columns[colnum] + ' of ' + og.iloc[i][1])
                elif not isinstance(t, float) and '[' in t:
                    t = ast.literal_eval(t)
                    for k in t:
                        if k == name:
                            if og.columns[colnum] == 'Senate Chair' or og.columns[colnum] == 'House Chair':
                                custom[1] = custom[1] + 2
                            else:
                                custom[1] = custom[1] + 1
                            custom[2] = custom[2] + 1
                            custom.append(og.columns[colnum] + ' of ' + og.iloc[i][1])
        
        customtest = custom[0].split(" ")
        if customtest[-1] == 'Jr.' or customtest[-1] == 'Jr' or customtest[-1] == 'III':
            customtest = customtest[:-1]
            
        last = customtest[-1]
        if "," in last:
            last = last[:-1]
        first = customtest[0]
        custom[0] = first + " " + last
        
        if customtest[0] == 'F.':
            custom[0] = 'F. Jay Barrows'
            
        if customtest[0] == 'Carlos' and 'Gon' in custom[0]:
            custom[0] = 'Carlos Gonzalez'
            
        infos.append(custom)
        
    d = {}

    for inf in infos:
        d[inf[0]] = (inf[1], inf[2], inf[3:])
        
    pointsdf = pd.DataFrame.from_dict(d).transpose()
    pointsdf = pointsdf.rename(columns={0: "Power", 1: "Positions", 2: "Titles"})
    pointsdf = pointsdf.sort_values(by = ['Power'], ascending=False)
    
    return pointsdf
    
def deets(collection):
    ff = 0
    colnames = ["Member", "Chamber", "District", "Party", "Room", "Phone", "Email"]
    comDeets = pd.DataFrame(columns = colnames)
    repLinks = []
    for members in collection:
        ff = ff + 1
        while members.find("href") < members.find("tbody"):
            members = members[members.find('<td><a href="/Legislators/Profile'):]
            repLinks.append("https://malegislature.gov/" + members[13:38])
            members = members[40:]
            first = members[:members.find('</a>')]
            
            members = members[members.find('<td><a href="/Legislators/Profile'):]
            members = members[40:]
            last = members[:members.find('</a>')]
            
            members = members[members.find('</td>\n<td>'):]
            members = members[10:]
            district = members[:members.find('</td>')]
            
            members = members[members.find('<td>'):]
            members = members[4:]
            party = members[:members.find('</td>')]
            
            members = members[members.find('<td>'):]
            members = members[4:]
            room = members[:members.find('</td>')]
            
            members = members[members.find('<td>'):]
            members = members[4:]
            number = members[:members.find('</td>')]
            
            members = members[members.find('.gov">'):]
            members = members[6:]
            email = members[:members.find('</a>')]
            
            if ff == 1:
                comDeets.loc[len(comDeets.index)] = [first + " " + last, "Senate", district, party, room, number, email]
            if ff == 2:
                comDeets.loc[len(comDeets.index)] = [first + " " + last, "House", district, party, room, number, email]
    
    comDeets = comDeets.set_index("Member")
    return comDeets, repLinks[:-1]

def prepareMemberPages(gcontext):
    
    reqsub = Request("https://malegislature.gov/Legislators/Members/Senate")
    html_pagesub = urlopen(reqsub, context = gcontext)
    soupsub = BeautifulSoup(html_pagesub, "lxml")
    senateMembers = str(soupsub)
    senateMembers.replace('á', 'a')
    
    reqsub = Request("https://malegislature.gov/Legislators/Members/House")
    html_pagesub = urlopen(reqsub, context = gcontext)
    soupsub = BeautifulSoup(html_pagesub, "lxml")
    houseMembers = str(soupsub)
    houseMembers.replace('á', 'a')
    
    return senateMembers, houseMembers
    
def main():
    
    gcontext = ssl._create_unverified_context() # only for idiots
    
    master = "https://malegislature.gov/Committees/"
    req = Request(master)
    html_page = urlopen(req, context = gcontext)
    soup = BeautifulSoup(html_page, "lxml")
    
    links = []
    for link in soup.findAll('a'):
        links.append(link.get('href'))
        
    comlinks = []
    for link in links:
        if isinstance(link, str) and 'Committees/Detail' in link:
            comlinks.append(link)
                
    nakedcomlinks = [link[12:] for link in comlinks]
    
    grabComstruct(master, nakedcomlinks, gcontext)
    
    comStruct = pd.read_excel("GeneralCourtCommitteeAppointments.xlsx")
    pointsdf = rankMembers(comStruct)
    
    senateMembers, houseMembers = prepareMemberPages(gcontext)
    
    comDeets, repLinks = deets([senateMembers, houseMembers])
    
    comDat = pd.merge(comDeets, pointsdf, left_index=True, right_index=True)
    comDat.to_excel("COMDATA.xlsx")
    
main()