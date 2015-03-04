# Read data
tcr = read.csv('/Users/Nikhil/dev/usf/cs-640/project/resources/single-cell-TCR.csv')

# Pull out only numeric columns for clustering
d = tcr[, 4:ncol(tcr)]

# Get a look a the data types of the columns
str(d)
# Notice that some are logical, others are int, etc...we need numbers only

# Replace NA with 0
d[is.na(d)] <- 0

# Now see that the data type of the columns is all numeric
str(d)

# You could run gap anlysis on the data (doesn't make sense with binary data)
library(cluster)
gap = clusGap(d, FUN=kmeans, K.max=20, B=200)
plot(gap)

# Check out the mona function (?mona)
# Make data as int first
dint <- sapply(d, function(x) {
    as.integer(x)
})
mona(dint)

# Binary data isn't suited for clustering or PCA. What can you do? Homogeneity
# analysis, maybe? Let's try.
# install.packages('homals')
# If on a Mac you'll need to install XQuartz
library(homals)

# Check out Multiple Factor analysis
library(Factoshiny)
