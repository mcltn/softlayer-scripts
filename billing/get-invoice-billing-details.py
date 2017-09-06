
import sys, simplejson, csv
import SoftLayer


client = SoftLayer.Client()
orderIds = []
csvwriter = None

def getInvoicesByDate(startDate, endDate):

    # Build Filter for Invoices
    InvoiceList = client['Account'].getInvoices(filter={
            'invoices': {
                'createDate': {
                    'operation': 'betweenDate',
                    'options': [
                         {'name': 'startDate', 'value': [startdate+" 00:00:00"]},
                         {'name': 'endDate', 'value': [enddate+" 23:59:59"]}

                    ]
                }
                ,'typeCode': {
                    'operation': 'in',
                    'options': [
                        {'name': 'data', 'value': ['RECURRING']}
                    ]
                    },
                }
            })

    for invoice in InvoiceList:
        global csvwriter 
        orderIds = []
        invoice_id = invoice['id']
        print(invoice_id)

        ## Define the columns to be exported into a CSV file
        fieldnames = ['id','billingItemId','parentId','datacenter','hostName', 'categoryCode', 'description','billingItemDescription','orderItemDescription','packageName','hourlyRecurringFee','recurringAfterTaxAmount','recurringFee']

        outputname = 'billing-invoice-' + str(invoice_id) + '.csv'
        outfile = open(outputname, 'w')
        csvwriter = csv.writer(outfile, delimiter='\t', quotechar='"', quoting=csv.QUOTE_ALL)
        csvwriter = csv.DictWriter(outfile, delimiter=',', fieldnames=fieldnames)
        csvwriter.writerow(dict((fn, fn) for fn in fieldnames))

        getInvoiceById(invoice_id)

        outfile.close()



def getInvoiceById(invoice_id):
    print("Looking up invoice " + str(invoice_id))
    #invoice_mask = 'invoiceTopLevelItems, invoiceTopLevelItems.totalRecurringAmount, invoiceTopLevelItems.billingItem, invoiceTotalAmount, invoiceTopLevelItemCount, invoiceTotalRecurringAmount'
    invoice_mask = 'itemCount' #,invoiceTotalAmount,items.resourceTableId,items.recurringAfterTaxAmount,items.oneTimeAfterTaxAmount,items.description,items.associatedChildren'
    Billing_Invoice = client['Billing_Invoice'].getObject(id=invoice_id, mask=invoice_mask)

    invoiceDate = Billing_Invoice['createDate'][0:10]

    itemCount = Billing_Invoice['itemCount']
    print('Items: ' + str(Billing_Invoice['itemCount']))
    print(Billing_Invoice)
    print('\n\n')

    offset = 0 #20900
    for i in range(0,itemCount,100):
        getInvoiceItemsById(invoice_id,i)


def getInvoiceItemsById(invoice_id,offset):
    print("Looking up items for invoice " + str(invoice_id) + " offset " + str(offset))
    #invoice_mask = 'invoiceTopLevelItems, invoiceTopLevelItems.totalRecurringAmount, invoiceTopLevelItems.billingItem, invoiceTotalAmount, invoiceTopLevelItemCount, invoiceTotalRecurringAmount'
    invoice_mask = 'hostName,domainName,associatedInvoiceItemId,billingItemId,categoryCode,createDate,description,hourlyRecurringFee,id,parentId,productItemId,recurringAfterTaxAmount,recurringFee,recurringFeeTaxRate,resourceTableId,billingItem,billingItem.orderItem.order.id,billingItem.package,product,location'
    Billing_Invoice_Items = client['Billing_Invoice'].getItems(id=invoice_id,mask=invoice_mask,limit=100,offset=offset)

    for item in Billing_Invoice_Items:
        print('\n')
        print(item['description'])
        print(simplejson.dumps(item, sort_keys=True, indent=4 * ' '))

        hourlyRecurringFee = 0
        recurringFee = 0
        hostName = ''
        if 'recurringFee' in item:
            recurringFee = item['recurringFee']
        if 'hourlyRecurringFee' in item:
            hourlyRecurringFee = item['hourlyRecurringFee']
        if 'hostName' in item:
            hostName = item['hostName']

        parentId = item['parentId']
        if parentId == '':
            parentId = item['id']

        orderItemDescription = ''
        if 'orderItem' in item['billingItem']:
            orderItemDescription = item['billingItem']['orderItem']['description']
            orderId = item['billingItem']['orderItem']['order']['id']
            # Putting OrderIds into an array in case we want to do additional lookups
            # outside of this loop
            if orderId not in orderIds:
                orderIds.append(orderId)

        packageName = ''
        if 'package' in item['billingItem']:
            packageName = item['billingItem']['package']['name']

        row = {
           'id': item['id'],
           'billingItemId': item['billingItemId'],
           'parentId': parentId,
           'datacenter': item['location']['name'],
           'hostName': hostName,
           'categoryCode': item['categoryCode'],
           'description': item['description'],
           'billingItemDescription': item['billingItem']['description'],
           'orderItemDescription': orderItemDescription,
           'packageName': packageName,
           'hourlyRecurringFee': hourlyRecurringFee,
           'recurringAfterTaxAmount': item['recurringAfterTaxAmount'],
           'recurringFee': recurringFee,
            }
        csvwriter.writerow(row)


####################################################
####################################################

# Define a date range to lookup invoices.
# This will loop throughinvoices and create csv files
startdate = '6/1/2017'
enddate = '6/30/2017'
getInvoicesByDate(startdate,enddate)

# If you know an invoice ID just run this by itself.
#invoice_id = 15291251
#getInvoiceById(invoice_id)

####################################################
####################################################

