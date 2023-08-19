import datetime
import json
import os

import requests
from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import AudioFileSerializer, BuySerializer
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import subprocess
from pymongo import MongoClient
import query_string
from pydub import AudioSegment
import platform


pay_url = 'https://api.zarinpal.com/pg/v4/payment/request.json'


class AudioFileView(APIView):
    def post(self, request):
        serializer = AudioFileSerializer(data=request.data)
        if serializer.is_valid():
            print(serializer.validated_data)
            audio_file = serializer.validated_data['audio_file']
            name = serializer.validated_data['name']
            tg_id = serializer.validated_data['tg_id']
            file_name = default_storage.save('audio/' + name, ContentFile(audio_file.read()))
            file_url = default_storage.url(file_name)

            # partitioning
            file_stats = os.stat(file_url[1:])
            arr = os.path.splitext(file_url)
            path = arr[0]
            ext = arr[1]
            print(path)
            AudioSegment.from_file(file_url[1:]).export(path[1:]+'.mp3', format="mp3")
            os.remove(file_url[1:])
            file_url = path + '.mp3'
            print(file_url)
            file_stats = os.stat(file_url[1:])
            arr = os.path.splitext(file_url)
            path = arr[0]
            ext = arr[1]
            f = open(file_url[1:], 'rb')
            print(file_stats.st_size)
            for i in range(int(file_stats.st_size / 100000) + 1):
                open(path[1:] + '_p' + str(i) + ext, 'wb').write(f.read(100000))
                if i != int(file_stats.st_size / 100000):
                    f.seek((i + 1) * 100000)
            f.close()
            os.remove(file_url[1:])
            for i in range(int(file_stats.st_size / 100000) + 1):
                f = open('output/freevc/' + name + '.mp3', 'ab')
                open('convert.txt', 'w').write(name + '_p' + str(i) + '|' + path[1:] + '_p' + str(i) + '.mp3' + '|' + '4.wav')
                try:
                    if platform.system() == 'Ubuntu':
                        subprocess.call(['sh', './inf.sh'])
                    if platform.system() == 'Windows':
                        subprocess.call([r'inf.bat'])
                except:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                AudioSegment.from_file('output/freevc/' + name + '_p' + str(i) + '.wav').export('output/freevc/' + name
                                                                            + '_p' + str(i) + '.mp3', format="mp3")
                os.remove('output/freevc/' + name + '_p' + str(i) + '.wav')
                t = open('output/freevc/' + name + '_p' + str(i) + '.mp3', 'rb')
                f.write(t.read())
                t.close()
                os.remove('output/freevc/' + name + '_p' + str(i) + '.mp3')
                os.remove(path[1:] + '_p' + str(i) + ext)
            AudioSegment.from_file('output/freevc/' + name + '.mp3').export('output/freevc/' + name
                                                                                            + '.wav', format="wav")

            return Response({'audio_file': '/output/freevc/' + name}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BuyView(APIView):
    def post(self, request, tg_id, amount):
        print(str(request))
        serializer = BuySerializer(data=request.data)
        print(request.data)
        if serializer.is_valid():
            res = requests.post(pay_url, json=request.data,
                                headers={'Content-Type': 'application/json', 'Accept': 'application/json'})
            print(res.text)
            return Response(res.text)

    def get(self, request, tg_id, amount):
        client = MongoClient('localhost', 27017)
        vc_db = client['vc_db']
        users = vc_db['user']
        user_account = vc_db['user_account']
        print(tg_id)
        if query_string.parse(str(request))['Status'] == "OK'>":
            user_account.insert_one({'tg_id': tg_id, 'coins': amount, 'cause': 'buy',
                                     'payment_link': 'https://www.zarinpal.com/pg/StartPay/' +
                                                     query_string.parse(str(request))['Authority'],
                                     'date': datetime.datetime.now()})
            return render(request, 'show_status.html', {'data': 1})
        else:
            return render(request, 'show_status.html', {'data': 0})
