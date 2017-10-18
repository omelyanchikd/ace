import csv

class FirmHistory:
    def __init__(self, firm, output = "firm_output.csv"):
        self.firm_id = firm.id
        self.firm_type = None
        self.decision_maker_type = None
        self.step = []
        self.output = output
        for variable in ['money', 'price', 'salary', 'sold', 'sales', 'stock', 'workers', 'profit', 'plan', 'labor_capacity',
            'total_salary', 'salary_budget', 'raw', 'raw_budget', 'raw_need', 'raw_expenses', 'capital', 'capital_budget',
                         'capital_need', 'capital_expenses']:
            setattr(self, variable, [])
        try:
            open(self.output, "r")
        except:
            output_file = open(self.output, "w", newline='')
            writer = csv.DictWriter(output_file, dialect = 'excel',
                                    fieldnames=['firm_id', 'id', 'firm_type', 'decision_maker_type', 'firm_step',
                                                'money', 'price', 'salary', 'sold', 'sales', 'stock', 'profit', 'plan',
                                                'labor_capacity', 'totaly_salary', 'salary_budget', 'raw', 'raw_budget', 'raw_need',
                                                'raw_expenses', 'capital', 'capital_budget', 'capital_need', 'capital_expenses', 'workers'])
            writer.writeheader()
            output_file.close()



    def add_record(self, firm):
        self.firm_type = firm.type
        self.decision_maker_type = firm.decision_maker.type
        row = [self.firm_type + str(firm.id), firm.id, self.firm_type, self.decision_maker_type]
        for variable in ['step', 'money', 'price', 'salary', 'sold', 'sales', 'stock', 'profit', 'plan', 'labor_capacity',
            'total_salary', 'salary_budget', 'raw', 'raw_budget', 'raw_need', 'raw_expenses', 'capital', 'capital_budget',
                         'capital_need', 'capital_expenses']:
            if hasattr(firm, variable):
                value = getattr(firm, variable)
            else:
                value = None
            getattr(self, variable).append(value)
            row.append(value)
        self.workers.append(len(firm.workers))
        row.append(len(firm.workers))
        with open(self.output, "a", newline='') as output_file:
            writer = csv.writer(output_file, dialect='excel')
            writer.writerow(row)



