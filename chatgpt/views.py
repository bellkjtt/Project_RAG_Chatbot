from django.shortcuts import render

from langchain_community.chat_models import ChatOpenAI
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from backends.db.chromadb import ChromaDBConnectionManager


# Chroma 데이터베이스 초기화 - 사전에 database가 완성 되어 있다는 가정하에 진행 - aivleschool_qa.csv 내용이 저장된 상태임
connection_manager = ChromaDBConnectionManager()
db_config = {
    "persist_directory": "./database",
    "embedding_function": OpenAIEmbeddings(model = "text-embedding-ada-002"),
}

def index(request):
    return render(request, 'gpt/index.html')

def chat(request):
    # post로 받은 question (index.html에서 name속성이 question인 input태그의 value값)을 가져옴
    query = request.POST.get('question')

    database = connection_manager.get_connection("aivle_faq", **db_config)
    #chatgpt API 및 lang chain을 사용을 위한 선언
    llm = ChatOpenAI(model="gpt-3.5-turbo")
    k = 3
    retriever = database.as_retriever(search_kwargs={"k": k})
    qa = RetrievalQA.from_llm(llm=llm,  retriever=retriever,  return_source_documents=True)

    result = qa(query)

    # result.html에서 사용할 context
    context = {
        'question': query,
        'result': result["result"]
    }

    # 응답을 보여주기 위한 html 선택 (위에서 처리한 context를 함께 전달)
    return render(request, 'gpt/result.html', context)



