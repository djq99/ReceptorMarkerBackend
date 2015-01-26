getabspath <- function(uri) {
  # Helper function to determine the absolute path of media files
  # to perform analysis on.
  # 
  # Accepts:
  #     uri: the uri to a file on the media server
  # Returns:
  #     path: the absolute path to the file on the media server
  par <- parse_url(uri)
  splitpath <- strsplit(as.character(par['path']), "/")[[1]]
  if (par['hostname'] == '66.66.66.10') {
    # development environment. return path to dev media folder.
    basepath <- '/vagrant/www-'
    path <- paste(splitpath, collapse='/')
    abspath <- paste0(basepath, path)
    return(abspath)
  }
  else if (splitpath[1] == 'media') {
    # using production site. return path to prod media folder.
    basepath <- '/server/env.example.com/www/'
    path <- paste(splitpath, collapse='/')
    abspath <- paste0(basepath, path)
    return(abspath)
  }
  else if (splitpath[1] == 'staging') {
    # using staging site. return path to staging media folder.
    basepath <- '/server/env.stage.example.com/www/'
    path <- paste(splitpath, collapse='/')
    abspath <- paste0(basepath, path)
    return(abspath)
  }
  else {
    return('error: uri to file is malformed or not of expected format')
  }
}

