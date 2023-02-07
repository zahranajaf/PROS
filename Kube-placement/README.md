## scalable Kubernetes scheduler


This tutorial provides information regarding the SKS service of a cloud provider:

https://community.exoscale.com/documentation/sks/quick-start/

https://www.youtube.com/watch?v=P_uR4dSorLM



The first steps:

PS C:\Users> C:\exoscale\exo.exe compute sks kubeconfig zsla kubernetes-admin -t 600000 --group system:masters > ~/.kube/config

PS C:\Users> .\kubectl.exe --kubeconfig .\.kube\config get pods -o wide

For other steps, we provided the details in the [figure](https://github.com/anonymousuni/PROS/tree/main/Kube-placement/figures).


## Kubernetes placement

We provided the details of the customized scheduling setup and its source codes in the [Codes](https://github.com/anonymousuni/PROS/tree/main/Kube-placement/Codes/ResProv).
