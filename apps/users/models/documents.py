from django.db import models

class Document(models.Model):
    id = models.BigAutoField(primary_key=True)
    content = models.TextField()
    embedding = models.JSONField()
    source = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Doc {self.id}"