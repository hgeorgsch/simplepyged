#-*- coding: utf-8 -*-
# $Id$

"""
This module provides the a Builder class for LaTeX output,
designed to work in a Builder pattern with the report generator
from the :mod:`report` module.
"""

import codecs

def bib_escape(x):
   return x.replace( "&", " and " )
def char_escape(x):
   return x.replace( "&", "\\&" ).replace( "%", "\\%" ).replace( "_", "\\_" ).replace( "#", "\\#" ).replace( ". ", ".\\ " ).replace( u"død", u"$\dagger$" )
def url_escape(x):
   if hasattr(x, 'replace' ):
       return x.replace( "#", "\\#" ).replace( "%", "\\%" ) ;
   else:
       return [ url_escape(y) for y in x ]

class texBuilder(object):
   llpackage = u"llbook"
   author = u"Hans Georg Schaathun"
   title = ""
   bibstyle = "plain"
   newperiod = True
   newsentence = False
   def __init__(self,file,title=""):
      self._sectiontype = "section"
      self._parsefilename(file)
      self.title = title

   def _parsefilename(self,file):
      f = file.split( "." )
      if len(f) > 1: bf = "".join(f[:-1])
      else: bf = file
      self.file    = codecs.open( file, "w", "UTF-8" )
      self.bibfile = codecs.open( bf + ".bib", "w", "UTF-8" )
      self.basename = bf

   def preamble(self,h=None,preamble=None):
       if preamble: self.file.write( preamble )
       else: self.file.write(
            u"\\documentclass[combine,nynorsk,pdftex,twocolumn,10pt,oneside]{scrartcl}\n"
            + u"\\pagestyle{myheadings}\n\n"
            + u"\\usepackage{" + self.llpackage + "}\n"
            + u"\\xdef\AncDec{Ancestors}\n\n"
            + u"\\begin{document}\n\n"
            + u"\\author{" + self.author + "}\n"
            + u"\\title{" + h + "}\n"
            + u"\\maketitle\n" )

   def postamble(self,txt=None):
      """
      Write necessary material to complete the report and close
      the files.
      """
      if txt:
         self.file.write( txt )
      else:
         self.file.write( "\\bibliographystyle{%s}\n" % (self.bibstyle,) )
         self.file.write( "\\bibliography{%s}\n" % (self.basename,) )
         self.file.write( "\\end{document}\n" )
      self.file.close()
      self.bibfile.close()
   def put_url(self,url,text="link"): 
       print(url)
       url = url_escape(url)
       self.file.write( "\\href{%s}{%s}" % (url,text,) )
   def put_cite(self,ref,page=None,media=[],quot=[],fq=[]): 
      ms = [ "\\href{" + url_escape(m) + "}{\\textcolor{magenta}{\\ding{253}}}"
             for m in media ]
      if page:
         ps = ", ".join(page)
      else: 
         ps = ""
      s = "".join( ms )
      if not ps:
         texstring = " \\cite{%s}" % (ref,)
      elif len(ps) < 20:
         texstring = " \\cite[%s]{%s}" % (ps,ref,) 
      else:
         texstring = " \\footnote{\\cite{%s} %s.}\n" % (ref, ps + " " +s) 
      if ms: texstring += s 
      if quot:
          qs = [ q.value_cont() for q in quot ]
          qs = [ q for q in qs if q[:7] != "http://" ]
          qs = [ q for q in qs if q[:7] != "Http://" ]
          for q in qs:
              self.put_quot_s()
              self.file.write( char_escape(q) )
              self.put_quot_m()
              self.file.write( texstring )
              self.put_quot_e()
      elif fq:
          qs = [ q.value_cont() for q in fq ]
          qs = [ q for q in qs if q[:7] != "http://" ]
          qs = [ q for q in qs if q[:7] != "Http://" ]
          for q in qs:
              self.file.write( u"\\footnote{«%\n" )
              self.file.write( char_escape(q)+u"»\n" )
              self.file.write( texstring + "}" )
      else:
         self.file.write( texstring )
      return
   def put_comment(self,x):
      if x == None: return 
      self.file.write( "% " + str(x) + "\n" )
   def put_name(self,fn,sn,key=None,ref=None): 
      if ref == None: s = "%s \\textsc{%s}" % (fn,sn,)
      else: s =  "%s \\textsc{%s} (\\textsc{%s})" % (fn,sn,ref)
      self.file.write( s )
      self.newperiod = False
   def put_phead(self,fn,sn,no,key): 
      self.file.write( "\\PersonHeader{%s}{%s %s}{%s}\n\n" % (no,fn,sn,key) )
   def put_phead_repeat(self,fn,sn,no,ref,key): 
      self.file.write( "\\PersonRepeat{%s}{%s}{%s %s}\n\n" % (ref,no,fn,sn) )
   def put_subheader(self,header):
      self.file.write( "\\paragraph{%s}\n" % (header,) )
   def put_shead_s(self):
      self.file.write( "\\" + self._sectiontype + "*{" )
   def put_shead_e(self):
      self.file.write( "}\n" )
   def put_shead(self,title=""):
      self.file.write( "\\" + self._sectiontype + "*{" + title + "}\n" )
   def put_chead(self,title=""):
      self.file.write( "\\chapter{" + title + "}\n" )
   def put_item_s(self):
      self.file.write( "  \\item " )
   def put_item_e(self): 
      self.file.write( "\n" )
   def put_enum_s(self,n=None): 
      self.file.write( "\\begin{enumerate}\n" )
      if not n is None:
         self.file.write( "\\setcounter{enumi}{" + str(n) + "}\n" )
   def put_enum_e(self): 
      self.file.write( "\\end{enumerate}\n" )
   def put_quot_s(self): 
      self.file.write( u"\\begin{quoting}\n«" )
   def put_quot_m(self): 
      self.file.write( u"»\n" )
   def put_quot_e(self): 
      self.file.write( u"\\end{quoting}\n" )
   def put_foot_s(self):
      self.file.write( "\\footnote{" )
   def put_foot_e(self): 
      self.file.write( "}\n" )
   def put_dagger(self):
      self.file.write( "$\\dagger" )
   def end_paragraph(self):
      self.file.write( "\n\n" )
      self.newperiod = True
      self.newsentence = False
   def end_sentence(self):
      self.newsentence = True
   def end_period(self,p="."):
      if not self.newperiod:
         self.file.write( p + "\n" )
         self.newperiod = True
         self.newsentence = False
   def put(self,x):
      if x == None: return 
      try:
         idx = x.find( u"http://" )
      except:
         print(x)
      if idx >= 0:
          s = char_escape(x[:idx]) 
          if self.newperiod: 
              s = capFirst(s)
              self.newperiod = False
          elif self.newsentence:
              s = ", " + s
          self.file.write( char_escape(x[:idx]) )
          x = x[idx:].split(None,1)
          if len(x) > 1:
             (url,x) = x
             self.put_url(url)
             self.put( x )
          else:
             self.put_url(x)
      else:
          if self.newperiod: 
              x = capFirst(x)
              self.newperiod = False
          elif self.newsentence:
              x = ", " + x
              self.newsentence = False
          else: x = " " + x
          try:
              self.file.write( char_escape(x) )
          except:
              print(x)
   def put_image( self, obj ):
          t = obj.get_title()
          f = obj.get_file()
          if not t: t = ""
          self.put_imagefloat(t,f,obj.xref())
   def put_imagefloat( self, title, file, label=None ):
      self.file.write( "\\begin{imagefloat}\n" )
      self.file.write( "\\begin{center}\n" )
      self.file.write( "\\includegraphics[width=0.84\\columnwidth]{" + file + "}\n" )
      self.file.write( "\\end{center}\n" )
      self.file.write( "\\caption{" + char_escape( title ) + "}\n" )
      if label: self.file.write( "\\label{" + label + "}\n" )
      self.file.write( "\\end{imagefloat}\n" )
      if label: self.file.write( "\\imgref{" + label + "}" )

   def put_bib( self, source ):
      self.bibfile.write( makeBibtex( source ) )
   def put_abstract_s( self ):
      self.file.write( "\\begin{abstract}\n" )
   def put_abstract_e( self ):
      self.file.write( "\\end{abstract}\n" )

def makeBibtexMisc( xref, author=None, title=None, url=None, publication=None, notes=None, media=[] ):
      r = "@misc{" + xref + ",\n" 
      if author != None:
         r += "  author = {" + bib_escape(author) + "},\n"
      if title != None:
         r += "   title = {{" +  char_escape(title) + "}},\n"
      if publication != None: n = char_escape(publication) 
      else: n = ""
      n += "".join( media )
      if n: r += "  note = {" + n + "},\n"
      if url != None:
         r += "     url = {" + url + "},\n"
      # TODO: Handle notes and URL
      r += "}\n" 
      return r
def makeBibtex( source ):
    bibtex = source.children_single_tag( "_TEX" )
    ms = source.children_tags( "OBJE" )
    ms = filter( lambda x : x, [ x.get_url() for x in ms ] )
    media = [ "\\href{" + url_escape(m) + "}{\\textcolor{magenta}{\\ding{253}}}"
             for m in ms ]
    if bibtex == None:
        author = source.children_single_val( "AUTH" )
        title  = source.children_single_val( "TITL" )
        pub    = source.children_single_val( "PUBL" )
        xref   = source.xref()
        return makeBibtexMisc( xref, author=author, title=title, publication=pub, media=media )
    else:
        return "@" + bibtex.value_cont()

def capFirst(s):
    if len(s) < 2: return s.capitalize()
    else: return s[0].capitalize() + s[1:]

class texChapterBuilder(texBuilder):
   def __init__(self,file,title="",headertype="chapter"):
      self._sectiontype = "section"
      self._parsefilename(file)
      self.title = title
      self.headertype = headertype
      if headertype != "chapter": self._sectiontype = "subsection"
   def preamble(self,h=None):
       if h:
          self.file.write( u"\\" + self.headertype + "{" + h + "}\n")

   def postamble(self):
      """
      Write necessary material to complete the report and close
      the files.
      """
      self.file.close()
      self.bibfile.close()
