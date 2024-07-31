import chromadb

from django.contrib.sessions.models import Session
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.conf import settings

from selfchatgpt.models import VectorDocument
from backends.db.chromadb import ChromaDBConnectionManager
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.chat_message_histories import SQLChatMessageHistory

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


@receiver(post_delete, sender=Session)
def delete_memory(sender, instance, **kwargs):
    session_key = instance.session_key
    try:
        chat_message_history = SQLChatMessageHistory(
            session_id=session_key,
            connection_string=settings.CHAT_MESSAGE_HISTORY_DB_NAME,
        )
        chat_message_history.clear()
    except:  # TODO: Better exception handling
        pass


@receiver(post_delete, sender=VectorDocument)
def delete_vector_db_document(sender, instance, **kwargs):
    uuid = instance.uuid
    chromadb.delete([str(uuid)])
