from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Classroom, ClassroomEnrollment, Assignment, AssignmentSubmission, Attendance
from .serializers import ClassroomSerializer, ClassroomEnrollmentSerializer, AssignmentSerializer, AssignmentSubmissionSerializer, AttendanceSerializer


class ClassroomListCreateView(generics.ListCreateAPIView):
    serializer_class = ClassroomSerializer

    def get_queryset(self):
        user_id = self.request.user.id
        # Teachers see their classrooms; students see enrolled ones
        enrolled_ids = ClassroomEnrollment.objects.filter(student_id=user_id).values_list('classroom_id', flat=True)
        return Classroom.objects.filter(teacher_id=user_id) | Classroom.objects.filter(id__in=enrolled_ids)

    def perform_create(self, serializer):
        serializer.save(teacher_id=self.request.user.id)


class ClassroomDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ClassroomSerializer
    queryset = Classroom.objects.all()


class AllAssignmentsView(generics.ListAPIView):
    """All assignments across classrooms the user is part of."""
    serializer_class = AssignmentSerializer

    def get_queryset(self):
        user_id = self.request.user.id
        classroom_ids = list(Classroom.objects.filter(teacher_id=user_id).values_list('id', flat=True))
        enrolled_ids  = list(ClassroomEnrollment.objects.filter(student_id=user_id).values_list('classroom_id', flat=True))
        return Assignment.objects.filter(classroom_id__in=set(classroom_ids + enrolled_ids))


class AllEnrollmentsView(generics.ListAPIView):
    """All enrollments for classrooms the user teaches."""
    serializer_class = ClassroomEnrollmentSerializer

    def get_queryset(self):
        classroom_ids = Classroom.objects.filter(teacher_id=self.request.user.id).values_list('id', flat=True)
        return ClassroomEnrollment.objects.filter(classroom_id__in=classroom_ids)


class EnrollView(APIView):
    def post(self, request, pk):
        enrollment, created = ClassroomEnrollment.objects.get_or_create(
            classroom_id=pk, student_id=request.user.id
        )
        return Response(ClassroomEnrollmentSerializer(enrollment).data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


class AssignmentListCreateView(generics.ListCreateAPIView):
    serializer_class = AssignmentSerializer

    def get_queryset(self):
        return Assignment.objects.filter(classroom_id=self.kwargs['pk'])

    def perform_create(self, serializer):
        serializer.save(classroom_id=self.kwargs['pk'])


class AssignmentSubmissionView(generics.ListCreateAPIView):
    serializer_class = AssignmentSubmissionSerializer

    def get_queryset(self):
        return AssignmentSubmission.objects.filter(assignment_id=self.kwargs['assignment_id'])

    def perform_create(self, serializer):
        serializer.save(student_id=self.request.user.id, assignment_id=self.kwargs['assignment_id'])


class AttendanceView(generics.ListCreateAPIView):
    serializer_class = AttendanceSerializer

    def get_queryset(self):
        return Attendance.objects.filter(classroom_id=self.kwargs['pk'])
