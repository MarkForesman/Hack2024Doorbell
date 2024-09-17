from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeResult
from azure.ai.documentintelligence import DocumentIntelligenceClient
import os

def di_ocr(document_intelligence_client: DocumentIntelligenceClient, image: str):
    with open(image, "rb") as f:
        poller = document_intelligence_client.begin_analyze_document(
            "prebuilt-layout", analyze_request=f, content_type="application/octet-stream"
        )
    result: AnalyzeResult = poller.result()

    if result.styles and any([style.is_handwritten for style in result.styles]):
        print("Document contains handwritten content")
    else:
        print("Document does not contain handwritten content")

    for page in result.pages:
        print(f"----Analyzing layout from page #{page.page_number}----")
        print(f"Page has width: {page.width} and height: {page.height}, measured with unit: {page.unit}")

    ocr_result = ""
    if result.paragraphs:
        for paragraph in result.paragraphs:
            ocr_result += paragraph.content
        print(ocr_result)

    return ocr_result