FROM rocker/r-base:latest

LABEL maintainer="Likangguo <lkg1116@outlook.com>"


# basic shiny functionality
RUN R -e "install.packages(pkgs = c('shiny', 'shinythemes'), repos = 'https://mirrors.tuna.tsinghua.edu.cn/CRAN/')"
RUN R -e "install.packages('dplyr', repos='https://cloud.r-project.org/')"
RUN R -e "install.packages('DT', repos='https://cloud.r-project.org/')"

RUN apt-get update && apt-get install -y \
  libssl-dev \
  libssh2-1-dev \
  libcurl4-openssl-dev \
  libxml2-dev \
  libcairo2-dev

# install dependencies of the this app
RUN R -e "install.packages('plotly', repos='https://cloud.r-project.org/')"
# copy the app to the image
RUN mkdir /root/app
COPY app.R /root/app/

COPY Rprofile.site /usr/lib/R/etc/

EXPOSE 3838

CMD ["R", "-e", "shiny::runApp('/root/app')"]
