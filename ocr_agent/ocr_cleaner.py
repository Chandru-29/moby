def clean_ocr_response(ocr_response):

    blocks = []

    for block in ocr_response:

        text = block.get("text_content", "").strip()
        box = block.get("box_2d", [])

        if text and box:
            x1, y1, x2, y2 = box

            blocks.append({
                "text": text,
                "x": x1,
                "y": y1
            })

    # sort by vertical position then horizontal
    blocks = sorted(blocks, key=lambda b: (b["y"], b["x"]))

    lines = [b["text"] for b in blocks]

    return "\n".join(lines)