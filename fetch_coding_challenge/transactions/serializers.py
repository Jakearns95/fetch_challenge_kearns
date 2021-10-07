from rest_framework import serializers
from transactions.models import transactions


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = transactions
        fields = '__all__'

        # def add(self, validated_data):
        #     """
        #     Create/add and return a new transaction instance, given the validated data.
        #     """

        #     """ 
        #     Need to check that we have al
        #     """
        #     print("checking data", validated_data)
        #     if validated_data.points > 0:
        #         return transactions.objects.create(**validated_data)

        # def update(self, instance, validated_data):
        #     """
        #     Update and return an existing transaction instance, given the validated data.
        #     """
        #     instance.payer = validated_data.get('payer', instance.payer)
        #     instance.points = validated_data.get('points', instance.points)
        #     instance.timestamp = validated_data.get('timestamp', instance.timestamp)
        #     instance.save()
        #     return instance


        """
        Need to figure out why my errors arent throwing
        """