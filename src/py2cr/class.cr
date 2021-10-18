#
# Foo.call() or Foo.() is nothing => Foo.new() call.
#
class Class
  
  def py_call(*args,**kwargs)
    self.new(*args, **kwargs)
  end

end


# 
# module PythonMethodEx
#   def getattr(*a)
#     if singleton_class.class_variables.includes? "@@#{a[0]}".to_sym
#       send(a[0])
#     elsif public_methods.include? a[0].to_sym
#       method(a[0])
#     elsif a.size == 2
#       return a[1]
#     else
#       raise NoMethodError, "undefined method `#{a[0]}'"
#     end
#   end
# end
# 
