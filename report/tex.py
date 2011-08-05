# $Id$

class texBuilder(object):
   def put_url(self,url,text="link"): 
      print "\href{%s}{%s}" % (url,text,)
   def put_cite(self,ref): 
      print "\cite{%s}" % (ref,)
   def put_name(self,fn,sn,ref=None): 
      if ref == None: print "%s \textsc{%s}" % (fn,sn,),
      else: print "%s \textsc{%s} (\textsc{%s})" % (fn,sn,ref),
   def put_phead(self,fn,sn,no,key): 
      print "\PersonHeader{%s}{%s %s}{%s}" % (no,fn,sn,key)
   def put_phead_repeat(self,fn,sn,no,ref): 
      print "\PersonRepeat{%s}{%s}{%s %s}" % (ref,no,fn,sn)
   def put_subheader(self,header): print "\paragraph{%s}" %s (header,)
   def put_shead_s(self): print "\section{",
   def put_shead_e(self): print "}"
   def put_chead_s(self): print "\chapter{",
   def put_chead_e(self): print "}"
   def put_item_s(self): print "  \item ",
   def put_item_e(self): print
   def put_enum_s(self): print "\begin{enumerate}\n",
   def put_enum_e(self): print "\end{enumerate}\n"
   def put_quot_s(self): print "\begin{quotation}\n«",
   def put_quot_e(self): print "\end{quotation}\n»"
   def put_foot_s(self): print "\footnote{",
   def put_foot_e(self): print "}"
   def put_dagger(self):
      print "$\dagger"
   def put_paragraph(self):
      print "\n\n"
   def put(self,x):
      # TODO: escape
      print x,
