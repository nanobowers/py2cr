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

  # :ditto:
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

  # Python str#rstrip
  def py_rstrip(chars : String = "")
    if chars == ""
      self.rstrip
    else
      self.gsub(/([#{chars}]*$)/, "")
    end
  end

  # Python str#count
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
