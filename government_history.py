import csv
import sqlite3

class GovernmentHistory:
    def __init__(self, output = "government_output.csv"):
        self.output = output
        for variable in ['step', 'participant_id', 'action', 'money']:
            setattr(self, variable, [])
        try:
            open(self.output, "r")
        except:
            output_file = open(self.output, "w", newline='')
            writer = csv.DictWriter(output_file, dialect = 'excel',
                                    fieldnames=['step', 'participant_id', 'action', 'money'])
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
        c.execute("INSERT INTO models_governmentresult(" + ','.join(record.keys()) + ") VALUES(?, ?, ?, ?, ?)",
                  tuple(record.values()))

        conn.commit()
        conn.close()



