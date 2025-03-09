# SEC 13F List PDF to XLSX/CSV Converter

A Python utility to extract securities data from SEC 13F List PDFs and convert them into machine-readable XLSX and CSV formats for database integration and analysis.

## Overview

The SEC publishes quarterly lists of securities in Form 13F reports as PDFs, which are not easily machine-readable. This utility extracts the tabular data from these PDFs and converts it into structured formats (XLSX and CSV) that can be imported into databases or used for analysis.

## Pre-Converted Files Available

For your convenience, I maintain a collection of pre-converted Excel and CSV files for SEC 13F list data from 2020 onwards at [sec13flist.com](http://sec13flist.com). If you need a specific SEC 13F PDF file converted to Excel or CSV format and don't want to run the converter yourself, please email me at contactus@sec13flist.com.

## Features

- Extracts securities data from SEC 13F PDF files
- Preserves the structure of the data using positional text extraction
- Generates intermediate text file for inspection and debugging
- Creates both XLSX and CSV output files
- Logs problematic lines to a separate .bad file for review
- Maintains CUSIP identifiers, issuer information, and security status

## Requirements

- Python 3.6+
- Required packages:
  - pdfplumber
  - openpyxl
  - pandas
  - re (built-in)
  - os (built-in)

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/sec-13f-converter.git
   cd sec-13f-converter
   ```

2. Install required dependencies:
   ```
   pip install pdfplumber openpyxl pandas
   ```

## Usage

1. Place your SEC 13F PDF file in the same directory as the script.

2. Update the filename in the script (if different from the default '13flist2020q4.pdf'):
   ```python
   pdf_path = 'your_13f_file.pdf'
   ```

3. Run the script:
   ```
   python sec13flist_pdf_to_csv.py
   ```

4. The script will generate four output files:
   - `[filename].txt`: Intermediate text representation of the PDF
   - `[filename].xlsx`: Excel spreadsheet with structured data
   - `[filename].csv`: CSV file with properly quoted values
   - `[filename].bad.txt`: Lines that couldn't be parsed correctly

## Understanding the .bad File

The `.bad.txt` file contains lines from the PDF that didn't match the expected pattern for securities data. This typically includes:

- Header and footer information
- Page numbers
- Section titles
- Notes or explanatory text
- Lines with formatting that differs from the expected pattern

Reviewing this file can help you:
1. Verify that important data wasn't missed
2. Identify patterns that might need additional parsing logic
3. Understand the structure of the document for future improvements

## Output Format

The generated XLSX and CSV files contain the following columns:

- **CUSIP**: The unique identifier for each security
- **Option Flag**: Indicator for option securities (typically an asterisk)
- **Issuer Name**: Name of the security issuer
- **Issuer Description**: Description of the security type
- **Status**: Current status information of the security

## Example

Input PDF line:
```
037833 10 0     * APPLE INC                      COM                 ADDED
```

Output CSV record:
```
"03783310","*","APPLE INC","COM","ADDED"
```

## Limitations

- The parser relies on consistent formatting in the PDF
- PDF structure changes by the SEC may require script adjustments
- Very long issuer names or descriptions might be truncated

## License

[MIT License](LICENSE)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
