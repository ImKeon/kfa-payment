from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
import time
import requests
from xml.etree.ElementTree import Element, tostring, SubElement, fromstring
from pydantic import BaseModel
from datetime import datetime
from dateutil.relativedelta import relativedelta
import urllib.parse
import json
from success_page import HTML_CONTENT

app = FastAPI()


RETURN_URL = 'https://payment.kfachallenge.info/pay_return'
KFA_SERVER_URL = 'https://api.kfachallenge.info/api/v1/purchase/payment-complete'
THE_PAY_URL = 'https://messagepay.thepay.kr/thepay_if/ProcRequest.action'
# THE_PAY_URL='https://dev-messagepay.thepay.kr:7080/thepay_if/ProcRequest.action'
# RETURN_URL = 'https://222.237.25.210:8000/pay_return'
# KFA_SERVER_URL = 'https://api.kfachallenge.info/api/v1/purchase/payment-complete'


class PaymentBody(BaseModel):
    userId: str
    pwd: str
    memberId: int
    productName: str
    amount: int
    userName: str


@app.get("/")
async def healthCheck():
    return {"status": 'true'}


@app.post("/")
async def root(paymentBody: PaymentBody):
    # URL 정의
    url = THE_PAY_URL

    # Create the XML structure
    root = Element('root')

    reqhead = SubElement(root, 'reqhead')
    userinfo = SubElement(reqhead, 'userinfo', userid=f'{paymentBody.userId}', passwd=f'{paymentBody.pwd}')
    reqbody = SubElement(root, 'reqbody')
    request = SubElement(reqbody, 'request', method='pay_request')
    # get this dat
    now = datetime.now()
    # get one month later
    one_month_later = now + relativedelta(months=1)
    orderno = str(int(time.time() * 1000))
    data = SubElement(request, 'data',
                      orderno=orderno,  # 임의의 랜덤값으로 변경 가능
                      payusernm=f'{paymentBody.userName}',
                      usernm=f'{paymentBody.userName}',
                      paycardarr="",
                      custid=f'{paymentBody.memberId}',  # 유저 ID
                      paymethod="0000",  # 결제수단
                      payhpno="01071035464",  # 고객핸드폰번호
                      goodsnm=f'{paymentBody.productName}',  # 결제 상품 명
                      payrequestamt=f'{paymentBody.amount}',  # 결제 요청 금액
                      payclosedt=f'{one_month_later}',  # 결제 마감 기간
                      birthdate="1993-07-11",
                      smssendyn="N",  # 문자(카톡) 발송이 필요할때 "Y"
                      imsyn="N",  # IMS 링크 사용 여부
                      payitemnm1="",  # 결제 요청 상세 항목 명칭
                      payitemamt1="",  # 결제 요청 상세 항목 금액
                      etcremark="기타사항",
                      telno="070-753-0103",  # 연락처
                      mediatype="MC02",  # MC01 -> PC 결제, MC02 -> 스마트폰 결제
                      returnurl=f'{RETURN_URL}',
                      # productitems='eyJwcm9kdWN0aXRlbXMiOiBbeyAgICAiY2F0ZWdvcnl0eXBlIjogIkVUQyIsICAgICJjYXRlZ29yeWlkIiA6ICJFVEMiLCAgICAidWlkIiA6ICIxMjM0IiwgICAgIm5hbWUiIDogInRlc3QiLCAgICAicGF5cmVmZXJyZXIiIDogIkVUQyIsICAgICJjb3VudCIgOiAxICB9LCB7ICAgICJjYXRlZ29yeXR5cGUiOiAiRVRDIiwgICAgImNhdGVnb3J5aWQiIDogIkVUQyIsICAgICJ1aWQiIDogIjQ1NjciLCAgICAibmFtZSIgOiAidGVzdDIiLCAgICAicGF5cmVmZXJyZXIiIDogIkVUQyIsICAgICJjb3VudCIgOiAyICB9XX0=',
                      complexpayyn='Y')

    # Convert the XML to string
    xml_body = tostring(root, encoding='utf-8').decode('utf-8')

    # Set the headers
    headers = {'Content-Type': 'application/xml'}

    # Send the POST request
    response = requests.post(url, data=xml_body, headers=headers)

    # Print the response
    if (response.status_code == 200):
        print(f'Response Is {response.text}')
        # Parse the response XML
        response_xml = fromstring(response.text)

        # Extract the payurl
        payurl = response_xml.find(".//data").attrib.get("payurl")

        return {
            "payUrl": f'{payurl}',
            "orderno": f'{orderno}'
        }


@app.post("/pay_return")
async def pay_return(request: Request):
    try:
        body = await request.body()
        body_query = body.decode("utf-8")
        parsed_dict = urllib.parse.parse_qs(body_query)
        parsed_dict = {k: v[0] for k, v in parsed_dict.items()}
        json_string = json.dumps(parsed_dict, ensure_ascii=False, indent=4)
        url = f'{KFA_SERVER_URL}'
        print(f'Server Url : {KFA_SERVER_URL} Reqeust Body : {json_string}')
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, data=json_string, headers=headers)
        print(f'Response Is {response.text}')
        # response_data = response.json()
        return response
    except Exception as e:
        print(f'Server Error IS {e}')
        print(f'Server Url : {KFA_SERVER_URL}')
        body = await request.body()
        body_query = body.decode("utf-8")
        print(f'Reqeust Body : {body_query}')
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/pay_return")
async def pay_return_get(request: Request):
    return HTMLResponse(content=HTML_CONTENT)
