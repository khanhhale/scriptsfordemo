# Copyright 2017, Google LLC All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse, os, logging, json, glob
import base64
import datetime
import time
import jwt
import requests, urllib
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
import uuid
import random, string
import collections
from flask import jsonify
from threading import Event, Thread
from googleapiclient import discovery
import dateutil.parser
import httplib2
from oauth2client.client import GoogleCredentials
from CloudApis import *
from CameraApi import *
from ServiceApi import *
from Utility import *
from google.protobuf.json_format import MessageToJson
from google.cloud import bigquery
import sys, subprocess
reload(sys)
sys.setdefaultencoding('utf8')
from google.cloud import monitoring
from random import *

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

serviceApiObj = ServiceApi() 
args = serviceApiObj.parse_command_line_args()
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]=args.credential  
 
utilityObj = Utility()   
cloudApisObj = CloudApis()
cameraApiObj = CameraApi()

client = monitoring.Client(project=args.project_id)

def publish_message():
   '''
    Description: 
       This function take an image and publish to the google cloud Pub/Sub.
    Args: 
       None
    Returns:
       None
    Raise:
       Throw an exception on failure
   ''' 

   try:      
      # list_time_series()
      write_time_series()
   except Exception, e:
      print e
   else:
      print('Successful sent data points.')

def list_time_series():
    # [START list_time_series]
    metric = 'compute.googleapis.com/instance/cpu/utilization'
    query_results = client.query(metric, minutes=5)
    for result in query_results:
        print(result)
    # [END list_time_series]

def write_time_series():
      resource = client.resource(
      type_='gce_instance',
      labels={
        'project_id': 'cloud-iot-testing-185623',
        'instance_id': '8272578876611649081',
        'zone': 'us-central1-f',
      })

      # Default arguments use endtime datetime.utcnow()
      metric = client.metric(type_='custom.googleapis.com/k_metric',labels={'point_x': 'x' })
      client.write_point(metric, resource, round(uniform(4, 6),2))
      metric = client.metric(type_='custom.googleapis.com/k_metric',labels={'point_y': 'y' })
      client.write_point(metric, resource, round(uniform(6, 8),2))
      metric = client.metric(type_='custom.googleapis.com/k_metric',labels={'point_z': 'z' })
      client.write_point(metric, resource, round(uniform(8, 10),2))

def setInterval(interval, callbackfunc):
   '''
     Description: 
       This function take an image and publish to the google cloud Pub/Sub.
     Args: 
       interval: interval in second between two publishing points
       callbackfunc: callback function
     Returns:
       None
     Raise:
       On Success: print "Image published" and publish image to Pub/Sub
       On failure: Throw an exception
   '''

   event_obj = Event()
   
   def loopFunc():
        while not event_obj.wait(interval):
            callbackfunc()
   Thread(target=loopFunc).start()    
   return event_obj.set

clearTime = setInterval(60, publish_message)
