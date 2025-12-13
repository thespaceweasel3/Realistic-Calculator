from PIL import Image

ico_path = 'calculator_multi.ico'
out_path = 'generated_multi.png'
try:
    im = Image.open(ico_path)
    print('FORMAT', im.format, 'SIZE', im.size)
    # save the largest frame (Pillow returns first frame by default)
    im.save(out_path)
    print('WROTE', out_path)
except Exception as e:
    print('ERROR', e)
    raise SystemExit(1)
