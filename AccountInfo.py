class AccountInfo:

    def __init__(self, input_dict: dict):
        self.mpan = input_dict["account"]["properties"][0]["electricityMeterPoints"][0]["mpan"]
        self.electricity_register = input_dict["account"]["properties"][0]["electricityMeterPoints"][0]["meters"][0]["registers"][0]["identifier"]
        self.electricity_meter_serial = input_dict["account"]["properties"][0]["electricityMeterPoints"][0]["meters"][0]["serialNumber"]
        self.mprn = input_dict["account"]["properties"][0]["gasMeterPoints"][0]["mprn"]
        self.gas_meter_serial = input_dict["account"]["properties"][0]["gasMeterPoints"][0]["meters"][0]["serialNumber"]

    def __repr__(self):
        return f"""
    Electricity:
        MPAN: {self.mpan}
        Meter serial: {self.electricity_meter_serial}
        Register ID: {self.electricity_register}
    Gas:        
        MPRN: {self.mprn}
        Meter serial: {self.gas_meter_serial}
        """

