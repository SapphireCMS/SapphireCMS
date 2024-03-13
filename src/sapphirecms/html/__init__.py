import sys, html

import pygments.util
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter

class Element:
    """
    Represents an HTML element.

    Attributes:
        name (str): The name of the element.
        paired (bool): Indicates whether the element is paired (has opening and closing tags).
        attributes (list): The list of attributes for the element.
        children (list): The list of child elements.
        styles (list): The list of styles for the element.
    """

    name = "element"
    paired = True

    def __init__(self, children=None, *args, **kwargs):
        """
        Initializes a new instance of the Element class.

        Args:
            *args: Variable length argument list for attributes.
            **kwargs: Arbitrary keyword arguments.
                children (list): The list of child elements.
                styles (list): The list of styles for the element.
        """
        self.attributes = list(args)
        
        if self.paired:
            self.children = []
            if type(children) != list:
                children = [children]
            if type(children) == str:
                children = children
            def flatten(l):
                for el in l:
                    if isinstance(el, list):
                        yield from flatten(el)
                    else:
                        yield el
            self.children = list(flatten(children))
        self.styles = kwargs.pop("styles", [])
        self.classes = kwargs.pop("classes", [])
        if type(self.classes) == list:
            self.classes = " ".join(self.classes)
        for key, value in kwargs.items():
                self.attributes.append(f'{key}="{value}"')

    def __iadd__(self, other):
        """
        Adds a child element to the current element.

        Args:
            other (Element): The child element to be added.

        Returns:
            Element: The updated element with the added child.
        """
        if isinstance(other, Element):
            self.children.append(other)
        if isinstance(other, str):
            escaped = html.escape(other)
            self.children.append(escaped)
        return self

    def __str__(self):
        """
        Returns the string representation of the element.

        Returns:
            str: The string representation of the element.
        """
        attrs = " " + (" ".join(self.attributes)) if len(self.attributes) > 0 else ""
        if type(self.classes) == list:
            classes = " ".join(self.classes)
            attrs += f' class="{classes}"'
        elif self.classes:
            attrs += f' class="{self.classes}"'
        return f"<{self.name}{attrs}>{''.join([str(child) for child in self.children])}</{self.name}>" if self.paired else f"<{self.name}{attrs}>"

    def __repr__(self):
        """
        Returns the string representation of the element.

        Returns:
            str: The string representation of the element.
        """
        return str(self)
    
    def render(self):
        """
        Renders the element.

        Returns:
            str: The rendered element.
        """
        return str(self)
    
    def prerender(self):
        """
        Prerenders the child elements.
        """
        self.children = [child.prerender() if isinstance(child, Element) else child for child in self.children]
    
    def prerendered(self):
        """
        Returns the prerendered element.

        Returns:
            str: The prerendered element.
        """
        return self.__class__(*self.attributes, children=''.join([str(child) for child in self.children]), styles=self.styles, classes=self.classes)
    
    def queryId(self, id):
        """
        Returns the element with the specified id.

        Args:
            id (str): The id of the element to be returned.

        Returns:
            Element: The element with the specified id.
        """
        if "id" in self.attributes and self.attributes["id"] == id:
            return self
        for child in self.children:
            if isinstance(child, Element):
                result = child.queryId(id)
                if result:
                    return result
                
    def queryClass(self, class_):
        """
        Returns the elements with the specified class.

        Args:
            class_ (str): The class of the elements to be returned.

        Returns:
            list: The elements with the specified class.
        """
        result = []
        if "classes" in self.attributes and class_ in self.attributes["classes"].split(" "):
            result.append(self)
        for child in self.children:
            if isinstance(child, Element):
                result.extend(child.queryClass(class_))
        return result
    
    @property
    def selector(self):
        """
        Returns the CSS selector for the element.

        Returns:
            str: The CSS selector for the element.
        """
        return f"{self.name}{''.join([f'[{attr}]' for attr in self.attributes])}" if 'id' not in self.attributes else f"#{self.attributes['id']}"

class Page:
    """
    Represents an HTML page.

    Attributes:
        tree (Element): The root element of the page.
    """
    
    tree = Element()
    
    def __init__(self, *args, **kwargs):
        """
        Initializes a new instance of the Page class.

        Args:
            *args: Variable length argument list for attributes.
            **kwargs: Arbitrary keyword arguments.
                children (list): The list of child elements.
                styles (list): The list of styles for the element.
        """
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __str__(self):
        """
        Returns the string representation of the page.

        Returns:
            str: The string representation of the page.
        """
        return f"<!DOCTYPE html>{str(self.tree)}"

    def __repr__(self):
        """
        Returns the string representation of the page.

        Returns:
            str: The string representation of the page.
        """
        return str(self)

    def render(self):
        """
        Renders the page.

        Returns:
            str: The rendered page.
        """
        return str(self)

    def prerender(self):
        """
        Prerenders the page.

        Returns:
            str: The prerendered page.
        """
        if type(self.tree) == Element:
            self.tree = self.tree.render()
        elif type(self.tree) == list:
            self.tree = [child.render() if isinstance(child, Element) else child for child in self.tree]
        elif type(self.tree) == str:
            pass
        else:
            raise TypeError(f"Invalid type {type(self.tree)} for tree attribute")
    
    def prerendered(self):
        """
        Returns the prerendered page.

        Returns:
            str: The prerendered page.
        """
        if type(self.tree) == Element:
            self.tree = self.tree.render()
        elif type(self.tree) == list:
            return Page([child.render() if isinstance(child, Element) else child for child in self.tree])
        elif type(self.tree) == str:
            pass
        else:
            raise TypeError(f"Invalid type {type(self.tree)} for tree attribute")
    
    def queryId(self, id):
        """
        Returns the element with the specified id.

        Args:
            id (str): The id of the element to be returned.

        Returns:
            Element: The element with the specified id.
        """
        return self.tree.queryId(id)
    
    def queryClass(self, class_):
        """
        Returns the elements with the specified class.

        Args:
            class_ (str): The class of the elements to be returned.

        Returns:
            list: The elements with the specified class.
        """
        return self.tree.queryClass(class_)

all_tags = ["a", "abbr", "address", "area", "article", "aside", "audio", "b", "base", "bdi", "bdo", "blockquote", "body", "br", "button", "canvas", "caption", "cite", "code", "col", "colgroup", "command", "datalist", "dd", "del", "details", "dfn", "div", "dl", "dt", "em", "embed", "fieldset", "figcaption", "figure", "footer", "form", "h1", "h2", "h3", "h4", "h5", "h6", "head", "header", "hgroup", "hr", "html", "i", "iframe", "img", "input", "ins", "kbd", "keygen", "label", "legend", "li", "link", "map", "mark", "math", "menu", "meta", "meter", "nav", "noscript", "object", "ol", "optgroup", "option", "output", "p", "param", "pre", "progress", "q", "rp", "rt", "ruby", "s", "samp", "script", "section", "select", "small", "source", "span", "strong", "style", "sub", "summary", "sup", "svg", "table", "tbody", "td", "textarea", "tfoot", "th", "thead", "time", "title", "tr", "track", "u", "ul", "var", "video", "wbr"]
paired_tags = ["a", "abbr", "address", "article", "aside", "audio", "b", "bdi", "bdo", "blockquote", "body", "button", "canvas", "caption", "cite", "code", "colgroup", "command", "datalist", "dd", "del", "details", "dfn", "div", "dl", "dt", "em", "fieldset", "figcaption", "figure", "footer", "form", "h1", "h2", "h3", "h4", "h5", "h6", "head", "header", "hgroup", "html", "i", "iframe", "ins", "kbd", "label", "legend", "li", "map", "mark", "math", "meter", "menu", "nav", "noscript", "object", "ol", "optgroup", "option", "output", "p", "pre", "progress", "q", "rp", "rt", "ruby", "s", "samp", "script", "section", "select", "small", "span", "strong", "style", "sub", "summary", "sup", "svg", "table", "tbody", "td", "textarea", "tfoot", "th", "thead", "time", "title", "tr", "u", "ul", "var", "video"]
unpaired_tags = ["area", "base", "br", "col", "embed", "hr", "img", "input", "keygen", "link", "meta", "param", "source", "track", "wbr"]


def code_block(code, language="python", colorscheme="default"):
    try:
        lexer = get_lexer_by_name(language, stripall=True)
    except pygments.util.ClassNotFound:
        raise NotImplementedError(f"Language '{language}' not supported.")
    formatter = HtmlFormatter(linenos=True, cssclass="code-block")
    return f"<code>{highlight(code, lexer, formatter)}</code>"

def initialize(context_name):
    for tag in paired_tags:
        setattr(sys.modules[context_name], tag, type(tag, (Element,), {"name": tag, "paired": True}))
        
    for tag in unpaired_tags:
        setattr(sys.modules[context_name], tag, type(tag, (Element,), {"name": tag, "paired": False}))
    
    setattr(sys.modules[context_name], "Page", Page)
    setattr(sys.modules[context_name], "code_block", code_block)