from PIL import Image
import sys

ico_path = 'calculator.ico'
out_path = 'generated_icon.png'
try:
    img = Image.open(ico_path)
    print('FORMAT', img.format, 'SIZE', img.size)
    img.save(out_path)
    print('WROTE', out_path)
except Exception as e:
    print('ERROR', e)
    sys.exit(1)
