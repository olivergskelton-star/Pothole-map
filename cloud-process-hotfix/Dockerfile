FROM gcr.io/pothole-warrior-upload/phw-cloud-process:persist-affected-tiles-20260717t111304z
COPY patch_runner.py /tmp/patch_runner.py
RUN python3 /tmp/patch_runner.py && rm /tmp/patch_runner.py
