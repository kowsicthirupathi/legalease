import streamlit as st
import requests
from datetime import date
from io import BytesIO
import re

from docx import Document
from fpdf import FPDF


BACKEND_URL = "https://legalease-api-kciy.onrender.com/generate"


st.set_page_config(
    page_title="LegalEase",
    page_icon="⚖️",
    layout="wide"
)


st.title("⚖️ LegalEase")
st.subheader("AI-Powered Legal Document Generator")

st.write(
    "Generate customizable legal documents using Generative AI."
)


document_type = st.selectbox(
    "Document Type",
    [
        "Employment Contract",
        "Lease Agreement",
        "Non-Disclosure Agreement (NDA)"
    ]
)


parties = st.text_area(
    "Parties",
    placeholder="Example: ABC Technologies Pvt Ltd and John Doe"
)


effective_date = st.date_input(
    "Effective Date",
    value=date.today()
)


terms = st.text_area(
    "Important Terms",
    placeholder="Enter salary, duration, rent, confidentiality terms, responsibilities, etc.",
    height=180
)


if st.button("Generate Legal Document", type="primary"):

    if not parties.strip():
        st.error("Please enter the parties.")

    elif not terms.strip():
        st.error("Please enter the important terms.")

    else:

        payload = {
            "document_type": document_type,
            "parties": parties,
            "terms": terms,
            "effective_date": str(effective_date)
        }

        try:

            with st.spinner("Generating your legal document..."):

                response = requests.post(
                    BACKEND_URL,
                    json=payload,
                    timeout=120
                )

            if response.status_code == 200:

                result = response.json()

                if result.get("success"):

                    document_content = result.get(
                        "document",
                        ""
                    )

                    st.success(
                        "Legal document generated successfully!"
                    )

                    st.subheader("Editable Document Preview")

                    edited_content = st.text_area(
                        "Edit your document",
                        value=document_content,
                        height=500
                    )


                    # TXT download

                    st.download_button(
                        label="Download TXT",
                        data=edited_content,
                        file_name="LegalEase_Document.txt",
                        mime="text/plain"
                    )


                    # DOCX generation

                    doc = Document()

                    for line in edited_content.splitlines():

                        if line.strip():

                            doc.add_paragraph(line)

                    docx_buffer = BytesIO()

                    doc.save(docx_buffer)

                    docx_buffer.seek(0)


                    st.download_button(
                        label="Download DOCX",
                        data=docx_buffer,
                        file_name="LegalEase_Document.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )


                    # PDF generation

                    pdf = FPDF()

                    pdf.set_auto_page_break(
                        auto=True,
                        margin=15
                    )

                    pdf.add_page()

                    pdf.set_font(
                        "Arial",
                        size=11
                    )


                    for line in edited_content.splitlines():

                        clean_line = re.sub(
                            r"[^\x00-\x7F]+",
                            "",
                            line
                        )

                        if clean_line.strip():

                            pdf.multi_cell(
                                0,
                                7,
                                clean_line
                            )

                            pdf.ln(1)


                    pdf_bytes = bytes(
                        pdf.output()
                    )


                    st.download_button(
                        label="Download PDF",
                        data=pdf_bytes,
                        file_name="LegalEase_Document.pdf",
                        mime="application/pdf"
                    )

                else:

                    st.error(
                        result.get(
                            "error",
                            "Document generation failed."
                        )
                    )

            else:

                st.error(
                    f"Backend error: HTTP {response.status_code}"
                )

                st.code(response.text)


        except requests.exceptions.Timeout:

            st.error(
                "The request timed out. Please try again."
            )


        except requests.exceptions.ConnectionError:

            st.error(
                "Could not connect to the LegalEase backend."
            )


        except Exception as error:

            st.error(
                f"Unexpected error: {error}"
            )