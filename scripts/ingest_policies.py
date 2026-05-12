# import os
# import re
# from uuid import uuid4

# from langchain_core.documents import Document
# from langchain_ollama import OllamaEmbeddings
# from langchain_chroma import Chroma

# from unstructured.partition.pdf import partition_pdf

# # -----------------------------
# # CONFIG
# # -----------------------------
# PERSIST_DIR = os.path.abspath("./data/chroma_policy_db")

# embedding = OllamaEmbeddings(model="mxbai-embed-large")

# vector_store = Chroma(
#     persist_directory=PERSIST_DIR,
#     embedding_function=embedding
# )

# # -----------------------------
# # TABLE NORMALIZATION
# # -----------------------------
# def normalize_table(table_element):

#     text = table_element.text

#     lines = text.split("\n")
#     structured_lines = []

#     for line in lines:
#         line = line.strip()

#         if not line:
#             continue

#         # detect rows with numbers / ranges
#         if re.search(r"\d", line):

#             # normalize spacing
#             line = re.sub(r"\s+", " ", line)

#             structured_lines.append(line)

#     if not structured_lines:
#         return text

#     return "Structured Financial Data:\n" + "\n".join(structured_lines)

#     return structured_text.strip()


# # -----------------------------
# # TEXT CLEANING
# # -----------------------------
# def clean_text(text):
#     return " ".join(text.split())


# # -----------------------------
# # MAIN INGEST FUNCTION
# # -----------------------------
# def ingest_pdf(file_path: str, bank: str):

#     print(f"\n📄 Processing: {file_path}")

#     elements = partition_pdf(
#         filename=file_path,
#         strategy="hi_res",           
#         infer_table_structure=True,  
#         model_name="yolox"          
#     )

#     docs = []

#     for e in elements:

#         # -----------------------------
#         # TABLES
#         # -----------------------------
#         if e.category == "Table":

#             content = normalize_table(e)

#             docs.append(
#                 Document(
#                     page_content=content,
#                     metadata={
#                         "id": str(uuid4()),
#                         "bank": bank,
#                         "type": "table",
#                         "source": file_path
#                     }
#                 )
#             )

#         # -----------------------------
#         # NORMAL TEXT
#         # -----------------------------
#         else:

#             text = clean_text(e.text)

#             if len(text) < 50:
#                 continue

#             docs.append(
#                 Document(
#                     page_content=text,
#                     metadata={
#                         "id": str(uuid4()),
#                         "bank": bank,
#                         "type": "text",
#                         "source": file_path
#                     }
#                 )
#             )

#     print(f"✅ Created {len(docs)} documents")

#     vector_store.add_documents(docs)

#     print(f"Inserted docs count: {len(docs)}")
#     all_docs = vector_store.get()
#     print(f"Total docs in DB: {len(all_docs['documents'])}")

#     for d in docs[:3]:
#         print(d.metadata)

#     print("✅ Stored in vector DB")


# # -----------------------------
# # RUN INGESTION
# # -----------------------------
# if __name__ == "__main__":
    
#     ingest_pdf("docs/SBI-Terms-and-Conditions.pdf", bank="SBI")

#     # add more:
#     # ingest_pdf("docs/hdfc_home_loan.pdf", bank="HDFC")










import os
import re
from uuid import uuid4
from bs4 import BeautifulSoup

from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

from unstructured.partition.pdf import partition_pdf
from unstructured.chunking.title import chunk_by_title

# -----------------------------
# CONFIG
# -----------------------------
PERSIST_DIR = os.path.abspath("./data/chroma_policy_db")

embedding = OllamaEmbeddings(model="mxbai-embed-large")

vector_store = Chroma(
    persist_directory=PERSIST_DIR,
    embedding_function=embedding
)


# -----------------------------
# SECTION TITLE EXTRACTOR
# -----------------------------
def get_section_title(chunk) -> str:
    """
    Extract parent section heading from unstructured chunk metadata.
    This is used to prefix chunk content so that similarly worded chunks
    (e.g. two penalty clauses with identical Rs 5000 structures) become
    semantically distinguishable during embedding + retrieval.

    Example output:
      "Penal Charges"
      "Non-renewal of insurance policy of property"
      "Fees and charges"
    """
    try:
        section = getattr(chunk.metadata, "section", None)
        if section and isinstance(section, str) and section.strip():
            return section.strip()
    except AttributeError:
        pass

    # Fallback for some unstructured versions
    try:
        parent = getattr(chunk.metadata, "parent_id", None)
        if parent:
            return str(parent).strip()
    except AttributeError:
        pass

    return ""


# -----------------------------
# TABLE HTML NORMALIZER
# -----------------------------
def normalize_table_html(table_element) -> str | None:
    """
    Convert HTML table (from unstructured) to clean pipe-separated rows.
    This gives embeddings clean financial text instead of HTML tag noise.

    Input (HTML):
      <table><tr><td>Up-to Rs. 30 lacs</td><td>90%</td></tr></table>

    Output (readable):
      Up-to Rs. 30 lacs | 90%
    """
    try:
        html = table_element.metadata.text_as_html
        if html:
            soup = BeautifulSoup(html, "html.parser")
            rows = []
            for tr in soup.find_all("tr"):
                cells = [td.get_text(strip=True) for td in tr.find_all(["td", "th"])]
                cells = [c for c in cells if c]
                if cells:
                    rows.append(" | ".join(cells))
            if rows:
                return "\n".join(rows)
    except Exception:
        pass
    return None


# -----------------------------
# TABULAR TEXT DETECTOR
# -----------------------------
def is_tabular_text(text: str) -> bool:
    """
    Heuristic to detect table-like content in text chunks that
    unstructured didn't classify as Table category.

    Catches:
    - LTV ratio slabs (percent + slab keyword)
    - Fee schedules (multiple rupee amounts)
    - Penalty tables (percentages)
    - Pipe-delimited rows

    Returns True if the chunk looks like structured financial data.
    """
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    if len(lines) < 2:
        return False

    percent_lines = sum(1 for l in lines if re.search(r'\d+(\.\d+)?%', l))
    rupee_lines   = sum(1 for l in lines if re.search(r'Rs\.?\s*[\d,]+', l))
    pipe_lines    = sum(1 for l in lines if '|' in l)
    slab_lines    = sum(1 for l in lines if re.search(
                        r'(upto|above|up to|below|between|lacs|lakhs)',
                        l, re.IGNORECASE))

    return (
        percent_lines >= 2
        or rupee_lines >= 3
        or pipe_lines >= 2
        or (percent_lines >= 1 and slab_lines >= 1)
    )


# -----------------------------
# TEXT CLEANING
# -----------------------------
def clean_text(text: str) -> str:
    return " ".join(text.split())


# -----------------------------
# MAIN INGEST FUNCTION
# -----------------------------
def ingest_pdf(file_path: str, bank: str):

    print(f"\n📄 Processing: {file_path}")

    # ✅ fast strategy — correct for digitally generated PDFs
    # hi_res caused OCR garbling on this clean digital PDF
    elements = partition_pdf(
        filename=file_path,
        strategy="fast",
        include_page_breaks=False,
    )

    print(f"🔍 Raw elements extracted: {len(elements)}")

    # ✅ chunk_by_title for section-aware chunking
    # - Respects section boundaries (headings/titles)
    # - Combines tiny bullet-point elements under same heading
    # - overlap=50 preserves context at chunk boundaries
    chunks = chunk_by_title(
        elements,
        max_characters=600,
        new_after_n_chars=400,
        combine_text_under_n_chars=150,
        overlap=50,
    )

    print(f"📦 Chunks after chunking: {len(chunks)}")

    docs = []

    for chunk in chunks:

        category = getattr(chunk, "category", "NarrativeText")
        raw_text  = chunk.text.strip()

        if not raw_text:
            continue

        # ✅ Extract section title for this chunk
        # Used to prefix content and stored in metadata
        section = get_section_title(chunk)

        # -----------------------------------------------
        # TABLE HANDLING
        # Detect via category OR content heuristic
        # -----------------------------------------------
        if category == "Table" or is_tabular_text(raw_text):

            if category == "Table":
                table_text = normalize_table_html(chunk)
                if not table_text:
                    lines = [l.strip() for l in raw_text.split("\n") if l.strip()]
                    table_text = "\n".join(lines)
            else:
                lines = [l.strip() for l in raw_text.split("\n") if l.strip()]
                table_text = "\n".join(lines)

            if not table_text or len(table_text) < 30:
                continue

            # ✅ FIX: Prepend section title to table content
            # This makes similar penalty clauses distinguishable:
            #   "Section: Non-renewal of insurance policy\nFinancial Table:\n..."
            #   "Section: Penal Charges\nFinancial Table:\n..."
            # Without this, both chunks embed nearly identically
            if section:
                content = f"Section: {section}\nFinancial Table:\n{table_text}"
            else:
                content = f"Financial Table:\n{table_text}"

            docs.append(Document(
                page_content=content,
                metadata={
                    "id": str(uuid4()),
                    "bank": bank,
                    "type": "table",
                    "section": section,      # ✅ stored for filtering/debugging
                    "source": file_path
                }
            ))

        # -----------------------------------------------
        # TEXT HANDLING
        # -----------------------------------------------
        else:
            text = clean_text(raw_text)

            if len(text) < 80:
                continue

            # ✅ FIX: Prepend section title to text chunks too
            # Helps retrieval distinguish between sections with
            # similar vocabulary (e.g. two sections both mentioning "penalty")
            if section:
                content = f"Section: {section}\n{text}"
            else:
                content = text

            docs.append(Document(
                page_content=content,
                metadata={
                    "id": str(uuid4()),
                    "bank": bank,
                    "type": "text",
                    "section": section,
                    "source": file_path
                }
            ))

    # -----------------------------------------------
    # PREVIEW
    # -----------------------------------------------
    print(f"\n✅ Total docs created: {len(docs)}")

    table_docs = [d for d in docs if d.metadata["type"] == "table"]
    text_docs  = [d for d in docs if d.metadata["type"] == "text"]

    print(f"   📊 Table chunks : {len(table_docs)}")
    print(f"   📝 Text chunks  : {len(text_docs)}")

    print("\n📊 All table chunks:")
    for d in table_docs:
        print(f"\n  Section : {d.metadata.get('section', 'N/A')}")
        print(f"  Content : {d.page_content[:300]}")
        print("  ---")

    vector_store.add_documents(docs)
    print(f"\n✅ Stored in vector DB")

    all_docs = vector_store.get()
    print(f"📊 Total docs in DB: {len(all_docs['documents'])}")


# -----------------------------
# RUN INGESTION
# -----------------------------
if __name__ == "__main__":
    ingest_pdf("docs/SBI-Terms-and-Conditions.pdf", bank="SBI")

    # Add more banks when ready:
    # ingest_pdf("docs/hdfc_home_loan.pdf", bank="HDFC")