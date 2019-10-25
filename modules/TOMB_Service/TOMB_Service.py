'''
    .SYNOPSIS
    Collects Services running/installed on host. Modular loaded via TOMB.py
    
    .NOTES
    DATE:       18 AUG 19
    VERSION:    0.9.0 - Initial Beta
    AUTHOR:     Brent Matlock -Lyx

    .DESCRIPTION
    Used to pull Services from host for ingest into Splunk

    .PARAMETER Computer
    Used to specify list of computers to collect against, if not provided then hosts are pulled from
    .\\includes\\tmp\\DomainList.csv

    .PARAMETER Path
    Used to specify where output folder should be, by default when lauched via TOMB.py this is the execution path
    where TOMB.py was launched

    .EXAMPLE
    WIll capture services on localhost
        TOMB_Service.py -c localhost

    .EXAMPLE
    Will capture services from the domain controller on the example.com domain.
        TOMB_Service.py -d "DC=example,DC=com" -c dc01
        TOMB_Service.py -c "dc01.cyber.lab"
'''

#Imports
import argparse
import sys
import os
import datetime
import wmi
import time

#Provides TOMB the ability to use commandline parameters via tabbing
def Main():
    #Generate the arguements for use when running without tomb.py
    parser = argparse.ArgumentParser()
    parser.add_argument("-d","--Domain", help="Specify Domain for Collection", type=str)
    parser.add_argument("-s","--Server", help="Specify Server hosting AD", type=str)
    parser.add_argument("-t","--Threads", help="Specify number of concurrent jobs", type=int, default=50)
    parser.add_argument("-c","--Computer", help="Specify Computer(s) for Collection", type=str)
    parser.add_argument("-C","--Collects", help="Specify Collection modules", type=str)
    parser.add_argument("-l","--LogID", help="Specify Event ID(s) for Collection", type=str)
    parser.add_argument("-S","--Setup", help="Guided Splunk installation", type=str)
    parser.add_argument("-P","--Path", help="Used to pass CWD to other modules", type=str)
    args = parser.parse_args()
    #Tie parameters to variables for later use
    Computer = (args.Computer)
    Path = (args.Path)
    startWMI(Computer, Path)


#WMI DCOM Connection Block
def startWMI(Computer, Path):
    #begin wmi dcom connection for Service Collection
    try:
        Computer = (Computer).lower().replace('"','')
        conn = wmi.WMI(Computer)
        for service in conn.Win32_Service():
            serviceOutput = open('.\\Files2Forward\\temp\\Service\\' + (Computer).replace('"','').replace('\n','') + '.json', 'a+')
            if service is not None:
                serviceOutput.write(str(service))
            serviceOutput.close()
        conn.close()
    #Capture any errors for errorlogs output
    except BaseException as error:
        ErrorLog = open('.\\logs\\errorlog\\service.log', 'a')
        date = datetime.datetime.now().strftime("%d.%b %Y %H:%M:%S")
        Error = ((date) + ": " + (Computer) + " :" + str(error))  + '\n'
        ErrorLog.writelines(Error)
        ErrorLog.close()
    #Move information from temporary located to folder being used for Splunk Batch
    finally:
        with open('.\\Files2Forward\\temp\\Service\\' + (Computer).replace('"','').replace('\n','') + '.json') as tempService:
            lines = tempService.read()
        with open('.\\Files2Forward\\Service\\' + (Computer).replace('"','').replace('\n','') + '.json', 'a+') as newService: 
            for line in lines:
                if line.strip("\n") != "instance of Win32_Service":
                    newService.write(line)


#Used to make file modular (Ran without utilizing tomb.py)
if __name__ == '__main__':
    Main()