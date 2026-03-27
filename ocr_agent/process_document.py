from ocr_agent import structure_document
from ocr_agent.agent import root_agent
from ocr_agent.ocr_cleaner import clean_ocr_response

from ocr_agent.reconstruct_tables import reconstruct_tables, table_to_json as bbox_table_to_json
from ocr_agent.extraction.extract_fields import extract_document_data

from ocr_agent.parsing.markdown_table_parser import (
    extract_markdown_tables,
    parse_table,
    table_to_json
)


def process_document(image_path):

#    run OCR
    ocr_response = root_agent.run(image_path)

    print("\n--- OCR BLOCKS ---")
    print(ocr_response)

    # extract simple fields 
    extracted_fields = extract_document_data(ocr_response)

    print("\n--- EXTRACTED FIELDS ---")
    print(extracted_fields)

    #  reconstruct tables using bounding boxes
    bbox_table = reconstruct_tables(ocr_response)
    bbox_table_json = bbox_table_to_json(bbox_table)

    print("\n--- BBOX TABLE DATA ---")
    print(bbox_table_json)

    #  clean OCR text
    raw_text = clean_ocr_response(ocr_response)

    print("\n--- CLEAN TEXT ---")
    print(raw_text)

    # parse markdown tables
    tables = extract_markdown_tables(raw_text)

    markdown_tables_json = []

    for table in tables:

        rows = parse_table(table)

        table_json = table_to_json(rows)

        if table_json:
            markdown_tables_json.append(table_json)

    print("\n--- MARKDOWN TABLES ---")
    print(markdown_tables_json)

    #  use LLM for reasoning fields
    structured_llm = structure_document(raw_text)

    print("\n--- LLM STRUCTURED ---")
    print(structured_llm)

    # merge results
    final_json = {
        **extracted_fields,
        "tables_bbox": bbox_table_json,
        "tables_markdown": markdown_tables_json,
        "llm_fields": structured_llm
    }

    print("\n--- FINAL OUTPUT ---")
    print(final_json)

    return final_json