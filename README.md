# Invoice PDF Extraction System

## Overview
The Invoice PDF Extraction System is a Python-based solution designed to extract relevant information from various types of invoice PDFs, including regular text-based PDFs, scanned PDFs, and mixed text/image PDFs. This system utilizes Optical Character Recognition (OCR) and regular expressions to retrieve structured data from invoices, which can then be saved for further analysis.

## Features
- Extracts data from different types of PDFs: regular, scanned, and mixed.
- Retrieves key information such as invoice number, date, taxable value, CGST, SGST, IGST rates, and final amounts.
- Outputs extracted data as a structured CSV file for easy analysis.

## Requirements
To run this project, you'll need the following Python libraries:
- `pandas`: For data manipulation and storage.
- `PyMuPDF`: For reading PDF files.
- `pytesseract`: For OCR processing of scanned images.
- `pdf2image`: To convert PDF pages into images.
- `pdfplumber`: An alternative library for extracting structured text and tables from PDFs.

You can install these libraries using the following command:

```bash
pip install pandas PyMuPDF pytesseract pdf2image pdfplumber
