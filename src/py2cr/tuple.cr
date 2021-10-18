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
