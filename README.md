# مشروع تحليل النصوص العربية باستخدام الذكاء الاصطناعي

## 📌 نظرة عامة
تطبيق ويب لتحليل النصوص العربية (POS Tagging, NER, Stemming) باستخدام:
- `camel-tools` للمورفولوجيا
- `transformers` للتعرف على الكيانات
- تقنيات معالجة اللغة الطبيعية


For Support and disclaimer Contact me:
E-mail: aidrooss12370@gmail.com
Whatsapp: +967 773006111
telegram: @aid12370
## ⚙️ التثبيت
```bash
git clone https://github.com/yourusername/arabic-nlp.git
pip install -r requirements.txt


## 🧩 هيكل المشروع
project/
├── app.py
├── requirements.txt
├── templates/
│   ├── index.html
│   ├── explanation.html
│   ├── text_analysis.html
│   ├── search.html
│   └── challenges.html
├── static/
│   ├── css/
│   └── js/
└── documents/
```

## 🔍 استكشاف الأخطاء وإصلاحها
إذا واجهت مشكلات مع camel_tools:
1. تأكد من تنزيل ملف [catalogue-1.5.json](https://raw.githubusercontent.com/CAMeL-Lab/camel-tools-data/main/catalogue-1.5.json)
2. ضعه في المسار: `C:\Users\<USER>\.camel_tools\data\`
3. أو عيّن مساراً مخصصاً:
```python
import os
os.environ['CAMELTOOLS_DATA'] = 'C:/custom_path/.camel_tools_data'
```
