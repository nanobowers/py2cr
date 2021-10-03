# TESTS for the py2cr/builtins/module.rb module

# $LOAD_PATH.unshift(File.join(File.dirname(__FILE__), '..'))

require "spec"
require "../py2cr/builtins/module"

describe "PyBultins" do
  it "zips with zip_p" do
    PythonZipEx.zip_p([0]).should eq [[0]]
    PythonZipEx.zip_p([0], [5]).should eq [[0, 5]]
    PythonZipEx.zip_p([0, 1], [5, 6]).should eq [[0, 5], [1, 6]]
    PythonZipEx.zip_p([0, 1, 2], [5, 6, 7]).should eq [[0, 5], [1, 6], [2, 7]]
    PythonZipEx.zip_p([0, 1], [5, 6], [8, 9]).should eq [[0, 5, 8], [1, 6, 9]]
  end

  it "test_is_bool_true" do
    PythonIsBoolEx.is_bool(1).should eq true
    PythonIsBoolEx.is_bool(true).should eq true
    PythonIsBoolEx.is_bool(-1).should eq true
    PythonIsBoolEx.is_bool("a").should eq true
    PythonIsBoolEx.is_bool([1]).should eq true
    PythonIsBoolEx.is_bool({:a => 1}).should eq true
  end

  it "test_is_bool_false" do
    empty_array = [] of Int32
    empty_hash = {} of String => Int32
    PythonIsBoolEx.is_bool(nil).should eq false
    PythonIsBoolEx.is_bool(false).should eq false
    PythonIsBoolEx.is_bool(0).should eq false
    PythonIsBoolEx.is_bool("").should eq false
    PythonIsBoolEx.is_bool(empty_array).should eq false
    PythonIsBoolEx.is_bool(empty_hash).should eq false
  end

  # Python
  #   str.find(sub[, start])
  # Crystal
  #   str.py_index(sub[, start])

  it "test_index" do
    "aiueo".py_index("ai", 0).should eq 0
    "aiueoai".py_index("ai").should eq 0
    "aiueo".py_index("iu").should eq 1
    "aiueo".py_index("iu", 2).should eq -1
    "aiueo".py_index("iu", 1).should eq 1
    "aiueo".py_index("hoge").should eq -1
  end

  # Python
  #   str.find(sub[, start[, end]])
  # Crystal
  #   str.py_find(sub[, start[, end]])

  it "test_find" do
    "aiueo".py_find("ai", 0).should eq 0
    "aiueoai".py_find("ai").should eq 0
    "aiueo".py_find("iu").should eq 1
    "aiueo".py_find("iu", 2).should eq -1
    "aiueo".py_find("iu", 1, 3).should eq 1
    "aiueo".py_find("iu", 1, 2).should eq -1
    "aiueo".py_find("hoge").should eq -1
  end

  # Python
  #   str.rindex(sub)
  # Crystal
  #   str.py_rindex(sub)
  it "test_rindex" do
    "aiueo".py_rindex("ai").should eq 0
    "aiueoai".py_rindex("ai").should eq 5
    "aiueo".py_rindex("iu").should eq 1
    "aiueo".py_rindex("hoge").should eq -1
  end

  # Python
  #   str.rfind(sub[, start[, end]])
  # Crystal
  #   str.py_rfind(sub[, start[, end]])
  it "test_rfind" do
    "aiueo".py_rfind("ai", 0).should eq 0
    "aiueoai".py_rfind("ai").should eq 5
    "aiueo".py_rfind("iu").should eq 1
    "aiueo".py_rfind("iu", 2).should eq -1
    "aiueo".py_rfind("iu", 1, 3).should eq 1
    "aiueo".py_rfind("iu", 1, 2).should eq -1
    "aiueo".py_rfind("iu", 1, -1).should eq 1
    "aiueo".py_rfind("hoge").should eq -1
  end
end
