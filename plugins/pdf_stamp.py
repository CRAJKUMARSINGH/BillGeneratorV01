def register():
    def add_stamp(pdf_path):
        # your stamping logic here
        return f"Stamped {pdf_path}"
    return {"add_stamp": add_stamp}