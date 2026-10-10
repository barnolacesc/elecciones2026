# Internal extraction only. Never used by the static build or serving image.
FROM python:3.12-alpine@sha256:1b668429b3511ab407d8e00648891631b0b1a4d7e15e3ca70f38ab5b91ad4ab4
RUN apk add --no-cache poppler-utils=25.12.0-r1
COPY worker.py /worker.py
USER 65534:65534
ENTRYPOINT ["python3", "-I", "/worker.py"]
