genradialphylo <- function(infile, seqscol){
  # Generates a data file for a radial phylogram.
  #
  # Accepts:
  #     infile: a uri to a file on the server, string format
  # Returns:
  #     phyloxml: a .phyloxml file 
  absfile <- getabspath(infile)
  # Step 1: Write sequences to file as .fasta
  ############### TESTING ################
  seqscol <- 'clone'
  # TODO: Need to get this input from Django
  ############# END TESTING ##############
  u <- read.csv(absfile)
  seqs <- u[u[, seqscol] != '', ]
  w <- with(seqs, paste0('>', seqs[, seqscol], '\n', seqs[, seqscol], collapse='\n'))
  seqsFile <- tempfile(pattern='seqs-', tmpdir=getwd(), fileext='.txt')
  write(w, seqsFile)
  # Step 2: Use muscle to do the MSA (read above file, and write result to file)
  alignedFile <- tempfile(pattern='aligned-', tmpdir=getwd(), fileext='.fasta')
  muscle::muscle(seqs=seqsFile, out=alignedFile, quiet=TRUE)
  # Step 3: Use seqinr to read the alignment file from above
  aligned <- seqinr::read.alignment(alignedFile, format='fasta')
  aligned_dist <- seqinr::dist.alignment(aligned)
  # Step 4: Use ape to build the phylo tree, output it as .newick
  tree <- ape::nj(aligned_dist)
  # TODO: There can be errors through this sequence of events. Try
  # catching them and displaying a better error than a JS error and
  # browser crash. See http://stackoverflow.com/questions/20261761/notifying-user-about-his-bad-input-in-shiny-app
  # To reproduce error, load the tumor.sample.groups.txt data and try
  # analyzing the 2nd column. You could also explore error handling
  # using R: http://mazamascience.com/WorkingWithData/?p=912.k
  class(tree)
  new_tree <- as.phylo(tree)
  newickFile <- tempfile(pattern='tree-', tmpdir=getwd(), fileext='.newick')
  write.tree(phy=new_tree, file=newickFile)
  # Step 5: Use the Java script to convert the .newick to .xml
  usrfolder <- getbasesavepath(infile)
  saveto <- paste0(usrfolder, 'radialphylo')
  dir.create(saveto)
  xmlFile <- tempfile(pattern='phyloxml-', tmpdir=saveto, fileext='.xml')
  system(sprintf("java -cp /server/rscripts/radialphylo/java/forester_1038.jar org.forester.application.phyloxml_converter -f=nn -ni %s %s", newickFile, xmlFile))
  # TODO: Allow user to select which column has the sequences rather than
  # requiring it to be named a certain way or in a certain column. Can
  # read headers and have a dropdown to select the right column.
  # TODO: Split this function up into smaller functions
  # TODO: Do some processing on sequence column in uploaded data (e.g.
  # strip of double quotes, things like that, so it can't mess up your
  # TODO: Restrict number of rows to plot in radial phylo, otherwise
  # looks messed up. Can dedupe data to make this easier.
  # code below
  # TODO: You need cleanup cronjob in linux to remove old temp files
  # generated below
  # Step 6: Send the .xml to jsPyhloSVG for plotting
  return(xmlFile)
}