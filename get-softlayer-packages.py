import SoftLayer
import sys, json, string, csv
from decimal import Decimal

class example():

    def __init__(self):

        self.client = SoftLayer.Client()

        outputname = 'product_packages-oct2017.csv'
        fieldnames = ['Package ID', 'Package Name', 'Item ID', 'Description', 'KeyName', 'Price ID', 'Hourly Fee', 'One Time Fee', 'Recurring Fee', 'Setup Fee', 'Usage Fee', 'Location Group', 'Locations']
        self.outfile = open(outputname, 'w')
        #self.csvwriter = csv.writer(self.outfile, delimiter='\t', quotechar='"', quoting=csv.QUOTE_ALL)
        self.csvwriter = csv.DictWriter(self.outfile, delimiter=',', fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL)
        #self.csvwriter.writerow(dict((fn, fn) for fn in fieldnames))
        self.csvwriter.writeheader()

    def main(self):
        """
        Gets ALL packages, and prints their name and price descriptions
        """
        mask = "mask[hourlyBillingAvailableFlag]"
        result = self.client['Product_Package'].getAllObjects();
        for product in result:
            print str(product['id']) + " - " + product['name']
            main.getPackage(product['id'], product['name'])
        self.outfile.close()
    
    def getPackage(self, package_id=0, package_name=''):
        """
        Gets a specific package and prints out some useful information
        """
        mask = "mask[items[prices[id,hourlyRecurringFee,oneTimeFee,recurringFee,setupFee,usageRate,locationGroupId,attributes,categories,item,orderOptions,pricingLocationGroup[locations]]]]"

        # Not all packages are available in all locations, you can check that with getLocations()
        # locations = self.client['Product_Package'].getLocations(id=package_id)
        # pp(locations)

        result = self.client['Product_Package'].getObject(mask=mask,id=package_id)

        for item in result['items']:

            print '\n\n'
            print(item)

            #print str(item['id']) + " - " + item['description'] + " --- " + item['keyName']

            #row = {'Package ID': package_id, 'Package Name': package_name, 'Item ID': item['id'], 'Description': item['description'], 'KeyName': item['keyName']}

            prices = None
            for prices in item['prices']:
            #    print "\t" + str(prices['id']) + " - locationGroupId: " + str(prices['locationGroupId']) 

                hourlyRecurringFee = 0
                if 'hourlyRecurringFee' in prices:
                    hourlyRecurringFee = prices['hourlyRecurringFee']

                oneTimeFee = 0
                if 'oneTimeFee' in prices:
                    oneTimeFee = prices['oneTimeFee']

                recurringFee = 0
                if 'recurringFee' in prices:
                    recurringFee = prices['recurringFee']

                setupFee = 0
                if 'setupFee' in prices:
                    setupFee = prices['setupFee']

                usageFee = 0
                if 'usageRate' in prices:
                    usageFee = prices['usageRate']

                locations = ''
                locationGroupId = ''
                if 'locationGroupId' in prices:
                    locationGroupId = prices['locationGroupId']
                    if 'pricingLocationGroup' in prices:
                        if 'locations' in prices['pricingLocationGroup']:
                            for loc in prices['pricingLocationGroup']['locations']:
                                locations = locations + '[' + loc['name'] + ']'

                row = {
                    'Package ID': package_id, 
                    'Package Name': package_name,
                    'Item ID': item['id'],
                    'Description': item['description'],
                    'KeyName': item['keyName'],
                    'Price ID': prices['id'],
                    'Hourly Fee': hourlyRecurringFee,
                    'One Time Fee': oneTimeFee,
                    'Recurring Fee': recurringFee,
                    'Setup Fee': setupFee,
                    'Usage Fee': usageFee,
                    'Location Group': locationGroupId,
                    'Locations': locations
                }

                self.csvwriter.writerow(row)

        # Will only get the server items for this package
        # serverItems = self.client['Product_Package'].getActiveServerItems(id=package_id)
        # print "SERVER ITEMS"
        # pp(serverItems)

        # Will only get the RAM items for the package
        # ramItems = self.client['Product_Package'].getActiveRamItems(id=package_id)
        # print "RAM ITEMS"
        # pp(ramItems)

     
    
    def getAllLocations(self):
        mask = "mask[id,locations[id,name]]"
        result = self.client['SoftLayer_Location_Group_Pricing'].getAllObjects(mask=mask);
        print(result)

if __name__ == "__main__":
    main = example()
    main.main()
    #main.getPackage(126)
    #main.getAllLocations()  


