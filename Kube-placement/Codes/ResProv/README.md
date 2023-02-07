# Scheduling

The following tutorial helps us to configure PROS schesuler ``pros-scheduler.py``:

https://sysdig.com/blog/kubernetes-scheduler/

Resource providers, such as Exoscale, deploy Algorithm 4 as a custom scheduler within the Kubernetes orchestrator to automate the application deployment with increased SLA assurance. They use Algorithm 1 beforehand to partition the infrastructure and elect coordinators, which in turn use Algorithm 2 for device SLA assurance and partitioning.

# Deplyoment of flask

kubectl apply -f deployment.yaml


kubectl apply -f service.yaml

