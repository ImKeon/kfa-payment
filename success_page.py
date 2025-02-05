HTML_CONTENT = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>결제 성공</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f4f4f4;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
            }
            .container {
                background-color: #fff;
                padding: 60px 40px;
                border-radius: 20px;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
                max-width: 400px;
                width: 90%;
                text-align: center;
                display: flex;
                flex-direction: column;
                justify-content: center;
                min-height: 450px;
            }
            .circle {
                width: 120px; /* 동그라미 크기 */
                height: 120px; /* 동그라미 크기 */
                margin: 0 auto 30px;
                border-radius: 50%;
                background-color: #007BFF; /* 파란색 */
                display: flex;
                justify-content: center;
                align-items: center;
                position: relative;
            }
            .checkmark {
                font-size: 90px; /* 체크 아이콘 크기 */
                color: #fff;
                position: absolute;
                top: 50%; /* 동그라미의 정중앙 */
                transform: translateY(-45%); /* 약간 아래로 내림 */
            }
            h1 {
                font-size: 24px;
                color: #333;
                margin: 10px 0;
            }
            .back-button {
                display: inline-block;
                margin-top: 30px;
                padding: 12px 25px;
                font-size: 18px;
                color: #fff;
                text-decoration: none;
                background-color: #007BFF;
                border: none;
                border-radius: 5px;
                transition: background-color 0.3s, color 0.3s;
                cursor: pointer;
            }
            .back-button:hover {
                background-color: #0056b3;
            }
        </style>
        <script>
            function closeWindow() {
                window.close();
            }
    
            // 1초 후 창 강제 닫기
            setTimeout(function() {
                window.close();
            }, 1000);
        </script>
    </head>
    <body>
        <div class="container">
            <div class="circle">
                <div class="checkmark">✓</div>
            </div>
            <h1>결제에 성공하였습니다</h1>
            <button class="back-button" onclick="closeWindow()">돌아가기</button>
        </div>
    </body>
    </html>
    """