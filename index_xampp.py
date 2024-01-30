# coding=utf-8
""" index_xampp.py 
    Make Sanskrit-Lexicon home page FOR local installations.
"""
from __future__ import print_function
import sys,codecs
import re
import os
import xml.etree.cElementTree as ET
import string
# True means funded DFG-NEH Project 2010-2013
# False means not so funded
asteriskData = {"ACC":True , "AE":False , "AP":False , "AP90":True,
       "BEN":True , "BHS":True , "BOP":True , "BOR":True,
       "BUR":True , "CAE":False , "CCS":True , "GRA":True,
       "GST":True , "IEG":True , "INM":True , "KRM":True,
       "MCI":True , "MD":False , "MW":False , "MW72":True,
       "MWE":True , "PD":True , "PE":True , "PGN":True,
       "PUI":True , "PWG":False , "PW":False , "SCH":False,
       "SHS":False , "SKD":True , "SNP":True , "STC":True,
       "VCP":True , "VEI":True , "WIL":False , "YAT":True,
       "LAN":False, "ARMH":False, "LRV":False, "ABCH":False,
	"ACPH":False, "ACSJ":False}

def get_version():
 versionFile = os.path.join('..', 'csl-orig', '.version')
 with codecs.open(versionFile, 'r', 'utf-8') as fin:
   return fin.read().rstrip()

version = get_version()

class Scan(object):
 def __init__(self,e):
  self.pfx = e.find('pfx').text
  self.year = e.find('year').text
  self.title = e.find('title').text
  self.dsize = e.find('dsize').text
  self.dyear = e.find('dyear').text
  self.authors = e.find('authors').text
  textdate = e.find('textdate').text
  textpages = e.find('textpages').text
  m = re.search(r'^([0-9]+)',textdate)
  if m:
   textdate = m.group(1)
  self.textdate = textdate
  m = re.search(r'^([0-9]+)',textpages)
  if m:
   textpages = m.group(1)
  self.textpages = textpages
 def toStringdbg(self):
  parts = [
           "pfx=%s" % self.pfx,
           "title=%s" % self.title,
           "dsize=%s" % self.dsize,
           "dyear=%s" % self.dyear,
           "authors=%s" % self.authors,
           "textdate=%s" % self.textdate,
           "textpages=%s" % self.textpages,
           ]
  return ','.join(parts)
  
def parse_indexdirs(filein):
 "returns a dict of Scan objects, indexed by pfx"
 d = {} # returned
 parser = ET.XMLParser(encoding="utf-8")
 tree = ET.parse(filein,parser=parser)
 root = tree.getroot()
 for entry in root:
  rec = Scan(entry)
  d[rec.pfx]=rec
 return d

def headerdiv():
 """ Aug 1, 2018. clarin logo.
   Changed to use flexbox.
 """
 div ="""
 <div id="header" style="display:flex; flex-flow: row wrap; justify-content:space-between; width:89%; align-items:center;">
  <div class="child1">
  <img src="csl-homepage/cologne_univ_seal.gif" id="logo" alt="IITS" title="Cologne Sanskrit Lexicon"/>
  <br/>
  <span class="style19">
   UNIVERSIT&Auml;T ZU K&Ouml;LN <br />
  </span>
  </div>
  <div class="child2" >
  <span class="style1">Cologne Digital Sanskrit Dictionaries</span>
  </div>
  <div class="child3" >
   <a href="https://www.clarin.eu/" class="child3" target="_blank" >
    
    <img src="csl-homepage/clarin-400x400.png" 
       width="90px" height="90px"
       title="CLARIN - Common Language Resources and Technology Infrastructure &#013; [by European Research Infrastructure Consortium (ERIC)]">
   </a>
  </div>
  </div> <!-- header-->
  <hr style="width:89%; margin-left:0px;"/>

"""
 #lines = string.split(div, '\n\r') 
 lines = div.split('\n\r')
 return lines

def purpos1ediv():
 div ="""
 <div id="purpose1">
   <p>
     Welcome to the Sanskrit lexicons prepared since 1994 by the Institute of Indology and Tamil Studies, Cologne University.
   <br/>
  The 42 dictionaries are organized primarily by the secondary language (English, German, etc.), and then by date of publication (1832 till 1993).
  <br/>
  Each dictionary has several types of display (B L A M), as well as PDF scan and XML (in <a href="https://en.wikipedia.org/wiki/SLP1">SLP1</a>) files for download (D).
  <br/>
  All dictionaries are also available for offline usage in android phones via <a href="https://play.google.com/store/apps/details?id=sanskritcode.sanskritdictionaryupdater&hl=en" target="_blank">this application</a>. It presumes that some form of stardict viewer is installed on your phone. You may try to install stardict viewer by searching for EBdic, colordict, goldendict or stardict.
  </p>

   <p>
     <a href='csl-doc/build/index.html' target="_csldoc"><b>Documentation</b></a>
 <!--
   &nbsp; &nbsp;
     <b>New Displays: </b> &nbsp;
    <a href="//www.sanskrit-lexicon.uni-koeln.de/scans/awork/apidev/sample/list-0.2.html">(Dec 2016)</a>
   &nbsp; 
    <a href="//www.sanskrit-lexicon.uni-koeln.de/scans/awork/apidev/simple-search/v1.0/list-0.2s.html">(Dec 2017)</a>
 -->
   &nbsp; &nbsp;
<!--
   <a href="csl-apidev/simple-search/v1.0/list-0.2s_xampp.html"><b>Simple-Search</b></a>
-->
<!-- make use of .htaccess rewrite. In xampp, .htaccess is in /cologne/
 -->
    <a href="/cologne/simple/"><b>Simple-Search</b></a>
	&nbsp; &nbsp;
   <b>version """ + version + """</b> 
   &nbsp; &nbsp;
   <a href="https://github.com/sanskrit-lexicon/csl-newsletter/"><b>Newsletter</b></a>
   <span style="position:absolute;right:11%">
    Found an error? 
    <a href='csl-doc/build/contrib.html' target="_csldoc">
      <b>Help us on <img src="csl-homepage/github-9-16.gif">GitHub</b>
    </a>
   </span>
   </p> 

  </div>
"""
 #lines = string.split(div, '\n\r') 
 lines = div.split('\n\r')
 return lines

def make_link(href,title,text):
 return "<a href='%s' title='%s'>%s</a>" %(href,title,text)

def make_links(data):
 parts=[]
 for (href,title,text) in data:
  parts.append(make_link(href,title,text))
  parts.append("&nbsp;")
 return parts


def dict_line_extralinks(s):
 "return extra links"
 extradata = {
  'WIL':[
       ('/scans/WILScan/index.php?sfx=jpg','Scanned edition, jpg','S'),
       ('#deprecated','Deprecated','Deprecated')
       ],
  'MD':[
      ('/scans/MDScan/index.php?sfx=jpg','Scanned edition, jpg','S')
      ],
  'MW':[
      ('/scans/MWScan/index.php?sfx=pdf','Scanned edition, pdf','S1'),
      ('/scans/MWScan/index.php?sfx=jpg','Scanned edition, jpg','S2'),
      ('/talkMay2008/markingMonier.html','Marking-Monier','Markup'),
      ('#deprecated','Deprecated','Deprecated')
      ],
  'AE': [
      ('/scans/AEScan/index.php?sfx=pdf','Scanned edition, pdf','S1'),
      ('/scans/AEScan/index.php?sfx=jpg','Scanned edition, jpg','S2'),
      ('#deprecated','Deprecated','Deprecated')
      ],
  'PWG':[
      ('/pwgindex.html','Scanned edition','S'),
      ('#deprecated','Deprecated','Deprecated')
      ],
  'PW':[
      ('/pwindex.html','Scanned edition','S'),
      ('#deprecated','Deprecated','Deprecated')
      ],
  'SCH':[
      ('/scans/SCHScan/index.php','Scanned edition','S')
      ],
  'CCS':[
      ('/scans/CCSScan/index.php?sfx=png','Scanned edition','S')
      ],
  'CAE':[
      ('/scans/CAEScan/index.php?sfx=png','Scanned edition','S')
      ],
  'STC':[
      ('/scans/STCScan/index.php?sfx=jpg','Scanned edition','S'),
      ('/scans/STCScan/web/index_fr.php',u'semi-numérique','SD'),
      ],
  'PGN':[
      ('/scans/PGNScan/2014/web/webscan/index.php','Scanned edition','S')
      ]
 }

 if s.pfx in extradata:
  return make_links(extradata[s.pfx])
 else:
  return [] # no extra links for this pfx

def dict_line_links(s):
 """Return list of strings
    June 15: for AP,PD, return special message
 """
 if s.pfx in ['AP','PD']:
  message = "<i>available on special request for research purposes</i>"
  parts = [message]
  return parts
 # usual case : links to various displays
 #basedir = "/scans/%sScan/%s/web" % (s.pfx,s.year)
 basedir = "%s/web" % s.pfx.lower()
 data = [
  ('%s/webtc/indexcaller.php' % basedir,'Basic Display','B'),
  ('%s/webtc1/index.php' % basedir,'List Display','L'),
  ('%s/webtc2/index.php' % basedir,'Advanced Search','A'),
  ('%s/mobile1/index.php' % basedir,'Mobile-Friendly','M'),
  ('%s/webtc/download.html' % basedir,'Downloads','D')
 ]
 if s.pfx == 'STC':
  data = [
  ('%s/webtc/indexcaller_fr.php' % basedir,'Recherche simple','B'),
  ('%s/webtc1/index.php' % basedir,'Recherche par liste','L'),
  ('%s/webtc2/index.php' % basedir,u'Recherche avancée','A'),
  ('%s/mobile1/index.php' % basedir,u'Écran de recherche pour téléphones portables','M'),
  ('%s/webtc/download_fr.html' % basedir,u'Téléchargements','D')
  ]

 parts = make_links(data)
 for link in dict_line_extralinks(s):
  pass  # skip these in local installation
  #parts.append(link)
 return parts


def dict_line(s,title_in):
 "'s' is a Scan element. Returns a string."
 parts=[]
 if title_in != '':
  title = title_in
  title1=s.title
 else:
  title = s.title
  title1= s.title # ?
 pfx1 = s.pfx
 # June 5, 2015
 asterisk = ''
 if asteriskData[pfx1]:
  asterisk = ' <span title="funded by the DFG-NEH Project 2010-2013">*</span>'
 pfx1 = "%s%s" %(pfx1,asterisk)
 parts.append("  <td width='6%%'><span style='font-size:10px;'>%s</span></td>" % pfx1)
 parts.append("  <td width='6%%'><span style='font-size:10px;'>%s</span></td>" % s.textdate)

 #basedir = "/scans/%sScan/%s/web" % (s.pfx,s.year)
 basedir = "%s/web" %s.pfx.lower()
 titlelink = "<a href='%s/index.php'>%s</a>" %(basedir,title)
 if s.pfx == 'STC':
  titlelink = "<a href='%s/index_fr.php'>%s</a>" %(basedir,title)
 elif s.pfx == 'AP':
  basedir1 = "/scans/csl-homepage/ap_pd_samples"
  titlelink = "<a href='%s/ap-sample.php'>%s</a>" % (basedir1,title)
 elif s.pfx == 'PD':
  basedir1 = "/scans/csl-homepage/ap_pd_samples"
  titlelink = "<a href='%s/pd-sample.php'>%s</a>" % (basedir1,title)

 style = 'font-size:12pt;'
 if s.pfx in ['MW','AP90']:
  style = style + 'font-weight:bold;'
 parts.append("  <td width='58%%' style='%s' title='%s,%s,%s pages'>%s</td>" % (style,s.authors,title1,s.textpages,titlelink))

 parts.append("<td class='tdlist'>")
 for link in dict_line_links(s):
  parts.append(link)
 parts.append("</td>")
 try:
  ans = "\n   ".join(parts)
 except:
  print("ERROR JOINING")
  for part in parts:
   print("part = ",part)
  exit(1)
 return ans

def section_sort(pfxs,pfxdict):
 """ pfxs is a list of pairs (pfx,title)
 """
 def sortkey(t):
  (pfx,title)=t
  return pfxdict[pfx].textdate
 return sorted(pfxs,key = sortkey)

def table_headers():
 """ returns a string ( <tr><th></th>...</tr>) 
  compare dict_line
 """
 parts=[]
 bgcolor="#FFFFCC" #pale yellow
 bgcolor="#D3D3D3" #LightGray
 style = "background:%s; font-size=12px; font-weight:bold; font-color:black;text-align:left;" % bgcolor
 parts.append('<tr style="%s">' % style)
 parts.append('  <th>ID</th>')
 parts.append('  <th>date</th>')
 parts.append('  <th>Dictionary</th>')
 parts.append('  <th>Displays and Downloads</th>')

 parts.append('</tr>')
 return '\n'.join(parts)

def section_lines(pfxs,section_title,pfxdict):
 pfxs = section_sort(pfxs,pfxdict)
 lines = []
 lines.append('\n')
 colspan=4
 lines.append('<tr style="background:#FFFFCC"><td colspan="%s" style="vertical-align:center;"><h2>%s</h2></td></tr>' % (colspan,section_title))
 #add column titles for first one
 if section_title.startswith('Sanskrit-English'):
  lines.append(table_headers())
 for (pfx,title) in pfxs:
  lines.append('<tr style="background:#FFFFCC">%s</tr>' %dict_line(pfxdict[pfx],title))
 return lines

def san_english(pfxdict):
 pfxs = [
  ("AP90","Apte Practical Sanskrit-English Dictionary"),
  ("BEN","Benfey Sanskrit-English Dictionary"),
  #("BHS","Edgerton Buddhist Hybrid Sanskrit Dictionary"),
  ("CAE","Cappeller Sanskrit-English Dictionary"),
  ("GST",u"Goldstücker Sanskrit-English Dictionary"),
  ("MD","Macdonell Sanskrit-English Dictionary"),
  ("MW72","Monier-Williams Sanskrit-English Dictionary"),
  ("MW","Monier-Williams Sanskrit-English Dictionary"),
  ("SHS","Shabda-Sagara Sanskrit-English Dictionary"),
  ("WIL","Wilson Sanskrit-English Dictionary"),
  ("YAT","Yates Sanskrit-English Dictionary"),
  ("LAN","Lanman's Sanskrit Reader Vocabulary"),
  ("LRV","Vaidya Sanskrit-English Dictionary"),
  # skip these in local installations
  #("AP","Practical Sanskrit-English Dictionary, revised edition"),
  #("PD","An Encyclopedic Dictionary of Sanskrit on Historical Principles")
 ]
 section_title='Sanskrit-English Dictionaries'
 return section_lines(pfxs,section_title,pfxdict)

def english_san(pfxdict):
 pfxs=[
  ("AE","Apte Student's English-Sanskrit Dictionary"),
  ("MWE","Monier-Williams English-Sanskrit Dictionary"),
  ("BOR","Borooah English-Sanskrit Dictionary")
 ]
 section_title='English-Sanskrit Dictionaries'
 return section_lines(pfxs,section_title,pfxdict)

def san_french(pfxdict):
 pfxs=[
 ("BUR",u"Burnouf Dictionnaire Sanscrit-Français"),
 ("STC",u"Stchoupak Dictionnaire Sanscrit-Français")
  ]
 section_title='Sanskrit-French Dictionaries'
 return section_lines(pfxs,section_title,pfxdict)

def san_german(pfxdict):
 pfxs=[
  ("PW",u"Böhtlingk Sanskrit-Wörterbuch in kürzerer Fassung"),
  ("PWG",u"Böhtlingk and Roth Grosses Petersburger Wörterbuch"),
  ("SCH",u"Schmidt Nachträge zum Sanskrit-Wörterbuch"),
  ("CCS",u"Cappeller Sanskrit Wörterbuch"),
  ("GRA",u"Grassmann Wörterbuch zum Rig Veda")
 ]
 section_title='Sanskrit-German Dictionaries'
 return section_lines(pfxs,section_title,pfxdict)

def san_latin(pfxdict):
 pfxs = [
  ("BOP","Bopp Glossarium Sanscritum")
 ]
 section_title='Sanskrit-Latin Dictionaries'
 return section_lines(pfxs,section_title,pfxdict)

def san_san(pfxdict):
 pfxs_sandict=[
  ("SKD",""),
  ("VCP",""),
  ("ARMH",""),
  ("ABCH",""),
  ("ACPH",""),
  ("ACSJ",""),
 ]
 pfxs=pfxs_sandict
 #section_title='Sanskrit-Sanskrit Dictionaries and Concordances'
 section_title='Sanskrit-Sanskrit Dictionaries'
 return section_lines(pfxs,section_title,pfxdict)

def san_special(pfxdict):
 pfxs=[
  ("KRM",""),
  ("ACC","Aufrecht's Catalogus Catalogorum"),
  ("BHS","Edgerton Buddhist Hybrid Sanskrit Dictionary"),
  ("PUI",""),
  ("VEI",""),
  ("PE",""),
  ("MCI",""),
  ("SNP","Meulenbeld's Sanskrit Names of Plants"),
  ("PGN",""),
  ("IEG",""),
  ("INM","")
 ]
 section_title = 'Specialized Dictionaries'
 return section_lines(pfxs,section_title,pfxdict)

def deprecated_line(href,title):
 colspan=4
 return '<tr style="background:#FFFFCC"><td colspan="%s"><a href="%s">%s</a></td></tr>\n' % (colspan,href,title)

def deprecated(pfxdict):
 colspan=4
 lines=[]
 section_title = '<a id="deprecated">Deprecated Editions</a>'
 lines.append('\n')
 lines.append('<tr style="background:#FFFFCC"><td colspan="%s"><h2>%s</h2></td></tr>' % (colspan,section_title))
 def dl(h,t): # for convenience
  return deprecated_line(h,t)
 lines.append(dl('/scans/MWScan/2012/web/index.php','Monier-Williams Sanskrit-English Dictionary, 2012/2013 displays'))
 lines.append(dl('/monier/indexcaller.php','Monier-Williams Sanskrit-English Dictionary, 2008'))
 # removed next 09-23-2019
 #lines.append(dl('/mwquery/index.html','Monier-Williams Advanced Search, 2008'))
 lines.append(dl('/scans/MWScan/tamil/index.html','Sanskrit and Tamil  Dictionaries, 2005'))
 lines.append(dl('/scans/WILScan/web/index.php','Wilson Sanskrit-English Dictionary, semi-digitized edition, 2008'))
 # removed next 09-23-2019
 #lines.append(dl('/aequery/index.html','Apte English-Sanskrit Dictionary, 2007'))
 lines.append(dl('/scans/PWGScan/disp2/index.php','Boehtlingk &amp; Roth Sanskrit-German Dictionary, 2011'))
 lines.append(dl('/scans/PWScan/disp2/index.php','Boehtlingk + Schmidt Sanskrit-German Dictionary, 2012'))

 return lines

def misc():
 colspan=4
 lines=[]
 section_title = '<a">Miscellany</a>'
 lines.append('\n')
 lines.append('<tr style="background:#FFFFCC"><td colspan="%s"><h2>%s</h2></td></tr>' % (colspan,section_title))
 def dl(h,t): # for convenience
  return deprecated_line(h,t)
 # add these modules if they are installed
 # detect installation by whether the php program file exists.
 # Idea: We could use the Cologne installation if local installation does not
 # exist
 apps = [
  ('csl-kale/disp/index.php','Kale Higher Sanskrit Grammar, 1894 (Scanned)'),
  ('csl-westergaard/disp/index.php','Westergaard Linguae Sanscritae, 1841 (Scanned)'),
  ('csl-whitroot/disp/index.php',"Whitney's Roots, 1885 (Scanned)"),
  ('csl-inflect/web/index.php',"MW Inflected forms"),
  ('csl-santam/php/index.html','Sanskrit and Tamil  Dictionaries, 2005'),
 ]
 for applink,apptitle in apps:
  # this index_xampp.py file is in csl-homepage, and
  # the the app directories of siblings of csl-homepage. Hence "../" needed.
  if os.path.exists("../"+applink):
   lines.append(dl(applink,apptitle))
 #lines.append(dl('/work/fflexphp/web/index.php','MW Inflected forms'))
 #lines.append(dl('/work/fflexphp/web1/index.php','MW Inflected forms, v2'))
 #lines.append(dl('/tamildictionaries/index.html','Tamil Lexicon'))
 lines.append(dl('https://dsal.uchicago.edu/dictionaries/pali/','Pali-English Dictionary at DSAL'))
 # 12-19-2023
 lines.append(dl('http://localhost/cologne/csl-apidev/sample/dalglob1.php','dalglob1: experimental multi-dictionary display'))
 lines.append(dl('http://localhost/cologne/csl-apidev/pwkvn/','Experimental displays for Böhtlingk/Schmidt dictionaries')) 
 
 return lines

def dictdiv(pfxdict):
 """The list of dictionaries, and their forms. Return list of string.
 """
 ans = []
 ans.append('<table width="90%">')
 parts = [san_english(pfxdict),english_san(pfxdict),
  san_french(pfxdict), san_german(pfxdict),
  san_latin(pfxdict), san_san(pfxdict),
  san_special(pfxdict),
  # skip these for local installation
  #deprecated(pfxdict),
  misc()
  ]
 for part in parts:
  ans = ans + ['<tr><td>'] + part + ['</td></tr>']
 ans.append('</table>')
 return ans


def index01_bodylines(pfxdict):
 # use '+' on lists to concatenate them
 lines=headerdiv() + purpos1ediv() + dictdiv(pfxdict) 
 return lines

def index01(filein,fileout):
 pfxdict = parse_indexdirs(filein)
 #print(pfxdict["PW"].toStringdbg())

 lines = [] # array of lines to be output
 import datetime
 today0 = datetime.datetime.now()
 today = today0.strftime("%B %d, %Y")
 head = """<!DOCTYPE html>
<html>
<head>
 <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
 <title>IITS Koeln </title>
 <link type="text/css" rel="stylesheet" href="csl-homepage/Cologne.css" />
<script src="//ajax.googleapis.com/ajax/libs/jquery/1.10.2/jquery.min.js"></script>
 <style>
 a.child3 {background-color: transparent !important;}
 </style>
</head>
<body>
"""
 tail = u"""
<!--
<hr/>
   <h2>Funding</h2>
 <p>Die mit * gekennzeichneten Werke sind unter dem
DFG-NEH Project 2010-2013 <br/>
entstanden:
 26*/38 digitalisierte Wörterbücher = *198/300 MB   
 </p>
-->
<hr style="width:89%; margin-left:0px;"/>
   <h2>Credits</h2>
  <p>The digitizations of works marked with an asterisk (*) were funded by the DFG-NEH Project 2010-2013.</p>
  </p>
     <p>The markup of the  Monier-Williams Sanskrit-English Dictionary is described in detail 
          <a href='https://www.sanskrit-lexicon.uni-koeln.de/talkMay2008/markingMonier.html'>here</a>.
     <br/>
     The markup of the various dictionaries was designed and implemented by: </p>
     <ul>
      <li>
       <a href="mailto:th.malten@gmail.com">Thomas Malten</a> (Cologne University) and <a href="https://www.sanskrit-lexicon.uni-koeln.de/images/Aurorachana_Staff_2006(1).jpg">assistants</a> in India
      </li>
      <li>
       <a href="//www.sanskritlibrary.org">Peter Scharf</a> (The Sanskrit Library)
      </li>
      <li>
       Malcolm D. Hyman 
       (Max-Planck-Institut für Wissenschaftsgeschichte, Berlin)
      </li>
      <li>
       Jim Funderburk
      </li>
     </ul>
<hr style="width:89%; margin-left:0px;"/>
   <h2>How to cite in academic publications?</h2>
   <h3>In text citation</h3>
  <p>(Cologne Digital Sanskrit Dictionaries)</p>
  <h3>Bibliographic reference</h3>
  <pre>
Cologne Digital Sanskrit Dictionaries, version """ + version + """,
Cologne University, accessed on {0},
https://www.sanskrit-lexicon.uni-koeln.de
  </pre>
   <h2>How to acknowledge usage of data in a website / application?</h2>
   <p>This website / application uses data from <a href="https://www.sanskrit-lexicon.uni-koeln.de">Cologne Digital Sanskrit Dictionaries</a>, Cologne University, accessed on {0}.</p>
  <hr style="width:89%; margin-left:0px;"/>
  <div id="privacy">
   <h2>Data protection</h2>
   <p><a href="https://www.portal.uni-koeln.de/impressum.html?L=0">Impressum</a></p>
   <p> This site uses cookies to save settings related to dictionary displays.
    <br/> We aim to comply with 
     <a href="https://www.portal.uni-koeln.de/9468.html">Cologne University data protection policies.</a>
    
   </p>
  </div>
  <hr style="width:89%; margin-left:0px;"/>
  <div id="footer">
   <a href="mailto:jfunderb@uni-koeln.de">Jim Funderburk</a> and <a href="mailto:drdhaval2785@gmail.com">Dr. Dhaval Patel</a> maintain this web site.
   <p>Last modified: {0} </p>
  </div>

</body>
</html>
""".format(today)
 headlines = head.split('\r\n')
 taillines = tail.split('\r\n')
 bodylines=index01_bodylines(pfxdict)
 for line in headlines:
  lines.append(line)
 for line in bodylines:
  lines.append(line)
 for line in taillines:
  lines.append(line)

 fout = codecs.open(fileout,"w","utf-8")
 for line in lines:
  fout.write("%s\n" % line)
 fout.close()

if __name__  =="__main__":
 filein = sys.argv[1]
 fileout = sys.argv[2]
 index01(filein,fileout)
 #print("DID YOU CHANGE 'Date last modified'?")
