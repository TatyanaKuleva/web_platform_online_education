from rest_framework import serializers
from rest_framework.serializers import ModelSerializer, SerializerMethodField

from materials.models import Course, CourseSubscription, Lesson

from .validators import validate_no_external_links_except_youtube


class LessonSerializer(ModelSerializer):
    title = serializers.CharField(validators=[validate_no_external_links_except_youtube])
    description = serializers.CharField(
        allow_blank=True, allow_null=True, required=False, validators=[validate_no_external_links_except_youtube]
    )
    video_url = serializers.URLField(validators=[validate_no_external_links_except_youtube])

    class Meta:
        model = Lesson
        fields = "__all__"


class CourseSerializer(ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    lesson_count_in_course = SerializerMethodField()
    lessons_in_course = SerializerMethodField()

    title = serializers.CharField(validators=[validate_no_external_links_except_youtube])
    description = serializers.CharField(
        allow_blank=True, allow_null=True, required=False, validators=[validate_no_external_links_except_youtube]
    )

    def get_lesson_count_in_course(self, obj):
        return obj.lessons.count()

    def get_lessons_in_course(self, obj):
        lessons = Lesson.objects.filter(course=obj)
        serializer = LessonSerializer(lessons, many=True)
        return serializer.data

    def get_is_subscribed(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return CourseSubscription.objects.filter(user=request.user, course=obj).exists()
        return False

    class Meta:
        model = Course
        fields = (
            "title",
            "description",
            "preview",
            "lesson_count_in_course",
            "lessons_in_course",
            "owner",
            "is_subscribed",
        )


class CourseDetailSerializer(ModelSerializer):
    lesson_count_in_course = SerializerMethodField()
    lessons_in_course = SerializerMethodField()

    title = serializers.CharField(validators=[validate_no_external_links_except_youtube])
    description = serializers.CharField(
        allow_blank=True, allow_null=True, required=False, validators=[validate_no_external_links_except_youtube]
    )

    def get_lesson_count_in_course(self, obj):
        return obj.lessons.count()

    def get_lessons_in_course(self, obj):
        lessons = Lesson.objects.filter(course=obj)
        serializer = LessonSerializer(lessons, many=True)
        return serializer.data

    class Meta:
        model = Course
        fields = ("title", "description", "preview", "lesson_count_in_course", "lessons_in_course", "owner")
