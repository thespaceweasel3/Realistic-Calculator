from PIL import Image
import os
keys = ['7','+','=', 'C']
base = os.path.join(os.path.expanduser('~'), 'keycaps')
for k in keys:
    safe = {'+':'plus','=':'equals','C':'C','7':'7'}.get(k,k)
    fn = os.path.join(base, f'keycap_{safe}.png')
    print('\n---', fn)
    if not os.path.exists(fn):
        print('MISSING')
        continue
    im = Image.open(fn)
    print('mode,size:', im.mode, im.size)
    try:
        bbox = im.getbbox()
    except Exception as e:
        bbox = None
    print('bbox:', bbox)
    # check alpha presence
    alpha = None
    if im.mode in ('RGBA','LA'):
        alpha = im.split()[-1]
        # compute bounding box of non-transparent pixels
        nontrans = alpha.getbbox()
        print('alpha non-transparent bbox:', nontrans)
    else:
        print('no alpha channel')
    # sample top-left/top-center pixels
    w,h = im.size
    samples = [(0,0),(w//2,0),(w-1,0),(0,h-1),(w//2,h//2)]
    for (x,y) in samples:
        try:
            px = im.getpixel((x,y))
        except Exception as e:
            px = None
        print('pixel', (x,y), px)
print('\nInspector done')
