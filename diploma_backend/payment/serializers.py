from rest_framework import serializers

from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    number = serializers.CharField(source="card_number")
    name = serializers.CharField(source="card_name")
    month = serializers.CharField(source="card_month")
    year = serializers.CharField(source="card_year")
    code = serializers.CharField(source="card_code")

    class Meta:
        model = Payment
        fields = ["number", "name", "month", "year", "code"]
