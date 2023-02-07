FROM ubuntu

RUN apt-get update && apt-get install -y ffmpeg python3 wget

# Set the working directory
WORKDIR /work

# Add python-script
COPY run-encoding.py /work
COPY 20-20000.mp4 /work
COPY 20.mp4 /work

RUN chmod +x /work/run-encoding.py
RUN chmod +x /work/20-20000.mp4 
RUN chmod +x /work/20.mp4 

#RUN wget -O  /usr/local/bin/kubetools https://github.com/kubemq-io/kubemqctl/releases/download/latest/kubemqctl_linux_386
#RUN chmod +x /usr/local/bin/kubetools

ENTRYPOINT ["python3", "run-encoding.py", "x264"]
