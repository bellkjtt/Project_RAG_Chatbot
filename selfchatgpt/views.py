import json
import chromadb

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator, EmptyPage
from langchain_core.documents import Document

from .forms import UserForm, QnABoardPostForm, QnABoardPostReplyForm, ApplicationForm
from django.shortcuts import render, redirect, get_object_or_404

from utils import get_chat_message_history, check_if_similar_documents
from backends.db.chromadb import ChromaDBConnectionManager
from selfchatgpt.models import ChatHistory, QnaPost, VectorDocument
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain_community.chat_models import ChatOpenAI
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

# 프롬프트 작성
system_instruction = "KT 에이블스쿨을 위한 챗봇입니다."
template = (
    f"{system_instruction} "
    "Context와 Chat History도 고려하여 Question을 답해주세요.\n"
    "질문에 대한 답을 모르면, ktaivle@kt.com로 문의해달라고 안내해주세요.\n"
    "질문이 아닌 경우에는, 어떻게 도와드릴 수 있는지 물어봐주세요.\n"
    "----------------------\n"
    "Context: {context}\n\n"
    "Chat History: {chat_history}\n\n"
    "Question: {question}"
)
prompt = PromptTemplate(
    input_variables=["chat_history", "question", "context"], template=template
)


def index(request):
    chat_message_history = get_chat_message_history(request)
    messages = chat_message_history.messages
    return render(
        request,
        "selfchatgpt/index.html",
        {"messages": messages},
    )


def chatbot(request):
    if request.method == "POST":
        data = json.loads(request.body.decode("utf-8"))
        user_message = data.get("message")
        database = connection_manager.get_connection("aivle_faq", **db_config)
        chat_message_history = get_chat_message_history(request)
        llm = ChatOpenAI(model="gpt-3.5-turbo")
        retriever = database.as_retriever(search_kwargs={"k": 3})
        memory = ConversationBufferMemory(
            memory_key="chat_history",
            chat_memory=chat_message_history,
            input_key="question",
            output_key="answer",
            return_messages=True,
            k=10,
        )
        qa = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=retriever,
            memory=memory,
            return_source_documents=True,
            output_key="answer",
            combine_docs_chain_kwargs={"prompt": prompt},
        )
        result = qa({"question": user_message})
        bot_response = result["answer"]
        ChatHistory.objects.create(
            question=user_message,
            answer=bot_response,
        )
        return JsonResponse({"response": bot_response})
    chat_message_history = get_chat_message_history(request)
    messages = chat_message_history.messages
    return render(
        request,
        "selfchatgpt/aivle-bot.html",
        {"messages": messages},
    )


# 회원가입
def signup(request):
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()

            username = form.cleaned_data.get("username")
            raw_password = form.cleaned_data.get("password1")
            user = authenticate(username=username, password=raw_password)  # 사용자 인증
            # login(request, user)  # 로그인
            return redirect(settings.LOGIN_URL)

        else:
            print("에러", form.errors)
    else:
        form = UserForm()

    return render(
        request,
        "selfchatgpt/signup.html",
        {"form": form},
    )


# 로그인로그아웃 뷰
def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect(
                "selfchatgpt:index"
            )  # 네임스페이스를 포함하여 URL 패턴 참조
        else:
            return render(
                request, "selfchatgpt/login.html", {"error": "Invalid credentials"}
            )
    return render(request, "selfchatgpt/login.html")


def logout_view(request):
    logout(request)
    return redirect("selfchatgpt:index")


# QnA 관련 Views
def post_list(request):
    page = request.GET.get("p", 1)
    post_list = QnaPost.objects.all()
    paginator = Paginator(post_list, 5)
    try:
        posts = paginator.page(int(page))
        return render(
            request,
            "board/post-list.html",
            {"posts": posts},
        )
    except EmptyPage:
        return redirect("/")


@login_required
def post_create(request):
    if request.method == "POST":
        form = QnABoardPostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect("selfchatgpt:post_detail", post_id=post.id)
    else:
        form = QnABoardPostForm()
    return render(request, "board/post-create.html", {"form": form})


@login_required
def post_reply(request, post_id: int):
    if request.method == "POST":
        form = QnABoardPostReplyForm(request.POST)
        post = get_object_or_404(QnaPost, pk=post_id)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.author = request.user
            reply.post = post
            reply.save()
            if form.cleaned_data["add_to_db"]:
                content = form.cleaned_data["content"]
                qa = f"{post.title}\n{post.content}\n{content}"
                chromadb = connection_manager.get_connection("aivle_faq", **db_config)
                if not check_if_similar_documents(chromadb, qa):
                    ids = chromadb.add_documents([Document(page_content=qa)])
                    if isinstance(ids, list) and len(ids) == 1:
                        VectorDocument.objects.create(uuid=ids[0])
            return redirect("selfchatgpt:post_detail", post_id=post_id)
    form = QnABoardPostReplyForm()
    post = get_object_or_404(QnaPost, pk=post_id)
    return render(request, "board/post-reply.html", {"form": form, "post": post})


def post_detail(request, post_id: int):
    post = get_object_or_404(QnaPost, pk=post_id)
    reply = None
    if post.has_reply():
        reply = post.reply
    return render(
        request,
        "board/post-detail.html",
        {"post": post, "reply": reply},
    )


@login_required
def apply(request):
    user = request.user
    application = None
    if hasattr(user, "application"):
        application = user.application
    if request.method == "POST":
        form = ApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.author = request.user
            application.save()
    return render(
        request, "apply/apply.html", {"user": user, "application": application}
    )
