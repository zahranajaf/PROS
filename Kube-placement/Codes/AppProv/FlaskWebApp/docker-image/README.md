To create a docker image from the web microframework application, you can apply the following command:

``docker build -t webserv .``


or the following in the case that you need the image whether for both x86-64 and ARM-based machines:

``docker buildx build -t webserv .``
