def extract_markdown_tables(text):

    lines = text.split("\n")

    tables = []
    current_table = []

    for line in lines:

        if line.strip().startswith("|"):

            current_table.append(line)

        else:

            if current_table:
                tables.append(current_table)
                current_table = []

    if current_table:
        tables.append(current_table)

    return tables




def parse_table(table_lines):

    rows = []

    for line in table_lines:

        cells = [c.strip() for c in line.split("|")[1:-1]]

        if cells:
            rows.append(cells)

    return rows



def table_to_json(rows):

    if len(rows) < 2:
        return []

    headers = rows[0]

    data = []

    for row in rows[2:]:

        obj = {}

        for i in range(min(len(headers), len(row))):

            key = headers[i].replace("\n", " ").strip()

            obj[key] = row[i]

        data.append(obj)

    return data