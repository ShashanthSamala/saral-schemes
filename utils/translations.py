UI_STRINGS = {
    "en": {
        "title": "SARAL - Scheme Access Portal",
        "lang_select": "🌐 Choose Language",
        "load_data": "🔄 Load Schemes Data",
        "stats": "📊 Statistics",
        "total_schemes": "Total Schemes",
        "cached": "Cached Translations",
        "about": "ℹ️ About SARAL",
        "features": "🎯 Key Features",
        "tech_stack": "🛠️ Technology Stack"
    },
    "hi": {
        "title": "सरल - योजना एक्सेस पोर्टल",
        "lang_select": "🌐 भाषा चुनें",
        "load_data": "🔄 डेटा लोड करें",
        "stats": "📊 सांख्यिकी",
        "total_schemes": "कुल योजनाएं",
        "cached": "कैश की गई अनुवाद",
        "about": "ℹ️ सरल के बारे में",
        "features": "🎯 प्रमुख विशेषताएं",
        "tech_stack": "🛠️ तकनीकी स्टैक"
    },
    "te": {
        "title": "సరళ - పథకాల సమాచార పోర్టల్",
        "lang_select": "🌐 భాషను ఎంచుకోండి",
        "load_data": "🔄 పథకాల డేటాను లోడ్ చేయండి",
        "stats": "📊 గణాంకాలు",
        "total_schemes": "మొత్తం పథకాలు",
        "cached": "సేవ్ చేసిన అనువాదాలు",
        "about": "ℹ️ సరళ గురించి",
        "features": "🎯 ముఖ్యమైన ఫీచర్లు",
        "tech_stack": "🛠️ టెక్నాలజీ స్టాక్"
    },
    "ta": {
        "title": "எளிய - திட்டங்கள் அணுகல் போர்டல்",
        "lang_select": "🌐 மொழியைத் தேர்ந்தெடுக்கவும்",
        "load_data": "🔄 திட்டங்களின் தரவை ஏற்றவும்",
        "stats": "📊 புள்ளிவிவரங்கள்",
        "total_schemes": "மொத்த திட்டங்கள்",
        "cached": "சேமிக்கப்பட்ட மொழிபெயர்ப்புகள்",
        "about": "ℹ️ எளிய பற்றி",
        "features": "🎯 முக்கிய அம்சங்கள்",
        "tech_stack": "🛠️ தொழில்நுட்ப அடுக்கு"
    },
    "kn": {
        "title": "ಸರಳ - ಯೋಜನೆ ಪ್ರವೇಶ ಪೋರ್ಟಲ್",
        "lang_select": "🌐 ಭಾಷೆಯನ್ನು ಆಯ್ಕೆಮಾಡಿ",
        "load_data": "🔄 ಯೋಜನೆಯ ಡೇಟಾವನ್ನು ಲೋಡ್ ಮಾಡಿ",
        "stats": "📊 ಅಂಕಿಅಂಶಗಳು",
        "total_schemes": "ಒಟ್ಟು ಯೋಜನೆಗಳು",
        "cached": "ಸೇವ್ ಮಾಡಿದ ಅನುವಾದಗಳು",
        "about": "ℹ️ ಸರಳ ಬಗ್ಗೆ",
        "features": "🎯 ಪ್ರಮುಖ ಲಕ್ಷಣಗಳು",
        "tech_stack": "🛠️ ತಂತ್ರಜ್ಞಾನ ಸ್ಟಾಕ್"
    }
}

def t(key, lang):
    return UI_STRINGS.get(lang, UI_STRINGS["en"]).get(key, UI_STRINGS["en"].get(key, key))
