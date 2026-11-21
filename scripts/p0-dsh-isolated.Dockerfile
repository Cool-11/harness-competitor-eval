FROM tb2-dsh-glibc-preflight:20261110
# New image only: retain the runtime, remove inherited task and home state.
RUN rm -rf /app /tests /logs /root /tmp /var/tmp && mkdir -p /work /root /tmp /var/tmp /control /state && chmod 1777 /tmp /var/tmp
WORKDIR /work
ENV DSH_HOME=/state/home
