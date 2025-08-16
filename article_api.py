# -*- coding: utf-8 -*-
"""
API محسن لاستخراج النص من المقالات العربية
يحتوي على دوال محسنة لإزالة التكرارات والمحتوى غير المرغوب
"""

import re
import difflib
import requests
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify
from flask_cors import CORS
import time
import uuid

app = Flask(__name__)
CORS(app)

# تخزين المهام
tasks = {}

def remove_duplicate_content(text: str) -> str:
    """
    إزالة المحتوى المكرر والمتكرر من النص
    """
    if not text:
        return ""
    
    # تقسيم النص إلى فقرات
    paragraphs = text.split('\n\n')
    
    # إزالة الفقرات الفارغة
    paragraphs = [p.strip() for p in paragraphs if p.strip()]
    
    # إزالة الفقرات المتكررة باستخدام خوارزمية ذكية
    unique_paragraphs = []
    seen_paragraphs = set()
    
    for paragraph in paragraphs:
        if len(paragraph) < 50:  # تجاهل الفقرات القصيرة جداً
            continue
            
        # تنظيف الفقرة
        clean_paragraph = re.sub(r'\s+', ' ', paragraph.strip())
        
        # حساب التشابه مع الفقرات السابقة
        is_duplicate = False
        for seen in seen_paragraphs:
            # استخدام خوارزمية تشابه النص
            similarity = difflib.SequenceMatcher(None, clean_paragraph, seen).ratio()
            if similarity > 0.7:  # إذا كان التشابه أكثر من 70%
                is_duplicate = True
                break
        
        if not is_duplicate:
            unique_paragraphs.append(paragraph)
            seen_paragraphs.add(clean_paragraph)
    
    return '\n\n'.join(unique_paragraphs)

def filter_content_quality(text: str) -> str:
    """
    فلترة جودة المحتوى وإزالة النصوص غير المرغوبة
    """
    if not text:
        return ""
    
    # قائمة الكلمات المفتاحية التي تشير إلى محتوى غير مرغوب
    unwanted_patterns = [
        r'الذكاء الاصطناعيSDAIAالهيئة السعودية للبيانات والذكاء الاصطناعيمعلومات سداياعن سداياالذكاء الاصطناعي',
        r'​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​',
        r'هل استفدت من المعلومات المقدمة في هذه الصفحة؟',
        r'نعملا0من الزوار أعجبهم محتوى الصفحة من أصل0',
        r'شكرا لمشاركتك تم استلام ملاحظاتك بنجاح',
        r'لقد قمت سابقا بتقديم ملاحظاتك',
        r'أضف السبب \(اختر من خيار واحد إلى خياران\)',
        r'هذا الحقل مطلوب',
        r'الرجاء كتابة نص صحيح',
        r'الملاحظات يجب ان تكون اقل من ٢٥٠ حرف',
        r'إرسال التعليق',
        r'إلغاء',
        r'شارك المقالة',
        r'فيسبوكتويتر',
        r'مواضيع ذات صلة بـ :',
        r'انضم الينا الان',
        r'كن جزء من غنائم و طور من متجرك',
        r'انظم الينا لان',
        r'Tags:',
        r'المقترحات',
        r'اعرف المزيد',
        r'دورات قد تهمك',
        r'مسارات تعليمية',
        r'فهرس المحتويات',
        r'مقالات شائعة',
        r'كتابة :',
        r'آخر تحديث:',
        r'تحميل',
        r'مشاهدة',
        r'للمزيد يرجى الاطلاع على',
        r'تمت الكتابة بواسطة:',
        r'آخر تحديث:',
        r'محتويات',
        r'المراجع',
        r'مجلوبة من',
        r'هل كان المقال مفيداً؟',
        r'الرجاء إجتياز الإختبار',
        r'رائع!',
        r'هل لديك مقترحات لتحسين تجربتك أكثر؟',
        r'بريدك الإلكتروني\*',
        r'هذا الحقل مطلوب',
        r'الإسم\*',
        r'الإشتراك بقائمة بريد موضوع',
        r'نأسف لذلك!',
        r'لماذا كان المقال غير مفيد؟',
        r'مطلوب الإختيار',
        r'يجب الاختيار للمتابعة',
        r'متابعة',
        r'تم الإرسال بنجاح، شكراً لك!',
        r'إغلاق',
        r'انضم الينا الان',
        r'كن جزء من غنائم و طور من متجرك و تكون التوب ترند في المملكة',
        r'انظم الينا لان'
    ]
    
    # إزالة الأنماط غير المرغوبة
    for pattern in unwanted_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    
    # إزالة الأسطر التي تحتوي على رموز أو أرقام فقط
    lines = text.split('\n')
    filtered_lines = []
    
    for line in lines:
        line = line.strip()
        if line:
            # تجاهل الأسطر التي تحتوي على رموز أو أرقام فقط
            if re.match(r'^[\d\s\-\.\*\(\)]+$', line):
                continue
            
            # تجاهل الأسطر القصيرة جداً
            if len(line) < 20:
                continue
            
            # تجاهل الأسطر التي تحتوي على تكرارات واضحة
            if re.search(r'(.{2,})\1{3,}', line):
                continue
            
            filtered_lines.append(line)
    
    return '\n\n'.join(filtered_lines)

def clean_and_organize_text(text: str) -> str:
    """
    تنظيف وتنظيم النص المستخرج من الموقع مع إزالة التكرارات والمحتوى غير المرغوب
    """
    if not text:
        return ""
    
    # 1. إزالة المسافات الزائدة في البداية والنهاية
    text = text.strip()
    
    # 2. تنظيف الفواصل المتكررة بين الفقرات
    while "\n\n\n" in text:
        text = text.replace("\n\n\n", "\n\n")
    
    # 3. إزالة الأسطر الفارغة في البداية والنهاية
    text = re.sub(r'^\n+', '', text)
    text = re.sub(r'\n+$', '', text)
    
    # 4. تنظيف المسافات الزائدة داخل النص
    text = re.sub(r' +', ' ', text)
    
    # 5. تنظيف الفواصل المتكررة
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # 6. فلترة جودة المحتوى
    text = filter_content_quality(text)
    
    # 7. إزالة المحتوى المكرر
    text = remove_duplicate_content(text)
    
    # 8. تنظيف نهائي
    text = text.strip()
    
    return text

def extract_text_from_url(url: str, min_length: int = 100) -> dict:
    """
    استخراج النص فقط من رابط واحد مع التنظيم والفلترة المتقدمة
    """
    print(f"🔍 جاري استخراج النص من: {url}")
    
    try:
        # إعداد headers لمحاكاة المتصفح
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ar,en-US;q=0.7,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        # جلب الصفحة
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()
        
        # تحليل HTML
        soup = BeautifulSoup(response.text, "html.parser")
        
        # ⭐ إزالة العناصر غير المرغوبة أولاً ⭐
        unwanted_elements = [
            'nav', 'header', 'footer', 'aside', 'menu',
            'script', 'style', 'noscript', 'iframe',
            '.navigation', '.menu', '.sidebar', '.footer',
            '.header', '.ads', '.advertisement', '.social',
            '.comments', '.related', '.recommended',
            '.breadcrumb', '.pagination', '.search',
            '.newsletter', '.subscribe', '.newsletter-signup'
        ]
        
        for element in unwanted_elements:
            if element.startswith('.'):
                # إزالة العناصر بالـ class
                for unwanted in soup.select(element):
                    unwanted.decompose()
            else:
                # إزالة العناصر بالـ tag
                for unwanted in soup.find_all(element):
                    unwanted.decompose()
        
        # ⭐ البحث عن المحتوى الرئيسي بذكاء ⭐
        main_content = None
        
        # البحث في ترتيب الأولوية
        selectors = [
            'article', 'main', 
            '[role="main"]', 
            '.post-content', '.article-content', '.entry-content',
            '#content', '#main-content', '#article-content',
            '.content', '.main-content', '.article-body',
            '.post-body', '.entry-body', '.article-text'
        ]
        
        for selector in selectors:
            main_content = soup.select_one(selector)
            if main_content:
                break
        
        # إذا لم نجد محتوى رئيسي، نبحث في الصفحة كلها
        search_area = main_content if main_content else soup
        
        # ⭐ استخراج النص بطريقة ذكية ومتقدمة ⭐
        # 1. البحث عن الفقرات والعناوين
        text_elements = search_area.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'div'], recursive=True)
        
        # 2. تجميع النص مع فلترة متقدمة
        article_texts = []
        
        for element in text_elements:
            # الحصول على النص
            text = element.get_text(strip=True)
            
            # فلترة النص المتقدمة
            if len(text) > 30 and len(text) < 2000:
                # إزالة النصوص التي تحتوي على عناصر واجهة المستخدم
                ui_keywords = [
                    'click here', 'read more', 'subscribe', 'follow us', 'share', 'like',
                    'comment', 'download', 'upload', 'login', 'register', 'sign up',
                    'تمت الكتابة بواسطة', 'آخر تحديث', 'محتويات', 'المراجع',
                    'هل استفدت', 'هل كان المقال مفيداً', 'نعم', 'لا',
                    'أضف السبب', 'هذا الحقل مطلوب', 'الرجاء كتابة نص صحيح',
                    'إرسال التعليق', 'إلغاء', 'شارك المقالة', 'فيسبوك', 'تويتر',
                    'مواضيع ذات صلة', 'انضم الينا', 'تواصل معنا', 'Tags:',
                    'المقترحات', 'اعرف المزيد', 'دورات قد تهمك', 'مسارات تعليمية',
                    'فهرس المحتويات', 'مقالات شائعة', 'كتابة :', 'آخر تحديث:',
                    'تحميل', 'مشاهدة', 'للمزيد', 'يرجى الاطلاع على'
                ]
                
                if any(keyword in text.lower() for keyword in ui_keywords):
                    continue
                
                # إزالة النصوص التي تحتوي على أرقام أو رموز متكررة
                if re.match(r'^[\d\s\-\.]+$', text):
                    continue
                
                # إزالة النصوص التي تحتوي على تكرارات واضحة
                if re.search(r'(.{3,})\1{2,}', text):
                    continue
                
                # إزالة النصوص التي تحتوي على روابط أو أزرار
                if any(char in text for char in ['http://', 'https://', 'www.', '.com', '.org']):
                    continue
                
                # إزالة النصوص التي تحتوي على رموز HTML أو CSS
                if re.search(r'[<>{}[\]]', text):
                    continue
                
                article_texts.append(text)
        
        # 3. تجميع النص مع فواصل واضحة
        if article_texts:
            raw_text = "\n\n".join(article_texts)
            # تنظيف وتنظيم النص
            clean_text = clean_and_organize_text(raw_text)
            
            if clean_text and len(clean_text) > min_length:  # استخدام الحد الأدنى المحدد
                print(f"✅ تم استخراج {len(article_texts)} فقرة بنجاح")
                return {
                    "status": "success",
                    "url": url,
                    "paragraphs_count": len(article_texts),
                    "text": clean_text,
                    "text_length": len(clean_text)
                }
        
        # إذا لم نجد محتوى في الفقرات، نجرب طريقة بديلة
        print("⚠️  لم نجد محتوى في الفقرات، نجرب طريقة بديلة...")
        
        # البحث في جميع النصوص مع فلترة إضافية
        all_text = search_area.get_text()
        if all_text:
            # تنظيف النص
            clean_text = clean_and_organize_text(all_text)
            if len(clean_text) > min_length:  # استخدام الحد الأدنى المحدد
                return {
                    "status": "success",
                    "url": url,
                    "paragraphs_count": 1,
                    "text": clean_text,
                    "text_length": len(clean_text),
                    "note": "تم الاستخراج بطريقة بديلة"
                }
        
        raise ValueError("لم يتم العثور على محتوى نصي واضح في هذه الصفحة")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ خطأ في جلب الصفحة: {e}")
        return {
            "status": "error",
            "url": url,
            "error": f"خطأ في جلب الصفحة: {e}"
        }
    except Exception as e:
        print(f"❌ خطأ غير متوقع: {e}")
        return {
            "status": "error",
            "url": url,
            "error": f"خطأ غير متوقع: {e}"
        }

@app.route('/search-articles/', methods=['POST'])
def search_articles():
    """
    نقطة نهاية للبحث عن المقالات واستخراج النص منها
    """
    try:
        data = request.get_json()
        query = data.get('query', '')
        min_length = data.get('min_length', 100)  # الحد الأدنى لطول النص (قابل للتخصيص)
        
        if not query:
            return jsonify({"error": "يجب توفير query"}), 400
        
        print(f"🔍 البحث عن: {query}")
        print(f"📏 الحد الأدنى لطول النص: {min_length}")
        
        # هنا يمكنك إضافة منطق البحث عن الروابط
        # في الوقت الحالي، سنستخدم مثال بسيط
        sample_urls = [
            "https://sdaia.gov.sa/ar/SDAIA/about/Pages/AboutAI.aspx",
            "https://mawdoo3.com/%D8%A3%D9%87%D9%85%D9%8A%D8%A9_%D8%A7%D9%84%D8%B0%D9%83%D8%A7%D8%A1_%D8%A7%D9%84%D8%A7%D8%B5%D8%B7%D9%86%D8%A7%D8%B9%D9%8A"
        ]
        
        results = []
        successful_articles = 0
        failed_articles = 0
        
        for url in sample_urls:
            result = extract_text_from_url(url, min_length)
            if result["status"] == "success":
                successful_articles += 1
                results.append(result)
            else:
                failed_articles += 1
                results.append(result)
        
        response_data = {
            "success": True,
            "query": query,
            "total_urls": len(sample_urls),
            "successful_articles": successful_articles,
            "failed_articles": failed_articles,
            "results": results,
            "min_length_used": min_length
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({"error": f"خطأ في معالجة الطلب: {str(e)}"}), 500

@app.route('/extract-single/', methods=['POST'])
def extract_single_article():
    """
    نقطة نهاية لاستخراج نص من رابط واحد
    """
    try:
        data = request.get_json()
        url = data.get('url', '')
        min_length = data.get('min_length', 100)  # الحد الأدنى لطول النص
        
        if not url:
            return jsonify({"error": "يجب توفير url"}), 400
        
        print(f"🔍 استخراج النص من: {url}")
        print(f"📏 الحد الأدنى لطول النص: {min_length}")
        
        result = extract_text_from_url(url, min_length)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": f"خطأ في معالجة الطلب: {str(e)}"}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """
    فحص صحة API
    """
    return jsonify({
        "status": "healthy",
        "message": "Article Extractor API is running",
        "features": [
            "Improved text extraction",
            "Duplicate content removal",
            "Content quality filtering",
            "Customizable minimum text length"
        ]
    })

if __name__ == "__main__":
    print("🚀 تشغيل Article Extractor API...")
    print("📝 النقاط النهائية المتاحة:")
    print("   POST /search-articles/ - البحث عن المقالات")
    print("   POST /extract-single/ - استخراج نص من رابط واحد")
    print("   GET  /health - فحص صحة API")
    print("\n💡 يمكنك تخصيص الحد الأدنى لطول النص باستخدام min_length")
    print("   مثال: {'query': 'أهمية الذكاء الاصطناعي', 'min_length': 1000}")
    
    app.run(host='0.0.0.0', port=5001, debug=True)
