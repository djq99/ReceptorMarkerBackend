getbasesavepath <- function(uri) {
  # Helper function to determine the base path to save analyses to.
  # This base path will be the user's folder in the /media/ folder,
  # which is available to the public. (Note: Rserve conn* folders)
  # are not made public, so R scripts need to save analyses back 
  # into user folders for viewing).
  # 
  # Accepts:
  #     uri: the uri to a file on the media server
  # Returns:
  #     path: the path to the user's media folder
  par <- parse_url(uri)
  splitpath <- strsplit(as.character(par['path']), "/")[[1]]
  if (par['hostname'] == '66.66.66.10') {
    # development environment. return path to dev user's folder.
    basepath <- '/server/www/media/'
    usr <- splitpath[2]
    usrpath <- paste0(basepath, usr, '/')
    return(usrpath)
  }
  else if (splitpath[1] == 'media') {
    # using production site. return path to prod user's folder.
    basepath <- '/server/env.example.com/www/media/'
    usr <- splitpath[2]
    usrpath <- paste0(basepath, usr, '/')
    return(usrpath)
  }
  else if (splitpath[1] == 'staging') {
    # using staging site. return path to staging user's folder.
    basepath <- '/server/env.stage.example.com/www/staging/media/'
    usr <- splitpath[3]
    usrpath <- paste0(basepath, usr, '/')
    return(usrpath)
  }
  else {
    return('error: uri to file is malformed or not of expected format')
  }
}