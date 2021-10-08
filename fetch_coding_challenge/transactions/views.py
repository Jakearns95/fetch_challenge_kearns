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

        # group up all the payers and sum the total number of points for each
        return JsonResponse(pd.DataFrame(serializer.data).groupby(['payer']).sum()['points'].to_json(), safe=False)

#this endpoint will add a transaction to the DB - allows one transaction at a time 
@csrf_exempt
@require_POST
def add(request):
    if request.method == 'POST':
        data = JSONParser().parse(request)

        # convert timestamps from string to datetime object
        try:
            data['timestamp'] = datetime.datetime.strptime(data['timestamp'], "%Y-%m-%dT%H:%M:%SZ")
        except:
            return JsonResponse("Failed to parse timestamp", safe=False)

        # check that the value is positive
        try:
            if int(data['points']) < 0:
                if adjust(data):
                    return JsonResponse(data, status = 201)
                else:
                    return HttpResponse('Failed to adjust transaction')

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

        #capture number of points
        try:
            points = int(data['points'])
        except:
            return JsonResponse("Failed to parse points, please check your input", status = 400)
        
        #create df to capture changes
        record_change = []

        #get total number of points available
        total_available = 0
        for line in serializer.data:
            total_available +=line['points']

        #check if points redeemed > the total number of points available and throw error if so
        if total_available < points:
            return HttpResponse('You do not have enough points to redeem. You have a total of {}'.format(total_available))
 
        #loop through all the transactions to redeem points unless all the points get redeemed
        for line in serializer.data:
            if points == 0:
                break
            else:

                # split up to remove all points from a transaction if the total 
                # number of points to be redeemed exceed the transaction
                if points >= int(line['points']) & int(line['points'])>0:
                    
                    # subtract the points
                    points -= line['points']

                    # track the change
                    record_change.append({'payer': line['payer'], 'points': -int(line['points'])})
                    
                    # update the dataframe with the new transaction value
                    try:
                        transaction = transactions.objects.get(id=line['id'])
                        transaction.points = 0
                        transaction.save()
                    except transactions.DoesNotExist:
                        return HttpResponse(status=404)

                # if the transaction exceeds the number of points to be redeemed, 
                # calcuate the difference and set the transaction to the remainder
                elif int(line['points']) > points:
                    
                    #record the change
                    record_change.append({'payer': line['payer'], 'points': -points})
                    
                    #update the file
                    try:
                        transaction = transactions.objects.get(id=line['id'])
                        transaction.points -= points
                        transaction.save()
                    except transactions.DoesNotExist:
                        return HttpResponse(status=404)
                    
                    #set points to zero so we can exit
                    points = 0

        # parse the recorded changeds, group by the payer name, 
        # sum totals and return the total number for each payer
        parsed_changeds = pd.DataFrame(record_change).groupby(['payer']).sum().reset_index().set_index('payer').T.to_json(orient="records")

        return JsonResponse(parsed_changeds, safe=False)

# if the point value < 0, adjust the oldest transaction for the payer
def adjust(data):
    try:
        # get transactions by payer
        transaction = transactions.objects.filter(payer=data['payer']).order_by('timestamp')[0]
        transaction.points = transaction.points + int(data['points'])
        transaction.save()
        return True
    except:
        return False

# reset/delete all records
@csrf_exempt
def delete(request):
    view_transactions = transactions.objects.all()
    view_transactions.delete()

    return HttpResponse('All transactions deleted')