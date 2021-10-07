from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from rest_framework.parsers import JSONParser
from django.views.decorators.http import require_POST,require_GET
from django.views.decorators.csrf import csrf_exempt
import datetime
import pandas as pd

from transactions.models import transactions
from transactions.serializers import TransactionSerializer



# This endpoint will query to view all rewards
@csrf_exempt
@require_GET
def view_all(request):
    if request.method == 'GET':
        view_transactions = transactions.objects.all()
        serializer = TransactionSerializer(view_transactions, many=True)
        return JsonResponse(pd.DataFrame(serializer.data).groupby(['payer']).sum()['points'].to_json(), safe=False)

#this endpoint will add a transaction to the DB    
@csrf_exempt
@require_POST
def add(request):
    if request.method == 'POST':
        data = JSONParser().parse(request)
        try:
            # convert timestamps from string to datetime object
            data['timestamp'] = datetime.datetime.strptime(data['timestamp'], "%Y-%m-%dT%H:%M:%SZ")
        except:
            return JsonResponse("Failed to parse timestamp", safe=False)

        # check that the value is positive
        try:
            if int(data['points']) < 0:
                return HttpResponse("Please only send positive values")

        except:
            return JsonResponse("Failed to parse timestamp", status = 400)
        
        #verify inputs and then save
        serializer = TransactionSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status = 201)
        return JsonResponse(serializer.error, status = 400)

#this endpoint will use points (starting with the oldest points first)
@csrf_exempt
@require_POST
def use(request):
    if request.method == 'POST':
        #parse request
        data = JSONParser().parse(request)

        #get all points
        view_transactions = transactions.objects.all().order_by('timestamp')

        #check if right format
        serializer = TransactionSerializer(view_transactions, many=True)
        print(serializer.data)

        #capture number of points
        try:
            points = int(data['points'])
        except:
            return JsonResponse("Failed to parse points, please check your input", status = 400)
        
        record_change = []
        #print total points available
        total_available = 0
        for line in serializer.data:
            total_available +=line['points']

        if total_available < points:
            return HttpResponse('You do not have enough points to redeem. You have a total of {}'.format(total_available))
 
        for line in serializer.data:
            if points == 0:
                break
            else:
                if points >= int(line['points']) & int(line['points'])>0:
                    points -= line['points']
                    record_change.append({'payer': line['payer'], 'points': -int(line['points'])})
                    
                    try:
                        transaction = transactions.objects.get(id=line['id'])
                        transaction.points = 0
                        transaction.save()
                    except transactions.DoesNotExist:
                        return HttpResponse(status=404)

                elif int(line['points']) > points:
                    record_change.append({'payer': line['payer'], 'points': -points})
                    try:
                        transaction = transactions.objects.get(id=line['id'])
                        transaction.points -= points
                        transaction.save()
                    except transactions.DoesNotExist:
                        return HttpResponse(status=404)
                    points = 0
        parsed_changeds = pd.DataFrame(record_change).groupby(['payer']).sum().reset_index().set_index('payer').T.to_json(orient="records")

        return JsonResponse(parsed_changeds, safe=False)

@csrf_exempt
def delete(request):
    view_transactions = transactions.objects.all()
    view_transactions.delete()

    return HttpResponse('All transactions deleted')