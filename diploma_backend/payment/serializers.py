from rest_framework import serializers

from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    """
    Serializer for processing payment transactions.
    Maps frontend-friendly field names (number, name, etc.) to the Payment model.
    All sensitive fields are marked as write-only for security reasons.
    """
    number = serializers.CharField(source="card_number", write_only=True)
    name = serializers.CharField(source="card_name", write_only=True)
    month = serializers.CharField(source="card_month", write_only=True)
    year = serializers.CharField(source="card_year", write_only=True)
    code = serializers.CharField(source="card_code", write_only=True)

    class Meta:
        model = Payment
        fields = ["number", "name", "month", "year", "code"]

    def validate_number(self, value):
        """Ensures the card number contains only digits and has a valid length."""
        if not value.isdigit():
            raise serializers.ValidationError("Card number must contain only digits.")
        return value
