import requests
import time

# رابط API
api_url = "http://localhost:8000/extract"

# رابط المقال المراد استخراجه
article_url = "https://www.bbc.com/news/articles/ce836yz8r69o"


payload = {
    "url": article_url,
    "format": "txt",
    "body_width": 500
}

# إنشاء المهمة
response = requests.post(api_url, json=payload)
if response.status_code == 202:
    task_data = response.json()
    task_id = task_data['task_id']
    print("تم إنشاء المهمة، task_id:", task_id)
else:
    print("خطأ أثناء إنشاء المهمة:", response.text)
    exit()

status_url = f"http://localhost:8000/task-status/{task_id}"
result_url = f"http://localhost:8000/task-result/{task_id}"

while True:
    status_response = requests.get(status_url)
    status_data = status_response.json()  # هذا قاموس
    status = status_data.get("status")    # نأخذ قيمة "status" من القاموس

    if status is None:
        print("تعذر الحصول على حالة المهمة")
        break

    if status.lower() in ["completed", "done"]:
        break

    print("المهمة جاري تنفيذها... ننتظر 2 ثانية")
    time.sleep(2)

# استرجاع النتيجة
result_response = requests.get(result_url)
if result_response.status_code == 200:
    article_text = result_response.json()
    print("\nمحتوى المقال:\n")
    print(article_text)
else:
    print("حدث خطأ أثناء استرجاع النتيجة:", result_response.status_code)
