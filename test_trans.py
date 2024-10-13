from googletrans import Translator

# Khởi tạo Translator
translator = Translator()

# Văn bản tiếng Việt cần dịch
text = "Xin chào, bạn khỏe không?"

# Dịch sang tiếng Anh
translated = translator.translate(text, src='vi', dest='en')

print("Tiếng Việt:", text)
print("Tiếng Anh:", translated.text)
