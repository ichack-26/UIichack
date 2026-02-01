from   _TFL._SDG._C.import_C import C
import _TFL._SDG._trace
C.Comment.out_level = 5

class T_Array (C.Array) :
    c_format = \
        ( "%(::*type:)s %(name)s"
          "%(:front= =%(NL)s%(base_indent)s:*initializers:)s;"
        )
# end class T_Array

if __name__ == "__main__" :
    s = C.Struct ( "TDFT_Sign_Mask"
                 , "unsigned long bit_mask    = 42 // mask for value"
                 , "unsigned long extend_mask // mask for sign extension"
                 )
    a2 = T_Array \
        ( "TDFT_Sign_Mask", "fubars", 2
        , init = [ dict (bit_mask = "57 % 2",  extend_mask = 137)
                 , dict (bit_mask = "142 % 4", extend_mask = -1)
                 ]
        )
    a2.write_to_c_stream ()

    v = C.Var ("int", "test", 2)
    v.write_to_c_stream ()
