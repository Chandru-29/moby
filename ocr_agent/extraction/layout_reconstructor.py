def reconstruct_layout(blocks):

    blocks = sorted(
        blocks,
        key=lambda b: (b["box_2d"][1], b["box_2d"][0])
    )

    text = []

    for block in blocks:
        text.append(block["text_content"])

    return "\n".join(text)