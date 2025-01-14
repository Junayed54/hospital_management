from rest_framework import viewsets
from rest_framework.views import APIView
from .models import TestType, TestOrder, TestCollectionAssignment, TestResult
from .serializers import TestTypeSerializer, TestOrderSerializer, TestCollectionAssignmentSerializer, TestResultSerializer
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.utils.timezone import now
from django.contrib.auth import get_user_model
User = get_user_model() 
from accounts.permissions import *
# View for TestType model
class TestTypeViewSet(viewsets.ModelViewSet):
    queryset = TestType.objects.all()
    serializer_class = TestTypeSerializer
    # You can add additional filtering, permissions, etc. here if needed


# View for TestOrder model
class TestOrderViewSet(viewsets.ModelViewSet):
    
    queryset = TestOrder.objects.all()
    serializer_class = TestOrderSerializer
    permission_classes = [IsPatientUser]

    def get_queryset(self):
        """
        This will filter TestOrders by the logged-in user.
        """
        return TestOrder.objects.filter(user=self.request.user)
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Save the TestOrder instance
            test_order = serializer.save()

            # Automatically create TestCollectionAssignment when the test order is created
            if test_order.status == 'requested':  # Only create when the status is 'requested'
                # You can assign the staff manually or automatically based on some logic
                # For example, let's assume you assign the first available staff member:
                staff_member = User.objects.filter(role='staff').first()  # Example of assigning the first staff
                if staff_member:
                    TestCollectionAssignment.objects.create(
                        
                        test_order=test_order,
                        status='Assigned',
                        collection_date=now(),  # Set the collection date/time
                        # Optionally, you can also assign the staff member here
                        # collector=staff_member,  # Assuming you have a field for the collector
                    )

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            print(serializer.errors)
            return Response(serializer.errors, status=400)
        
    def update(self, request, *args, **kwargs):
        """
        Override the update method to handle nested TestType updates.
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)


# View for TestCollectionAssignment model
class TestCollectionAssignmentViewSet(viewsets.ModelViewSet):
    queryset = TestCollectionAssignment.objects.all()
    serializer_class = TestCollectionAssignmentSerializer
    # You can add filtering by status or hospital_team_member if needed


class TestAssignments(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        List all TestCollectionAssignments and the assignments specific to the logged-in user (staff).
        The assignments are filtered by their status and whether they are assigned to the logged-in user.
        """
        # Filter assignments by status for the logged-in user
        completed_assignments = TestCollectionAssignment.objects.filter(
            status='Completed', collector=request.user
        )

        assigned_assignments = TestCollectionAssignment.objects.filter(
            status='Assigned'
        )

        in_progress_assignments = TestCollectionAssignment.objects.filter(
            status='In Progress', collector=request.user
        )

        # Serialize filtered assignments
        completed_assignments_serializer = TestCollectionAssignmentSerializer(completed_assignments, many=True)
        assigned_assignments_serializer = TestCollectionAssignmentSerializer(assigned_assignments, many=True)
        in_progress_assignments_serializer = TestCollectionAssignmentSerializer(in_progress_assignments, many=True)

        return Response(
            {
                "completed_assignments": completed_assignments_serializer.data,
                "assigned_assignments": assigned_assignments_serializer.data,
                "in_progress_assignments": in_progress_assignments_serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class UpdateAssignmentCollectorAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, id):
        try:
            assignment = TestCollectionAssignment.objects.get(id=id)
            assignment.collector = request.user
            testOrder = assignment.test_order
            testOrder.status = "processing"
            assignment.status = "In Progress"
            testOrder.save()
            assignment.save()
            return Response({"message": "Assignment claimed successfully"}, status=status.HTTP_200_OK)
        except TestCollectionAssignment.DoesNotExist:
            return Response({"error": "Assignment not found"}, status=status.HTTP_404_NOT_FOUND)

# View for TestResult model
class TestResultViewSet(viewsets.ModelViewSet):
    queryset = TestResult.objects.all()
    serializer_class = TestResultSerializer
    # You can add filtering by test_order or result_sent if needed


class UpdateAssignmentStatusAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk, *args, **kwargs):
        """
        Update the status of the TestCollectionAssignment.
        """
        try:
            assignment = TestCollectionAssignment.objects.get(id=pk)
        except TestCollectionAssignment.DoesNotExist:
            return Response({"detail": "Assignment not found."}, status=status.HTTP_404_NOT_FOUND)

        # Ensure the logged-in user is allowed to update this assignment
        if assignment.user != request.user:
            return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
        
        # Update the status
        status = request.data.get("status", None)
        if status not in ['In Progress', 'Completed']:
            return Response({"detail": "Invalid status."}, status=status.HTTP_400_BAD_REQUEST)

        assignment.status = status
        assignment.save()
        
        # Serialize the updated assignment
        serializer = TestCollectionAssignmentSerializer(assignment)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    

class UploadTestResultView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, id):
        test_order = TestOrder.objects.get(id=id)
        
        try:
            # Fetch the TestOrder instance
            test_order = TestOrder.objects.get(id=id)
            assignment = TestCollectionAssignment.objects.get(test_order=test_order)
            
            if not assignment:
                return Response({"error": "Assingnment not found"}, status=status.HTTP_404_NOT_FOUND) 
            # Update the TestResult
            result_serializer = TestResultSerializer(data=request.data)
            if result_serializer.is_valid():
                result_instance, created = TestResult.objects.update_or_create(
                    test_order=test_order,
                    defaults={
                        "result": result_serializer.validated_data.get('result'),
                        "result_file": result_serializer.validated_data.get('result_file'),
                        "result_sent": result_serializer.validated_data.get('result_sent'),
                    },
                )

                # Update the TestOrder status
                test_order.status = 'result_delivered'
                assignment.status = "Completed"
                test_order.result_sent = result_serializer.validated_data.get('result_sent', False)
                test_order.save()
                assignment.save()

                return Response(
                    {"message": "Test result updated successfully", "id": result_instance.id},
                    status=status.HTTP_200_OK,
                )
            else:
                print(result_serializer.errors)
                return Response(result_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except TestOrder.DoesNotExist:
            return Response({"error": "Test order not found"}, status=status.HTTP_404_NOT_FOUND)