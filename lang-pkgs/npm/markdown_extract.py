from mistune import Renderer, Markdown

class PlaintextExtract(Renderer):
  # Block Level
  def block_code(self, code, language=None):
    # TODO: extract usable comment
    return ""
  def block_quote(self, text):
    # print "Block Quote: ", text
    return ""
  def block_html(self, html):
    return ""
  def header(self, text, level, raw=None):
    # print "Header Lvl #%d: " % level, text
    return ""
  def hrule(self):
    return ""
  def list(self, body, ordered=True):
    return body
  def list_item(self, text):
    return " %s " % text
  def paragraph(self, text):
    return " %s\n" % text
  def table(self, header, body):
    return ""
  def table_row(self, content):
    return ""
  def table_cell(self, content, **flags):
    return ""
  # Span Level
  def autolink(self, link, is_email=False):
    return ""
  def codespan(self, text):
    return text
  def double_emphasis(self, text):
    return text
  def emphasis(self, text):
    return text
  def image(self, src, title, alt_text):
    return "%s %s" % (title or "", alt_text or "")
  def linkbreak(self):
    # print "Line break"
    return ""
  def newline(self):
    # print "New line"
    return ""
  def link(self, link, title, content):
    return content or ""
  def strikethrough(self, text):
    return ""
  def text(self, text):
    return text
  def inline_html(self, text):
    # print "Inline HTML"
    return ""
  def footnote_ref(self, key, index):
    return ""
  def footnote_item(self, key, text):
    return ""
  def footnotes(self, text):
    return ""

__parser = [None]

def getParser():
  if __parser[0] is None:
    __parser[0] = Markdown(renderer = PlaintextExtract())
  return __parser[0]

def extractText(md):
  # print "Original", md
  return getParser()(md)

if __name__ == '__main__':
  import sys
  print extractText(sys.argv[1])
