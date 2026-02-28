# AAPI Pro Hub - الأتمتة البرمجية الذكية

<div align="center">

![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?style=for-the-badge&logo=github-actions)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python)
![GitHub Pages](https://img.shields.io/badge/GitHub_Pages-222222?style=for-the-badge&logo=github)
![License](https://img.shields.io/badge/License-MIT-green)

</div>

## نظرة عامة

**AAPI Pro Hub** هو نظام أتمتة برمجية متكامل يمكّنك من:
- إرسال طلبات (Prompts) عبر صفحة ويب
- تحليل الطلبات وتحويلها لمواصفات دقيقة
- توليد أكواد برمجية تلقائياً
- تنفيذ واختبار المشاريع
- التكرار التلقائي حتى تحقيق الهدف

## كيف يعمل النظام

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  المستخدم   │────▶│  AI-1       │────▶│  Spec       │
│  (برومبت)   │     │  المحلل     │     │  مُنظَّم    │
└─────────────┘     └──────────────┘     └─────────────┘
                                               │
                                               ▼
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  دمج        │◀────│  AI-2       │◀────│  توليد      │
│  (Merge)    │     │  المُنتج    │     │  الكود      │
└─────────────┘     └──────────────┘     └─────────────┘
       │                   │
       │                   ▼
       │            ┌──────────────┐
       │            │ GitHub       │
       └───────────▶│ Actions      │
                    │ (Build/Test) │
                    └──────────────┘
```

## الأدوار

| الذكاء الاصطناعي | الدور |
|-----------------|-------|
| **ChatGPT-5** | التحليل والتوليد الرئيسي للكود |
| **Gemini 3 Flash** | المراجعة والتحسينات متعددة الوسائط |

## المميزات

- ✅ **صفحة ويب تفاعلية** على GitHub Pages
- ✅ **تنفيذ سحابي** عبر GitHub Actions
- ✅ **تكرار تلقائي** حتى تحقيق الطلب
- ✅ **تعديلات دقيقة** بدون إعادة كتابة الملفات
- ✅ **ضغط Zstd** للملفات
- ✅ **دعم GitHub Releases & Caches**

## البدء السريع

### 1. استنساخ المشروع

```bash
git clone https://github.com/YOUR_USERNAME/aapi-pro-hub.git
cd aapi-pro-hub
```

### 2. إعداد GitHub Token

1. اذهب إلى [GitHub Settings > Developer settings > Personal access tokens](https://github.com/settings/tokens)
2. أنشئ token جديد مع صلاحيات:
   - `repo` (كامل)
   - `workflow`
   - `read:packages`

### 3. تفعيل GitHub Pages

1. اذهب إلى **Settings > Pages**
2. اختر `main` branch
3. احفظ

### 4. استخدام النظام

1. افتح صفحة GitHub Pages
2. أدخل GitHub Token
3. أدخل اسم المستودع (username/repo)
4. اكتب طلبك وابدأ!

## هيكل المشروع

```
aapi-pro-hub/
├── .github/
│   └── workflows/
│       ├── main.yml           # سير العمل الرئيسي
│       ├── gemini_api.yml    # دمج Gemini
│       └── gpt_api.yml       # دمج ChatGPT
├── scripts/
│   ├── analyzer.py            # محلل الطلبات
│   ├── code_generator.py     # مولد الكود
│   ├── evaluator.py          # المقيم/المراجع
│   └── patcher.py            # المُعدِّل الذكي
├── src/
│   └── (ملفات المشروع المُنشأ)
├── index.html                # واجهة المستخدم
├── SPEC.md                   # مواصفات النظام
└── README.md
```

## أوامر API

### تشغيل الطلب

```bash
curl -X POST \
  -H "Authorization: token YOUR_GITHUB_TOKEN" \
  https://api.github.com/repos/USER/REPO/actions/workflows/main.yml/dispatches \
  -d '{
    "ref": "main",
    "inputs": {
      "prompt": "اكتب لي كود بايثون",
      "request_id": "unique_id_123"
    }
  }'
```

## SDK - مكتبة Python

```python
import requests, time, zipfile, io, json, uuid

class AAPI_Pro_Client:
    def __init__(self, token, owner, repo):
        self.headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github.v3+json"}
        self.base_url = f"https://api.github.com/repos/{owner}/{repo}"

    def ask_ai(self, prompt, engine="gemini"):
        workflow = "gemini_api.yml" if engine == "gemini" else "gpt_api.yml"
        req_id = str(uuid.uuid4().hex)[:10]
        
        trigger_url = f"{self.base_url}/actions/workflows/{workflow}/dispatches"
        data = {"ref": "main", "inputs": {"prompt": prompt, "request_id": req_id}}
        
        print(f"📡 إرسال الطلب لـ {engine}...")
        res = requests.post(trigger_url, headers=self.headers, json=data)
        if res.status_code != 204: return f"Error: {res.text}"

        artifact_name = f"{engine}-json-{req_id}"
        print("⏳ جاري المعالجة سحابياً...")
        
        for attempt in range(30):
            time.sleep(5)
            runs_url = f"{self.base_url}/actions/runs?status=completed&per_page=5"
            run_data = requests.get(runs_url, headers=self.headers).json()
            
            for run in run_data.get("workflow_runs", []):
                arts_res = requests.get(run["artifacts_url"], headers=self.headers).json()
                for art in arts_res.get("artifacts", []):
                    if art["name"] == artifact_name:
                        print("📥 تم استلام الرد!")
                        zip_res = requests.get(art["archive_download_url"], headers=self.headers)
                        with zipfile.ZipFile(io.BytesIO(zip_res.content)) as z:
                            file_name = f"{engine}_result.json"
                            with z.open(file_name) as f:
                                return json.loads(f.read().decode('utf-8'))['response']
        
        return "Timeout: استغرق وقتاً طويلاً."

# تشغيل
api = AAPI_Pro_Client("ghp_TOKEN", "USER", "REPO")
print(api.ask_ai("اكتب كود بايثون للتشفير"))
```

## المواصفات التقنية

| المكون | التقنية |
|--------|--------|
| الواجهة | HTML5, CSS3, JavaScript |
| المعالجة | GitHub Actions |
| الذكاء الاصطناعي | Gemini API, ChatGPT API |
| الضغط | Zstd (tar.zst) |
| التخزين | GitHub Artifacts |

## الترخيص

MIT License - انظر ملف [LICENSE](LICENSE)

---

<div align="center">

**صنع بـ ❤️ بواسطة AAPI Pro Hub**

</div>
