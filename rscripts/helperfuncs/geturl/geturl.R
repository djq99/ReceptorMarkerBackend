geturl <- function(uri) {
  # Helper function to determine the URL of a file on the media server.
  # This would be a good URL to return back to the client.
  #
  # Accepts:
  #     uri: the uri to a file on the media server
  # Returns:
  #     url: the url of the file
  par <- parse_url(uri)
  splitpath <- strsplit(as.character(par['path']), "/")[[1]]
  splitpath <- splitpath[2:length(splitpath)]  # First element blank because of leading /
  if (splitpath[1] == 'server' && splitpath[2] == 'www') {
    # development environment. return url for dev server.
    basepath <- 'http://66.66.66.10/media/'
    restofpath <- paste(splitpath[4:length(splitpath)], collapse='/')
    url <- paste0(basepath, restofpath)
    return(url)
  }
  else if (splitpath[1] == 'server' && splitpath[2] == 'env.example.com') {
    # using production site. return path to staging user's folder.
    basepath <- 'http://media.receptormarker.com/media/'
    restofpath <- paste(splitpath[5:length(splitpath)], collapse='/')
    url <- paste0(basepath, restofpath)
    return(url)
  }
  else if (splitpath[1] == 'server' && splitpath[2] == 'env.stage.example.com') {
    # using staging site. return url for staging server.
    basepath <- 'http://media.receptormarker.com/staging/media/'
    restofpath <- paste(splitpath[6:length(splitpath)], collapse='/')
    url <- paste0(basepath, restofpath)
    return(url)
  }
  else {
    return('error: uri to file is malformed or not of expected format')
  }
}