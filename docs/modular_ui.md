# Modular UI — BillGeneratorV01

## Why modularize?
- Clean separation between UI and computation logic
- Easier to rebrand and add internationalization
- Simpler unit testing of UI flows

## How to use
1. Import components:
```py
from app_components.streamlit_components import page_header, file_uploader, run_button, status_message, outputs_list
```

2. Replace inline Streamlit calls in `deployable_app.py` with the above functions.
3. Do not change computation functions; call them from event handlers (button clicks).

## Theming

* Place logo files in `branding/`
* Colors & fonts described in `branding/README.md`