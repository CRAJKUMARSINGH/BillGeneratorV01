def hint_from_error(msg: str) -> str:
    msg = msg.lower()
    if "missing column" in msg:
        return "Check that all required columns exist in your input file."
    if "schema" in msg:
        return "Ensure XML follows the statutory schema (.xsd)."
    if "encoding" in msg:
        return "Save the file in UTF-8 before uploading."
    return "See documentation → Troubleshooting section."