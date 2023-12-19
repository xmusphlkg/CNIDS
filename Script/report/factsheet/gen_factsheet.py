""" Factsheet generator

This shows how to use our preppy templating system and RML2PDF markup.
All of the formatting is inside rml/factsheet.prep
"""
import sys, os, datetime, json
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFont
from rlextra.rml2pdf import rml2pdf
import jsondict
from rlextra.radxml.html_cleaner import cleanBlocks
from rlextra.radxml.xhtml2rml import xhtml2rml
import preppy


def bb2rml(text):
    return preppy.SafeString(xhtml2rml(cleanBlocks(bbcode.render_html(text)),ulStyle="normal_ul", olStyle="normal_ol"))

def generate_pdf(json_file_name, options):
    data = json.load(open(json_file_name))

    here = os.path.abspath(os.path.dirname('__file__'))
    output = os.path.abspath(options.output)
    if not os.path.isdir(output):
        os.makedirs(output,0o755)

    #wrap it up in something friendlier
    data = jsondict.condJSONSafe(data)

    #make a dictionary to pass into preppy as its namespace.
    #you could pass in any Python objects or variables,
    #as long as the template expressions evaluate
    ns = dict(data=data, bb2rml=bb2rml, format="long" if options.longformat else "short")

    #we usually put some standard things in the preppy namespace
    ns['DATE_GENERATED'] = datetime.date.today()
    ns['showBoundary'] = "1" if options.showBoundary else "0"

    #let it know where it is running; trivial in a script, confusing inside
    #a big web framework, may be used to compute other paths.  In Django
    #this might be relative to your project path,
    ns['RML_DIR'] = os.getcwd()     #os.path.join(settings.PROJECT_DIR, appname, 'rml')

    #we tend to keep fonts in a subdirectory.  If there won't be too many,
    #you could skip this and put them alongside the RML
    FONT_DIR = ns['FONT_DIR'] = os.path.join(ns['RML_DIR'], 'fonts')


    #directory for images, PDF backgrounds, logos etc relating to the PDF
    ns['RSRC_DIR'] = os.path.join(ns['RML_DIR'], 'resources')

    #We tell our template to use Preppy's standard quoting mechanism.
    #This means any XML characters (&, <, >) will be automatically
    #escaped within the prep file.
    template = preppy.getModule('rml/factsheet.prep')
    

    #this hack will allow rmltuils functions to 'know' the default quoting mechanism
    #try:
    #   import builtins as __builtin__
    #except:
    #   import __builtin__
    #__builtin__._preppy_stdQuote = preppy.stdQuote
    rmlText = template.getOutput(ns, quoteFunc=preppy.stdQuote)

    file_name_root = os.path.join(output,os.path.splitext(os.path.basename(json_file_name))[0])
    if options.saverml:
        #It's useful in development to save the generated RML.
        #If you generate some illegal RML, pyRXP will complain
        #with the exact line number and you can look to see what
        #went wrong.  Once running, no need to save.  Within Django
        #projects we usually have a settings variable to toggle this
        #on and off.
        rml_file_name = file_name_root + '.rml'
        open(rml_file_name, 'w').write(rmlText)
    pdf_file_name = file_name_root + '.pdf'

    #convert to PDF on disk.  If you wanted a PDF in memory,
    #you could pass a StringIO to 'outputFileName' and
    #retrieve the PDF data from it afterwards.
    rml2pdf.go(rmlText, outputFileName=pdf_file_name)
    print('saved %s' % pdf_file_name)




if __name__=='__main__':
    from optparse import OptionParser
    usage = "usage: gen_factsheet.py [--long] myfile.json"
    parser = OptionParser(usage=usage)
    parser.add_option("-l", "--long",
                      action="store_true", dest="longformat", default=False,
                      help="Do long profile (rather than short)")
    parser.add_option("-r","--rml",
                      action="store_true", dest="saverml", default=False,
                      help="save a copy of the generated rml")
    parser.add_option("-s","--showb",
                      action="store_true", dest="showBoundary", default=False,
                      help="turn on global showBoundary flag")
    parser.add_option("-o", "--output",
                      action="store", dest="output", default='output',
                      help="where to store result")

    options, args = parser.parse_args()

    if len(args) != 1:
        print(parser.usage)
    else:
        filename = args[0]
        generate_pdf(filename, options)

