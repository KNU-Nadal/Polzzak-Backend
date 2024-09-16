# 베이스 이미지로 Python 3.12 사용
FROM python:3.12-slim

# 컨테이너 내에서 작업할 디렉토리를 설정
WORKDIR /app

# 로컬의 requirements.txt 파일을 컨테이너로 복사
COPY requirements.txt requirements.txt

# 필요한 파이썬 패키지 설치
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 파일을 컨테이너로 복사 및 압축 해제
COPY . .


# FLASK_APP 환경 변수를 설정
ENV FLASK_APP=polzzak

# Flask가 컨테이너 내부에서 실행될 때 0.0.0.0으로 바인딩되도록 설정
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5000

# 컨테이너에서 Flask 실행
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]