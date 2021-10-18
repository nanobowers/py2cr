module PySys
  # Create an Object like Python's sys.argv

  # Initialize with PROGRAM_NAME ($0) and ARGV
  @@argv : Array(String) = [PROGRAM_NAME, *ARGV]

  # Class-instance-variable accessor
  class_getter :argv

  # Create accessors similar to python sys.stdout/stderr and
  # sys.__stdout__/__stderr__

  @@__stderr__ = STDERR
  @@__stdin__ = STDIN
  @@__stdout__ = STDOUT

  @@stderr : IO = STDERR
  @@stdin : IO = STDIN
  @@stdout : IO = STDOUT

  # get/set these.
  class_property :stderr
  class_property :stdin
  class_property :stdout

  # do not allow setting these.
  class_getter :__stderr__
  class_getter :__stdin__
  class_getter :__stdout__
end
