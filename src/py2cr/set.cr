struct Set
  def remove(x)
    self.delete(x)
    return
  end
  def py_in?(element)
    self.includes?(element)
  end
end
