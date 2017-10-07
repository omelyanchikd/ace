import csv

class GoodMarketHistory:
    def __init__(self, output = "good_market_output.csv"):
        self.output = output
        for variable in ['step', 'seller_id', 'buyer_id', 'quantity', 'money']:
            setattr(self, variable, [])
        try:
            open(self.output, "r")
        except:
            output_file = open(self.output, "w", newline='')
            writer = csv.DictWriter(output_file, dialect = 'excel',
                                    fieldnames=['step', 'seller_id', 'buyer_id', 'quantity', 'money'])
            writer.writeheader()
            output_file.close()



    def add_record(self, record):
        for variable, value in record.items():
            getattr(self, variable).append(value)
        with open(self.output, "a", newline='') as output_file:
            writer = csv.DictWriter(output_file, dialect='excel', fieldnames=['step', 'seller_id', 'buyer_id', 'quantity', 'money'])
            writer.writerow(record)



