import uuid
import chromadb

from django.conf import settings
from django.db import models
from django.contrib.auth.models import User

from typing import Dict, Any
from backends.db.chromadb import ChromaDBConnectionManager
from langchain_community.embeddings import OpenAIEmbeddings

connection_manager = ChromaDBConnectionManager()
db_config = {
    "embedding_function": OpenAIEmbeddings(model="text-embedding-ada-002"),
    "client_settings": chromadb.config.Settings(
        anonymized_telemetry=False,
        is_persistent=True,
        persist_directory=settings.CHROMADB_PATH,
    ),
}
chromadb = connection_manager.get_connection("aivle_faq", **db_config)


class VectorDocument(models.Model):

    __query_cache = None

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def __load_from_chromadb(self) -> Dict[str, Any]:
        if self.__query_cache is None:
            self.__query_cache = chromadb.get(ids=[str(self.uuid)])
        return self.__query_cache

    @property
    def content(self):
        documents = self.__load_from_chromadb()["documents"]
        if isinstance(documents, list) and len(documents) == 1:
            return documents[0]

    @property
    def metadata(self):
        metadatas = self.__load_from_chromadb()["metadatas"]
        if isinstance(metadatas, list) and len(metadatas) == 1:
            return metadatas[0]


class ChatHistory(models.Model):
    class Meta:
        db_table = "chat_history"
        verbose_name_plural = "chat histories"

    created_at = models.DateTimeField(auto_now_add=True)
    question = models.TextField()
    answer = models.TextField()
    relevant_documents = models.ManyToManyField(VectorDocument)


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20)
    address = models.CharField(max_length=50)


class QnaPost(models.Model):

    title = models.CharField(max_length=100)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def has_reply(self):
        return hasattr(self, "reply")


class QnAReply(models.Model):
    post = models.OneToOneField(
        QnaPost, on_delete=models.CASCADE, related_name="reply", null=True, blank=True
    )
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="replies")
    created_at = models.DateTimeField(auto_now_add=True)


class Application(models.Model):

    DX = "DX"
    AI = "AI"

    TRACK_CHOICES = [(DX, "DX"), (AI, "AI")]

    name = models.CharField(max_length=10)
    essay = models.TextField()
    dob = models.DateField()
    track = models.CharField(
        max_length=2,
        choices=TRACK_CHOICES,
        default=AI,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="application",
        null=True,
        blank=True,
    )
