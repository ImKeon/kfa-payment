from fastapi import FastAPI
import time
import requests
from xml.etree.ElementTree import Element, tostring, SubElement, fromstring
from pydantic import BaseModel

app = FastAPI()


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
    url = "https://dev-messagepay.thepay.kr:7080/thepay_if/ProcRequest.action"

    # Create the XML structure
    root = Element('root')

    reqhead = SubElement(root, 'reqhead')
    # weright, 7110eda4d09e062aa5e4a390b0a572ac0d2c0220
    userinfo = SubElement(reqhead, 'userinfo', userid=f'{paymentBody.userId}', passwd=f'{paymentBody.pwd}')

    reqbody = SubElement(root, 'reqbody')
    request = SubElement(reqbody, 'request', method='pay_request')

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
                      payclosedt="2024-07-21",  # 결제 마감 기간
                      birthdate="1993-07-11",
                      smssendyn="N",  # 문자(카톡) 발송이 필요할때 "Y"
                      imsyn="N",  # IMS 링크 사용 여부
                      payitemnm1="",  # 결제 요청 상세 항목 명칭
                      payitemamt1="",  # 결제 요청 상세 항목 금액
                      etcremark="기타사항",
                      telno="070-753-0103",  # 연락처
                      mediatype="MC02",  # MC01 -> PC 결제, MC02 -> 스마트폰 결제
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
        # Parse the response XML
        response_xml = fromstring(response.text)

        # Extract the payurl
        payurl = response_xml.find(".//data").attrib.get("payurl")

        # Print the payurl
        print(payurl)
        return {
            "payUrl": f'{payurl}',
            "orderno": f'{orderno}'
        }
