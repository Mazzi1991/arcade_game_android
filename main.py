import sys
import os
import traceback

def custom_excepthook(exc_type, exc_value, exc_traceback):
    msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    try:
        from android.storage import primary_external_storage_path
        doc_dir = os.path.join(primary_external_storage_path(), "Documents")
        os.makedirs(doc_dir, exist_ok=True)
        with open(os.path.join(doc_dir, "kivy_test_crash.txt"), "w") as f:
            f.write("KIVY CRASH:\n" + msg)
    except:
        pass
    sys.__excepthook__(exc_type, exc_value, exc_traceback)
    sys.exit(1)

sys.excepthook = custom_excepthook

import kivy
kivy.require('2.3.0')
from kivy.app import App
from kivy.uix.label import Label
from kivy.core.window import Window

class TestApp(App):
    def build(self):
        Window.clearcolor = (0, 0.5, 0, 1) # Green background so we know it worked
        return Label(
            text="Kivy funciona!\nEl problema es Pygame/SDL2", 
            font_size='30sp',
            halign='center'
        )

if __name__ == '__main__':
    TestApp().run()
