class Vacation:
    def __init__(self,  vacation_id: int, country_id:int, desc: str, start_date: str, end_date: str, price: float, pic_name: str):
        self.vacation_id = vacation_id
        self.country_id = country_id
        self.desc = desc
        self.start_date = start_date
        self.end_date = end_date
        self.price = price
        self.pic_name = pic_name