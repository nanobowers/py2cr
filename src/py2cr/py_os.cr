module PyOs

  # Similar to a unix find, but only gets the directory and subdirectories
  def self.find_subdir_tree(dir)
    ps = [dir]
    outlist = [] of String
    while !ps.empty? && (file = ps.shift)
      if File.directory?(file)
        outlist << file
        fs = Dir.children(file)
        fs.each do |f|
          f = File.join(file, f)
          ps.unshift f
        end
      end
    end
    outlist
  end

  # Should be equivalent of python os.walk function.
  # Note that we create a new Dir.find_subdir_tree since Crystal has no
  # builtin equivalent of a Unix `find`.
  def self.walk(dir)
    rootnames = self.find_subdir_tree(dir)

    walks = [] of Tuple(String, Array(String), Array(String))

    rootnames.each do |root|
      dirnames = [] of String
      filenames = [] of String

      Dir.children(root).each do |f|
        path = File.join(root, f)
        if File.directory?(path)
          dirnames << f
        elsif File.file?(path)
          filenames << f
        end
      end
      walks << {root, dirnames, filenames}
    end

    return walks
  end

  # os.environ : Does not match python behavior whereby
  # a missing key will cause an error
  def self.environ
    return ENV
  end

  # os.getenv
  def self.getenv(arg)
    return ENV[arg]?
  end
end
