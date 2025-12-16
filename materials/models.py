from django.db import models


class Course(models.Model):
    title = models.CharField(
        max_length=255, verbose_name="Полное название курса", help_text="Введите полное название курса"
    )
    description = models.TextField(
        blank=True, null=True, verbose_name="Краткое описание курса", help_text="Введите краткое описание курса"
    )
    preview = models.ImageField(upload_to="materials/previews/", blank=True, null=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"


class Lesson(models.Model):
    course = models.ForeignKey(
        Course, on_delete=models.SET_NULL, blank=True, null=True, related_name="lessons", verbose_name="Курс"
    )
    title = models.CharField(
        max_length=255, verbose_name="Полное название урока", help_text="Введите полное название урока"
    )
    description = (
        models.TextField(
            blank=True, null=True, verbose_name="Краткое описание урока", help_text="Введите краткое описание урока"
        ),
    )
    preview = (models.ImageField(upload_to="materials/previews/", blank=True, null=True),)
    video_url = models.URLField(verbose_name="Ссылка на видео урока")

    def __str__(self):
        return f"{self.course.title} - {self.title}"

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"
