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
