# type: ignore[a,abbr,address,area,article,aside,audio,b,base,bdi,bdo,blockquote,body,br,button,canvas,caption,cite,code,col,colgroup,command,datalist,dd,del,details,dfn,div,dl,dt,em,embed,fieldset,figcaption,figure,footer,form,h1,h2,h3,h4,h5,h6,head,header,hgroup,hr,html,i,iframe,img,input,ins,kbd,keygen,label,legend,li,link,map,mark,math,menu,meta,meter,nav,noscript,object,ol,optgroup,option,output,p,param,pre,progress,q,rp,rt,ruby,s,samp,script,section,select,small,source,span,strong,style,sub,summary,sup,svg,table,tbody,td,textarea,tfoot,th,thead,time,title,tr,track,u,ul,var,video,wbr]
from sapphirecms.html import initialize, Element, Page
import unittest
from halo import Halo


class TestHTML(unittest.TestCase):
    def test_single_tag(self):
        self.assertEqual(html("Hello, World!").render(), "<html>Hello, World!</html>")
        
    def test_nested_tags(self):
        self.assertEqual(html(head(title("Hello, World!"))).render(), "<html><head><title>Hello, World!</title></head></html>")
        
    def test_attributes(self):
        self.assertEqual(a("Hello, World!", href="https://www.example.com").render(), '<a href="https://www.example.com">Hello, World!</a>')
        
    def test_css(self):
        self.assertEqual(div("Hello, World!", style="color: red;").render(), '<div style="color: red;">Hello, World!</div>')
        
    def test_js(self):
        self.assertEqual(script("alert('Hello, World!');").render(), '<script>alert(\'Hello, World!\');</script>')
        
    def test_custom_tags(self):
        custom = type('custom', (Element,), {"name": 'custom', "paired": True})
        self.assertEqual(custom("Hello, World!").render(), "<custom>Hello, World!</custom>")
        
    def test_custom_tags_with_attributes(self):
        custom = type('custom', (Element,), {"name": 'custom', "paired": True})
        self.assertEqual(custom("Hello, World!", href="https://www.example.com").render(), '<custom href="https://www.example.com">Hello, World!</custom>')
        
    def test_custom_tags_with_css(self):
        custom = type('custom', (Element,), {"name": 'custom', "paired": True})
        self.assertEqual(custom("Hello, World!", style="color: red;").render(), '<custom style="color: red;">Hello, World!</custom>')
        
    def test_page(self):
        class myPage(Page):
            def __init__(self, pagetitle, content):
                self.tree = html([head(title(pagetitle)), body(content)])
        page = myPage("Hello, World!", "Hello, World!")
        self.assertEqual(page.render(), '<!DOCTYPE html><html><head><title>Hello, World!</title></head><body>Hello, World!</body></html>')
        self.assertEqual(page.render(), f"<!DOCTYPE html>{html([head(title('Hello, World!')), body('Hello, World!')])}")
        self.assertEqual(page.render(), f"<!DOCTYPE html>{page.tree}")
        
    def setUp(self):
        initialize(__name__)
        
    def runTest(self):
        print("Running HTML tests...")
        fails = 0
        with Halo(text="Running HTML.single_tag", spinner="dots2") as spinner:
            try:
                self.test_single_tag()
                spinner.succeed()
            except Exception as e:
                spinner.fail()
                fails += 1
        with Halo(text="Running HTML.nested_tags", spinner="dots2") as spinner:
            try:
                self.test_nested_tags()
                spinner.succeed()
            except Exception as e:
                spinner.fail()
                fails += 1
        with Halo(text="Running HTML.attributes", spinner="dots2") as spinner:
            try:
                self.test_attributes()
                spinner.succeed()
            except Exception as e:
                spinner.fail()
                fails += 1
        with Halo(text="Running HTML.css", spinner="dots2") as spinner:
            try:
                self.test_css()
                spinner.succeed()
            except Exception as e:
                spinner.fail()
                fails += 1
        with Halo(text="Running HTML.js", spinner="dots2") as spinner:
            try:
                self.test_js()
                spinner.succeed()
            except Exception as e:
                spinner.fail()
                fails += 1
        with Halo(text="Running HTML.custom_tags", spinner="dots2") as spinner:
            try:
                self.test_custom_tags()
                spinner.succeed()
            except Exception as e:
                spinner.fail()
                fails += 1
        with Halo(text="Running HTML.custom_tags_with_attributes", spinner="dots2") as spinner:
            try:
                self.test_custom_tags_with_attributes()
                spinner.succeed()
            except Exception as e:
                spinner.fail()
                fails += 1
        with Halo(text="Running HTML.custom_tags_with_css", spinner="dots2") as spinner:
            try:
                self.test_custom_tags_with_css()
                spinner.succeed()
            except Exception as e:
                spinner.fail()
                fails += 1
        with Halo(text="Running HTML.page", spinner="dots2") as spinner:
            try:
                self.test_page()
                spinner.succeed()
            except Exception as e:
                spinner.fail()
                fails += 1
                
        if fails == 0:
            print("All HTML tests passed.")
        else:
            print(f"{fails}/{9} HTML tests failed.")

        

if __name__ == "__main__":
    unittest.main()