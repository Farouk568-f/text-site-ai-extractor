# -*- coding: utf-8 -*-
"""
Vercel API endpoint for Text Site AI Extractor
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import re
import difflib

app = Flask(__name__)
CORS(app)

def remove_duplicate_content(text: str) -> str:
    """إزالة المحتوى المكرر والمتكرر من النص"""
    if not text:
        return ""
    
    paragraphs = text.split('\n\n')
    paragraphs = [p.strip() for p in paragraphs if p.strip()]
    
    unique_paragraphs = []
    seen_paragraphs = set()
    
    for paragraph in paragraphs:
        if len(paragraph) < 50:
            continue
            
        clean_paragraph = re.sub(r'\s+', ' ', paragraph.strip())
        
        is_duplicate = False
        for seen in seen_paragraphs:
            similarity = difflib.SequenceMatcher(None, clean_paragraph, seen).ratio()
            if similarity > 0.7:
                is_duplicate = True
                break
        
        if not is_duplicate:
            unique_paragraphs.append(paragraph)
            seen_paragraphs.add(clean_paragraph)
    
    return '\n\n'.join(unique_paragraphs)

def filter_content_quality(text: str) -> str:
    """فلترة جودة المحتوى وإزالة النصوص غير المرغوبة"""
    if not text:
        return ""
    
    unwanted_patterns = [
        r'هل استفدت من المعلومات المقدمة في هذه الصفحة؟',
        r'نعملا',
        r'شكرا لمشاركتك',
        r'أضف السبب',
        r'هذا الحقل مطلوب',
        r'الرجاء كتابة نص صحيح',
        r'إرسال التعليق',
        r'إلغاء',
        r'شارك المقالة',
        r'فيسبوكتويتر',
        r'مواضيع ذات صلة',
        r'انضم الينا',
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
        r'محتويات',
        r'المراجع',
        r'مجلوبة من',
        r'هل كان المقال مفيداً؟',
        r'الرجاء إجتياز الإختبار',
        r'رائع!',
        r'هل لديك مقترحات لتحسين تجربتك أكثر؟',
        r'بريدك الإلكتروني*',
        r'الإسم*',
        r'الإشتراك بقائمة بريد موضوع',
        r'نأسف لذلك!',
        r'لماذا كان المقال غير مفيد؟',
        r'مطلوب الإختيار',
        r'يجب الاختيار للمتابعة',
        r'متابعة',
        r'تم الإرسال بنجاح، شكراً لك!',
        r'إغلاق'
    ]
    
    for pattern in unwanted_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    
    lines = text.split('\n')
    filtered_lines = []
    
    for line in lines:
        line = line.strip()
        if line:
            if re.match(r'^[\d\s\-\.\*\(\)]+$', line):
                continue
            
            if len(line) < 20:
                continue
            
            if re.search(r'(.{2,})\1{3,}', line):
                continue
            
            filtered_lines.append(line)
    
    return '\n\n'.join(filtered_lines)

def clean_and_organize_text(text: str) -> str:
    """تنظيف وتنظيم النص المستخرج من الموقع"""
    if not text:
        return ""
    
    text = text.strip()
    
    while "\n\n\n" in text:
        text = text.replace("\n\n\n", "\n\n")
    
    text = re.sub(r'^\n+', '', text)
    text = re.sub(r'\n+$', '', text)
    text = re.sub(r' +', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    text = filter_content_quality(text)
    text = remove_duplicate_content(text)
    
    return text.strip()

def extract_text_from_url(url: str, min_length: int = 100) -> dict:
    """استخراج النص فقط من رابط واحد مع التنظيم والفلترة المتقدمة"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ar,en-US;q=0.7,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        
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
                for unwanted in soup.select(element):
                    unwanted.decompose()
            else:
                for unwanted in soup.find_all(element):
                    unwanted.decompose()
        
        main_content = None
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
        
        search_area = main_content if main_content else soup
        
        text_elements = search_area.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'div'], recursive=True)
        
        article_texts = []
        
        for element in text_elements:
            text = element.get_text(strip=True)
            
            if len(text) > 30 and len(text) < 2000:
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
                
                if re.match(r'^[\d\s\-\.]+$', text):
                    continue
                
                if re.search(r'(.{3,})\1{2,}', text):
                    continue
                
                if any(char in text for char in ['http://', 'https://', 'www.', '.com', '.org']):
                    continue
                
                if re.search(r'[<>{}[\]]', text):
                    continue
                
                article_texts.append(text)
        
        if article_texts:
            raw_text = "\n\n".join(article_texts)
            clean_text = clean_and_organize_text(raw_text)
            
            if clean_text and len(clean_text) > min_length:
                return {
                    "status": "success",
                    "url": url,
                    "paragraphs_count": len(article_texts),
                    "text": clean_text,
                    "text_length": len(clean_text)
                }
        
        all_text = search_area.get_text()
        if all_text:
            clean_text = clean_and_organize_text(all_text)
            if len(clean_text) > min_length:
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
        return {
            "status": "error",
            "url": url,
            "error": f"خطأ في جلب الصفحة: {e}"
        }
    except Exception as e:
        return {
            "status": "error",
            "url": url,
            "error": f"خطأ غير متوقع: {e}"
        }

@app.route('/search-articles/', methods=['POST'])
def search_articles():
    """نقطة نهاية للبحث عن المقالات واستخراج النص منها"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        min_length = data.get('min_length', 100)
        
        if not query:
            return jsonify({"error": "يجب توفير query"}), 400
        
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
    """نقطة نهاية لاستخراج نص من رابط واحد"""
    try:
        data = request.get_json()
        url = data.get('url', '')
        min_length = data.get('min_length', 100)
        
        if not url:
            return jsonify({"error": "يجب توفير url"}), 400
        
        result = extract_text_from_url(url, min_length)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": f"خطأ في معالجة الطلب: {str(e)}"}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """فحص صحة API"""
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

# Export the Flask app for Vercel
if __name__ == "__main__":
    app.run()
