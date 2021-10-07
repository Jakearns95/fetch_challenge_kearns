from django.db import models

#Model to handle all transactions
class transactions(models.Model):

    payer = models.CharField(max_length=100) #Dont want to make this unique so we can track time stamps
    points = models.IntegerField()
    timestamp = models.DateTimeField()