import re
import json

def extract_document_data(ocr_blocks):

    # ---- STEP 1: sort blocks by layout ----
    blocks = sorted(
        ocr_blocks,
        key=lambda b: (b["box_2d"][1], b["box_2d"][0])
    )

    all_text = "\n".join([b["text_content"] for b in blocks])

    data = {}

    # ---- STEP 2: simple regex extraction ----
    doc_match = re.search(r"\b\d{4}-\d+\b", all_text)
    if doc_match:
        data["document_number"] = doc_match.group()

    date_match = re.search(r"\d{2}/\d{2}/\d{4}", all_text)
    if date_match:
        data["document_date"] = date_match.group()

    customer_match = re.search(
        r"CLIENTE-CUSTOMER\s*(.*?)\n",
        all_text,
        re.DOTALL
    )

    if customer_match:
        data["customer"] = customer_match.group(1).strip()

    quality_match = re.search(
        r"QUALITY\s*([A-Z0-9\+\s]+)",
        all_text
    )

    if quality_match:
        data["quality"] = quality_match.group(1).strip()

    # ---- STEP 3: detect chemical columns ----
    columns = {
        "C": [],
        "Mn": [],
        "Si": [],
        "P": [],
        "S": [],
        "Al": []
    }

    for block in blocks:

        text = block["text_content"]

        for col in columns.keys():

            if text.startswith(col):

                values = text.split("\n")[1:]

                columns[col] = values

    # ---- STEP 4: reconstruct rows ----
    rows = []
    row_count = max(len(v) for v in columns.values() if v)

    for i in range(row_count):

        row = {}

        for col in columns:

            if i < len(columns[col]):
                row[col] = columns[col][i]

        rows.append(row)

    data["chemical_composition"] = rows

    return data


# Example usage
if __name__ == "__main__":

    import json

    with open("ocr_output.json") as f:
        ocr_blocks = json.load(f)

    result = extract_document_data(ocr_blocks)

    print(json.dumps(result, indent=2))