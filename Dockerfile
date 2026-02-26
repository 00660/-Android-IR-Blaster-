FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir flask flask-cors requests

COPY ir_decoder_service.py .
COPY libirdecode_jni_1.5.2_x86_64.so .

EXPOSE 8082

CMD ["python", "ir_decoder_service.py"]
