# Deplyoment of flask

kubectl apply -f deployment.yaml


kubectl apply -f service.yaml


Application providers define the application services as a YAML file containing dockerized images and dependencies to other services. They send the application definition through a request message to the resource provider, who downloads the images from the Docker hub and uses Kubernetes and the custom PROS scheduler for orchestration:
https://github.com/microservices-demo/microservices-demo