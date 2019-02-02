from flask import request, jsonify
from flask_restful import Resource, reqparse, abort
from datetime import datetime, timezone
import json
import uuid
import jsonpatch
from enum import Enum
from shutil import move
from os import fdopen, remove
import base64
import requests

FILNE = 'Accolade.txt'
FILTEMP = 'tmp.txt'
ENCODING = 'utf-8'

class Status(Enum):
    NEW = 1
    UPDATED = 2
    DELETED = 3

class Record(Resource):
    def get(self, recordId):
        
        with open(FILNE, 'r+') as f:
            lines = f.readlines()     
            for i in range(0, len(lines)):
               
                line = eval(lines[i])
                if (line['recordId'] == recordId):
                    return jsonify(line)
        return {'message': 'Record does not exist'}, 404

    def post(self):
        recordId = str(uuid.uuid1())
        recordData = str('null')
        if request.headers['Content-Type'] == 'application/octet-stream' and (len(request.data) > 0):
            encodedData = base64.b64encode(request.data)
            recordData = encodedData.decode(ENCODING)

        file = open(FILNE,'a') 
        record_fields = {
            'recordId': recordId,
            'info': {
                'recordStatus': Status(1).name,
                'created': datetime.now(timezone.utc).astimezone().isoformat(),
                'updated': [],
                'recordData': recordData
            }
        } 
        json.dump(record_fields,file)
        file.write('\n')
        file.close() 

        return {
            'message': 'New record created', 
            'recordId': recordId 
            },201

    def patch(self, recordId): 
        with open(FILNE, 'r+') as f:
            lines = f.readlines()       
            fout = open(FILTEMP, 'wt')
            for i in range(0, len(lines)):
                line = eval(lines[i])
                if (line['recordId'] == recordId):
                    if (line['info']['recordStatus'] != Status(3).name):
                        updatedList = line['info']['updated']
                        updatedList.append(datetime.now(timezone.utc).astimezone().isoformat())
                        patch = [
                            { 'op': 'replace', 'path': '/info/updated', 'value': updatedList},
                            { 'op': 'replace', 'path': '/info/recordStatus', 'value': Status(2).name}
                        ]
                        line = jsonpatch.apply_patch(line, patch)
                    else:
                        fout.close()
                        f.close()
                        remove(FILTEMP)
                        return {'message':'Record is already deleted'},400
                json.dump(line,fout)
                fout.write('\n')
            fout.close()
            f.close()
            remove(FILNE)
            move(FILTEMP, FILNE)
            
        return {'message': 'Record updated'},201

    def delete(self, recordId):
        with open(FILNE, 'r+') as f:
            lines = f.readlines()          
            fout = open(FILTEMP, 'wt')
            for i in range(0, len(lines)):
                line = eval(lines[i])
                if (line['recordId'] == recordId):
                    if (line['info']['recordStatus'] != Status(3).name):
                        line['info']['deleted'] = datetime.now(timezone.utc).astimezone().isoformat()
                        line['info']['recordStatus'] = Status(3).name
                    else:
                        return {'message': 'Record has already been deleted'},400
                json.dump(line,fout)
                fout.write('\n')
        fout.close()
        f.close()
        remove(FILNE)
        move(FILTEMP, FILNE)
        return {'message': 'RecordStatus is now set to DELETED'},200


        