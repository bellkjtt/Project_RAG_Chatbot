import csv
import chromadb

from django.conf import settings
from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib.messages import ERROR

from io import TextIOWrapper
from selfchatgpt.forms import CSVUploadForm
from selfchatgpt.models import ChatHistory, VectorDocument
from backends.db.chromadb import ChromaDBConnectionManager
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.schema import Document


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


@admin.register(ChatHistory)
class ChatHistoryAdmin(admin.ModelAdmin):
    list_display = ["id", "created_at", "question", "answer"]
    readonly_fields = ("created_at", "question", "answer", "relevant_documents")
    search_fields = ["created_at"]
    list_filter = ["created_at"]


@admin.register(VectorDocument)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ["id", "uuid", "content", "metadata"]
    search_fields = ["uuid"]

    change_list_template = "admin/document_changelist.html"

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super(DocumentAdmin, self).get_search_results(
            request, queryset, search_term
        )
        try:
            query_results = chromadb.get(where_document={"$contains": search_term})
            ids = query_results["ids"]
            queryset |= VectorDocument.objects.filter(uuid__in=ids)
        except:
            pass
        return queryset, use_distinct

    def __validate_column_names(self, request, row, target_col_name):
        if target_col_name not in row:
            self.message_user(
                request=request,
                message=f"'{target_col_name}' 칼럼을 찾을 수 없습니다.",
                level=ERROR,
                fail_silently=True,
            )
            return False
        return True

    def __get_document(self, row, target_col_loc, threshold=0.1):
        document = row[target_col_loc]
        similar_documents = chromadb.similarity_search_with_score(document)
        for _, score in similar_documents:
            if score < threshold:
                return None
        return document

    def get_urls(self):
        urls = super().get_urls()
        info = self.opts.app_label, self.opts.model_name
        custom_urls = [
            path(
                "upload-csv/",
                self.admin_site.admin_view(self.upload_csv),
                name="upload_csv",
            ),
            path(
                "add/",
                self.admin_site.admin_view(self.upload_csv),
                name="%s_%s_add" % info,
            ),
        ]
        return custom_urls + urls

    def upload_csv(self, request):
        if request.method == "POST":
            form = CSVUploadForm(request.POST, request.FILES)
            count = 0
            duplicate_count = 0
            if form.is_valid():
                csv_file = TextIOWrapper(
                    request.FILES["csv_file"].file, encoding="utf-8"
                )
                reader = csv.reader(csv_file)
                qa_loc = None
                for idx, row in enumerate(reader):
                    if idx == 0:
                        if not self.__validate_column_names(request, row, "QA"):
                            return redirect(".")
                        qa_loc = row.index("QA")
                    else:
                        document = self.__get_document(row, qa_loc)
                        if document is not None:
                            ids = chromadb.add_documents(
                                [Document(page_content=document)]
                            )
                            if isinstance(ids, list) and len(ids) == 1:
                                VectorDocument.objects.create(uuid=ids[0])
                                count += 1
                        else:
                            duplicate_count += 1
                self.message_user(
                    request,
                    f"성공적으로 {count}개의 데이터가 추가됐습니다. 총 {duplicate_count}개의 중복된 데이터를 감지했습니다.",
                )
                return redirect("..")
        else:
            form = CSVUploadForm()

        context = {"form": form, "title": "데이터 추가 (CSV 업로드)"}
        return render(request, "admin/csv_upload.html", context)
