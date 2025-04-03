# This will parse a SQL query and extract the SELECT columns.

import re

def extract_columns(sql_query):
    """Extracts column names from a SQL SELECT query, ensuring aliases, functions, and subqueries are handled correctly."""
    extracted_columns = []

    # First, capture everything between the first SELECT and the second FROM (if present)
    match = re.search(r"SELECT(.*?FROM.*?FROM)", sql_query, re.IGNORECASE | re.DOTALL)
    
    if match:
        # If we have a match, we are dealing with a query with a second FROM (like nested SELECTs)
        columns = match.group(1).strip()

        # Split the columns correctly while avoiding commas inside parentheses (for functions/subqueries)
        column_list = re.split(r",\s*(?![^()]*\))", columns)

        for col in column_list:
            col = col.strip()

            # Extract alias if present (AS keyword)
            alias_match = re.search(r"AS\s+([\w_]+)", col, re.IGNORECASE)
            if alias_match:
                extracted_columns.append(alias_match.group(1))

            # Handle CASE statements by extracting alias after END AS
            case_match = re.search(r"END\s+AS\s+([\w_]+)", col, re.IGNORECASE)
            if case_match:
                extracted_columns.append(case_match.group(1))

            # Handle functions and subqueries: Extract alias if present
            subquery_or_function_match = re.search(r"\)\s+AS\s+([\w_]+)", col, re.IGNORECASE)
            if subquery_or_function_match:
                extracted_columns.append(subquery_or_function_match.group(1))

            # Handle direct column selections without aliases
            direct_col_match = re.search(r"^\s*([\w_]+)\s*$", col)
            if direct_col_match:
                extracted_columns.append(direct_col_match.group(1))

    else:
        # For simple queries (without a nested SELECT and second FROM)
        match = re.search(r"SELECT(.*?)FROM", sql_query, re.IGNORECASE | re.DOTALL)
        
        if match:
            columns = match.group(1).strip()

            # Split the columns correctly while avoiding commas inside parentheses (for functions/subqueries)
            column_list = re.split(r",\s*(?![^()]*\))", columns)

            for col in column_list:
                col = col.strip()

                # Extract alias if present (AS keyword)
                alias_match = re.search(r"AS\s+([\w_]+)", col, re.IGNORECASE)
                if alias_match:
                    extracted_columns.append(alias_match.group(1))

                # Handle CASE statements by extracting alias after END AS
                case_match = re.search(r"END\s+AS\s+([\w_]+)", col, re.IGNORECASE)
                if case_match:
                    extracted_columns.append(case_match.group(1))

                # Handle functions and subqueries: Extract alias if present
                subquery_or_function_match = re.search(r"\)\s+AS\s+([\w_]+)", col, re.IGNORECASE)
                if subquery_or_function_match:
                    extracted_columns.append(subquery_or_function_match.group(1))

                # Handle direct column selections without aliases
                direct_col_match = re.search(r"^\s*([\w_]+)\s*$", col)
                if direct_col_match:
                    extracted_columns.append(direct_col_match.group(1))

    # Ensure no duplicates
    extracted_columns = list(set(extracted_columns))

    # Debug print the extracted columns
    print(f"Extracted Columns: {extracted_columns}")

    return extracted_columns


# Example Usage for a simple query
sql_simple = """
SELECT customer_id, sales, pls_work, please as pls
    FROM orders 
    WHERE order_date >= '2024-01-01'
"""
columns_simple = extract_columns(sql_simple)

# Example Usage for a complex query -- the limitation is it will not read columns after the first Subquery in the main select
sql_complex = """
SELECT 
    customer_id, customer_id as cust_id,
    CASE 
        WHEN total_sales > 1000 THEN 'VIP'
        ELSE 'Regular'
    END AS customer_status, pls_work,
    (SELECT AVG(sales) FROM transactions WHERE transactions.customer_id = orders.customer_id) AS avg_customer_sales,
    SUM(sales) AS total_sales
FROM (
    SELECT customer_id, sales 
    FROM orders 
    WHERE order_date >= '2024-01-01'
) orders
GROUP BY customer_id
"""
columns_complex = extract_columns(sql_complex)
