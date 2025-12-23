from rest_framework.serializers import ModelSerializer, SerializerMethodField

from materials.models import Course, Lesson


class LessonSerializer(ModelSerializer):
    class Meta:
        model = Lesson
        fields = "__all__"


class CourseSerializer(ModelSerializer):
    lesson_count_in_course = SerializerMethodField()
    lessons_in_course = SerializerMethodField()

    def get_lesson_count_in_course(self, obj):
        return obj.lessons.count()

    def get_lessons_in_course(self, obj):
        lessons = Lesson.objects.filter(course=obj)
        serializer = LessonSerializer(lessons, many=True)
        return serializer.data

    class Meta:
        model = Course
        fields = ("title", "description", "preview", "lesson_count_in_course", "lessons_in_course")


class CourseDetailSerializer(ModelSerializer):
    lesson_count_in_course = SerializerMethodField()
    lessons_in_course = SerializerMethodField()

    def get_lesson_count_in_course(self, obj):
        return obj.lessons.count()

    def get_lessons_in_course(self, obj):
        lessons = Lesson.objects.filter(course=obj)
        serializer = LessonSerializer(lessons, many=True)
        return serializer.data

    class Meta:
        model = Course
        fields = ("title", "description", "preview", "lesson_count_in_course", "lessons_in_course")
