import csv

class FirmHistory:
    def __init__(self, firm, output = "firm_output.csv"):
        self.output = output
        for variable in ['money', 'price', 'salary', 'sold', 'sales', 'stock', 'workers', 'profit', 'plan', 'labor_capacity',
            'salary_budget', 'raw', 'raw_budget', 'raw_need', 'capital', 'capital_budget', 'capital_need', 'capital_expenses']:
            setattr(self, variable, [])
        try:
            open(self.output, "r")
        except:
            output_file = open(self.output, "w", newline='')
            writer = csv.DictWriter(output_file, dialect = 'excel',
                                    fieldnames=['firm_id', 'id', 'firm_type', 'decision_maker_type', 'firm_step',
                                                'money', 'price', 'salary', 'sold', 'sales', 'stock', 'profit', 'plan',
                                                'labor_capacity', 'salary_budget', 'raw', 'raw_budget', 'raw_need',
                                                'capital', 'capital_budget', 'capital_need', 'capital_expenses', 'workers'])
            writer.writeheader()
            output_file.close()



    def add_record(self, firm):
        row = [firm.__class__.__name__ + str(firm.id), firm.id, firm.type, firm.decision_maker.type, firm.step]
        for variable in ['money', 'price', 'salary', 'sold', 'sales', 'stock', 'profit', 'plan', 'labor_capacity',
            'salary_budget', 'raw', 'raw_budget', 'raw_need', 'capital', 'capital_budget', 'capital_need', 'capital_expenses']:
            try:
                value = getattr(firm, variable)
            except:
                value = None
            getattr(self, variable).append(value)
            row.append(value)
        self.workers.append(len(firm.workers))
        row.append(len(firm.workers))
        with open(self.output, "a", newline='') as output_file:
            writer = csv.writer(output_file, dialect='excel')
            writer.writerow(row)



