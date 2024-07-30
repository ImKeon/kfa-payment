from pydantic import BaseModel


class Payment(BaseModel):
    # id: str
    result_code: str = None
    result_msg: str = None
    result_payno: str = None
    issuenm: str = None
    payment: str = None
    payno: str = None
    status: str = None
    vanuniquekey: str = None