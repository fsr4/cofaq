from html.parser import HTMLParser
from io import StringIO


class CoronaNewsParser(HTMLParser):
    def error(self, message):
        pass

    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.text = StringIO()
        self.inside_main = False

    def handle_starttag(self, tag, attrs):
        if tag == "main":
            self.inside_main = True

    def handle_endtag(self, tag):
        if tag == "main":
            self.inside_main = False

    def handle_data(self, d):
        if self.inside_main:
            d = d.strip()
            if d != "":
                self.text.write(d + "\n")

    def get_data(self):
        return self.text.getvalue()
