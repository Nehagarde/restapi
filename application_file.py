from flask import Flask
import csv
import json
import datetime

app = Flask(__name__)

#reading product reference file
try:
    products_file = open('input_files/ProductReference.csv')
    product_details = csv.DictReader(products_file)
except:
    product_details = "Product reference file not found"


def get_all_transactions():
    #reading Transactions file
    try:
        check_file = csv.DictReader(open('input_files/Transaction_20180101101010.csv'))
    except:
        return "File Not Found!"

    return check_file

def get_formatted_output(summary,summary_type):
    #Format processed data as per requested summary type (product/city) 
    detailed_summary = {}
    summary_list = []
    for row in summary:
        total_amount = {}
        summary_type_details = {}
        details_and_amount = {}

        summary_type_details[summary_type] = row
        total_amount['totalAmount'] = summary[row] 
        
        details_and_amount = summary_type_details, total_amount
        summary_list.append(details_and_amount)

    detailed_summary['summary'] = summary_list
    return detailed_summary

def process_transaction_details(days,summary_type):
    #fetch transaction details based on requested summary type 
    no_of_days = int(days)
    end_date = datetime.datetime.now() - datetime.timedelta(days=no_of_days)

    all_transactions = get_all_transactions()
    if isinstance(all_transactions, str):
        return all_transactions

    if isinstance(product_details, str):
        return product_details

    products_file.seek(0)
    details= {}
    records_found = False
    
    for row in all_transactions:
        transaction_date_time = datetime.datetime.strptime(row['transactionDateTime'],'%Y-%m-%d %H:%M:%S')
        
        products_file.seek(0)
        if transaction_date_time >= end_date and transaction_date_time <= datetime.datetime.now():
            records_found = True
            
            for r1 in product_details:
                if r1['productId'] == row['productId']:
                    key = r1[summary_type]
                    if key in details:
                        details[key] += (float)(row['transactionAmount'])
                    else:
                        details[key] = (float)(row['transactionAmount']) 

    if not records_found:
        return "No Records Found!"
    else:
        return details

@app.route('/')
def index():
    return "Implementation of REST APIs."

@app.route('/transaction/<id>')
def get_transaction_details(id):
    """
        Arguments: Transaction Id
        Description: Based on the Transaction Id the function processes the transaction details

    """

    all_transactions = get_all_transactions()
    if isinstance(product_details, str):
        return product_details
    products_file.seek(0)
    transaction_details = {}
    
    records_found = False
    for row in all_transactions:
        if id == row['transactionId']:
            transaction_details['transactionId'] = row['transactionId']
            transaction_details['transactionAmount'] = row['transactionAmount']
            transaction_details['transactionDateTime'] = row['transactionDateTime']
            transaction_details['productName'] = [product['productName'] for product in product_details if product['productId'] == row['productId']][0]

            records_found = True

    if not records_found:
        return "No Records Found!"        
    return json.dumps(transaction_details)    


@app.route('/transactionSummaryByProduct/<days>')
def get_transaction_summary_by_product(days):
    """
        Arguments: No.of Days
        Description: The function produces the detailed summary of transactions by product for Last 'N' Days

    """
    details_by_product_id = process_transaction_details(days,'productName')
    
    if isinstance(details_by_product_id, str):
        return details_by_product_id
    return json.dumps(get_formatted_output(details_by_product_id,'productName'))


@app.route('/transactionSummaryByManufacturingCity/<days>')
def get_transaction_summary_by_city(days):
    """
        Arguments: No.of Days
        Description: The function produces the detailed summary of transactions by product for Last 'N' Days

    """
    details_by_manufacturing_city = process_transaction_details(days,'productManufacturingCity')
    
    if isinstance(details_by_manufacturing_city, str):
        return details_by_manufacturing_city
    return json.dumps(get_formatted_output(details_by_manufacturing_city,'cityName'))


if __name__ == '__main__':
    app.run()