"""Offline fallback guidance for the Nagrik AI demo. Verify current rules on official portals."""

SERVICE_DATA = {
    "income": {
        "title": "Income Certificate",
        "steps": [
            "Check the current Income Certificate service on Maharashtra Aaple Sarkar.",
            "Review the eligibility and applicant category shown on the official portal.",
            "Prepare the documents requested for your exact case and submit through the official channel.",
            "Save the application/acknowledgement number and use the portal to track status."
        ],
        "docs": ["Identity proof as accepted by the portal", "Address/residence proof", "Income proof or self-declaration, if required", "Photograph and application details, if requested"],
        "fee": "Fee varies by service and current government rules; verify on Aaple Sarkar before paying."
    },
    "domicile": {
        "title": "Domicile Certificate",
        "steps": ["Open Maharashtra Aaple Sarkar and find the domicile/residence service.", "Check the residence-duration and eligibility rules for your case.", "Prepare accepted identity, address and residence evidence.", "Submit through the official channel and keep the acknowledgement."],
        "docs": ["Identity proof", "Address proof", "Residence evidence", "Birth/school records or other supporting documents if requested"],
        "fee": "Verify the current fee on the official portal."
    },
    "caste": {
        "title": "Caste Certificate",
        "steps": ["Find the Caste Certificate service on Aaple Sarkar.", "Check the exact category and evidence requirements.", "Prepare family/caste records and other supporting evidence requested by the authority.", "Submit the application and keep the acknowledgement."],
        "docs": ["Identity proof", "Address proof", "Applicant and family records", "Caste-related evidence as requested by the competent authority"],
        "fee": "Verify the current fee and any service charges on the official portal."
    },
    "scholarship": {
        "title": "Scholarship",
        "steps": ["Identify the exact scholarship and academic year.", "Read the official eligibility, income, category and course rules.", "Prepare the documents listed for that scheme.", "Apply on the official portal before the deadline and save the acknowledgement."],
        "docs": ["Student ID/admission proof", "Marksheets", "Income certificate if required", "Category certificate and non-creamy-layer certificate if applicable", "Domicile/bank details only through the official secure portal"],
        "fee": "Scholarship applications are often free, but verify the specific scheme. Do not pay unofficial agents."
    },
    "pension": {
        "title": "Pension",
        "steps": ["Identify the exact pension scheme and responsible department.", "Check eligibility and whether it is a new, paused or restarted pension case.", "Prepare the scheme-specific records and any notice/reference number.", "Use the official channel or authorised office to submit a request and obtain an acknowledgement."],
        "docs": ["Identity proof through official channel", "Scheme or pension reference number", "Bank proof if officially required", "Age/disability/dependency or other scheme-specific evidence"],
        "fee": "Confirm the scheme's official fee; be cautious of anyone demanding unofficial payment."
    },
    "pan": {
        "title": "PAN Card",
        "steps": ["Use the official Income Tax portal or an authorised PAN service provider.", "Choose new PAN or correction based on your situation.", "Follow the secure identity verification and document instructions.", "Keep the acknowledgement number."],
        "docs": ["Identity proof accepted by the provider", "Date-of-birth proof", "Address/contact details as requested"],
        "fee": "The fee depends on the application type and delivery option; check the official checkout before paying."
    },
    "property-tax": {
        "title": "Property Tax Correction",
        "steps": ["Identify your municipal corporation/local authority and property account number.", "Collect the bill and identify the exact incorrect field.", "Submit a correction request through the official portal or authorised ward office.", "Keep copies of the request and acknowledgement."],
        "docs": ["Property tax bill/account number", "Proof supporting the correction", "Ownership/occupancy records if requested", "Contact details"],
        "fee": "Correction charges, if any, depend on the local authority; verify before paying."
    },
    "birth": {
        "title": "Birth Certificate",
        "steps": ["Identify the municipal/local registrar responsible for the birth record.", "Choose new registration, certificate copy or correction as applicable.", "Check which hospital/parent/record details are required.", "Submit through the official local authority and retain the acknowledgement."],
        "docs": ["Hospital/registration record if available", "Parent/applicant identity evidence as required", "Existing certificate or registration number for corrections"],
        "fee": "Fees and late-registration procedures vary by local authority; verify officially."
    },
}
ALIASES = {
    "income": ["income certificate", "income", "उत्पन्न", "आय प्रमाण", "आय प्रमाणपत्र"],
    "domicile": ["domicile", "residence certificate", "रहिवासी", "अधिवास", "निवास प्रमाण"],
    "caste": ["caste certificate", "caste", "जात प्रमाणपत्र", "जात प्रमाण"],
    "scholarship": ["scholarship", "छात्रवृत्ति", "शिष्यवृत्ती", "स्कॉलरशिप"],
    "pension": ["pension", "पेन्शन", "पेंशन"],
    "pan": ["pan card", "pan", "पॅन", "पैन कार्ड"],
    "property-tax": ["property tax", "tax correction", "मालमत्ता कर", "प्रॉपर्टी टैक्स"],
    "birth": ["birth certificate", "जन्म प्रमाणपत्र", "जन्म दाखला"],
}

def find_service(text, selected=""):
    combined = f"{selected} {text}".lower()
    for key, aliases in ALIASES.items():
        if key in combined or any(alias.lower() in combined for alias in aliases):
            return key
    return ""

def get_checklist(service, language="English"):
    key = find_service("", service)
    lang = str(language).lower()
    if lang in {"hindi", "hi", "हिन्दी", "हिंदी"} and key in LOCALIZED["Hindi"]:
        item = LOCALIZED["Hindi"][key]
        return item["docs"] + ["शुल्क: " + item["fee"]]
    if lang in {"marathi", "mr", "मराठी"} and key in LOCALIZED["Marathi"]:
        item = LOCALIZED["Marathi"][key]
        return item["docs"] + ["शुल्क: " + item["fee"]]
    if not key:
        return ["Check the exact service and eligibility on the official portal.", "Prepare identity/address proof only if requested.", "Keep copies of submissions and acknowledgement numbers.", "Never share OTPs, passwords or Aadhaar numbers in chat."]
    data = SERVICE_DATA[key]
    return data["docs"] + [data["fee"]]

def get_fallback_answer(message, language="auto", service=""):
    key = find_service(message, service)
    if str(language).lower() in {"hindi", "hi", "हिन्दी", "हिंदी", "marathi", "mr", "मराठी"}:
        return _localized_answer(key, language)
    if not key:
        return (
            "I can help with income, domicile, caste certificates, scholarships, pensions, PAN, property-tax corrections and birth certificates. "
            "Tell me the service name and your state/district (do not share Aadhaar, OTP, password or bank details). "
            "For Maharashtra, start at https://aaplesarkar.mahaonline.gov.in/. Requirements and fees can change, so verify them officially."
        )
    item = SERVICE_DATA[key]
    lines = [f"{item['title']} — general guidance", "", "Steps:"]
    lines += [f"{i}. {step}" for i, step in enumerate(item["steps"], 1)]
    lines += ["", "Common document categories (your exact case may differ):"]
    lines += [f"• {doc}" for doc in item["docs"]]
    lines += ["", f"Fees: {item['fee']}", "", "Official starting point: https://aaplesarkar.mahaonline.gov.in/"]
    lines += ["Safety: Do not share OTPs, passwords, Aadhaar numbers or scans of identity documents in this chat."]
    return "\n".join(lines)

# Full local-language guidance so the demo remains useful without an AI API key.
LOCALIZED = {
"Hindi": {
"income": {"title":"आय प्रमाणपत्र", "steps":["महाराष्ट्र आपले सरकार पोर्टल पर आय प्रमाणपत्र सेवा खोलें।","अपने मामले की पात्रता और आवेदक श्रेणी जाँचें।","पोर्टल पर माँगे गए दस्तावेज़ तैयार करें और आधिकारिक माध्यम से आवेदन करें।","आवेदन/पावती संख्या सुरक्षित रखें और उससे स्थिति जाँचें।"],"docs":["स्वीकृत पहचान प्रमाण","पता/निवास प्रमाण","आय प्रमाण या स्व-घोषणा, यदि माँगी जाए","फोटो और आवेदन विवरण, यदि माँगे जाएँ"],"fee":"शुल्क बदल सकता है। भुगतान से पहले आधिकारिक पोर्टल पर वर्तमान शुल्क जाँचें।"},
"domicile": {"title":"अधिवास / निवासी प्रमाणपत्र", "steps":["आपले सरकार पर अधिवास/निवास प्रमाणपत्र सेवा खोजें।","अपने मामले के लिए निवास अवधि और पात्रता नियम जाँचें।","स्वीकृत पहचान, पता और निवास संबंधी प्रमाण तैयार करें।","आधिकारिक माध्यम से आवेदन करें और पावती सुरक्षित रखें।"],"docs":["पहचान प्रमाण","पता प्रमाण","निवास का प्रमाण","जन्म/स्कूल रिकॉर्ड या अन्य सहायक दस्तावेज़, यदि माँगे जाएँ"],"fee":"वर्तमान शुल्क आधिकारिक पोर्टल पर जाँचें।"},
"caste": {"title":"जाति प्रमाणपत्र", "steps":["आपले सरकार पर जाति प्रमाणपत्र सेवा खोजें।","अपनी श्रेणी और साक्ष्य संबंधी सटीक आवश्यकताएँ जाँचें।","परिवार/जाति रिकॉर्ड और माँगे गए सहायक प्रमाण तैयार करें।","आवेदन जमा करें और पावती सुरक्षित रखें।"],"docs":["पहचान प्रमाण","पता प्रमाण","आवेदक और परिवार के रिकॉर्ड","सक्षम प्राधिकारी द्वारा माँगा गया जाति-संबंधी प्रमाण"],"fee":"वर्तमान शुल्क और सेवा शुल्क आधिकारिक पोर्टल पर जाँचें।"},
"scholarship": {"title":"छात्रवृत्ति", "steps":["सही छात्रवृत्ति योजना और शैक्षणिक वर्ष चुनें।","आधिकारिक पात्रता, आय, श्रेणी और पाठ्यक्रम के नियम पढ़ें।","उस योजना में सूचीबद्ध दस्तावेज़ तैयार करें।","समय-सीमा से पहले आधिकारिक पोर्टल पर आवेदन करें और पावती सुरक्षित रखें।"],"docs":["छात्र पहचान/प्रवेश प्रमाण","अंकपत्र","आय प्रमाणपत्र, यदि आवश्यक हो","जाति और नॉन-क्रीमी लेयर प्रमाणपत्र, यदि लागू हो","निवास/बैंक विवरण केवल आधिकारिक सुरक्षित पोर्टल पर, यदि माँगे जाएँ"],"fee":"कई छात्रवृत्ति आवेदन निःशुल्क होते हैं, लेकिन योजना की शर्तें जाँचें। अनधिकृत एजेंट को भुगतान न करें।"},
"pension": {"title":"पेंशन", "steps":["संबंधित पेंशन योजना और विभाग की पहचान करें।","नई, रुकी हुई या दोबारा शुरू की जाने वाली पेंशन के नियम जाँचें।","योजना के अनुसार रिकॉर्ड और संदर्भ/नोटिस संख्या तैयार करें।","आधिकारिक माध्यम या अधिकृत कार्यालय में अनुरोध जमा करें और पावती लें।"],"docs":["आधिकारिक माध्यम से पहचान प्रमाण","योजना/पेंशन संदर्भ संख्या","बैंक प्रमाण, यदि आधिकारिक रूप से आवश्यक हो","आयु/दिव्यांगता/आश्रित या योजना-विशिष्ट प्रमाण"],"fee":"आधिकारिक शुल्क की पुष्टि करें। अनौपचारिक भुगतान की माँग से सावधान रहें।"},
"pan": {"title":"पैन कार्ड", "steps":["आयकर विभाग के आधिकारिक पोर्टल या अधिकृत पैन सेवा प्रदाता का उपयोग करें।","स्थिति के अनुसार नया पैन या सुधार विकल्प चुनें।","सुरक्षित पहचान सत्यापन और दस्तावेज़ निर्देशों का पालन करें।","पावती संख्या सुरक्षित रखें।"],"docs":["सेवा प्रदाता द्वारा स्वीकृत पहचान प्रमाण","जन्मतिथि प्रमाण","माँगे गए पते/संपर्क विवरण"],"fee":"आवेदन के प्रकार और डिलीवरी विकल्प के अनुसार शुल्क बदलता है; भुगतान से पहले आधिकारिक चेकआउट जाँचें।"},
"property-tax": {"title":"संपत्ति कर सुधार", "steps":["अपनी नगर निगम/स्थानीय प्राधिकरण और संपत्ति खाता संख्या पहचानें।","कर बिल लें और गलत विवरण चिन्हित करें।","आधिकारिक पोर्टल या अधिकृत वार्ड कार्यालय में सुधार अनुरोध दें।","अनुरोध की प्रति और पावती सुरक्षित रखें।"],"docs":["संपत्ति कर बिल/खाता संख्या","सुधार का समर्थन करने वाला प्रमाण","माँगे जाने पर स्वामित्व/कब्जे के रिकॉर्ड","संपर्क विवरण"],"fee":"यदि कोई सुधार शुल्क हो, तो वह स्थानीय प्राधिकरण पर निर्भर करता है; पहले पुष्टि करें।"},
"birth": {"title":"जन्म प्रमाणपत्र", "steps":["जन्म रिकॉर्ड के लिए जिम्मेदार नगर निकाय/स्थानीय रजिस्ट्रार की पहचान करें।","ज़रूरत के अनुसार नया पंजीकरण, प्रमाणपत्र की प्रति या सुधार चुनें।","अस्पताल/माता-पिता/रिकॉर्ड से संबंधित आवश्यकताएँ जाँचें।","स्थानीय प्राधिकरण के माध्यम से आवेदन करें और पावती सुरक्षित रखें।"],"docs":["अस्पताल/पंजीकरण रिकॉर्ड, यदि उपलब्ध हो","आवश्यकतानुसार अभिभावक/आवेदक पहचान प्रमाण","सुधार के लिए मौजूदा प्रमाणपत्र या पंजीकरण संख्या"],"fee":"शुल्क और देर से पंजीकरण की प्रक्रिया स्थानीय प्राधिकरण के अनुसार बदलती है। आधिकारिक पुष्टि करें।"}
},
"Marathi": {
"income": {"title":"उत्पन्न प्रमाणपत्र", "steps":["महाराष्ट्र आपले सरकार पोर्टलवर उत्पन्न प्रमाणपत्र सेवा उघडा.","तुमच्या प्रकरणातील पात्रता आणि अर्जदाराची श्रेणी तपासा.","पोर्टलवर मागितलेली कागदपत्रे तयार करा आणि अधिकृत मार्गाने अर्ज करा.","अर्ज/पोचपावती क्रमांक जतन करा आणि त्याद्वारे स्थिती तपासा."],"docs":["मान्य ओळखपत्र","पत्ता/रहिवासाचा पुरावा","उत्पन्नाचा पुरावा किंवा स्वघोषणा, आवश्यक असल्यास","फोटो व अर्जाचा तपशील, मागितल्यास"],"fee":"शुल्क बदलू शकते. पैसे भरण्यापूर्वी अधिकृत पोर्टलवर सध्याचे शुल्क तपासा."},
"domicile": {"title":"अधिवास / रहिवासी प्रमाणपत्र", "steps":["आपले सरकारवर अधिवास/रहिवासी प्रमाणपत्र सेवा शोधा.","तुमच्या प्रकरणासाठी रहिवास कालावधी आणि पात्रतेचे नियम तपासा.","मान्य ओळख, पत्ता आणि रहिवासाचे पुरावे तयार करा.","अधिकृत मार्गाने अर्ज करा आणि पोचपावती जतन करा."],"docs":["ओळखपत्र","पत्त्याचा पुरावा","रहिवासाचा पुरावा","जन्म/शाळेच्या नोंदी किंवा मागितलेली इतर कागदपत्रे"],"fee":"सध्याचे शुल्क अधिकृत पोर्टलवर तपासा."},
"caste": {"title":"जात प्रमाणपत्र", "steps":["आपले सरकारवर जात प्रमाणपत्र सेवा शोधा.","तुमच्या प्रवर्गासाठी आवश्यक पुरावे आणि अटी तपासा.","कुटुंब/जात नोंदी आणि मागितलेले पूरक पुरावे तयार करा.","अर्ज सादर करा आणि पोचपावती जतन करा."],"docs":["ओळखपत्र","पत्त्याचा पुरावा","अर्जदार व कुटुंबाच्या नोंदी","सक्षम प्राधिकरणाने मागितलेला जात-संबंधित पुरावा"],"fee":"सध्याचे शुल्क व सेवा शुल्क अधिकृत पोर्टलवर तपासा."},
"scholarship": {"title":"शिष्यवृत्ती", "steps":["योग्य शिष्यवृत्ती योजना आणि शैक्षणिक वर्ष निवडा.","अधिकृत पात्रता, उत्पन्न, प्रवर्ग आणि अभ्यासक्रमाचे नियम वाचा.","त्या योजनेत नमूद केलेली कागदपत्रे तयार करा.","अंतिम तारखेपूर्वी अधिकृत पोर्टलवर अर्ज करा आणि पोचपावती जतन करा."],"docs":["विद्यार्थी ओळख/प्रवेशाचा पुरावा","गुणपत्रिका","आवश्यक असल्यास उत्पन्न प्रमाणपत्र","लागू असल्यास जात व नॉन-क्रीमी लेयर प्रमाणपत्र","रहिवास/बँक तपशील फक्त अधिकृत सुरक्षित पोर्टलवर, मागितल्यास"],"fee":"अनेक शिष्यवृत्ती अर्ज विनामूल्य असतात; तरी योजनेची अट तपासा. अनधिकृत एजंटला पैसे देऊ नका."},
"pension": {"title":"पेन्शन", "steps":["संबंधित पेन्शन योजना आणि विभाग ओळखा.","नवीन, थांबलेली किंवा पुन्हा सुरू करायची पेन्शन यासाठीचे नियम तपासा.","योजनेनुसार नोंदी आणि संदर्भ/नोटीस क्रमांक तयार ठेवा.","अधिकृत मार्गाने किंवा अधिकृत कार्यालयात विनंती सादर करा आणि पोचपावती घ्या."],"docs":["अधिकृत मार्गाने ओळखपत्र","योजना/पेन्शन संदर्भ क्रमांक","अधिकृतरीत्या आवश्यक असल्यास बँक पुरावा","वय/दिव्यांगत्व/अवलंबित्व किंवा योजनेनुसार आवश्यक पुरावा"],"fee":"अधिकृत शुल्काची खात्री करा. अनधिकृत पैसे मागितल्यास सावध राहा."},
"pan": {"title":"पॅन कार्ड", "steps":["आयकर विभागाचे अधिकृत पोर्टल किंवा अधिकृत पॅन सेवा प्रदाता वापरा.","तुमच्या परिस्थितीनुसार नवीन पॅन किंवा दुरुस्ती निवडा.","सुरक्षित ओळख पडताळणी आणि कागदपत्रांच्या सूचनांचे पालन करा.","पोचपावती क्रमांक जतन करा."],"docs":["सेवा प्रदात्याने मान्य केलेला ओळख पुरावा","जन्मतारखेचा पुरावा","मागितलेला पत्ता/संपर्क तपशील"],"fee":"अर्जाचा प्रकार आणि वितरण पर्यायानुसार शुल्क बदलते; पैसे भरण्यापूर्वी अधिकृत चेकआउट तपासा."},
"property-tax": {"title":"मालमत्ता कर दुरुस्ती", "steps":["तुमची महानगरपालिका/स्थानिक संस्था आणि मालमत्ता खाते क्रमांक ओळखा.","कर बिल मिळवा आणि चुकीचा तपशील नोंदवा.","अधिकृत पोर्टल किंवा अधिकृत प्रभाग कार्यालयात दुरुस्तीची विनंती द्या.","विनंतीची प्रत आणि पोचपावती जतन करा."],"docs":["मालमत्ता कर बिल/खाते क्रमांक","दुरुस्तीला आधार देणारा पुरावा","मागितल्यास मालकी/ताब्याच्या नोंदी","संपर्क तपशील"],"fee":"दुरुस्ती शुल्क असल्यास ते स्थानिक संस्थेनुसार बदलते; आधी खात्री करा."},
"birth": {"title":"जन्म प्रमाणपत्र", "steps":["जन्म नोंदीसाठी जबाबदार महानगरपालिका/स्थानिक निबंधक ओळखा.","गरजेनुसार नवीन नोंदणी, प्रमाणपत्राची प्रत किंवा दुरुस्ती निवडा.","रुग्णालय/पालक/नोंदीसंबंधी आवश्यक कागदपत्रे तपासा.","स्थानिक संस्थेकडे अर्ज करा आणि पोचपावती जतन करा."],"docs":["रुग्णालय/नोंदणीची नोंद, उपलब्ध असल्यास","आवश्यकतेनुसार पालक/अर्जदाराचे ओळखपत्र","दुरुस्तीसाठी विद्यमान प्रमाणपत्र किंवा नोंदणी क्रमांक"],"fee":"शुल्क आणि उशिरा नोंदणीची प्रक्रिया स्थानिक संस्थेनुसार बदलते. अधिकृत पुष्टी घ्या."}
}}

def _localized_answer(key, language):
    lang = "Hindi" if str(language).lower() in {"hindi", "hi", "हिन्दी", "हिंदी"} else "Marathi"
    translations = LOCALIZED[lang]
    if key not in translations:
        if lang == "Hindi":
            return "मैं आय, निवास, जाति प्रमाणपत्र, छात्रवृत्ति, पेंशन, पैन, संपत्ति कर और जन्म प्रमाणपत्र में मदद कर सकता हूँ। कृपया सेवा का नाम बताएँ। आधिकारिक जानकारी के लिए https://aaplesarkar.mahaonline.gov.in/ देखें। नियम और शुल्क बदल सकते हैं। इस चैट में आधार नंबर, OTP, पासवर्ड या बैंक विवरण साझा न करें।"
        return "मी उत्पन्न, रहिवासी, जात प्रमाणपत्र, शिष्यवृत्ती, पेन्शन, पॅन, मालमत्ता कर आणि जन्म प्रमाणपत्राबाबत मदत करू शकतो. कृपया सेवेचे नाव सांगा. अधिकृत माहितीसाठी https://aaplesarkar.mahaonline.gov.in/ पहा. नियम व शुल्क बदलू शकतात. या चॅटमध्ये आधार क्रमांक, OTP, पासवर्ड किंवा बँक तपशील शेअर करू नका."
    item = translations[key]
    lines = [f"{item['title']} — सामान्य मार्गदर्शन", "", "पुढील पायऱ्या:" if lang == "Marathi" else "आवेदन के चरण:"]
    lines += [f"{i}. {step}" for i, step in enumerate(item["steps"], 1)]
    lines += ["", "सामान्य कागदपत्रे (प्रकरणानुसार बदलू शकतात):" if lang == "Marathi" else "सामान्य दस्तावेज़ (आपके मामले में बदल सकते हैं):"]
    lines += [f"• {doc}" for doc in item["docs"]]
    lines += ["", f"शुल्क: {item['fee']}", "", "अधिकृत पोर्टल: https://aaplesarkar.mahaonline.gov.in/", "OTP, पासवर्ड, आधार क्रमांक किंवा ओळखपत्रांचे फोटो या चॅटमध्ये शेअर करू नका." if lang == "Marathi" else "सुरक्षा: इस चैट में OTP, पासवर्ड, आधार नंबर या पहचान दस्तावेज़ों की तस्वीरें साझा न करें."]
    return "\n".join(lines)
