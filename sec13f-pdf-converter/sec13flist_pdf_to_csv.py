import pdfplumber
import openpyxl
import csv
import pandas as pd
import re
import os

def extract_securities_to_xlsx_and_csv(pdf_path, output_csv_path, text_output_path, output_xlsx_path, bad_output_path):
    """
    Extracts tabular securities data from a PDF, saves it as a text file, writes to XLSX, and then exports to CSV.
    """
    try:
        # Extract text from PDF and write to an intermediate text file
        with pdfplumber.open(pdf_path) as pdf:
            with open(text_output_path, 'w', encoding='utf-8') as text_file:
                for page_num, page in enumerate(pdf.pages, 1):
                    print(f"Processing page {page_num}...")
                    words = page.extract_words(x_tolerance=3, keep_blank_chars=True)
                    words.sort(key=lambda w: (float(w['top']), float(w['x0'])))
                    current_line, current_y = "", None

                    for word in words:
                        if current_y != word['top']:
                            if current_line:
                                text_file.write(current_line.rstrip() + "\n")
                            current_line = ""
                            current_y = word['top']
                        x_pos = int(word['x0'])
                        while len(current_line) < x_pos // 6:
                            current_line += " "
                        current_line += word['text'] + " "
                    if current_line:
                        text_file.write(current_line.rstrip() + "\n")

                print(f"Text data has been saved to: {text_output_path}")

        print(f"Finished processing PDF to text.")

        # Open a new XLSX file for writing
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.title = "SEC 13F List"
        sheet.append(["CUSIP", "Option Flag", "Issuer Name", "Issuer Description", "Status"])

        # Open the text file and parse its content
        print(f"Opening text file: {text_output_path} for conversion to XLSX and CSV.")
        with open(text_output_path, 'r', encoding='utf-8') as text_file, open(bad_output_path, 'w', encoding='utf-8') as bad_file:
            for line in text_file:
                line = line.strip()
                # Check if the line contains a CUSIP field (using regex to find CUSIP pattern)
               # if re.search(r'\b[A-Za-z0-9]{6,8}\s\d{1,2}\s\d{1,2}\b', line):  # Looking for CUSIP pattern
               # if re.search(r'\b[A-Za-z0-9]{6}\s?[A-Za-z0-9]{2}\s?[A-Za-z0-9]{1}\b', line):  # Looking for CUSIP pattern
                if re.search(r'\b[A-Za-z0-9]{6}\s{1,3}[A-Za-z0-9]{2}\s{1,3}[A-Za-z0-9]{1}\b', line):  # Looking for CUSIP pattern
                    # Define fixed widths based on the structure of the input lines
                    cusip = line[0:6].strip()  # First 7 characters for CUSIP
                    digit_1 = line[7:9].strip()  # Digits after CUSIP
                    digit_2 = line[10:11].strip()  # Additional digits
                    asterisk = line[12:14].strip() 
                    issuer_name = line[15:43].strip()  # Characters from position 13 to 43 for the issuer name
                    issuer_description = line[43:63].strip()  # Characters from 43 to 73 for description
                    status = line[63:].strip()  # Status is the rest of the line after position 73

                    full_cusip = f"{cusip}{digit_1}{digit_2}"  # Combine CUSIP parts to match original layout
                    # Append data to Excel sheet
                    sheet.append([full_cusip, asterisk, issuer_name, issuer_description, status])
                else:
                    bad_file.write(line + "\n")
        workbook.save(output_xlsx_path)
        print(f"Spreadsheet has been saved to: {output_xlsx_path}")

        # Convert to CSV using pandas to retain proper quoting
        df = pd.read_excel(output_xlsx_path, dtype=str)
        df.to_csv(output_csv_path, index=False, quoting=csv.QUOTE_NONNUMERIC)
        print(f"CSV has been saved to: {output_csv_path}")

    except Exception as e:
        print(f"Error processing PDF: {e}")

if __name__ == "__main__":
    pdf_path = '13flist2020q4.pdf'
    # Get base name without extension
    base_name = os.path.splitext(pdf_path)[0]
    
    # Create output paths using base name
    output_csv_path = f"{base_name}.csv"
    text_output_path = f"{base_name}.txt"
    bad_output_path = f"{base_name}.bad.txt"
    output_xlsx_path = f"{base_name}.xlsx"
    extract_securities_to_xlsx_and_csv(pdf_path, output_csv_path, text_output_path, output_xlsx_path, bad_output_path)

