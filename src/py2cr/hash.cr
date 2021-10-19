class Hash
  
  def py_each(&b)
    self.each_key do |kk|
      yield kk
    end
  end

  def py_in?(element)
    self.has_key?(element)
  end
end
