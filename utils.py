from django.core.handlers.wsgi import WSGIRequest

from backends.db.chat_message_history import ChatMessageHistoryDBManager


def get_session_key(request):
    session_key = request.session.session_key
    if not session_key:
        request.session.create()
        session_key = request.session.session_key
    return session_key


def get_chat_message_history(request: WSGIRequest):
    """
    유저가 로그인 되어 있는 상태면, user_message_store 테이블에서 'key' 유저 대화 내역을 불러옵니다.
    아니라면 session_message_store 테이블에서 'key'와 같은 session_id의 대화 내역을 불러옵니다.
    """
    chat_history_manager = ChatMessageHistoryDBManager()
    # 로그인 상태
    if request.user.is_authenticated:
        user_id = request.user.id
        return chat_history_manager.get_chat_message_history("user", user_id)
    # 세션 키 생성 및 추출
    session_key = get_session_key(request)
    return chat_history_manager.get_chat_message_history("session", session_key)


def check_if_similar_documents(db_client, document, threshold=0.1):
    similar_documents = db_client.similarity_search_with_score(document)
    for _, score in similar_documents:
        if score < threshold:
            return True
    return False
