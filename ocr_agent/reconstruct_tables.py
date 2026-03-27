import json
from collections import defaultdict


def reconstruct_tables(ocr_blocks, row_tolerance=15, col_tolerance=40):

    cells = []

    # flattening OCR blocks into cells
    for block in ocr_blocks:

        x1, y1, x2, y2 = block["box_2d"]

        text_lines = block["text_content"].split("\n")

        for i, line in enumerate(text_lines):

            if line.strip():

                cells.append({
                    "text": line.strip(),
                    "x": x1,
                    "y": y1 + (i * 10)  # approximate vertical split
                })

    #  grouping cells into rows
    rows = []

    cells = sorted(cells, key=lambda c: c["y"])

    current_row = [cells[0]]

    for cell in cells[1:]:

        if abs(cell["y"] - current_row[0]["y"]) <= row_tolerance:
            current_row.append(cell)

        else:
            rows.append(current_row)
            current_row = [cell]

    rows.append(current_row)

    # detected column positions
    column_positions = []

    for row in rows:

        for cell in row:

            x = cell["x"]

            found = False

            for col in column_positions:

                if abs(x - col) <= col_tolerance:
                    found = True
                    break

            if not found:
                column_positions.append(x)

    column_positions = sorted(column_positions)

    # building grid
    table = []

    for row in rows:

        grid_row = [""] * len(column_positions)

        for cell in row:

            x = cell["x"]

            col_index = min(
                range(len(column_positions)),
                key=lambda i: abs(column_positions[i] - x)
            )

            grid_row[col_index] = cell["text"]

        table.append(grid_row)

    return table


def table_to_json(table):

    headers = table[0]

    rows = []

    for row in table[1:]:

        row_json = {}

        for i, header in enumerate(headers):

            if header.strip():
                row_json[header] = row[i]

        rows.append(row_json)

    return rows



if __name__ == "__main__":

    with open("ocr_output.json") as f:
        ocr_data = json.load(f)

    table = reconstruct_tables(ocr_data)

    table_json = table_to_json(table)

    print(json.dumps(table_json, indent=2))