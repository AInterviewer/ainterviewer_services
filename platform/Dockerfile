# first stage
FROM python:3.8.12 AS builder

RUN apt update
RUN python -m pip install --upgrade pip

COPY platform/requirements.txt .

# install dependencies to the local user directory (eg. /root/.local)
RUN pip install --user -r requirements.txt

# second unnamed stage
FROM python:3.8.12-slim
WORKDIR /app

# copy only the dependencies installation from the 1st stage image
COPY --from=builder /root/.local /root/.local
COPY --from=builder /root/.local/bin /root/.local/bin
COPY src .

# update PATH environment variable
ENV PATH=/root/.local:$PATH

CMD [ "python", "main.py" ]
