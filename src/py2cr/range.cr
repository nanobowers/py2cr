
class PyRange
  include Iterator(Int32)

  def initialize(@start : Int32, @stop : Int32, @step : Int32 = 1)
    raise ArgumentError.new("Step cannot be zero") if @step.zero?
    @curval = @start
  end

  def next
    value = @curval
    if (@step > 0 && (value < @stop)) ||
       (@step < 0 && (value > @stop))
      @curval += @step # nextval
      return value
    else
      stop
    end
  end

  # Two/three argument form
  def self.range(start : Int32, stop : Int32, step : Int32 = 1)
    self.new(start, stop, step)
  end

  # One-argument form (stop-value)
  def self.range(stop : Int32)
    self.new(0, stop, 1)
  end
end
