from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from langchain_community.chat_message_histories import SQLChatMessageHistory


class ChatMessageHistoryDBManager:

    __instance = None
    __ALLOWED_USER_TYPES = {
        "USER": "user_message_store",
        "SESSION": "message_store",
    }

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            cls.__instance.__init__()
        return cls.__instance

    def get_chat_message_history(self, user_type: str, key: str):
        if user_type.upper() not in self.__ALLOWED_USER_TYPES:
            raise ImproperlyConfigured(f"'{user_type}'은 지원하지 않습니다.")
        return SQLChatMessageHistory(
            session_id=key,
            connection_string=settings.CHAT_MESSAGE_HISTORY_DB_NAME,
            table_name=self.__ALLOWED_USER_TYPES[user_type.upper()],
        )
