import datetime
import csv

class WorldHistory:
    def __init__(self, output = "world_output.csv"):
        self.output = output
        self.step = []
        self.date = datetime.datetime.now().isoformat()
        for type in ['raw_', 'capital_', 'production_','']:
            for variable in ['price', 'salary', 'sold', 'stock', 'sales', 'money', 'employed', 'labor_capacity', 'total_salary', 'salary_budget']:
                setattr(self, type + variable, [])
        self.unemployment_rate = []
        for type in ['raw', 'capital']:
            for variable in ['', '_need', '_budget', '_expenses']:
                setattr(self, type + variable, [])
        self.firms = []
        self.raw_firms = []
        self.capital_firms = []
        self.production_firms = []
        self.households = []
        self.expected_sales_growth = []
        self.expected_sold_growth = []

        try:
            open(self.output, "r")
        except:
            output_file = open(self.output, "w", newline='')
            writer = csv.DictWriter(output_file, dialect = 'excel',
                                    fieldnames=['date', 'step', 'firms', 'raw_firms', 'capital_firms', 'production_firms',
                                                'households', 'price', 'raw_price', 'capital_price', 'production_price',
                                                'salary', 'raw_salary', 'capital_salary', 'production_salary',
                                                'sold', 'raw_sold', 'capital_sold', 'production_sold',
                                                'stock', 'raw_stock', 'capital_stock', 'production_stock',
                                                'sales', 'raw_sales', 'capital_sales', 'production_sales',
                                                'money', 'raw_money', 'capital_money', 'production_money',
                                                'employed', 'raw_employed', 'capital_employed', 'production_employed',
                                                'labor_capacity', 'raw_labor_capacity', 'capital_labor_capacity', 'production_labor_capacity',
                                                'total_salary', 'raw_total_salary', 'capital_total_salary', 'production_total_salary',
                                                'salary_budget', 'raw_salary_budget', 'capital_salary_budget',
                                                'production_salary_budget', 'unemployment_rate',
                                                'raw', 'raw_need', 'raw_budget', 'raw_expenses',
                                                'capital', 'capital_need', 'capital_budget', 'capital_expenses',
                                                'expected_sales_growth', 'expected_sold_growth'
                                                ])
            writer.writeheader()
            output_file.close()

    def add_record(self, stats):
        for variable, value in stats.__dict__.items():
            if hasattr(self, variable):
                getattr(self, variable).append(value)
        with open(self.output, "a", newline='') as output_file:
            writer = csv.DictWriter(output_file, dialect = 'excel', fieldnames = ['date', 'step', 'firms', 'raw_firms',
                                                                                'capital_firms', 'production_firms',
                                                'households', 'price', 'raw_price', 'capital_price', 'production_price',
                                                'salary', 'raw_salary', 'capital_salary', 'production_salary',
                                                'sold', 'raw_sold', 'capital_sold', 'production_sold',
                                                'stock', 'raw_stock', 'capital_stock', 'production_stock',
                                                'sales', 'raw_sales', 'capital_sales', 'production_sales',
                                                'money', 'raw_money', 'capital_money', 'production_money',
                                                'employed', 'raw_employed', 'capital_employed', 'production_employed',
                                                'labor_capacity', 'raw_labor_capacity', 'capital_labor_capacity', 'production_labor_capacity',
                                                'total_salary', 'raw_total_salary', 'capital_total_salary', 'production_total_salary',
                                                'salary_budget', 'raw_salary_budget', 'capital_salary_budget',
                                                'production_salary_budget', 'unemployment_rate',
                                                'raw', 'raw_need', 'raw_budget', 'raw_expenses',
                                                'capital', 'capital_need', 'capital_budget', 'capital_expenses',
                                                'expected_sales_growth', 'expected_sold_growth'
                                                ])
            writer.writerow({**stats.__dict__, **{'date': self.date}})

