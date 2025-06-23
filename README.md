# مشروع تحليل النصوص العربية باستخدام الذكاء الاصطناعي

## 📌 نظرة عامة
تطبيق ويب لتحليل النصوص العربية (POS Tagging, NER, Stemming) باستخدام:
- `camel-tools` للمورفولوجيا
- `transformers` للتعرف على الكيانات
- تقنيات معالجة اللغة الطبيعية

## ⚙️ التثبيت
```bash
git clone https://github.com/yourusername/arabic-nlp.git
pip install -r requirements.txt


## 🧩 حل مشكلة camel_tools
إذا واجهت خطأ في تحميل البيانات:
1. حمل [catalogue-1.5.json](https://raw.githubusercontent.com/CAMeL-Lab/camel-tools-data/main/catalogue-1.5.json)
2. ضعه في المسار:  C:\Users\USER\.camel_tools\data\
أو عيّن مسارًا مخصصًا عبر:
```python
import os
os.environ['CAMELTOOLS_DATA'] = 'custom_path'
