# ==================================== BASE ====================================
ARG INSTALL_PYTHON_VERSION=${INSTALL_PYTHON_VERSION:-3.9}
FROM python:${INSTALL_PYTHON_VERSION}-slim AS base

WORKDIR /app
COPY ["./", "./"]
RUN pip install pipenv
ENV PYTHONPATH "${PYTHONPATH}:."

# =============================== PRODUCTION-BASE ==============================
FROM base AS production-base

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libc6-dev  \
    && rm -rf /var/lib/apt/lists/* \
    && pipenv install \
    && apt-get purge -y --auto-remove gcc libc6-dev

# ================================= PRODUCTION =================================
FROM production-base AS production
COPY supervisord.conf /etc/supervisor/supervisord.conf
COPY supervisord_programs /etc/supervisor/conf.d
EXPOSE 10090
ENTRYPOINT ["/bin/bash", "shell_scripts/supervisord_entrypoint.sh"]
CMD ["-c", "/etc/supervisor/supervisord.conf"]
