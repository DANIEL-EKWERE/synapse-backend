from rest_framework import serializers
from .models import Classroom, ClassroomEnrollment, Assignment, AssignmentSubmission, Attendance


class ClassroomEnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassroomEnrollment
        fields = '__all__'
        read_only_fields = ['id', 'student_id', 'enrolled_at']


class ClassroomSerializer(serializers.ModelSerializer):
    student_count = serializers.SerializerMethodField()

    class Meta:
        model = Classroom
        fields = '__all__'
        read_only_fields = ['id', 'teacher_id', 'created_at']

    def get_student_count(self, obj):
        return obj.enrollments.count()


class AssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class AssignmentSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignmentSubmission
        fields = '__all__'
        read_only_fields = ['id', 'student_id', 'submitted_at']


class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = '__all__'
        read_only_fields = ['id', 'created_at']
