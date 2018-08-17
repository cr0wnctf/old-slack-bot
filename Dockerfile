FROM python:3

# Bundle app source
COPY . /src/
WORKDIR /src/

# Install requirements
RUN pip install --no-cache-dir -r requirements.txt

CMD exec python run.py
