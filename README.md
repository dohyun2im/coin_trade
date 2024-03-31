## 자동매매 구성
- 3일 이동평균을 구함.
- 넘을 경우 구매.
- 0.25% 이익이 있을 경우 판매. (수수료 제외 0.15%)
- 반복

## 실행 방법
- brew install python
- python3 -m venv test
- source test/bin/activate
- pip install python-dotenv requests pyupbit
- python3 test.py

## env 파일 구성
```
UPBIT_ACCESS_KEY=
UPBIT_SECRET_KEY=
SLACK_TOKEN=
```

- [Slack API 공식 문서](https://api.slack.com/apps)
- [Upbit API 안내](https://upbit.com/service_center/open_api_guide)
- [pyupbit Github](https://github.com/sharebook-kr/pyupbit)
