# 🚀 نشر Text Site AI Extractor في Vercel

## 📋 المتطلبات

- حساب GitHub
- حساب Vercel
- مشروع GitHub يحتوي على الكود

## 🚀 خطوات النشر

### 1. رفع المشروع إلى GitHub

```bash
# تهيئة Git
git init

# إضافة الملفات
git add .

# أول commit
git commit -m "🚀 Initial commit: Advanced Arabic Text Extraction API"

# إضافة remote
git remote add origin https://github.com/Farouk568-f/text-site-ai-extractor.git

# رفع المشروع
git branch -M main
git push -u origin main
```

### 2. ربط المشروع بـ Vercel

1. **اذهب إلى [vercel.com](https://vercel.com)**
2. **سجل دخول بحساب GitHub**
3. **اضغط "New Project"**
4. **اختر المستودع `text-site-ai-extractor`**
5. **اضغط "Import"**

### 3. إعدادات Vercel

#### Build Settings:
- **Framework Preset**: Other
- **Build Command**: `pip install -r requirements-vercel.txt`
- **Output Directory**: `api`
- **Install Command**: `pip install -r requirements-vercel.txt`

#### Environment Variables:
```
FLASK_ENV=production
FLASK_APP=api/index.py
```

### 4. النشر

1. **اضغط "Deploy"**
2. **انتظر اكتمال البناء**
3. **احصل على الرابط**

## 🔧 هيكل الملفات لـ Vercel

```
text-site-ai-extractor/
├── api/
│   ├── index.py          # نقطة الدخول لـ Vercel
│   └── vercel.json       # إعدادات Vercel
├── article_api.py         # API الرئيسي
├── improved_text_extractor.py
├── requirements-vercel.txt # متطلبات Vercel
├── vercel.json            # إعدادات المشروع
└── runtime.txt            # إصدار Python
```

## 🌐 استخدام API

### بعد النشر في Vercel:

```python
import requests

# استخدام الرابط الجديد من Vercel
vercel_url = "https://your-project.vercel.app"

# البحث عن المقالات
payload = {
    "query": "أهمية الذكاء الاصطناعي",
    "min_length": 1000  # كما طلبت - محتوى كامل ونقي
}

response = requests.post(f"{vercel_url}/search-articles/", json=payload)
result = response.json()

print(f"عدد المقالات الناجحة: {result['successful_articles']}")
print(f"الحد الأدنى المستخدم: {result['min_length_used']}")
```

### استخراج نص من رابط واحد:

```python
payload = {
    "url": "https://sdaia.gov.sa/ar/SDAIA/about/Pages/AboutAI.aspx",
    "min_length": 1000
}

response = requests.post(f"{vercel_url}/extract-single/", json=payload)
result = response.json()

if result["status"] == "success":
    print(f"عدد الفقرات: {result['paragraphs_count']}")
    print(f"طول النص: {result['text_length']}")
    print(f"النص: {result['text'][:200]}...")
```

## 🛠️ استكشاف الأخطاء

### مشكلة: Build فشل
- تأكد من `requirements-vercel.txt`
- تأكد من `runtime.txt`
- تأكد من `api/index.py`

### مشكلة: API لا يستجيب
- تحقق من logs في Vercel
- تأكد من Environment Variables
- تحقق من Function Timeout

### مشكلة: Import Error
- تأكد من `sys.path.append` في `api/index.py`
- تأكد من وجود جميع الملفات

## 📊 مراقبة الأداء

### في Vercel Dashboard:
1. **Functions**: مراقبة استهلاك الوقت
2. **Analytics**: مراقبة الطلبات
3. **Logs**: مراقبة الأخطاء

## 🔄 التحديثات

### لتحديث المشروع:
```bash
git add .
git commit -m "Update: description"
git push origin main
```

Vercel سيقوم تلقائياً بإعادة النشر!

## 💡 نصائح مهمة

1. **استخدم `min_length: 1000` للحصول على محتوى كامل ونقي**
2. **تأكد من أن جميع المكتبات موجودة في `requirements-vercel.txt`**
3. **راقب Function Timeout (30 ثانية)**
4. **استخدم Environment Variables للمتغيرات الحساسة**

## 🌟 الميزات المتاحة

- ✅ `/search-articles/` - البحث عن المقالات
- ✅ `/extract-single/` - استخراج نص من رابط واحد
- ✅ `/health` - فحص صحة API
- ✅ إزالة التكرارات تلقائياً
- ✅ فلترة المحتوى المتقدمة
- ✅ خيارات قابلة للتخصيص

---

**🎉 مبروك! API يعمل الآن في Vercel!**
