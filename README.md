# 🚀 Text Site AI Extractor

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-2.3+-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An advanced Arabic text extraction API that intelligently removes duplicates and unwanted content from web articles, providing clean and organized text output.

## ✨ Features

### 🔧 Advanced Text Processing
- **Duplicate Removal**: Smart algorithm using `difflib.SequenceMatcher` to detect and remove similar content
- **Content Filtering**: Removes UI elements, comments, and navigation components
- **Text Cleaning**: Eliminates extra spaces, symbols, and unwanted characters

### 📏 Customizable Options
- **Minimum Text Length**: Configurable threshold (default: 100 characters)
- **Smart Filtering**: Ignores overly short or long text segments
- **Advanced Search**: Prioritizes main content areas

### 🌐 Multiple Endpoints
- `/search-articles/` - Search and extract from multiple articles
- `/extract-single/` - Extract text from a single URL
- `/health` - API health check

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the API
```bash
python article_api.py
```

The API will run on port 5001

### 3. Test the API
```bash
python test_improved_api.py
```

## 📝 Usage Examples

### Search Articles with Custom Minimum Length

```python
import requests

# Search with minimum length 1000 (complete and clean content)
payload = {
    "query": "أهمية الذكاء الاصطناعي",
    "min_length": 1000  # As requested - complete and clean content
}

response = requests.post("http://localhost:5001/search-articles/", json=payload)
result = response.json()

print(f"Successful articles: {result['successful_articles']}")
print(f"Minimum length used: {result['min_length_used']}")
```

### Extract Text from Single URL

```python
import requests

# Extract text from URL with minimum length 1000
payload = {
    "url": "https://sdaia.gov.sa/ar/SDAIA/about/Pages/AboutAI.aspx",
    "min_length": 1000
}

response = requests.post("http://localhost:5001/extract-single/", json=payload)
result = response.json()

if result["status"] == "success":
    print(f"Paragraphs: {result['paragraphs_count']}")
    print(f"Text length: {result['text_length']}")
    print(f"Text: {result['text'][:200]}...")
```

## ⚙️ Configuration Options

### Minimum Text Length

| Value | Result |
|-------|--------|
| `100` | Short content (default) |
| `500` | Medium content |
| `1000` | **Complete and clean content (recommended)** |
| `2000` | Very long content |

### Optimal Usage Example

```python
# For complete and clean content as requested
payload = {
    "query": "أهمية الذكاء الاصطناعي",
    "min_length": 1000  # This will give you complete and clean content
}
```

## 🔍 How It Works

### 1. Remove Unwanted Elements
- `nav`, `header`, `footer`, `aside`
- `script`, `style`, `noscript`
- `.navigation`, `.menu`, `.sidebar`
- `.ads`, `.comments`, `.related`

### 2. Find Main Content
```python
selectors = [
    'article', 'main', 
    '[role="main"]', 
    '.post-content', '.article-content', '.entry-content',
    '#content', '#main-content', '#article-content'
]
```

### 3. Text Filtering
- Remove very short text (< 30 characters)
- Remove very long text (> 2000 characters)
- Remove UI elements
- Remove links and symbols

### 4. Duplicate Removal
- Uses `difflib.SequenceMatcher`
- Similarity threshold: 70%
- Ignores short paragraphs (< 50 characters)

## 📊 Results Comparison

### Before Improvement
```
الذكاء الاصطناعيSDAIAالهيئة السعودية للبيانات والذكاء الاصطناعيمعلومات سداياعن سداياالذكاء الاصطناعي
الذكاء الاصطناعيSDAIAالهيئة السعودية للبيانات والذكاء الاصطناعيمعلومات سداياعن سداياالذكاء الاصطناعي
هل استفدت من المعلومات المقدمة في هذه الصفحة؟نعملا
```

### After Improvement
```
يُعد الذكاء الاصطناعي (Artificial Intelligence) من أهم التقنيات الحديثة التي تسهم بشكل ملحوظ في التطور التقني السريع وزيادة فرص الابتكار والنمو في مختلف المجالات.

يؤدي الذكاء الاصطناعي دوراً مهماً في رفع الجودة، وزيادة الإمكانات وكفاءة الأعمال وتحسين الإنتاجية.
```

## 🛠️ Troubleshooting

### Issue: API Not Responding
```bash
# Check API health
curl http://localhost:5001/health
```

### Issue: Text Too Short
```python
# Increase minimum length
payload = {
    "query": "أهمية الذكاء الاصطناعي",
    "min_length": 1000  # Instead of 100
}
```

### Issue: Duplicate Content
- System automatically removes duplicates
- Can adjust similarity threshold in code

## 📈 Future Improvements

- [ ] Google search integration
- [ ] Advanced linguistic filtering
- [ ] Multi-language support
- [ ] Enhanced duplicate detection algorithm
- [ ] Web interface

## 🤝 Contributing

We welcome contributions! Please:

1. Fork the project
2. Create a new branch
3. Make your changes
4. Submit a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🌟 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=Farouk568-f/text-site-ai-extractor&type=Date)](https://star-history.com/#Farouk568-f/text-site-ai-extractor&Date)

---

**💡 Tip**: Use `min_length: 1000` to get complete and clean content as requested!

## 📞 Support

If you have any questions or need help, please open an issue on GitHub.

---

Made with ❤️ for Arabic text processing
