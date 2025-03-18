FROM ghcr.io/camptocamp/docker-odoo-project:17.0-master-20250130
LABEL maintainer="Kal-It"
ARG UID=999
# Steps are grouped by dependency
# and ordered by compromizing cost and frequency

## Base requirements (Libs and packages)
# frequency: rarely
# cost:      high
COPY ./*requirements.txt /odoo/
COPY ./before-migrate-entrypoint.d /odoo/before-migrate-entrypoint.d
COPY ./start-entrypoint.d /odoo/start-entrypoint.d

# CSV Loader
# `parallel` + `importer.sh` are needed to load heavy files
COPY ./bin/importer.sh /odoo-bin/

## Prepare pip install
# frequency: never
# cost     : very light
COPY ./setup.py /odoo/

## Main activity
# frequency: always
# costs:     very high to very light
COPY ./src /odoo/src
COPY ./external-src /odoo/external-src
COPY ./local-src /odoo/local-src
COPY ./data /odoo/data/project
COPY ./songs /odoo/songs
COPY ./VERSION /odoo/
COPY ./migration.yml /odoo/
COPY ./history.yml /odoo/

USER root
# Install additional debian and python packages if needed
RUN set -x; \
    apt-get update \
    # && pip install --upgrade pip \
    && apt-get install -y --no-install-recommends \
    # if you need some dev packages for python packages, you need to clean them afterwards
    build-essential parallel libsasl2-dev libldap2-dev libssl-dev libmagic1 libpq-dev python3-dev \
    libffi-dev pkg-config libcairo2-dev libgirepository1.0-dev git cmake ffmpeg libsm6 libxext6 \
    # cleaning of dev packages
    && apt-get remove -y build-essential \
    # && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false -o APT::AutoRemove::SuggestsImportant=false \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Entrypoints
RUN chmod +x /odoo/before-migrate-entrypoint.d/* \
    && chmod +x /odoo/start-entrypoint.d/*

RUN usermod -u $UID -o odoo
RUN groupmod -g $UID odoo

RUN chown -R odoo:odoo /odoo

USER odoo
WORKDIR /odoo
# run in a virtualenv
RUN /odoo/.venv/bin/pip install --user -r requirements.txt
RUN /odoo/.venv/bin/pip install -r /odoo/src/requirements.txt
RUN /odoo/.venv/bin/pip install -e /odoo/src

## Environment
# frequency: sometimes
# cost:      very light
ENV ADDONS_PATH="/odoo/src/addons, \
  /odoo/local-src" \
  LIMIT_TIME_CPU=86400 \
  LIMIT_TIME_REAL=86400 \
  LIMIT_MEMORY_SOFT=1342177280 \
  LIMIT_MEMORY_HARD=1610612736 \
  ODOO_DATA_PATH=/odoo/data/project
