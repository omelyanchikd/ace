import csv
import sqlite3

class OutsideWorldHistory:
    def __init__(self, output = "outside_world_output.csv"):
        self.output = output
        self.step = []
        for type in ['raw', 'capital', 'production']:
            for variable in ['price', 'sales', 'sold', 'expenses', 'bought']:
                setattr(self, type + '_' + variable, [])
        try:
            open(self.output, "r")
        except:
            output_file = open(self.output, "w", newline='')
            writer = csv.DictWriter(output_file, dialect = 'excel',
                                    fieldnames=['step', 'raw_price', 'capital_price', 'production_price',
                                                'raw_sales', 'raw_sold', 'raw_expenses', 'raw_bought',
                                                'capital_sales', 'capital_sold', 'capital_expenses', 'capital_bought',
                                                'production_sales', 'production_sold', 'production_expenses', 'production_bought'])
            writer.writeheader()
            output_file.close()



    def add_record(self, record):
        for variable, value in record.items():
            getattr(self, variable).append(value)
        with open(self.output, "a", newline='') as output_file:
            writer = csv.DictWriter(output_file, dialect='excel', fieldnames=['step', 'participant_id', 'action', 'money'])
            writer.writerow(record)


    def add_database_record(self, record):
        conn = sqlite3.connect("D:\multiagent projects\phdjango\phdjango\db.sqlite3")
        c = conn.cursor()
        c.execute("INSERT INTO models_outsideworldresult(" + ','.join(record.keys()) + ") VALUES(?, ?, ?, ?, ?)",
                  tuple(record.values()))
        conn.commit()
        conn.close()



