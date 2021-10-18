# Extend Crystal Enumerable with equivalent of Python's all/any methods

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
