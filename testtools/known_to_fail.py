"""lists all the tests that are known to fail"""
KNOWN_TO_FAIL = [
    "tests/basic/nestedclass.py",
    "tests/basic/listcomp2.py",
    "tests/basic/del_local.py",
    "tests/basic/del_global.py",
    "tests/basic/valueerror.py",
    "tests/basic/generator.py",
    "tests/basic/default.py",  # Can't call local variable in arguments.
    #"tests/basic/for_in2.py", # WORKING! Can't support dict (not use items()/keys()/values()) case.

    "tests/basic/oo_super.py",   # Multiple inheritance can not be supported
    "tests/basic/oo_diamond.py", # Multiple inheritance can not be supported
    "tests/basic/oo_static_inherit2.py", # Class method of the lowercase name class is unsupported.


    "tests/basic/vars.py",       # Can't match variable scope
    "tests/basic/vars2.py",      # Can't match variable scope
    "tests/basic/yield.py",      # Difficult

    "tests/functions/sort_cmp.py",
    "tests/functions/sort23.py",

    # decorators may be technically possible in Crystal with lots of
    # gymnastics and lambdas, but it's probably not worth the hassle..
    "tests/decorator/class.py",
    "tests/decorator/decorator.py",
    "tests/decorator/function1.py",
    "tests/decorator/function2.py",
    "tests/decorator/function3.py",

    "tests/basic/assign_bad.py", # known bad multi-assignment of val,nothing via tuple
    "tests/basic/getattr.py", # crystal disallows dynamic method dispatch

    "tests/basic/hasattr1.py", # crystal cannot define inst-vars on the fly
    "tests/basic/hasattr2.py", # crystal cannot define inst-vars on the fly

    # lambdas do not work currently because they must be typed in crystal.
    # typing of lambdas is very uncommon in python-land.
    # Might be supportable with typeannotation of Callable in the future, but
    # doubtful would have any practical use.
    "tests/basic/lambda.py",
    "tests/basic/lambda2.py",
    "tests/basic/lambda3.py",

    "tests/basic/del_attr.py", # cannot delete an instance variable in crystal, afaik.


    # These failing OO tests: for these these we are generating
    # a nilable inst-var for each class-var and it is very tricky
    # to figure out how to type these variables.
    # Possibly can revisit with something tricky in the future
    "tests/basic/oo.py", #py2cr fail
    "tests/basic/oo_attributes.py", # py2cr fail
    "tests/basic/oo_inherit.py", # py2cr fail
    "tests/basic/oo_inherit_simple.py", # py2cr fail
    "tests/basic/oo_inherit_simple_super1.py", # py2cr fail
    "tests/basic/oo_inherit_simple_super2.py", # py2cr fail
    "tests/basic/oo_inherit_simple_super3.py", # py2cr fail


    "tests/basic/set.py", # crystal set requires templating type

    "tests/basic/super2.py", # technically, crystal doesnt support this via
    # https://forum.crystal-lang.org/t/call-a-method-on-parent-thats-also-defined-on-the-child-from-a-different-method/3493

    "tests/basic/tuple2.py", # diff issue: one case returns Array instead of Tuple

    "tests/lists/super2.py", # cry not working
    "tests/lists/subclass.py", # cry not working
    "tests/lists/subclass2.py", # cry not working
    "tests/lists/subclass3.py", # cry not working


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

    "tests/strings/fstrings_diff.py",     # output formatting DIFFERENCES
    "tests/strings/other_strings.py",     # not support byte-strings
    "tests/strings/string_format_efg.py", # crystal doesnt support %F
    "tests/strings/string_format_o.py",   # output formatting DIFFERENCES
    "tests/strings/string_format_u.py",   # unsupported in python per PEP-237
    "tests/strings/string_format_x.py",   # output formatting DIFFERENCES

    # No numpy or unittest cases work.

    "tests/deep-learning-from-scratch/and_gate.py", # relies on numpy
    "tests/deep-learning-from-scratch/relu.py", # relies on numpy
    "tests/deep-learning-from-scratch/sigmoid.py", # relies on numpy
    "tests/deep-learning-from-scratch/step_function.py", # relies on numpy

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

    # Tests from py2many were added to expose additional corner cases.
    # the vast majority of them do not work and may never work...
    "tests/py2many/assert.py",
    "tests/py2many/asyncio_test.py",
    #"tests/py2many/binit.py [4]: ....                                 [OK]
    #"tests/py2many/bitops.py [4]: ....                                [OK]
    "tests/py2many/bubble_sort.py",
    #"tests/py2many/built_ins.py [4]: ....                             [OK]
    "tests/py2many/byte_literals.py",
    #"tests/py2many/classes.py [4]: ....                               [OK]
    #"tests/py2many/cls.py [4]: ....                                   [OK]
    "tests/py2many/comb_sort.py",
    "tests/py2many/comment_unsupported.py",
    "tests/py2many/complex.py",
    "tests/py2many/coverage.py",
    "tests/py2many/datatypes.py",
    "tests/py2many/demorgan.py",
    "tests/py2many/dict.py",
    "tests/py2many/equations.py",
    "tests/py2many/exceptions.py",
    #"tests/py2many/fib.py [4]: ....                                   [OK]
    "tests/py2many/fib_with_argparse.py",
    #"tests/py2many/fstring.py [4]: ....                               [OK]
    #"tests/py2many/global.py [4]: ....                                [OK]
    #"tests/py2many/global2.py [4]: ....                               [OK]
    #"tests/py2many/hello_world.py [4]: ....                           [OK]
    "tests/py2many/import_tests.py",
    #"tests/py2many/infer.py [4]: ....                                 [OK]
    "tests/py2many/infer_ops.py",
    "tests/py2many/int_enum.py",
    "tests/py2many/lambda.py",
    "tests/py2many/langcomp_bench.py",
    #"tests/py2many/loop.py [4]: ....                                  [OK]
    "tests/py2many/nested_dict.py",
    "tests/py2many/print.py",
    "tests/py2many/rect.py",
    "tests/py2many/sealed.py",
    "tests/py2many/smt_types.py",
    "tests/py2many/str_enum.py",
    # "tests/py2many/sys_argv.py [4]: ....                              [OK]
    "tests/py2many/sys_exit.py",
    "tests/py2many/with_open.py",

    ]
