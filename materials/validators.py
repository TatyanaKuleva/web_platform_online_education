import re

from rest_framework.exceptions import ValidationError


def validate_no_external_links_except_youtube(text):
    """
    Проверяет, что в тексте нет ссылок кроме youtube.com и youtu.be.
    Если найдены другие ссылки — выдает ValidationError.
    """
    urls = re.findall(r"https?://[^\s]+", text)

    youtube_pattern = re.compile(r"^https?://(www\.)?(youtube\.com|youtu\.be)/")

    for url in urls:
        if not youtube_pattern.match(url):
            raise ValidationError(
                "В тексте нельзя использовать ссылки на сторонние ресурсы, кроме youtube.com и youtu.be."
            )
