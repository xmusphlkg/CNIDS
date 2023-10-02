FROM rocker/r-base:latest

LABEL maintainer="Likangguo <lkg1116@outlook.com>"

# system libraries of general use
RUN apt-get update && apt-get install -y \
  sudo \
  pandoc \
  pandoc-citeproc \
  libcurl4-gnutls-dev \
  libcairo2-dev \
  libxt-dev \
  libssl-dev \
  libssh2-1-dev \
  libxml2-dev \
  libudunits2-dev \
  libgdal-dev \
  gdal-bin \
  libproj-dev \
  proj-data \
  proj-bin \
  libgeos-dev\
  libsodium-dev \
  libssl1.1 \
  && rm -rf /var/lib/apt/lists/*

# system library dependency for the this app
RUN apt-get update && apt-get install -y \
  libmpfr-dev \
  && rm -rf /var/lib/apt/lists/*

# basic shiny functionality
RUN R -e "install.packages(pkgs = c('shiny', 'shinythemes'), repos = 'https://mirrors.tuna.tsinghua.edu.cn/CRAN/')"

# install dependencies of the this app
RUN R -e "install.packages('plotly', repos='https://cloud.r-project.org/')"
RUN R -e "install.packages('dplyr', repos='https://cloud.r-project.org/')"
RUN R -e "install.packages('DT', repos='https://cloud.r-project.org/')"

# copy the app to the image
RUN mkdir /root/app
COPY app.R /root/app/

COPY Rprofile.site /usr/lib/R/etc/

EXPOSE 3838

CMD ["R", "-e", "shiny::runApp('/root/app')"]
