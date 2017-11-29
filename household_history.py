import csv
import sqlite3


class HouseholdHistory:
    def __init__(self, output = "household_output.csv"):
        self.output = output
        for variable in ['id', 'step', 'salary', 'base_salary', 'money', 'income', 'employer', 'unemployment_period',
                         'consumption_need', 'consumption', 'consumption_budget', 'consumption_expenses']:
            setattr(self, variable, [])
        try:
            open(self.output, "r")
        except:
            output_file = open(self.output, "w", newline='')
            writer = csv.DictWriter(output_file, dialect = 'excel',
                                    fieldnames=['household_id', 'step', 'salary', 'base_salary', 'money', 'income', 'employer',
                                    'unemployment_period', 'consumption_need', 'consumption', 'consumption_budget',
                                    'consumption_expenses'])
            writer.writeheader()
            output_file.close()



    def add_record(self, household):
        record = {}
        for variable in self.__dict__:
            if hasattr(household, variable):
                getattr(self, variable).append(getattr(household, variable))
                if variable == 'id':
                    record['household_id'] = getattr(household, variable)
                else:
                    record[variable] = getattr(household, variable)

        with open(self.output, "a", newline='') as output_file:
            writer = csv.DictWriter(output_file, dialect='excel', fieldnames=['household_id', 'step', 'salary', 'base_salary',
                         'money', 'income', 'employer', 'unemployment_period',
                         'consumption_need', 'consumption', 'consumption_budget', 'consumption_expenses'])
            writer.writerow(record)


    def add_database_record(self, household):
        record = {}
        for variable in self.__dict__:
            if hasattr(household, variable):
                getattr(self, variable).append(getattr(household, variable))
                if variable == 'id':
                    record['household_id'] = getattr(household, variable)
                else:
                    record[variable] = getattr(household, variable)

        conn = sqlite3.connect("D:\multiagent projects\phdjango\phdjango\db.sqlite3")
        c = conn.cursor()
        c.execute("INSERT INTO models_householdresult(" + ','.join(record.keys()) + ") VALUES(" + ','.join(['?'] * len(record.keys())) + ")",
                  tuple(record.values()))
        conn.commit()
        conn.close()



