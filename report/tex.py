#-*- coding: utf-8 -*-
# $Id$

import codecs

def char_escape(x):
   return x.replace( "&", "\\&" ).replace( "%", "\\%" ).replace( "_", "\\_" ).replace( "#", "\\#" )

class texBuilder(object):
   llpackage = u"llbook"
   author = u"Hans Georg Schaathun"
   title = ""
   def __init__(self,file):
     self.file = codecs.open( file, "w", "UTF-8" )

   def preamble(self,h):
     self.file.write(
	    u"\\documentclass[pdftex,twocolumn,10pt,oneside,titlepage]{book}\n"
            + u"\\pagestyle{myheadings}\n\n"
            + u"\\usepackage{" + self.llpackage + "}\n"
            + u"\\xdef\AncDec{Ancestors}\n\n"
            + u"\\begin{document}\n\n"
            + u"\\author{" + self.author + "}\n"
            + u"\\title{" + h + "}\n"
            + u"\\maketitle\n" )

   def postamble(self):
      # TODO: process references here
      self.file.write( "\\end{document}\n" )
      self.file.close()
   def put_url(self,url,text="link"): 
      self.file.write( "\\href{%s}{%s}" % (url,text,) )
   def put_cite(self,ref,page=None): 
      if page == None: self.file.write( "\\cite{%s}" % (ref,) )
      else: self.file.write( "\\cite[%s]{%s}" % (page,ref,) )
   def put_name(self,fn,sn,ref=None): 
      if ref == None: s = "%s \\textsc{%s}" % (fn,sn,)
      else: s =  "%s \\textsc{%s} (\\textsc{%s})" % (fn,sn,ref)
      self.file.write( s )
   def put_phead(self,fn,sn,no,key): 
      self.file.write( "\\PersonHeader{%s}{%s %s}{%s}\n\n" % (no,fn,sn,key) )
   def put_phead_repeat(self,fn,sn,no,ref): 
      self.file.write( "\\PersonRepeat{%s}{%s}{%s %s}\n\n" % (ref,no,fn,sn) )
   def put_subheader(self,header):
      self.file.write( "\\paragraph{%s}\n" % (header,) )
   def put_shead_s(self):
      self.file.write( "\\section*{" )
   def put_shead_e(self):
      self.file.write( "}\n" )
   def put_chead_s(self):
      self.file.write( "\\chapter{" )
   def put_chead_e(self):
      self.file.write( "}\n" )
   def put_item_s(self):
      self.file.write( "  \\item " )
   def put_item_e(self): 
      self.file.write( "\n" )
   def put_enum_s(self): 
      self.file.write( "\\begin{enumerate}\n" )
   def put_enum_e(self): 
      self.file.write( "\\end{enumerate}\n" )
   def put_quot_s(self): 
      self.file.write( u"\\begin{quotation}\n«" )
   def put_quot_e(self): 
      self.file.write( u"»\\end{quotation}\n" )
   def put_foot_s(self):
      self.file.write( "\\footnote{" )
   def put_foot_e(self): 
      self.file.write( "}\n" )
   def put_dagger(self):
      self.file.write( "$\\dagger" )
   def put_paragraph(self):
      self.file.write( "\n\n" )
   def put(self,x):
      # TODO: escape
      try:
         idx = x.find( u"http://" )
      except:
	 print x
      if idx >= 0:
         self.file.write( char_escape(x[:idx]) )
	 x = x[idx:].split(None,1)
	 if len(x) > 1:
	    (url,x) = x
	    self.put_url(url)
            self.put( x )
         else:
	    self.put_url(x)
      else:
	 try:
           self.file.write( char_escape(x) )
	 except:
	    print x
