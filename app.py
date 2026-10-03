import streamlit as st
import requests
from datetime import date
from io import BytesIO
import re

from docx import Document
from fpdf import FPDF


# ============================================================
# DOCX GENERATOR
# ============================================================

def create_docx(document_text):

    document = Document()

    document_text = str(document_text)

    for line in document_text.splitlines():
        document.add_paragraph(line)

    output = BytesIO()

    document.save(output)

    output.seek(0)

    return output.getvalue()


# ============================================================
# PDF TEXT CLEANER
# ============================================================

def prepare_pdf_text(text):

    text = str(text)

    # Replace common Unicode punctuation
    replacements = {
        "\u2013": "-",
        "\u2014": "-",
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2022": "-",
        "\u00a0": " ",
        "\u2026": "...",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    # Convert remaining unsupported characters
    text = text.encode(
        "latin-1",
        "replace"
    ).decode(
        "latin-1"
    )

    return text


# ============================================================
# PDF LINE WRAPPER
# ============================================================

def split_long_words(text, max_length=70):

    words = text.split(" ")

    result = []

    for word in words:

        if len(word) <= max_length:

            result.append(word)

        else:

            # Break extremely long words
            # so FPDF always has a break point.

            chunks = [
                word[i:i + max_length]
                for i in range(
                    0,
                    len(word),
                    max_length
                )
            ]

            result.extend(chunks)

    return " ".join(result)


# ============================================================
# PDF GENERATOR
# ============================================================

def create_pdf(document_text):

    pdf = FPDF(
        format="A4"
    )

    pdf.set_margins(
        15,
        15,
        15
    )

    pdf.set_auto_page_break(
        auto=True,
        margin=15
    )

    pdf.add_page()

    pdf.set_font(
        "Helvetica",
        size=11
    )

    # Calculate safe printable width
    usable_width = (
        pdf.w
        - pdf.l_margin
        - pdf.r_margin
    )

    # Clean the generated document
    safe_text = prepare_pdf_text(
        document_text
    )

    # Process every line
    for original_line in safe_text.splitlines():

        # Remove problematic control characters
        line = re.sub(
            r"[\x00-\x08\x0b\x0c\x0e-\x1f]",
            "",
            original_line
        )

        # Empty line
        if not line.strip():

            pdf.ln(5)

            continue

        # Break very long words
        line = split_long_words(
            line,
            max_length=70
        )

        # Render using explicit width
        pdf.multi_cell(
            usable_width,
            7,
            line
        )

    # Return PDF as bytes
    return bytes(
        pdf.output()
    )


# ============================================================
# STREAMLIT PAGE CONFIGURATION
# ============================================================

st.set_page_config(

    page_title="LegalEase",

    page_icon="⚖️",

    layout="wide"
)


# ============================================================
# HEADER
# ============================================================

st.title(
    "⚖️ LegalEase"
)

st.subheader(
    "AI-Powered Legal Document Generator"
)

st.write(
    "Create customizable legal documents quickly using Gemini AI."
)

st.divider()


# ============================================================
# DOCUMENT TYPE
# ============================================================

document_type = st.selectbox(

    "Document Type",

    [
        "Employment Contract",
        "Lease Agreement",
        "Non-Disclosure Agreement (NDA)",
        "Service Agreement",
        "Partnership Agreement"
    ]
)


# ============================================================
# PARTIES
# ============================================================

parties = st.text_area(

    "Parties",

    placeholder=
    "Example: ABC Company and John Doe"
)


# ============================================================
# TERMS
# ============================================================

terms = st.text_area(

    "Terms & Conditions",

    placeholder=
    "Enter the important terms and conditions..."
)


# ============================================================
# EFFECTIVE DATE
# ============================================================

effective_date = st.date_input(

    "Effective Date",

    value=date.today()
)


# ============================================================
# GENERATE BUTTON
# ============================================================

if st.button(

    "Generate Document",

    type="primary"
):

    # --------------------------------------------------------
    # VALIDATION
    # --------------------------------------------------------

    if not parties.strip():

        st.warning(
            "Please enter the parties."
        )

    elif not terms.strip():

        st.warning(
            "Please enter the terms and conditions."
        )

    else:

        data = {

            "document_type":
                document_type,

            "parties":
                parties,

            "terms":
                terms,

            "effective_date":
                str(effective_date)
        }


        try:

            # ------------------------------------------------
            # FASTAPI REQUEST
            # ------------------------------------------------

            response = requests.post(

                "http://127.0.0.1:8000/generate",

                json=data,

                timeout=120
            )


            # ------------------------------------------------
            # SUCCESSFUL HTTP RESPONSE
            # ------------------------------------------------

            if response.status_code == 200:

                result = response.json()


                # ============================================
                # GEMINI SUCCESS
                # ============================================

                if result.get("success"):

                    st.success(

                        "AI legal document generated successfully!"
                    )


                    st.subheader(

                        "Generated Legal Document"
                    )


                    generated_document = str(

                        result.get(
                            "document",
                            ""
                        )
                    )


                    # ----------------------------------------
                    # EDITABLE PREVIEW
                    # ----------------------------------------

                    edited_document = st.text_area(

                        "Preview / Edit Document",

                        value=generated_document,

                        height=600
                    )


                    st.divider()


                    st.subheader(

                        "Download Document"
                    )


                    # ========================================
                    # TXT DOWNLOAD
                    # ========================================

                    st.download_button(

                        label="Download TXT",

                        data=edited_document,

                        file_name=
                        "LegalEase_Document.txt",

                        mime="text/plain"
                    )


                    # ========================================
                    # DOCX DOWNLOAD
                    # ========================================

                    try:

                        docx_data = create_docx(

                            edited_document
                        )


                        st.download_button(

                            label="Download DOCX",

                            data=docx_data,

                            file_name=
                            "LegalEase_Document.docx",

                            mime=
                            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        )

                    except Exception as error:

                        st.error(

                            f"DOCX generation error: {error}"
                        )


                    # ========================================
                    # PDF DOWNLOAD
                    # ========================================

                    try:

                        pdf_data = create_pdf(

                            edited_document
                        )


                        st.download_button(

                            label="Download PDF",

                            data=pdf_data,

                            file_name=
                            "LegalEase_Document.pdf",

                            mime="application/pdf"
                        )

                    except Exception as error:

                        st.error(

                            f"PDF generation error: {error}"
                        )


                # ============================================
                # GEMINI FAILURE
                # ============================================

                else:

                    st.error(

                        "Gemini could not generate the document."
                    )

                    st.code(

                        result.get(

                            "error",

                            "Unknown backend error"
                        )
                    )


            # ------------------------------------------------
            # HTTP ERROR
            # ------------------------------------------------

            else:

                st.error(

                    f"Backend returned an error: "
                    f"{response.status_code}"
                )

                st.code(
                    response.text
                )


        # ----------------------------------------------------
        # FASTAPI CONNECTION ERROR
        # ----------------------------------------------------

        except requests.exceptions.ConnectionError:

            st.error(

                "FastAPI backend is not running. "
                "Please start the FastAPI server first."
            )


        # ----------------------------------------------------
        # TIMEOUT
        # ----------------------------------------------------

        except requests.exceptions.Timeout:

            st.error(

                "The AI request took too long. "
                "Please try again."
            )


        # ----------------------------------------------------
        # OTHER ERROR
        # ----------------------------------------------------

        except Exception as error:

            st.error(

                f"Something went wrong: {error}"
            )