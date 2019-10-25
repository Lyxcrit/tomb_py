'''
    .SYNOPSIS
    Used as the initiator for TOMB execution against Hosts

    .DESCRIPTION
    TOMB (The One Mission Builder) is a host collection script that is setup for forwarding data
    into Splunk via a Splunk Universal Forwarder, as such artifacts collected are converted into JSON
    For this reason, output is hardcoded into the provided file structure for easy setup and execution.
    **For SplunkForwarder setup please read the provided documentation or use the provided Splunk_Setup.py for automated setup.**
    
    .NOTES
    DATE:       20 MAR 19
    VERSION:    1.1.1
    AUTHOR:     Brent Matlock -Lyx

    .PARAMETER Domain
    Determins if ran against domain objects, or localmachine
    Intent for localmachine is typically baseline of image.
    When provided syntax for Domain should be a string for the
    required orginizational unit to pull hosts from.

    .PARAMETER Server
    Required Parameter when running against domain.
    Used to specify the Domain Controller you will be collecting from.

    .PARAMETER Collects
    Used to specify the collections that are gathered from hosts.
    Parameter to be passed should be an array that is seperated by a comma(,).

    .PARAMETER Threads
    Used to limit the number of parallel jobs. Default value is set to 50.

    .EXAMPLE
    Collection of processes, services and signature on domain foo.bar
        TOMB -Collects Service,Process,Signatures -Domain "OU=foo,OU=bar" -Server 8.8.8.8 -Threads 25

    .EXAMPLE
    Collection for specific hosts without query of the domain.
        TOMB.py -Collects Service,Process -Computer localhost
'''

#Imports
import os
import csv
import sys
import wmi
import time
import datetime
import argparse
import subprocess

#Import modules for use with TOMB
from modules.TOMB_Service.TOMB_Service import startWMI as Service
from modules.TOMB_Process.TOMB_Process import startWMI as Process
from modules.TOMB_Registry.TOMB_Registry import startWMI as Registry
from modules.TOMB_EventLog.TOMB_EventLog import startWMI as EventLog
from modules.TOMB_Signature.TOMB_Signature import startWMI as Signature
from modules.TOMB_SchedTask.TOMB_SchedTask import startWMI as SchedTask

#TODO:
#from ldap3 import Server, Connection, SUBTREE


#Provides TOMB the ability to use commandline parameters via tabbing
def Main():
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
    
    if args.Setup:
        splunkSetup()
    else:
        Domain = (args.Domain)
        Server = (args.Server)
        Threads = (args.Threads)
        Computer = (args.Computer)
        Collects = str(args.Collects).split(',')
        LogID = str(args.LogID).split(',')
        Setup = "False"
        Path = os.getcwd()
        Begin(Domain, Server, Threads, Computer, Collects, LogID, Setup, Path, args)


def splunkSetup():
    print("This is where setup for Splunk will go!")


def Begin(Domain, Server, Threads, Computer, Collects, LogID, Setup, Path, args):
    if Setup:
        splunkSetup
    if Computer:
        print("Computer switch provided " + Computer)
        startCollects(Threads, Computer, Collects, LogID, Path, args)
    if Domain and Server:
        print("Pulling computer objects from Domain: " + str(Domain))
        startCollects(Threads, Computer, Collects, LogID, Path, args)
    else: 
        print("No correct options")


def startCollects(Threads, Computer, Collects, LogID, Path, args):
    ComputerList = []
    if 'RunAll' in Collects:
        Collects = ['Service','Process','Registry','Signature','SchedTask','EventLog']
    if Computer is None:
        hostfile = open('.\\host.txt','r')
        ComputerList = hostfile.readlines()[1:]
        hostfile.close()        
    elif Computer:
        ComputerList = (Computer).split(',')
    for Computer in ComputerList:
        if "Service" in Collects:
            print("Connecting to: " + Computer)
            Service(Computer, Path)
            #Delete the temporary Service File
            os.remove('.\\Files2Forward\\temp\\Service\\' + (Computer).replace('"','').replace('\n','') + '.json')
        if "Process" in Collects:
            print("Connecting to: " + Computer)
            Process(Computer, Path)
            #Delete the temporary Process File
            os.remove('.\\Files2Forward\\temp\\Process\\' + (Computer).replace('"','').replace('\n','') + '.json')
        if "Registry" in Collects:
            print("Connecting to: " + Computer)
            Registry(Computer, Path)
            #Delete the temporary Registry File
            os.remove('.\\Files2Forward\\temp\\Registry\\' + (Computer).replace('"','').replace('\n','') + '.json')
        if "Signature" in Collects:
            print("Connecting to: " + Computer)
            Signature(Computer, Path)
            #Delete the temporary Signature File
            os.remove('.\\Files2Forward\\temp\\Signature\\' + (Computer).replace('"','').replace('\n','') + '.json')
        if "SchedTask" in Collects:
            print("Connecting to: " + Computer)
            SchedTask(Computer, Path)
            #Delete the temporary SchedTask File
            os.remove('.\\Files2Forward\\temp\\SchedTask\\' + (Computer).replace('"','').replace('\n','') + '.json')
        if "EventLog" in Collects:
            print("Connecting to: " + Computer)
            EventLog(Computer, Path)
            #Delete the temporary EventLog File
            os.remove('.\\Files2Forward\\temp\\EventLog\\' + (Computer).replace('"','').replace('\n','') + '.json')


if __name__ == '__main__':
    Main()