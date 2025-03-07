import aiohttp
from fastapi import FastAPI, Request, HTTPException, Body, Form
from fastapi.responses import HTMLResponse
import time
import requests
from xml.etree.ElementTree import Element, tostring, SubElement, fromstring, ElementTree, ParseError
from pydantic import BaseModel
from datetime import datetime
from dateutil.relativedelta import relativedelta
import urllib.parse
import json
import logging

from payment_model import Payment
from success_page import HTML_CONTENT

import aiomysql
import asyncio

app = FastAPI()


# <Prod>
# FANTASY_RETURN_URL = 'https://payment.kfachallenge.info/fantasy-return'
# FANTASY_SERVER_URL = 'https://api.kleaguefantasy.com/api/v1/member/point/fantasy'

RETURN_URL = 'https://payment.kfachallenge.info/pay_return'
KFA_SERVER_URL = 'https://api.kfachallenge.info/api/v1/purchase/payment-complete'
KFA_SERVER_URL_V2 = 'https://api.kfachallenge.info/api/v1/purchase/payment-complete-v2'
THE_PAY_URL = 'https://messagepay.thepay.kr/thepay_if/ProcRequest.action'
API_KEY = 'da2-cggjypn5wvflfjfaixnbc7vhfy'
GRAPH_END = 'https://fxzd5ujmmrfhtcpenoanjcaooi.appsync-api.ap-northeast-2.amazonaws.com/graphql'

# <Dev>
FANTASY_RETURN_URL = 'https://payment.kfachallenge.info/fantasy-return'
FANTASY_SERVER_URL_T = 'https://api-dev.kleaguefantasy.com/api/v1/member/point/fantasy'
FANTASY_SERVER_URL = 'https://api-v2.kleaguefantasy.com/api/v1/member/point/fantasy'

# RETURN_URL = 'https://222.237.25.210:8000/pay_return'
# KFA_SERVER_URL = 'http://222.237.25.210:8080/api/v1/purchase/payment-complete'
# THE_PAY_URL='https://dev-messagepay.thepay.kr:7080/thepay_if/ProcRequest.action'


DB_CONFIG = {
    "host": "with-common.cz4y4tgkfy2i.ap-northeast-2.rds.amazonaws.com",
    "user": "admin",
    "password": "dnlemdlfqks!",
    "db": "with-payment",
    "port": 3306
}


async def get_db_connection():
    return await aiomysql.connect(
        host=DB_CONFIG["host"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        db=DB_CONFIG["db"],
        port=DB_CONFIG["port"],
        autocommit=True
    )


class PaymentBody(BaseModel):
    userId: str
    pwd: str
    memberId: int
    productName: str
    amount: int
    userName: str


class FantasyPaymentBody(BaseModel):
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
                      orderno=f'kfa-{orderno}',  # 임의의 랜덤값으로 변경 가능
                      payusernm=f'{paymentBody.userName}',
                      usernm=f'{paymentBody.userName}',
                      paycardarr="",
                      custid=f'{paymentBody.memberId}',  # 유저 ID
                      paymethod="0000",  # 결제수단
                      payhpno="01047871844",  # 고객핸드폰번호
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
                      # returnurl=f'{RETURN_URL}',
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
            "orderno": f'kfa-{orderno}'
        }


@app.post("/fantasy-test/{device_type}")
async def fantasy_test(device_type: str, paymentBody: FantasyPaymentBody):
    device_type = device_type.lower()
    paymethod = "0000"
    mediatype = "MC02"
    if device_type == "mobile":
        paymethod = "0000"
        mediatype = "MC02"
    elif device_type == "pc":
        paymethod = "0019"
        mediatype = "MC01"
    else:
        paymethod = "0000"


    user_id = '7788701253@288'
    pwd = '7110eda4d09e062aa5e4a390b0a572ac0d2c0220'
    # URL 정의
    url = THE_PAY_URL

    # Create the XML structure
    root = Element('root')

    reqhead = SubElement(root, 'reqhead')
    userinfo = SubElement(reqhead, 'userinfo', userid=f'{user_id}', passwd=f'{pwd}')
    reqbody = SubElement(root, 'reqbody')
    request = SubElement(reqbody, 'request', method='pay_request')
    # get this dat
    now = datetime.now()
    # get one month later
    one_month_later = now + relativedelta(months=1)
    orderno = str(int(time.time() * 1000))
    data = SubElement(request, 'data',
                      orderno=f'fantasy-{orderno}',  # 임의의 랜덤값으로 변경 가능
                      payusernm=f'{paymentBody.userName}',
                      usernm=f'{paymentBody.userName}',
                      paycardarr="",
                      custid=f'{paymentBody.memberId}',  # 유저 ID
                      paymethod=paymethod,  # 결제수단
                      payhpno="01047871844",  # 고객핸드폰번호
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
                      mediatype=mediatype,  # MC01 -> PC 결제, MC02 -> 스마트폰 결제
                      # returnurl=f'{FANTASY_RETURN_URL}',
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
            "orderno": f't-f-{orderno}'
        }


@app.post("/fantasy/{device_type}")
async def fantasy(device_type: str, paymentBody: FantasyPaymentBody):
    device_type = device_type.lower()
    paymethod = "0000"
    mediatype = "MC02"
    if device_type == "mobile":
        paymethod = "0000"
        mediatype = "MC02"
    elif device_type == "pc":
        paymethod = "0019"
        mediatype = "MC01"
    else:
        paymethod = "0000"


    user_id = '7788701253@288'
    pwd = '7110eda4d09e062aa5e4a390b0a572ac0d2c0220'
    # URL 정의
    url = THE_PAY_URL

    # Create the XML structure
    root = Element('root')

    reqhead = SubElement(root, 'reqhead')
    userinfo = SubElement(reqhead, 'userinfo', userid=f'{user_id}', passwd=f'{pwd}')
    reqbody = SubElement(root, 'reqbody')
    request = SubElement(reqbody, 'request', method='pay_request')
    # get this dat
    now = datetime.now()
    # get one month later
    one_month_later = now + relativedelta(months=1)
    orderno = str(int(time.time() * 1000))
    data = SubElement(request, 'data',
                      orderno=f'fantasy-{orderno}',  # 임의의 랜덤값으로 변경 가능
                      payusernm=f'{paymentBody.userName}',
                      usernm=f'{paymentBody.userName}',
                      paycardarr="",
                      custid=f'{paymentBody.memberId}',  # 유저 ID
                      paymethod=paymethod,  # 결제수단
                      payhpno="01047871844",  # 고객핸드폰번호
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
                      mediatype=mediatype,  # MC01 -> PC 결제, MC02 -> 스마트폰 결제
                      # returnurl=f'{FANTASY_RETURN_URL}',
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
            "orderno": f'fantasy-{orderno}'
        }

@app.post("/fantasy-return")
async def fantasy_pay_return(request: Request):
    try:
        body = await request.body()
        body_query = body.decode("utf-8")
        parsed_dict = urllib.parse.parse_qs(body_query)
        parsed_dict = {k: v[0] for k, v in parsed_dict.items()}
        json_string = json.dumps(parsed_dict, ensure_ascii=False, indent=4)
        url = f'{FANTASY_RETURN_URL}'
        print(f'Server Url : {FANTASY_RETURN_URL} Reqeust Body : {json_string}')
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, data=json_string, headers=headers)
        print(f'Response Is {response.text}')
        # response_data = response.json()
        return HTMLResponse(content=HTML_CONTENT)
    except Exception as e:
        print(f'Server Error IS {e}')
        print(f'Server Url : {KFA_SERVER_URL}')
        body = await request.body()
        body_query = body.decode("utf-8")
        print(f'Reqeust Body : {body_query}')
        raise HTTPException(status_code=400, detail=str(e))



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
        return HTMLResponse(content=HTML_CONTENT)
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


@app.post("/amplify-upload")
async def amplify_upload_post(payment: Payment):
    query = """
        mutation createPAYMENT($input: CreatePAYMENTInput!) {
            createPAYMENT(input: $input) {
                result_code
                result_msg
                result_payno
                issuenm
                payment
                payno
                status
                vanuniquekey
            }
        }
        """
    variables = {
        "input": payment.dict()
    }
    print(payment.dict)
    headers = {
        "x-api-key": API_KEY,
        "Content-Type": "application/json"
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(GRAPH_END, json={"query": query, "variables": variables}, headers=headers) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            result = await response.json()
            return result
    return 1


@app.post("/in-app/ios")
async def in_app_test(request: Request):
    body = await request.body()
    print(f'Apple In App Purchase {body}')
    return HTMLResponse(content=HTML_CONTENT)


@app.post("/pay-call-back")
async def pay_call_back(reqxml: str = Form(...)):
    logging.info("💰 pay_call_back start")

    try:
        # URL 디코딩 (만약 URL 인코딩된 XML이 들어오면 디코딩 처리)
        decoded_xml = urllib.parse.unquote(reqxml)
        logging.info(f"📩 Received Encoded XML: {reqxml}")
        logging.info(f"📩 Decoded XML: {decoded_xml}")

        # XML 파싱
        root = fromstring(decoded_xml)

        # <userinfo> 태그에서 userid, passwd 가져오기
        user_info = root.find(".//userinfo")
        if user_info is None:
            logging.error("🚨 No 'userinfo' tag found in XML")
            return {"status": "error", "message": "No 'userinfo' tag found in XML"}
        user_data = user_info.attrib

        # <data> 태그에서 결제 정보 가져오기 (여러 개의 <data> 태그 지원)
        data_nodes = root.findall(".//data")
        if not data_nodes:
            logging.error("🚨 No 'data' tag found in XML")
            return {"status": "error", "message": "No 'data' tag found in XML"}

        conn = await get_db_connection()

        results = []
        for data_node in data_nodes:
            orderno = data_node.attrib.get("orderno")
            if not orderno:
                logging.warning("⚠️ No orderno found in XML, skipping...")
                continue  # orderno 없는 경우 무시

            # MySQL에 요청 기록 저장
            async with conn.cursor() as cur:
                await cur.execute("""
                        INSERT INTO payments_log (orderno, request_time, processed) 
                        VALUES (%s, NOW(), FALSE);
                    """, (orderno,))

            # 데이터 변환 및 API 요청
            data_dict = data_node.attrib
            data_dict.update(user_data)  # userid, passwd 추가

            if "partcanc_yn" in data_dict:
                data_dict["partcancyn"] = data_dict.pop("partcanc_yn")  # 필드명 변경

            # JSON 변환
            pay_data = PayData(**data_dict)
            json_data = pay_data.model_dump()

            # API 요청 보내기
            if "fantasy" in pay_data.orderno:
                logging.info(f"🏆 Sending Fantasy API request for order: {orderno}")
                response = requests.post(FANTASY_SERVER_URL, json=json_data)
            elif "t-f" in pay_data.orderno:
                logging.info(f"📢 Sending Fantasy Test API request for order: {orderno}")
                response = requests.post(FANTASY_SERVER_URL_T, json=json_data)
            else:
                logging.info(f"⚽ Sending KFA API request for order: {orderno}")
                response = requests.post(KFA_SERVER_URL_V2, json=json_data)

            logging.info(f"✅ API Response for order {orderno}: {response.text}")

            # 요청이 성공하면 processed 상태 업데이트
            async with conn.cursor() as cur:
                await cur.execute("""
                        UPDATE payments_log SET processed = TRUE WHERE orderno = %s
                    """, (orderno,))

            results.append({"orderno": orderno, "response": response.json()})

        await conn.ensure_closed()
        return {"status": "success", "processed_orders": results}

    except ParseError as parse_error:
        logging.error(f"🚨 XML parsing error: {str(parse_error)}")
        return {"status": "error", "message": f"XML parsing error: {str(parse_error)}"}

    except requests.RequestException as request_error:
        logging.error(f"🚨 Request error: {str(request_error)}")
        return {"status": "error", "message": f"Request error: {str(request_error)}"}

    except Exception as e:
        logging.error(f"🚨 Unexpected error: {str(e)}")
        return {"status": "error", "message": f"Unexpected error: {str(e)}"}


# Pydantic 데이터 모델
class PayData(BaseModel):
    userid: str
    passwd: str
    payno: str
    orderno: str
    seq: str
    respcd: str
    resptext: str
    paymethod: str
    paytype: str
    custmessage: str
    cardcd: str
    cardnm: str
    payrequestamt: str
    payamt: str
    status: str
    approvaltype: str
    approvaldt: str
    approvalno: str
    canceldt: str
    installmonth: str
    vanuniquekey: str
    cardbintype01: str
    cardbintype02: str
    partcancyn: str  # 기존 partcanc_yn 필드를 매핑하여 수정
    useretc1: str
    useretc2: str
    useretc3: str
    outerkey1: str
    outerkey2: str

