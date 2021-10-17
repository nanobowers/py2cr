
# To match a python `assert` error
class AssertionError < Exception
end

class Method
  # Monkeypath Method#to_s to provide a consistent output for multiple
  # versions of crystal. This is dirty, but easiest way to proceed without
  # ripping up the test suite to provide several different expected
  # outputs for all the changes from 2.4 .. 3.0
  # This will probably come back to bite me....
  def to_s
    loc = self.source_location
    return "#<#{self.class}: #{self.owner}\##{self.original_name}>"
  end
end

class Dir
  # Similar to a unix find, but only gets the directory and subdirectories
  def self.find_subdir_tree(dir)
    ps = [dir]
    outlist = [] of String
    while !ps.empty? && (file = ps.shift)
      if File.directory?(file)
        outlist << file
        fs = Dir.children(file)
        fs.each do |f|
          f = File.join(file, f)
          ps.unshift f
        end
      end
    end
    outlist
  end
end

#
# Foo.call() or Foo.() is nothing => Foo.new() call.
#
class Class
  
  def py_call(*args,**kwargs)
    self.new(*args, **kwargs)
  end
  
  def method_missing(method, *args)
    if method == :call
      self.new(*args)
    else
      super
    end
  end
end

struct Set
  def remove(x)
    self.delete(x)
    return
  end
end

class Array(T)
  def remove(val) : Void
    idx = self.index(val)
    unless idx.nil?
      self.delete_at(idx)
    end
  end

  # TODO: Add range-based slice assignment
  #def []=(idxrange : Range(Int32, Int32), arrayval : Array(T))
  #end
  
end

module PythonMethodEx
  def getattr(*a)
    if singleton_class.class_variables.includes? "@@#{a[0]}".to_sym
      send(a[0])
    elsif public_methods.include? a[0].to_sym
      method(a[0])
    elsif a.size == 2
      return a[1]
    else
      raise NoMethodError, "undefined method `#{a[0]}'"
    end
  end
end

# Array python-zip with more than one arg.
# Note that we allow nils to propagate from Crystal Enumerable#zip,
# and then we have to filter out any cases with nils, then convert to an array.
def py_zip(a, *otherargs)
  return a.zip?(*otherargs).select(&.all?).map(&.to_a)
end

# Array python-zip with one arg.
def py_zip(a)
  [a.to_a]
end

# String variant of python-zip
def py_zip(a : String, *otherargs : String)
  rest = otherargs.map(&.chars)
  return a.chars.zip?(*rest).select(&.all?).map(&.to_a)
end

def py_print(*args)
  # $, = " "   # array field separator
  # $\ = "\n"  # output record separator
  args.each_with_index do |arg, idx|
    if arg.is_a?(Iterator)
      print arg.to_a
    else
      print arg
    end
    print " " unless idx == args.size - 1
  end
  print "\n"
end

def py_print
  print "\n"
end

def py_is_bool(a)
  if a.responds_to?(:empty?) && a.empty?
    return false
  end
  case a
  when nil, false, 0, ""
    return false
  else
    return true
  end
end

def py_del(ary : Array(U), rng : Range(U, U)) forall T, U
  ary.replace ary.each_with_index.reject { |(x, i)| rng.includes?(i) }.map(&.first).to_a
end

class String
  def py_in?(substr : String)
    self.includes?(substr)
  end

  # Two argument replace is just a gsub (replaces all)
  def py_replace(substr, replace_value)
    self.gsub(substr, replace_value)
  end

  # Three argument replace is harder..
  # This is a blatant ripoff of gsub in stdlib with tweaks
  def py_replace(string : String, replacement, numtimes : Int32) : String
    py_replace(string, numtimes) { replacement }
  end

  def py_replace(string : String, numtimes : Int32, &block)
    byte_offset = 0
    index = self.byte_index(string, byte_offset)
    return self unless index

    last_byte_offset = 0
    replace_count = 0

    String.build(bytesize) do |buffer|
      while index && (replace_count < numtimes)
        buffer.write unsafe_byte_slice(last_byte_offset, index - last_byte_offset)
        buffer << yield string

        replace_count += 1

        if string.bytesize == 0
          byte_offset = index + 1
          last_byte_offset = index
        else
          byte_offset = index + string.bytesize
          last_byte_offset = byte_offset
        end

        index = self.byte_index(string, byte_offset)
      end

      if last_byte_offset < bytesize
        buffer.write unsafe_byte_slice(last_byte_offset)
      end
    end
  end

  def py_index(substr, offset = 0)
    ret = self.index(substr, offset)
    return ret.nil? ? -1 : ret
  end

  def py_rindex(substr)
    ret = self.rindex(substr)
    return ret.nil? ? -1 : ret
  end

  def py_find(substr, start_pos : Int32 = 0, end_pos : Int32? = nil)
    if end_pos.nil?
      ret = index(substr, start_pos)
    else
      ret = self[0...end_pos].index(substr, start_pos)
    end
    return ret.nil? ? -1 : ret
  end

  def py_rfind(substr, start_pos = 0, end_pos = nil)
    if end_pos.nil?
      ret = self[start_pos..-1].rindex(substr)
      unless ret.nil?
        ret = self[0..-1].rindex(substr)
      end
    else
      ret = self[start_pos...end_pos].rindex(substr)
      unless ret.nil?
        ret = self[0...end_pos].rindex(substr)
      end
    end
    return ret.nil? ? -1 : ret
  end

  def py_split(sep : String? = nil, maxsplit = -1) : Array(String)
    case sep
    when nil then sep = /\s+/
    when " " then sep = / /
    end
    if maxsplit > 0
      self.split(sep, maxsplit + 1)
    else
      self.split(sep)
    end
  end

  def py_strip(chars : String = "")
    if chars == ""
      self.strip
    else
      self.gsub(/(^[#{chars}]*)|([#{chars}]*$)/, "")
    end
  end

  def py_lstrip(chars : String = "")
    if chars == ""
      self.lstrip
    else
      self.gsub(/(^[#{chars}]*)/, "")
    end
  end

  def py_rstrip(chars : String = "")
    if chars == ""
      self.rstrip
    else
      self.gsub(/([#{chars}]*$)/, "")
    end
  end

  # Replace to Python String#count
  def py_count(substr : String, start_pos : Int32? = nil, end_pos : Int32? = nil)
    if start_pos.nil?
      self.scan(substr).size
    elsif end_pos.nil?
      self[start_pos..-1].scan(substr).size
    else
      self[start_pos...end_pos].scan(substr).size
    end
  end

  # alias :count_r :count
  # alias :each :chars
end

class Array
  def py_in?(element)
    self.includes?(element)
  end

  def py_count(x)
    self.count(x)
  end

  def py_remove(obj)
    i = self.index(obj)
    self.delete_at(i)
    return
  end
end

struct Tuple

  def py_count(x)
    self.count(x)
  end

  # Monkeypatch to_s to use parentheses when printing a Tuple
  # so that tuples will print the same way as Python
  def to_s(io : IO) : Nil
    io << '('
    join(io, ", ") { |item|
      if item.responds_to?(:py_inspect)
        item.py_inspect(io)
      else
        item.inspect(io)
      end
    }
    io << ')'
  end
  
end

module ENV
  # handles "key" in os.environ case
  def self.py_in?(key : String) : Bool
    self.has_key?(key)
  end
end
    
class Hash
  def py_in?(element)
    self.has_key?(element)
  end
end

class IO
  def py_read : String
    self.gets_to_end
  end
  # TODO: need py_read with byte-limit argument
end

module Enumerable
  def py_all?
    result = true
    self.each do |a|
      result = false if a.nil? || a == false || a == 0 || a == ""
      result = false if a.responds_to?(:empty?) && a.empty?
    end
    return result
  end

  def py_any?
    result = false
    self.each do |a|
      result = true unless a.nil? || a == false || a == 0 || a == ""
      result = a.py_any? if a.responds_to?(:each)
    end
    return result
  end
end

class PyRange
  include Iterator(Int32)

  def initialize(@start : Int32, @stop : Int32, @step : Int32 = 1)
    raise ArgumentError.new("Step cannot be zero") if @step.zero?
    @curval = @start
  end

  def next
    value = @curval
    if (@step > 0 && (value < @stop)) ||
       (@step < 0 && (value > @stop))
      @curval += @step # nextval
      return value
    else
      stop
    end
  end

  # Two/three argument form
  def self.range(start : Int32, stop : Int32, step : Int32 = 1)
    self.new(start, stop, step)
  end

  # One-argument form (stop-value)
  def self.range(stop : Int32)
    self.new(0, stop, 1)
  end
end

module PyOs
  # Should be equivalent of python walk function.
  # Note that we create a new Dir.find_subdir_tree since Crystal has no
  # builtin equivalent of a Unix `find`.

  def self.walk(dir)
    rootnames = Dir.find_subdir_tree(dir)

    walks = [] of Tuple(String, Array(String), Array(String))

    rootnames.each do |root|
      dirnames = [] of String
      filenames = [] of String

      Dir.children(root).each do |f|
        path = File.join(root, f)
        if File.directory?(path)
          dirnames << f
        elsif File.file?(path)
          filenames << f
        end
      end
      walks << {root, dirnames, filenames}
    end

    return walks
  end

  # os.environ : Does not match python behavior whereby
  # a missing key will cause an error
  def self.environ
    return ENV
  end

  # os.getenv
  def self.getenv(arg)
    return ENV[arg]?
  end
end

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
