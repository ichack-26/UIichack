from _TFL._SDG._XML.Document  import *
from _TFL._SDG._XML.Elem_Type import *

import _TFL._SDG._trace
#d = Document ("Test", "Test for TFL.SDG.XML.Elem_Type creation and use")
d = Document ("Test")
X = Elem_Type ( "X", foo = None, bar = 42, bazzzzz = "quuux")
Y = Elem_Type ( "Y", bases = (TFL.SDG.XML.Empty, )
              , foo = None, bar = 42, baz = "quuux"
              )
#d.add (X ("A foo-carrying X", foo = "wibble"))
#d.add (Y (bar = "wobble"))
#d.add (X ("A bar-less X", bar = None))
d.add (X (bar = None))
#d.add (Y (baz = None, x_attrs = dict (qux = 84, quy = 85)))
#d.write_to_xml_stream ()
