"""lists all the tests that are known to fail"""
KNOWN_TO_FAIL = [
    "tests/basic/nestedclass.py",
    "tests/basic/listcomp2.py",
    "tests/basic/del_local.py",
    "tests/basic/valueerror.py",
    "tests/basic/del_global.py",
    "tests/basic/generator.py",
    "tests/basic/default.py",    # Can't call local variable in arguments.
    "tests/basic/for_in2.py",    # Can't support dict (not use items()/keys()/values()) case.
    "tests/basic/hasattr2.py",
    "tests/basic/oo_super.py",   # Multiple inheritance can not be supported
    "tests/basic/oo_diamond.py", # Multiple inheritance can not be supported
    "tests/basic/oo_static_inherit2.py", # A class method of the lowercase name class is unsupported.
    "tests/basic/vars.py",       # Can't match variable scope
    "tests/basic/vars2.py",      # Can't match variable scope
    "tests/basic/yield.py",      # Difficult

    "tests/functions/sort_cmp.py",
    "tests/functions/sort23.py",

    "tests/decorator/class.py",
    "tests/decorator/decorator.py",

    # lambdas do not work currently because they must be typed in crystal.
    # typing of lambdas is very uncommon in python-land.
    # Might be supportable with typeannotation of Callable in the future, but
    # doubtful would have any practical use.
    "tests/basic/lambda.py",
    "tests/basic/lambda2.py",
    "tests/basic/lambda3.py",
    "tests/basic/lambda_map.py",

    "tests/basic/del_attr.py", # cannot delete an instance variable in crystal, afaik.
    
    "tests/lists/reduce.py",
    #"tests/lists/subclass.py", 
    #"tests/lists/subclass2.py",
    #"tests/lists/subclass3.py",

    "tests/libraries/xmlwriter.py",

    
    "tests/basic/raise_nameerror.py", # Makes no sense in crystal, b/c is a runtime error.

    # No module imports work properly.
    "tests/modules/classname.py",
    "tests/modules/from_import.py",
    "tests/modules/from_import_as_module.py",
    "tests/modules/import.py",
    "tests/modules/import_alias.py",
    "tests/modules/import_as_module.py",
    "tests/modules/import_class.py",
    "tests/modules/import_global.py",
    "tests/modules/import_init.py",
    "tests/modules/import_multi.py",
    "tests/modules/import_diamond.py",
    "tests/modules/module_name.py",
    "tests/modules/rng.py",

    "tests/strings/other_strings.py",    # not support byte-strings
    "tests/strings/string_format_efg.py", # crystal doesnt support %F
    "tests/strings/string_format_o.py",   # not support, diffs
    "tests/strings/string_format_u.py",   # unsupported in python per PEP-237
    "tests/strings/string_format_x.py",  # not support, diffs

    # No numpy or unittest cases work.
    
    "tests/numpy/abs.py",
    "tests/numpy/all.py",
    "tests/numpy/any.py",
    "tests/numpy/arange.py",
    "tests/numpy/arg_max_min.py", # Not Compatible with axis case
    "tests/numpy/array2string.py",
    "tests/numpy/asarray.py",
    "tests/numpy/ellipsis.py",
    "tests/numpy/empty.py",
    "tests/numpy/ext_slice.py",
    "tests/numpy/full.py",
    "tests/numpy/insert.py",
    "tests/numpy/like.py",
    "tests/numpy/linspace.py",
    "tests/numpy/max_min.py",
    "tests/numpy/maximum_minimum.py",
    "tests/numpy/ndarray.py",
    "tests/numpy/ndarray2.py",
    "tests/numpy/ndarray3.py",
    "tests/numpy/not_like.py",
    "tests/numpy/np_copy.py",
    "tests/numpy/product.py",
    "tests/numpy/random_rand.py",
    "tests/numpy/random_randint.py",
    "tests/numpy/random_random.py",
    "tests/numpy/random_uniform.py",
    "tests/numpy/special_values.py",
    "tests/numpy/sqrt.py",
    "tests/numpy/sum.py",
    "tests/numpy/trigonometric_funcitons.py",
    "tests/numpy/type.py",
    "tests/unittest/assertAlmostEqual.py",
    "tests/unittest/assertCompare.py",
    "tests/unittest/assertEqual.py",
    "tests/unittest/assertIn.py",
    "tests/unittest/assertIs.py",
    "tests/unittest/assertIsInstance.py",
    "tests/unittest/assertRaises.py",
    "tests/unittest/assertTrueFalseNone.py",
    "tests/unittest/class.py",

    ]


