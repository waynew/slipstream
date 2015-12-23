FROM python:3.5.1
MAINTAINER Wayne Werner <waynejwerner@gmail.com>

COPY dist/slipstream-0.1.0.tar.gz /slipstream.tar.gz
RUN python -m pip install tornado flask commonmark
RUN python -m pip install /slipstream.tar.gz

ENTRYPOINT slipstream-vortex
