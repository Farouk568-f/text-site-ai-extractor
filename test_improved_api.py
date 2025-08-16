# -*- coding: utf-8 -*-
"""
ملف اختبار لـ API المحسن لاستخراج النص من المقالات
"""

import requests
import json

# رابط API المحسن
API_BASE_URL = "http://localhost:5001"

def test_search_articles():
    """
    اختبار نقطة النهاية /search-articles/ مع خيارات مختلفة للحد الأدنى
    """
    print("🔍 اختبار البحث عن المقالات...")
    
    # اختبار 1: الحد الأدنى الافتراضي (100)
    print("\n📝 الاختبار 1: الحد الأدنى الافتراضي (100)")
    payload1 = {
        "query": "أهمية الذكاء الاصطناعي"
    }
    
    try:
        response1 = requests.post(f"{API_BASE_URL}/search-articles/", json=payload1)
        if response1.status_code == 200:
            result1 = response1.json()
            print(f"✅ نجح الاختبار 1")
            print(f"   الحد الأدنى المستخدم: {result1.get('min_length_used', 'غير محدد')}")
            print(f"   عدد المقالات الناجحة: {result1.get('successful_articles', 0)}")
            print(f"   عدد المقالات الفاشلة: {result1.get('failed_articles', 0)}")
            
            # عرض عينة من النص
            if result1.get('results'):
                first_result = result1['results'][0]
                if first_result.get('status') == 'success':
                    text_sample = first_result.get('text', '')[:200]
                    print(f"   عينة من النص: {text_sample}...")
        else:
            print(f"❌ فشل الاختبار 1: {response1.status_code}")
            print(f"   الخطأ: {response1.text}")
    except Exception as e:
        print(f"❌ خطأ في الاختبار 1: {e}")
    
    # اختبار 2: الحد الأدنى 1000 (كما طلبت)
    print("\n📝 الاختبار 2: الحد الأدنى 1000 (محتوى كامل ونقي)")
    payload2 = {
        "query": "أهمية الذكاء الاصطناعي",
        "min_length": 1000
    }
    
    try:
        response2 = requests.post(f"{API_BASE_URL}/search-articles/", json=payload2)
        if response2.status_code == 200:
            result2 = response2.json()
            print(f"✅ نجح الاختبار 2")
            print(f"   الحد الأدنى المستخدم: {result2.get('min_length_used', 'غير محدد')}")
            print(f"   عدد المقالات الناجحة: {result2.get('successful_articles', 0)}")
            print(f"   عدد المقالات الفاشلة: {result2.get('failed_articles', 0)}")
            
            # عرض عينة من النص
            if result2.get('results'):
                first_result = result2['results'][0]
                if first_result.get('status') == 'success':
                    text_sample = first_result.get('text', '')[:300]
                    print(f"   عينة من النص: {text_sample}...")
        else:
            print(f"❌ فشل الاختبار 2: {response2.status_code}")
            print(f"   الخطأ: {response2.text}")
    except Exception as e:
        print(f"❌ خطأ في الاختبار 2: {e}")
    
    # اختبار 3: الحد الأدنى 2000 (محتوى طويل جداً)
    print("\n📝 الاختبار 3: الحد الأدنى 2000 (محتوى طويل جداً)")
    payload3 = {
        "query": "أهمية الذكاء الاصطناعي",
        "min_length": 2000
    }
    
    try:
        response3 = requests.post(f"{API_BASE_URL}/search-articles/", json=payload3)
        if response3.status_code == 200:
            result3 = response3.json()
            print(f"✅ نجح الاختبار 3")
            print(f"   الحد الأدنى المستخدم: {result3.get('min_length_used', 'غير محدد')}")
            print(f"   عدد المقالات الناجحة: {result3.get('successful_articles', 0)}")
            print(f"   عدد المقالات الفاشلة: {result3.get('failed_articles', 0)}")
            
            # عرض عينة من النص
            if result3.get('results'):
                first_result = result3['results'][0]
                if first_result.get('status') == 'success':
                    text_sample = first_result.get('text', '')[:400]
                    print(f"   عينة من النص: {text_sample}...")
        else:
            print(f"❌ فشل الاختبار 3: {response3.status_code}")
            print(f"   الخطأ: {response3.text}")
    except Exception as e:
        print(f"❌ خطأ في الاختبار 3: {e}")

def test_extract_single():
    """
    اختبار نقطة النهاية /extract-single/ مع خيارات مختلفة
    """
    print("\n🔍 اختبار استخراج نص من رابط واحد...")
    
    test_url = "https://sdaia.gov.sa/ar/SDAIA/about/Pages/AboutAI.aspx"
    
    # اختبار 1: الحد الأدنى 100
    print("\n📝 الاختبار 1: الحد الأدنى 100")
    payload1 = {
        "url": test_url,
        "min_length": 100
    }
    
    try:
        response1 = requests.post(f"{API_BASE_URL}/extract-single/", json=payload1)
        if response1.status_code == 200:
            result1 = response1.json()
            if result1.get('status') == 'success':
                print(f"✅ نجح الاختبار 1")
                print(f"   عدد الفقرات: {result1.get('paragraphs_count', 0)}")
                print(f"   طول النص: {result1.get('text_length', 0)}")
                text_sample = result1.get('text', '')[:200]
                print(f"   عينة من النص: {text_sample}...")
            else:
                print(f"❌ فشل في استخراج النص: {result1.get('error', 'خطأ غير معروف')}")
        else:
            print(f"❌ فشل الاختبار 1: {response1.status_code}")
            print(f"   الخطأ: {response1.text}")
    except Exception as e:
        print(f"❌ خطأ في الاختبار 1: {e}")
    
    # اختبار 2: الحد الأدنى 1000
    print("\n📝 الاختبار 2: الحد الأدنى 1000")
    payload2 = {
        "url": test_url,
        "min_length": 1000
    }
    
    try:
        response2 = requests.post(f"{API_BASE_URL}/extract-single/", json=payload2)
        if response2.status_code == 200:
            result2 = response2.json()
            if result2.get('status') == 'success':
                print(f"✅ نجح الاختبار 2")
                print(f"   عدد الفقرات: {result2.get('paragraphs_count', 0)}")
                print(f"   طول النص: {result2.get('text_length', 0)}")
                text_sample = result2.get('text', '')[:300]
                print(f"   عينة من النص: {text_sample}...")
            else:
                print(f"❌ فشل في استخراج النص: {result2.get('error', 'خطأ غير معروف')}")
        else:
            print(f"❌ فشل الاختبار 2: {response2.status_code}")
            print(f"   الخطأ: {response2.text}")
    except Exception as e:
        print(f"❌ خطأ في الاختبار 2: {e}")

def test_health_check():
    """
    اختبار نقطة النهاية /health
    """
    print("\n🔍 اختبار فحص صحة API...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ API يعمل بشكل صحيح")
            print(f"   الحالة: {result.get('status', 'غير معروف')}")
            print(f"   الرسالة: {result.get('message', 'غير معروف')}")
            print(f"   الميزات: {', '.join(result.get('features', []))}")
        else:
            print(f"❌ فشل في فحص صحة API: {response.status_code}")
            print(f"   الخطأ: {response.text}")
    except Exception as e:
        print(f"❌ خطأ في فحص صحة API: {e}")

def main():
    """
    الدالة الرئيسية لاختبار جميع النقاط النهائية
    """
    print("🚀 بدء اختبار API المحسن لاستخراج النص من المقالات...")
    print("=" * 70)
    
    # اختبار فحص صحة API
    test_health_check()
    
    # اختبار البحث عن المقالات
    test_search_articles()
    
    # اختبار استخراج نص من رابط واحد
    test_extract_single()
    
    print("\n" + "=" * 70)
    print("✅ انتهى الاختبار!")
    print("\n💡 ملاحظات:")
    print("   - الحد الأدنى 100: يحصل على محتوى قصير")
    print("   - الحد الأدنى 1000: يحصل على محتوى كامل ونقي (كما طلبت)")
    print("   - الحد الأدنى 2000: يحصل على محتوى طويل جداً")
    print("\n🔧 لتشغيل API:")
    print("   python article_api.py")

if __name__ == "__main__":
    main()
