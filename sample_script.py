# coding: utf-8
import runpod
import os

runpod.api_key = os.environ['RUNPOD_KEY']
pods = runpod.get_pods()
for pod in pods:
    print(pod['name'])
