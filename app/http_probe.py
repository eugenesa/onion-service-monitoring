import pycurl
import urllib.parse
from flask import current_app
from validators import url as url_validate
from validators import domain as domain_validate
from prometheus_client import Gauge, generate_latest, CollectorRegistry


def probe(url: str):
    registry = CollectorRegistry()

    dns_lookup_seconds = Gauge('dns_lookup_seconds', 'Time for DNS resolution', registry=registry)
    http_connect_seconds = Gauge('http_connect_seconds', 'Time to establish TCP connection', registry=registry)
    http_ttfb_seconds = Gauge('http_ttfb_seconds', 'Time To First Byte', registry=registry)
    http_total_seconds = Gauge('http_total_seconds', 'Time to complete request', registry=registry)
    http_status_code = Gauge('http_status_code', 'Response status code', registry=registry)
    http_up = Gauge('http_up', 'Indicates what site is up', registry=registry)
    probe_success = Gauge('probe_success', 'Displays whether or not the probe was a success', registry=registry)
    current_app.logger.info(f"Probing: {url}")

    if url_validate(url) or domain_validate(url):
        current_app.logger.debug("Url looks valid")
    else:
        current_app.logger.error(f"Provided URL {url} is not semantic correct")
        raise ValueError("Incorrect URL")

    try:
        timings = pycurl_probe(url)
    except RuntimeError:
        probe_success.set(False)
        return generate_latest(registry)

    if timings:
        dns_lookup_seconds.set(timings['dns'])
        http_connect_seconds.set(timings['tcp'])
        http_ttfb_seconds.set(timings['ttfb'])
        http_total_seconds.set(timings['total'])
        http_status_code.set(timings['response_code'])
        if int(timings['response_code']) < 500:
            http_up.set(True)
        else:
            http_up.set(False)
        probe_success.set(True)

    return generate_latest(registry)


def pycurl_probe(target: str) -> dict:
    c = pycurl.Curl()

    if ".onion" in urllib.parse.urlsplit(target).path:
        _target = target
        c.setopt(pycurl.PROXY, current_app.config['TOR']['host'])
        c.setopt(pycurl.PROXYPORT, current_app.config['TOR']['port'])
        c.setopt(pycurl.PROXYTYPE, pycurl.PROXYTYPE_SOCKS5_HOSTNAME)
    elif not urllib.parse.urlsplit(target).scheme:
        _target = f"https://{target}"
    else:
        _target = target

    c.setopt(pycurl.URL, _target)
    c.setopt(pycurl.FOLLOWLOCATION, 1)
    c.setopt(pycurl.WRITEFUNCTION, lambda _bytes: len(_bytes))
    try:
        content = c.perform()
    except:
        raise RuntimeError("Can't perform probe")

    response_code = c.getinfo(pycurl.HTTP_CODE)
    dns_time = c.getinfo(pycurl.NAMELOOKUP_TIME)
    tcp_time = c.getinfo(pycurl.CONNECT_TIME)
    ttfb_time = c.getinfo(pycurl.STARTTRANSFER_TIME)
    total_time = c.getinfo(pycurl.TOTAL_TIME)
    c.close()

    data = {
        'response_code': response_code,
        'dns': dns_time,
        'tcp': tcp_time,
        'ttfb': ttfb_time,
        'total': total_time
    }
    current_app.logger.info(f"PyCURL metrics: {data}")
    return data
