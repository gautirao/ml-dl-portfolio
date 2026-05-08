# Import Assumptions

When importing bank data, LedgerMind Local makes several assumptions to standardise the information.

## Supported Formats
- **Monzo**: Directly imports standard Monzo CSV exports.
- **HSBC Minimal**: Handles minimal HSBC exports which may lack full merchant details by attempting to extract information from the description field.

## Data Mapping
- **Date**: Standardised to YYYY-MM-DD.
- **Amount**: Normalised to a decimal value. Inflows are positive, outflows are negative.
- **Merchant**: Extracted from the transaction description or a dedicated merchant field if available.
- **Category**: Initial categories are suggested based on historical patterns or keywords, but require user approval.

## Duplication
The system uses a combination of date, amount, and description to fingerprint transactions and avoid duplicates during re-imports.
