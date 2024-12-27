from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import PaymentMethod, Payment, Transaction
from .serializers import PaymentMethodSerializer, PaymentSerializer, TransactionSerializer


# PaymentMethod Views
class PaymentMethodListCreateView(APIView):
    """
    View to list and create PaymentMethods.
    """
    def get(self, request):
        methods = PaymentMethod.objects.filter(is_active=True)
        serializer = PaymentMethodSerializer(methods, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = PaymentMethodSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print(serializer.errors)  # Debugging
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class PaymentMethodDetailView(APIView):
    """
    View to retrieve, update, and delete a specific PaymentMethod.
    """
    def get(self, request, pk):
        method = get_object_or_404(PaymentMethod, pk=pk)
        serializer = PaymentMethodSerializer(method)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        method = get_object_or_404(PaymentMethod, pk=pk)
        serializer = PaymentMethodSerializer(method, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        method = get_object_or_404(PaymentMethod, pk=pk)
        method.is_active = False  # Soft delete
        method.save()
        return Response({"message": "Payment method deactivated"}, status=status.HTTP_204_NO_CONTENT)


# Payment Views
class PaymentListCreateView(APIView):
    """
    View to list and create Payments.
    """
    def get(self, request):
        payments = Payment.objects.filter(user=request.user)
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = PaymentSerializer(data=request.data, context={'user': request.user})
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PaymentDetailView(APIView):
    """
    View to retrieve, update, and delete a specific Payment.
    """
    def get(self, request, pk):
        payment = get_object_or_404(Payment, pk=pk, user=request.user)
        serializer = PaymentSerializer(payment)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        payment = get_object_or_404(Payment, pk=pk, user=request.user)
        serializer = PaymentSerializer(payment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        payment = get_object_or_404(Payment, pk=pk, user=request.user)
        payment.delete()
        return Response({"message": "Payment deleted"}, status=status.HTTP_204_NO_CONTENT)


# Transaction Views
class TransactionDetailView(APIView):
    """
    View to retrieve details of a specific Transaction.
    """
    def get(self, request, pk):
        transaction = get_object_or_404(Transaction, payment__user=request.user, pk=pk)
        serializer = TransactionSerializer(transaction)
        return Response(serializer.data, status=status.HTTP_200_OK)


# Additional View for User Payments Summary
class UserPaymentSummaryView(APIView):
    """
    View to provide a summary of user payments.
    """
    def get(self, request):
        payments = Payment.objects.filter(user=request.user)
        total_payments = payments.count()
        total_amount = payments.aggregate(total=models.Sum('amount'))['total'] or 0.00
        data = {
            "total_payments": total_payments,
            "total_amount": total_amount,
            "recent_payments": PaymentSerializer(payments[:5], many=True).data,  # Last 5 payments
        }
        return Response(data, status=status.HTTP_200_OK)
