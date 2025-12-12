import importlib.util
spec = importlib.util.spec_from_file_location('calcmod', r'c:\workspace\calculator.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
# instantiate the Calculator (this creates a Tk root but we won't call mainloop)
calc = mod.Calculator()
# call the generator
calc._prepare_keycap_images()
print('GENERATION_DONE')
