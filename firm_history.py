import csv
import sqlite3

class FirmHistory:
    def __init__(self, firm, output = "firm_output.csv"):
        self.firm_id = firm.id
        self.firm_type = None
        self.decision_maker_type = None
        self.step = []
        self.output = output
        for variable in ['money', 'price', 'salary', 'sold', 'sales', 'stock', 'workers', 'profit', 'plan', 'labor_capacity',
            'total_salary', 'salary_budget', 'raw', 'raw_budget', 'raw_need', 'raw_expenses', 'raw_bought', 'capital', 'capital_budget',
                         'capital_need', 'capital_expenses', 'capital_bought', 'total_capital_expenses']:
            setattr(self, variable, [])
        try:
            open(self.output, "r")
        except:
            output_file = open(self.output, "w", newline='')
            writer = csv.DictWriter(output_file, dialect = 'excel',
                                    fieldnames=['firm_id', 'firm_type', 'decision_maker_type', 'step',
                                                'money', 'price', 'salary', 'sold', 'sales', 'stock', 'profit', 'plan',
                                                'labor_capacity', 'total_salary', 'salary_budget', 'raw', 'raw_budget', 'raw_need',
                                                'raw_expenses', 'raw_bought', 'capital', 'capital_budget', 'capital_need',
                                                'capital_expenses', 'total_capital_expenses', 'capital_bought', 'workers'])
            writer.writeheader()
            output_file.close()



    def add_record(self, firm):
        self.firm_type = firm.type
        self.decision_maker_type = firm.decision_maker.type
        record = {"firm_id": firm.id, "firm_type": self.firm_type, "decision_maker_type": self.decision_maker_type}
        for variable in ['step', 'money', 'price', 'salary', 'sold', 'sales', 'stock', 'profit', 'plan', 'labor_capacity',
            'total_salary', 'salary_budget', 'raw', 'raw_budget', 'raw_need', 'raw_expenses', 'raw_bought', 'capital', 'capital_budget',
                         'capital_need', 'capital_bought', 'capital_expenses', 'total_capital_expenses']:
            if hasattr(firm, variable):
                value = getattr(firm, variable)
                record[variable] = value
            else:
                value = None
            getattr(self, variable).append(value)
        self.workers.append(len(firm.workers))
        record['workers'] = len(firm.workers)

        with open(self.output, "a", newline='') as output_file:
            writer = csv.DictWriter(output_file, dialect='excel', fieldnames=['firm_id', 'firm_type', 'decision_maker_type', 'step',
                                                'money', 'price', 'salary', 'sold', 'sales', 'stock', 'profit', 'plan',
                                                'labor_capacity', 'total_salary', 'salary_budget', 'raw', 'raw_budget', 'raw_need',
                                                'raw_expenses', 'raw_bought', 'capital', 'capital_budget', 'capital_need',
                                                'capital_expenses', 'total_capital_expenses', 'capital_bought', 'workers'])
            writer.writerow(record)


    def add_database_record(self, firm):
        self.firm_type = firm.type
        self.decision_maker_type = firm.decision_maker.type
        row = [firm.id, self.firm_type, self.decision_maker_type]
        for variable in ['step', 'money', 'price', 'salary', 'sold', 'sales', 'stock', 'profit', 'plan', 'labor_capacity',
            'total_salary', 'salary_budget', 'raw', 'raw_budget', 'raw_need', 'raw_expenses', 'raw_bought', 'capital', 'capital_budget',
                         'capital_need', 'capital_bought', 'capital_expenses']:
            if hasattr(firm, variable):
                value = getattr(firm, variable)
            else:
                value = None
            row.append(value)
        row.append(len(firm.workers))

        fieldnames = ['firm_id', 'firm_type', 'decision_maker_type', 'step',
                                                'money', 'price', 'salary', 'sold', 'sales', 'stock', 'profit', 'plan',
                                                'labor_capacity', 'total_salary', 'salary_budget', 'raw', 'raw_budget', 'raw_need',
                                                'raw_expenses', 'raw_bought', 'capital', 'capital_budget', 'capital_need',
                                                'capital_expenses', 'capital_bought', 'workers']

        conn = sqlite3.connect("D:\multiagent projects\phdjango\phdjango\db.sqlite3")
        c = conn.cursor()
        c.execute("INSERT INTO models_firmresult(" + ','.join(fieldnames) + ") VALUES(" + ','.join(['?'] * len(fieldnames)) + ")",
                  row)

        conn.commit()
        conn.close()




