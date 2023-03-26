# onion-service-monitoring
## Project highlights
Yep, we already have two awesome projects: [Blackbox exporter](https://github.com/prometheus/blackbox_exporter) and [Onionprobe](https://gitlab.torproject.org/tpo/onion-services/onionprobe/-/tree/main) from onion project. 
But afaik first didn't support calls with socks proxy, second is not much popular. 
So where is all in one solution which can monitor your http/onion targets using the multi-target exporter pattern from prometheus.


For now, this is some kind of POC or hobby-like project. But any feedback is appreciated. 

For quick overview and testing you can find compose file inside [deploy](./deploy/local) directory.
## Project requirements
Some additional packages should be installed for host system to run application. 
```shell
sudo apt-get install \
    libgnutls28-dev \
    libcurl4-gnutls-dev \
    libexpat1-dev gettext   \
    libz-dev \
    libssl-dev \
    libcurl4-openssl-dev
```
## Standalone exporter run
Create or use existing python3.8+ virtual env. before standalone run. 
Requirements file can be found [here](./requirements.txt).
```shell
gunicorn run:app --reload
curl -v localhost:8000/probe?target=https://www.wikipedia.org/
```