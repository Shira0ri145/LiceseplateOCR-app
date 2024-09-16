# ใช้ภาพพื้นฐานของ Python
FROM python:3.12.5

# ตั้งค่า directory ที่จะใช้ใน container
WORKDIR /code

# คัดลอกไฟล์ requirements.txt และติดตั้ง dependencies
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir -r /code/requirements.txt

# คัดลอกโค้ดของแอพพลิเคชันไปยัง container
COPY ./app /code/app

# เปิดพอร์ตที่ Uvicorn จะฟัง
EXPOSE 8000

# คำสั่งในการรันแอพพลิเคชันในโหมดพัฒนา
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
