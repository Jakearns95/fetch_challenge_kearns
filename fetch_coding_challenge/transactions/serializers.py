from rest_framework import serializers
from transactions.models import transactions


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = transactions
        fields = '__all__'

        """
        Need to figure out why my errors arent throwing
        """