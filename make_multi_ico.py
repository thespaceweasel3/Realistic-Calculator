from PIL import Image

src = 'generated_icon.png'
out = 'calculator_multi.ico'
try:
    im = Image.open(src).convert('RGBA')
except Exception as e:
    raise SystemExit(f'Failed to open {src}: {e}')
# ensure large enough
base = im
if im.size[0] < 256:
    base = im.resize((256,256), Image.LANCZOS)
sizes = [(16,16),(24,24),(32,32),(48,48),(64,64),(128,128),(256,256)]
base.save(out, sizes=sizes)
print('WROTE', out)
