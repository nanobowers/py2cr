# Extension for Crystal ENV

module ENV
  # Handles "key in os.environ" case
  def self.py_in?(key : String) : Bool
    self.has_key?(key)
  end
end
