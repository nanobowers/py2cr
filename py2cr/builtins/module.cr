# require "pathname"
  
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


#
# Foo.call() or Foo.() is nothing => Foo.new() call.
#
class Class
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

module PythonZipEx
  # python : zip(l1, l2, [l3, ..])
  #  array : l1
  def self.zip_p(a, *otherargs)
    #args = inargs.to_a.map {|i| i.is_a?(String) ? i.split("") : i}
    #a = args.shift
    #return a.zip(*args).select{|i| !i.includes?(nil)}
    return a.zip(*otherargs).map(&.to_a)
  end
  def self.zip_p(a)
    [a.to_a]
  end
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

module PythonPrintEx
  def print(*args)
    #      $, = ' '
    #      $\ = "\n"
    super(*args)
  end
end

module PythonIsBoolEx
    def self.is_bool(a)
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
end

class String
  def py_index(substr, offset=0)
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
  
  def py_rfind(substr, start_pos=0, end_pos=nil)
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
end

module PythonSplitEx # String
    def split_p(sep = "", limit=0)
      case sep
      when " "
        sep = / /
#      when ""
#        sep = $;
      end
      if limit > 0
        limit +=1
      end
      self.split(sep, limit)
    end
end

module PythonStripEx # String
    def strip(chars="")
      if chars == ""
         super()
      else
         self.gsub(/(^[#{chars}]*)|([#{chars}]*$)/, "")
      end
    end

    def lstrip(chars="")
      if chars == ""
         super()
      else
         self.gsub(/(^[#{chars}]*)/, "")
      end
    end

    def rstrip(chars="")
      if chars == ""
         super()
      else
         self.gsub(/([#{chars}]*$)/, "")
      end
    end
end

module PythonStringCountEx # String
    # Replace to Python String#count
    def count(substr, start_pos=nil, end_pos=nil)
      if start_pos.nil?
         self.scan(substr).size
      elsif end_pos.nil?
         self[start_pos..-1].scan(substr).size
      else
         self[start_pos...end_pos].scan(substr).size
      end
    end

    #alias :count_r :count
    #alias :each :chars
end

module PythonRemoveEx # Array
    def remove(obj)
      i = self.index(obj)
      self.delete_at(i)
      return
    end
end

module EnumerableEx # Enumerable
    def is_all?()
      result = true
      self.each do |a|
        result = false if a.nil? || a == false || a == 0 || a == ""
        result = false if a.responds_to?(:empty?) && a.empty?
      end
      return result
    end

    def is_any?()
      result = false
      self.each do |a|
        result = true unless a.nil? || a == false || a == 0 || a == ""
        result = true unless a.responds_to?(:empty?) && a.empty?
      end
      return result
    end
end


module PyLib
  # >>> Pylib.range(start, stop)
  # >>> Pylib.range(start, stop, step)
  #
  # Creating something that works similarly to Python's
  # range(a,b) and range(a,b,c) operator and returns an Enumerator
  #
  # Note that it doesnt work for `range(x)`, but you can implement with
  # Crystal's `x.times`
  
  def self.range(start, stop, step=1)
    curval = start
    Enumerator.new() do |y|
      while step > 0 ? (curval < stop) : (curval > stop)
        y << curval
        curval += step
      end
    end
  end
  
end


module PyOs

# tests/os/testdir/
#              test_file1.txt
#              test_file2.txt
#              test_child_dir/
#                  test_child_file1.txt
#                  test_child_file2.txt
#<dirpath>  tests/os/testdir
#<dirnames> ['test_child_dir']
#<filenames>['test_file1.txt', 'test_file2.txt']
#
#<dirpath>  tests/os/testdir/test_child_dir
#<dirnames> []
#<filenames>['test_child_file1.txt', 'test_child_file2.txt']

#<dirpath> tests/os/testdir
#<dirnames> ["tests/os/testdir/test_child_dir"]
#<filenames> ["tests/os/testdir/test_child_dir/test_child_file1.txt", "tests/os/testdir/test_child_dir/test_child_file2.txt", "tests/os/testdir/test_file1.txt", "tests/os/testdir/test_file2.txt"]

  def self.walk(dir)
    dirpath = Pathname.new(dir)
    rootnames = [] of String
    Pathname.new(dirpath).find do |path|
      if path.directory?
        rootnames << path.to_s
      end
    end

    walks = [] of String
    rootnames.each{|root|
      dirnames = [] of String
      filenames = [] of String
      
      Dir.foreach(root){|f|
        path = File.join(root, f)
        case File.ftype(path)
        when "directory"
          if ("." != f) && (".." != f)
            dirnames << f
          end
        when "file"
          filenames << f
        end
      }
      walks << [root, dirnames, filenames]
    }

    return walks
  end

  # os.environ : Does not match python behavior whereby
  # a missing key will cause an error
  def self.environ
    return ENV
  end

  # os.getenv
  def self.getenv(arg)
    return ENV[arg]
  end
  
end

module PySys

  # Create an Object like Python's sys.argv

  # Initialize with PROGRAM_NAME ($0) and ARGV
  @@argv : Array(String) = [PROGRAM_NAME, *ARGV]

  # Override array getter function for this object.
  # Python ARGV will throw an IndexError when out of bounds,
  # so we use fetch here so that Crystal exhibits the same behavior
  #TODO
  #def @argv.[](idx)
  #  self.fetch(idx)
  #end

  # Class-instance-variable accessor
  class_getter :argv
  #def self.argv
  #  @argv
  #end

end
