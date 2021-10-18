# Global methods

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
