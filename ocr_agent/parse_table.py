from bs4 import BeautifulSoup


def parse_html_table(html_content):

    soup = BeautifulSoup(html_content, "html.parser")

    table = soup.find("table")

    rows = []

    for tr in table.find_all("tr"):

        cells = []

        for td in tr.find_all("td"):
            cells.append(td.get_text(strip=True))

        if cells:
            rows.append(cells)

    return rows



def table_to_json(rows):

    headers = rows[1]

    data = []

    for row in rows[2:]:

        row_json = {}

        for i in range(min(len(headers), len(row))):
            row_json[headers[i]] = row[i]

        data.append(row_json)

    return data