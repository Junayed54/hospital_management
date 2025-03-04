from rest_framework import viewsets
from rest_framework.views import APIView
from .models import TestType, TestOrder, TestCollectionAssignment, TestResult
from .serializers import TestTypeSerializer, TestOrderSerializer, TestCollectionAssignmentSerializer, TestResultSerializer
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.utils.timezone import now
from rest_framework import generics

from django.contrib.auth import get_user_model
User = get_user_model() 
from accounts.permissions import *
# View for TestType model
class TestTypeViewSet(viewsets.ModelViewSet):
    queryset = TestType.objects.all()
    serializer_class = TestTypeSerializer
    # You can add additional filtering, permissions, etc. here if needed

class TestTypeCreateView(generics.CreateAPIView):
    queryset = TestType.objects.all()
    serializer_class = TestTypeSerializer
    permission_classes = [permissions.IsAuthenticated]
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
        try:
            # Fetch the TestOrder instance
            test_order = TestOrder.objects.get(id=id)
        except TestOrder.DoesNotExist:
            return Response({"type": "error", "error": "Test order not found"}, status=status.HTTP_404_NOT_FOUND)

        try:
            assignment = TestCollectionAssignment.objects.get(test_order=test_order)
        except TestCollectionAssignment.DoesNotExist:
            return Response({"type": "error", "error": "Assignment not found"}, status=status.HTTP_404_NOT_FOUND)

        # Check if a TestResult already exists
        test_result, created = TestResult.objects.get_or_create(test_order=test_order)

        # Validate new result data
        result_serializer = TestResultSerializer(test_result, data=request.data, partial=True)
        if result_serializer.is_valid():
            result_serializer.save()

            # Update the statuses
            test_order.status = 'result_delivered'
            assignment.status = "Completed"
            test_order.result_sent = result_serializer.validated_data.get('result_sent', test_order.result_sent)
            test_order.save()
            assignment.save()

            return Response(
                {
                    "type": "success",
                    "message": "Test result updated successfully" if not created else "Test result uploaded successfully",
                    "id": test_result.id,
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response({"type": "error", "errors": result_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
        
class TestResultDeleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # Ensure only authenticated users can delete test results

    def delete(self, request, *args, **kwargs):
        """
        Delete a test result by ID (provided in request body).
        """
        test_result_id = request.data.get("test_result_id")  # Get the ID from the request body

        if not test_result_id:
            return Response(
                {"error": "Test result ID is required in the request body."},
                status=status.HTTP_400_BAD_REQUEST
            )

        test_result = get_object_or_404(TestResult, id=test_result_id)

        # Ensure only the doctor who created the test result or an admin can delete it
        if not request.user.is_staff and request.user != test_result.test_order.doctor.user:
            return Response(
                {"error": "Permission denied. You can only delete your own test results."},
                status=status.HTTP_403_FORBIDDEN
            )

        test_result.delete()
        return Response(
            {"message": "Test result deleted successfully."},
            status=status.HTTP_204_NO_CONTENT
        )
