class HolidaysData:
    def __init__(self, nume, data, tip):
        self.nume = nume
        self.data = data
        self.tip = tip

    def __str__(self):
        return f"Holiday: {self.nume}, Date: {self.data}, Type: {self.tip}"