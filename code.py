import pdfplumber
import re
import pandas as pd
import os

def extract_invoice_details(pdf_path):
    # Open the PDF file
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        # Extract text from each page
        for page in pdf.pages:
            text += page.extract_text()

    # Clean up the text
    text = text.strip()
    
    invoice_number_pattern = r"Invoice\s*#:\s*(\S+)"
    invoice_date_pattern = r"Invoice\s*Date:\s*(\d{2}\s\w+\s\d{4})"
    taxable_value_pattern = r"Taxable\s*Amount\s*₹(\d+,\d+.\d{2}|\d+.\d{2})"
    cgst_pattern = r"CGST\s+(\d+.\d+%)\s*₹(\d+.\d{2})"
    sgst_pattern = r"SGST\s+(\d+.\d+%)\s*₹(\d+.\d{2})"
    igst_pattern = r"IGST\s+(\d+.\d+%)\s*₹(\d+.\d{2})"
    final_amount_pattern = r"Total\s₹(\d+,\d+.\d{2}|\d+.\d{2})"
    place_of_supply_pattern = r"Place\s*of\s*Supply\s*:\s*(\S+)"
    place_of_origin_pattern = r"Place\s*of\s*Origin\s*:\s*(\S+)"
    gstin_supplier_pattern = r"GSTIN\s*:\s*(\S+)"
    gstin_recipient_pattern = r"GSTIN\s*(\S+)\s*\n.*\n(.*)"

    # Search and extract relevant details
    invoice_number = re.search(invoice_number_pattern, text)
    invoice_date = re.search(invoice_date_pattern, text)
    taxable_value = re.search(taxable_value_pattern, text)
    cgst = re.search(cgst_pattern, text)
    sgst = re.search(sgst_pattern, text)
    igst = re.search(igst_pattern, text)
    final_amount = re.search(final_amount_pattern, text)
    place_of_supply = re.search(place_of_supply_pattern, text)
    place_of_origin = re.search(place_of_origin_pattern, text)
    gstin_supplier = re.search(gstin_supplier_pattern, text)
    gstin_recipient = re.search(gstin_recipient_pattern, text)
    cgst_matches = re.findall(cgst_pattern, text)
    sgst_matches = re.findall(sgst_pattern, text)
    igst_matches = re.findall(igst_pattern, text)
    # Create a dictionary to store the extracted data
    
    
    invoice_data = {
        "Invoice Number": invoice_number.group(1) if invoice_number else None,
        "Invoice Date": invoice_date.group(1) if invoice_date else None,
        "Taxable Value": taxable_value.group(1) if taxable_value else None,
        "CGST Rate": cgst.group(1) if cgst else None,
        "CGST Amount": cgst.group(2) if cgst else None,
        "SGST Rate": sgst.group(1) if sgst else None,
        "SGST Amount": sgst.group(2) if sgst else None,
        "IGST Rate": igst.group(1) if igst else None,
        "IGST Amount": igst.group(2) if igst else None,
        "Final Amount": final_amount.group(1) if final_amount else None,
        "Place of Supply": place_of_supply.group(1) if place_of_supply else None,
        "Place of Origin": place_of_origin.group(1) if place_of_origin else None,
        "Supplier GSTIN": gstin_supplier.group(1) if gstin_supplier else None,
        "Recipient GSTIN": gstin_recipient.group(1) if gstin_recipient else None,
        "CGST Rate": [float(rate[:-1]) for rate, _ in cgst_matches],  # Store rates as float
        "Total CGST Amount": sum(float(amount) for _, amount in cgst_matches),  # Total amount
        "SGST Rate": [float(rate[:-1]) for rate, _ in sgst_matches],  # Store rates as float
        "Total SGST Amount": sum(float(amount) for _, amount in sgst_matches),  # Total amount
        "IGST Rate": [float(rate[:-1]) for rate, _ in igst_matches],  # Store rates as float
        "Total IGST Amount": sum(float(amount) for _, amount in igst_matches),  # Total amount
    }
    return invoice_data

# Example usage
pdf_file_path = "C:\Created\LODA\Jan to Mar\INV-135_Mohith Saragur.pdf"
invoice_data = extract_invoice_details(pdf_file_path)

# Convert to pandas DataFrame for further manipulation if needed
invoice_df = pd.DataFrame([invoice_data])

invoice_df['Taxable Value'] = pd.to_numeric(invoice_df['Taxable Value'].str.replace(',', ''), errors='coerce')
invoice_df['Final Amount'] = pd.to_numeric(invoice_df['Final Amount'].str.replace(',', ''), errors='coerce')

# Calculate tax_amount
invoice_df['tax_amount'] = invoice_df['Final Amount'] - invoice_df['Taxable Value']

# Calculate tax_rate
invoice_df['tax_rate'] = (invoice_df['tax_amount'] / invoice_df['Taxable Value']) * 100  # converting to percentage

folder_path = r"C:\Created\LODA\Jan to Mar"
invoice_data_list = []

# Iterate through each PDF file in the folder
for filename in os.listdir(folder_path):
    if filename.endswith(".pdf"):
        pdf_file_path = os.path.join(folder_path, filename)
        invoice_data = extract_invoice_details(pdf_file_path)
        invoice_data_list.append(invoice_data)

# Convert list of dictionaries to a pandas DataFrame
invoice_df = pd.DataFrame(invoice_data_list)

# Convert relevant columns to numeric, handling commas and percentages appropriately
invoice_df['Taxable Value'] = pd.to_numeric(invoice_df['Taxable Value'].str.replace(',', ''), errors='coerce')
invoice_df['Final Amount'] = pd.to_numeric(invoice_df['Final Amount'].str.replace(',', ''), errors='coerce')

# Calculate tax_amount
invoice_df['tax_amount'] = invoice_df['Final Amount'] - invoice_df['Taxable Value']

# Calculate tax_rate
invoice_df['tax_rate'] = (invoice_df['tax_amount'] / invoice_df['Taxable Value']) * 100  # converting to percentage

# Display the final DataFrame
print(invoice_df)

invoice_df.to_csv("invoice_details.csv", index=False)
invoice_df.to_excel("invoice_details.xlsx", index=False)

## Confidence and accuracy checker

def validate_gstin(gstin):
    """Validate GSTIN format (15 characters: first 2 digits are state code, rest alphanumeric)."""
    gstin_pattern = r"\d{2}[A-Z]{5}\d{4}[A-Z]{1}[A-Z\d]{1}[Z]{1}[A-Z\d]{1}"
    return bool(re.match(gstin_pattern, gstin))

def validate_rate(rate):
    """Validate that the rate is a list of percentages (e.g., [6.0, 9.0])."""
    if not isinstance(rate, list):
        return False
    return all(isinstance(r, (float, int)) and 0 <= r <= 100 for r in rate)

def validate_amount(amount):
    """Validate that the amount is a number, including None."""
    return amount is None or isinstance(amount, (int, float))

def validate_place(place):
    """Validate that the place of supply is formatted as expected."""
    return isinstance(place, str) and '-' in place

def validate_final_amount(amount):
    """Validate the final amount is a positive number."""
    return isinstance(amount, (int, float)) and amount >= 0

# Accuracy and Confidence Check
def calculate_confidence_percentage(df):
    total_rows = len(df)
    confidence_metrics = {}
    
    # Initialize counters for each column
    metrics = {
        'CGST Rate': 0,
        'SGST Rate': 0,
        'IGST Rate': 0,
        'IGST Amount': 0,
        'Final Amount': 0,
        'Place of Supply': 0,
        'Recipient GSTIN': 0
    }

    for _, row in df.iterrows():
        # Increment counters if validation passes
        metrics['CGST Rate'] += 1 if validate_rate(row['CGST Rate']) else 0
        metrics['SGST Rate'] += 1 if validate_rate(row['SGST Rate']) else 0
        metrics['IGST Rate'] += 1 if validate_rate(row['IGST Rate']) else 0
        metrics['IGST Amount'] += 1 if validate_amount(row['IGST Amount']) else 0
        metrics['Final Amount'] += 1 if validate_final_amount(row['Final Amount']) else 0
        metrics['Place of Supply'] += 1 if validate_place(row['Place of Supply']) else 0
        metrics['Recipient GSTIN'] += 1 if validate_gstin(row['Recipient GSTIN']) else 0

    # Calculate the percentage of valid entries for each column
    for key in metrics:
        confidence_metrics[key] = (metrics[key] / total_rows) * 100
    
    return confidence_metrics

# Run accuracy check and calculate confidence percentages
confidence_percentages = calculate_confidence_percentage(invoice_df)

# Display the confidence percentages
confidence_percentages

def calculate_total_confidence(confidence_metrics):
    # Calculate the overall confidence as the average of all individual confidence metrics
    total_confidence = sum(confidence_metrics.values()) / len(confidence_metrics)
    return total_confidence

# Calculate confidence percentages for each column
confidence_percentages = calculate_confidence_percentage(invoice_df)

# Calculate the total confidence metric for the entire dataset
total_confidence = calculate_total_confidence(confidence_percentages)

# Display the total confidence metric as a percentage
print(f"Total Confidence Metric: {total_confidence:.2f}%")